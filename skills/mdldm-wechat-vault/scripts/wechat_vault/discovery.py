from pathlib import Path
import re
from .errors import require

def database_files(source):
    source=Path(source).resolve()
    require(source.is_dir(),'SOURCE_MISSING','源数据库目录不可访问。')
    result={}
    for p in sorted(source.rglob('*.db')):
        require(not p.is_symlink() and p.resolve().is_relative_to(source),'SOURCE_SYMLINK','源库包含符号链接，拒绝越界读取。')
        if p.is_file():result[p.relative_to(source).as_posix()]=p
    require(bool(result),'SOURCE_EMPTY','未找到数据库文件。')
    return result

def discover():
    base=Path.home()/'Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files'
    return [{'db_dir':str(p),'database_count':len(list(p.rglob('*.db')))} for p in sorted(base.glob('*/db_storage'))]

def inspect(store):
    from .crypto import verify_key
    keys=store.keys();rows=[]
    for rel,p in selected_files(store).items():
        k=keys.get(rel)
        state='missing'
        if k:
            try: verify_key(p,k);state='verified_first_page'
            except Exception:state='invalid_or_unsupported'
        rows.append({'database':rel,'key_status':state,'bytes':p.stat().st_size,'wal_present':Path(str(p)+'-wal').exists()})
    return {'databases':rows,'all_keys_verified':all(x['key_status']=='verified_first_page' for x in rows),
            'keys_are_not_output':True}


def selected_files(store):
    files=database_files(store.source())
    if store.config().get('scope','messages')=='all':return files
    selected={r:p for r,p in files.items() if r in ('contact/contact.db','session/session.db') or re.fullmatch(r'message/message_[0-9]+\.db',r)}
    require(bool(selected),'SOURCE_EMPTY','未发现消息范围内的数据库。')
    return selected
