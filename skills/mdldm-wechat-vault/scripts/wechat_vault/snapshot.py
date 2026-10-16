import json,os,shutil,sqlite3,subprocess,tempfile,uuid
from datetime import datetime,timezone
from pathlib import Path
from .crypto import decrypt_database
from .discovery import selected_files
from .errors import require
from .store import atomic_json,digest
from .wal import replay

def wechat_running():
    for name in ('WeChat','Weixin'):
        p=subprocess.run(['pgrep','-x',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if p.returncode==0:return True
    return False

def inventory(store):
    files={}
    for rel,p in selected_files(store).items():
        files[rel]=p
        for suffix in ('-wal','-journal'):
            side=Path(str(p)+suffix)
            if side.exists():
                require(not side.is_symlink(),'SOURCE_SYMLINK','源日志包含符号链接。')
                require(suffix!='-journal' or side.stat().st_size==0,'ROLLBACK_JOURNAL','检测到回滚日志，暂不支持此快照。')
                if suffix=='-wal':files[rel+suffix]=side
    return files

def signature(files):return {r:(p.stat().st_size,p.stat().st_mtime_ns,p.stat().st_ino,digest(p)) for r,p in files.items()}

def refresh(store,offline=False):
    require(offline or not wechat_running(),'SOURCE_BUSY','请正常退出微信后 refresh；离线副本可使用 --offline-source，不能用于运行中的原库。')
    source=store.source()
    live_root=Path.home()/'Library/Containers'
    require(not offline or not source.is_relative_to(live_root),'OFFLINE_SOURCE_INVALID','原微信容器不能标记为离线副本。')
    with store.locked():
        files=inventory(store);before=signature(files);keys=store.keys()
        missing=[r for r in files if r.endswith('.db') and r not in keys]
        require(not missing,'KEYS_MISSING',f'有 {len(missing)} 个数据库缺少密钥；请运行 doctor 查看。')
        staging=store.path/'staging';staging.mkdir(exist_ok=True,mode=0o700)
        temporary=Path(tempfile.mkdtemp(dir=staging));encrypted=temporary/'encrypted';plain=temporary/'data'
        try:
            for rel,p in files.items():
                dest=encrypted/rel;dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                shutil.copyfile(p,dest);os.chmod(dest,0o600)
            after=signature(inventory(store))
            require(before==after and (offline or not wechat_running()),'SOURCE_CHANGED','读取时源数据库发生变化，旧快照保持不变。')
            require(all(digest(encrypted/r)==v[3] for r,v in before.items()),'COPY_MISMATCH','快照复制校验失败。')
            records=[]
            for rel in sorted(r for r in files if r.endswith('.db')):
                dst=plain/rel;dst.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                codec=decrypt_database(encrypted/rel,dst,keys[rel]);os.chmod(dst,0o600)
                wal=replay(Path(str(encrypted/rel)+'-wal'),dst,codec)
                # A private immutable snapshot must not enter SQLite's live WAL protocol.
                with dst.open('r+b') as f:f.seek(18);f.write(bytes([1,1]))
                con=sqlite3.connect(dst.as_uri()+'?mode=ro&immutable=1',uri=True)
                try:result=con.execute('PRAGMA integrity_check').fetchall()
                finally:con.close()
                require(result==[('ok',)],'SQLITE_INTEGRITY','解密后的数据库结构校验失败。')
                records.append({'database':rel,'page_auth':'hmac_sha512_verified','sqlite_integrity':'ok','wal':wal})
            sid=uuid.uuid4().hex
            manifest={'version':1,'snapshot':sid,'account':store.account,'created_at':datetime.now(timezone.utc).isoformat(),
                      'consistency':'offline_source_hash_checked' if offline else 'wechat_stopped_source_hash_checked',
                      'scope':store.config().get('scope','messages')+'_local_snapshot_not_phone_or_cloud','databases':records,'all_selected_databases_decrypted':True}
            atomic_json(temporary/'manifest.json',manifest);shutil.rmtree(encrypted)
            target=store.path/'snapshots'/sid;target.parent.mkdir(exist_ok=True,mode=0o700)
            os.replace(temporary,target);atomic_json(store.path/'current.json',{'snapshot':sid})
            return {'snapshot':sid,'database_count':len(records),'consistency':manifest['consistency']}
        finally:
            if temporary.exists():shutil.rmtree(temporary)
