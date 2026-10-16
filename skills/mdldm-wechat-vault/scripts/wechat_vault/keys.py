import json,platform,shutil,subprocess,time,threading
from pathlib import Path
from .crypto import verify_key
from .discovery import selected_files
from .errors import VaultError,require
from .store import atomic_json,load

def import_keys(store,path):
    # Explicit migration/import only, never discover or read another tool's configuration.
    data=load(Path(path).expanduser());require(isinstance(data,dict),'KEY_FILE_FORMAT','需要数据库相对路径到 raw key 的 JSON 对象。')
    files=selected_files(store);accepted={}
    for rel,value in data.items():
        if rel not in files:continue
        verify_key(files[rel],value);accepted[rel]=value
    require(bool(accepted),'NO_VALID_KEYS','没有验证通过的目标数据库密钥。')
    with store.locked():
        merged=store.keys();merged.update(accepted);atomic_json(store.path/'keys.json',merged)
    return {'verified_keys':len(accepted),'discovered_databases':len(files)}

def prepare_copy(store):
    require(platform.system()=='Darwin','PLATFORM_UNSUPPORTED','目前只实现 macOS 微信 4.x 密钥获取。')
    original=Path('/Applications/WeChat.app');dest=store.root/'apps/WeChat.app'
    require(original.is_dir(),'WECHAT_MISSING','未找到官方微信应用。')
    require(not dest.exists(),'COPY_EXISTS','副本已存在，不自动覆盖。')
    dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    try:
        shutil.copytree(original,dest,symlinks=True)
        r=subprocess.run(['codesign','--force','--deep','--sign','-',str(dest)],capture_output=True,text=True)
        require(r.returncode==0,'SIGN_FAILED','副本重签失败；未修改原微信。')
    except Exception:
        if dest.exists():shutil.rmtree(dest)
        raise
    return {'prepared':True,'original_app_modified':False,'location':'runtime_root/apps/WeChat.app',
            'next':'正常退出原微信后 capture-keys --spawn-copy，并在副本里完成登录。'}

def capture(store,pid=None,spawn_copy=False,seconds=60):
    require(platform.system()=='Darwin','PLATFORM_UNSUPPORTED','密钥捕获当前只支持 macOS。')
    require(5<=seconds<=600,'INVALID_DURATION','捕获时长应为 5–600 秒。')
    require(bool(pid) != bool(spawn_copy),'CAPTURE_TARGET','必须选择 --pid 或 --spawn-copy。')
    import frida
    files=selected_files(store);salt_files={}
    for rel,p in files.items():
        with p.open('rb') as f:salt=f.read(16).hex()
        salt_files.setdefault(salt,[]).append((rel,p))
    device=frida.get_local_device();session=None;accepted={};lock=threading.Lock();statuses=set()
    try:
        if spawn_copy:
            require(not any(p.name in ('WeChat','Weixin') for p in device.enumerate_processes()),'WECHAT_RUNNING','先正常退出原微信，避免同时运行两个实例。')
            app=store.root/'apps/WeChat.app/Contents/MacOS/WeChat'
            require(app.is_file(),'COPY_MISSING','请先 prepare-copy，或选择已有微信 PID。')
            pid=device.spawn([str(app)])
        else:
            target=next((p for p in device.enumerate_processes() if p.pid==pid),None)
            require(target is not None and target.name in ('WeChat','Weixin'),'TARGET_NOT_WECHAT','只允许附加到明确选定的微信主进程。')
        session=device.attach(pid)
        js=Path(__file__).with_name('capture.js').read_text().replace('__TARGETS__',json.dumps(list(salt_files)))
        script=session.create_script(js)
        def message(msg,_data):
            if msg.get('type')=='error':statuses.add('script_error');return
            payload=msg.get('payload',{})
            if payload.get('kind')=='status':statuses.add(payload.get('value','unknown'));return
            if payload.get('kind')!='candidate':return
            for rel,p in salt_files.get(payload.get('salt'),[]):
                try:verify_key(p,payload['key'])
                except Exception:continue
                with lock:accepted[rel]=payload['key']
        script.on('message',message);script.load()
        if spawn_copy:device.resume(pid)
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            with lock:
                if len(accepted)==len(files):break
            time.sleep(.2)
        session.detach();session=None
    except VaultError:raise
    except Exception:
        raise VaultError('PROCESS_ACCESS_DENIED','无法访问微信进程。请检查系统授权；可使用独立重签副本流程，不会自动修改原应用。')
    finally:
        if session:
            try:session.detach()
            except Exception:pass
    with lock:result=dict(accepted)
    require(bool(result),'NO_KEYS_CAPTURED','未捕获有效目标密钥。请确认账号匹配，并在捕获期间打开对应聊天、收藏或朋友圈。')
    with store.locked():
        merged=store.keys();merged.update(result);atomic_json(store.path/'keys.json',merged)
    return {'verified_keys':len(result),'discovered_databases':len(files),'captured_all':len(result)==len(files),
            'collector_status':sorted(statuses),'raw_keys_output':False}
