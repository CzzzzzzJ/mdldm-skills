import os,platform,subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from .errors import VaultError,require
from .store import Store,atomic_json

CAPABILITIES={
 'source_discovery':'macos_wechat4','key_capture':'own_frida_memory_scan_and_pbkdf_hook',
 'key_validation':'sqlcipher4_page_hmac_sha512','database_decryption':'own_streaming_aes256cbc',
 'wal':'checksum_and_committed_replay','snapshot':'offline_verified_atomic_publish',
 'query':'own_sqlite_reader','attachments':'not_implemented','ai_provider':'not_implemented',
 'http':'not_implemented','runtime_dependency':'python_pycryptodome_zstandard_frida',
 'external_wechat_tools_required':False}

def epoch(s):
    try:
        d=datetime.fromisoformat(s)
        return int((d if d.tzinfo else d.replace(tzinfo=ZoneInfo('Asia/Shanghai'))).timestamp())
    except Exception:raise VaultError('INVALID_TIME','请使用 ISO 日期或时间，默认 Asia/Shanghai。')

def dispatch(r):
    from . import discovery,keys,query,snapshot
    op=r.get('operation');store=Store(r.get('root'),r.get('account','default'))
    if op=='capabilities':return {'items':CAPABILITIES}
    if op=='discover':return {'items':discovery.discover()}
    if op=='init':
        src=Path(r['db_dir']).expanduser().resolve()
        require(not store.root.resolve().is_relative_to(src) and not src.is_relative_to(store.root.resolve()),'DATA_LAYOUT','运行目录与微信源目录必须分离。')
        require(r.get('scope','messages') in ('messages','all'),'INVALID_SCOPE','scope 必须为 messages 或 all。')
        dbs=discovery.database_files(src)
        with store.locked():
            if (store.path/'config.json').exists():require(store.source()==src,'ACCOUNT_ALREADY_BOUND','该账号代号已绑定其他源目录，请换一个账号代号。')
            atomic_json(store.path/'config.json',{'version':1,'db_dir':str(src),'account':store.account,'scope':r.get('scope','messages')})
        return {'items':{'initialized':True,'database_count':len(dbs),'account':store.account}}
    if op=='doctor':return {'items':discovery.inspect(store)}
    if op=='import-keys':return {'items':keys.import_keys(store,r['file'])}
    if op=='prepare-copy':
        require(r.get('acknowledge_app_copy') is True,'APP_COPY_ACK_REQUIRED','此操作复制并重签微信副本，可能需要重新登录及授权；请明确使用 --acknowledge-app-copy。')
        return {'items':keys.prepare_copy(store)}
    if op=='capture-keys':return {'items':keys.capture(store,r.get('pid'),r.get('spawn_copy',False),r.get('seconds',60))}
    if op=='refresh':return {'items':snapshot.refresh(store,r.get('offline_source',False))}
    require(op in ('sessions','history','material'),'CAPABILITY_UNAVAILABLE','请求的能力尚未实现。')
    limit=r.get('limit',200);offset=r.get('offset',0)
    require(isinstance(limit,int) and not isinstance(limit,bool) and 1<=limit<=2000,'INVALID_LIMIT','limit 应为 1–2000。')
    require(isinstance(offset,int) and not isinstance(offset,bool) and 0<=offset<=100000,'INVALID_OFFSET','offset 应为 0–100000。')
    if op=='sessions':return query.sessions(store,limit)
    start,end=epoch(r.get('start')),epoch(r.get('end'))
    require(start<end,'INVALID_RANGE','结束时间必须晚于开始时间。')
    chat=r.get('chat');require(isinstance(chat,str) and 0<len(chat)<=512,'INVALID_CHAT','需要精确 chat_id。')
    result=query.history(store,chat,start,end,limit,offset)
    if op=='material':
        import json
        path=Path(r['output']).expanduser()
        require(path.parent.is_dir(),'OUTPUT_DIRECTORY_MISSING','请先创建私有导出目录。')
        try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError:raise VaultError('OUTPUT_EXISTS','文件已存在，不覆盖。')
        try:
            with os.fdopen(fd,'w') as f:json.dump(result,f,ensure_ascii=False,indent=2)
        except Exception:path.unlink(missing_ok=True);raise
        return {'items':{'exported_messages':len(result['items'])},'meta':result['meta']}
    return result

def execute(request):
    try:return {'schema_version':'2.0','ok':True,**dispatch(request)}
    except VaultError as e:return {'schema_version':'2.0','ok':False,'error':{'code':e.code,'message':e.message}}
    except ImportError:return {'schema_version':'2.0','ok':False,'error':{'code':'DEPENDENCY_MISSING','message':'请使用 bootstrap 创建的 Python 环境运行。'}}
    except Exception:return {'schema_version':'2.0','ok':False,'error':{'code':'LOCAL_OPERATION_FAILED','message':'本地操作失败；未输出路径、密钥或数据库内容。'}}
