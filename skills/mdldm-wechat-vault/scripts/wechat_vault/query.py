"""Read only our published snapshots, never another CLI or global tool configuration."""
import hashlib,sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from .errors import VaultError,require
from .store import load
TZ=ZoneInfo('Asia/Shanghai')

def connect(path):
    require(path.is_file(),'DATABASE_MISSING','快照缺少请求的数据库。')
    c=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True)
    c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON');return c

def tables(c):return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
def columns(c,t):return {r[1] for r in c.execute('PRAGMA table_info("'+t.replace('"','""')+'")')}
def quote(s):return '"'+s.replace('"','""')+'"'

def text(value):
    if value is None:return ''
    if isinstance(value,str):return value
    if isinstance(value,bytes):
        if value.startswith(bytes.fromhex('28b52ffd')):
            try:
                import zstandard
                value=zstandard.ZstdDecompressor().decompress(value,max_output_size=16*1024*1024)
            except Exception:return '[压缩内容未成功解析]'
        try:return value.decode('utf-8')
        except UnicodeError:return '[二进制内容未解析]'
    return str(value)

def names(snapshot):
    p=snapshot/'data/contact/contact.db';result={}
    if not p.exists():return result
    with connect(p) as c:
        if 'contact' not in tables(c):return result
        cols=columns(c,'contact')
        if 'username' not in cols:return result
        for row in c.execute('SELECT * FROM contact'):
            d=dict(row);u=d['username'];result[u]=d.get('remark') or d.get('nick_name') or u
    return result

def metadata(snapshot):
    manifest=load(snapshot/'manifest.json')
    return {'snapshot':manifest['snapshot'],'snapshot_at':manifest['created_at'],
            'consistency':manifest['consistency'],'scope':manifest['scope'],
            'all_selected_databases_decrypted':manifest['all_selected_databases_decrypted'],
            'live':False,'phone_history_complete':False,'attachments_resolved':False}

def sessions(store,limit):
    snap=store.current();display=names(snap)
    with connect(snap/'data/session/session.db') as c:
        require('SessionTable' in tables(c),'SCHEMA_UNSUPPORTED','会话表结构尚不支持。')
        required={'username','last_timestamp','summary'}
        require(required<=columns(c,'SessionTable'),'SCHEMA_UNSUPPORTED','会话字段结构尚不支持。')
        rows=c.execute('SELECT * FROM SessionTable ORDER BY last_timestamp DESC LIMIT ?',(limit+1,)).fetchall()
    items=[{'chat_id':r['username'],'name':display.get(r['username'],r['username']),
            'timestamp':r['last_timestamp'],'preview':text(r['summary'])} for r in rows[:limit]]
    return {'items':items,'meta':{**metadata(snap),'preview_only':True,'has_more':len(rows)>limit}}

def history(store,chat,start,end,limit,offset=0):
    snap=store.current();display=names(snap);table='Msg_'+hashlib.md5(chat.encode()).hexdigest()
    shards=sorted(p for p in (snap/'data/message').glob('message_*.db') if p.stem[8:].isdigit())
    require(bool(shards),'DATABASE_MISSING','快照没有消息分库。')
    results=[];found=0
    for path in shards:
        with connect(path) as c:
            if table not in tables(c):continue
            found+=1;cols=columns(c,table)
            required={'local_id','create_time','local_type','message_content'}
            require(required<=cols,'SCHEMA_UNSUPPORTED','消息表字段结构不支持，不返回不完整结果。')
            senders={}
            if 'Name2Id' in tables(c) and 'user_name' in columns(c,'Name2Id'):
                senders={r[0]:r[1] for r in c.execute('SELECT rowid,user_name FROM Name2Id')}
            sql='SELECT * FROM '+quote(table)+' WHERE create_time>=? AND create_time<? ORDER BY create_time,local_id LIMIT ?'
            for row in c.execute(sql,(start,end,offset+limit+1)):
                d=dict(row);kind=int(d['local_type'])&0xffffffff
                body=text(d['message_content']);sender=senders.get(d.get('real_sender_id'),'')
                if not body and d.get('compress_content'):body=text(d['compress_content'])
                if kind in (3,34,43,47):body={3:'[图片]',34:'[语音]',43:'[视频]',47:'[表情]'}[kind]
                source={'database':'message/'+path.name,'table':table,'local_id':d['local_id'],'server_id':d.get('server_id')}
                uid=hashlib.sha256((store.account+'|'+source['database']+'|'+table+'|'+str(d['local_id'])).encode()).hexdigest()
                results.append({'id':uid,'chat_id':chat,'timestamp':d['create_time'],
                    'time':datetime.fromtimestamp(d['create_time'],TZ).isoformat(),'sender_id':sender,
                    'sender':display.get(sender,sender),'type':kind,'content':body,'source':source,
                    'attachment_status':'not_resolved'})
    require(found>0,'CHAT_NOT_FOUND','快照中没有这个精确会话的消息表；不等同于从未有过聊天。')
    results.sort(key=lambda x:(x['timestamp'],x['source']['database'],x['source']['local_id']))
    return {'items':results[offset:offset+limit],'meta':{**metadata(snap),'has_more':len(results)>offset+limit,
            'offset':offset,'limit':limit,'queried_shards':len(shards),'matched_shards':found,
            'start_inclusive':start,'end_exclusive':end,'ordering':'timestamp,database,local_id',
            'completeness':'query_of_verified_local_snapshot_only'}}
