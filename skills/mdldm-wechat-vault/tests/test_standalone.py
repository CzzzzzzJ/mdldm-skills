import hashlib,json,os,sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from wechat_vault.crypto import verify_key,decrypt_database
from wechat_vault.errors import VaultError
from wechat_vault.keys import import_keys
from wechat_vault.query import history
from wechat_vault.service import execute
from wechat_vault.snapshot import refresh
from wechat_vault.store import Store,atomic_json
from wechat_vault.wal import replay
from fixtures import sqlite_fixture,encrypt,wal_file

class Standalone(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.key=os.urandom(32);self.salt=os.urandom(16)
        self.source=self.p/'source';self.source.mkdir();self.store=Store(self.p/'vault','test')
        self.chat='synthetic@chatroom';self.table='Msg_'+hashlib.md5(self.chat.encode()).hexdigest()
        self.sql=f'CREATE TABLE {self.table}(local_id INTEGER PRIMARY KEY,create_time INTEGER,local_type INTEGER,message_content TEXT); INSERT INTO {self.table} VALUES(1,1792080000,1,"before");'
        self.plain=self.p/'plain.db';sqlite_fixture(self.plain,self.sql)
        self.db=self.source/'message/message_0.db';encrypt(self.plain,self.db,self.key,self.salt)
        self.store.path.mkdir(parents=True)
        atomic_json(self.store.path/'config.json',{'db_dir':str(self.source),'account':'test'})
        atomic_json(self.store.path/'keys.json',{'message/message_0.db':self.key.hex()})
    def tearDown(self):self.tmp.cleanup()
    def test_full_independent_pipeline(self):
        with patch.dict(os.environ,{'PATH':'/nonexistent'}):
            out=refresh(self.store,offline=True)
            r=history(self.store,self.chat,1792080000,1792166400,20)
        self.assertEqual(r['items'][0]['content'],'before')
        self.assertEqual(r['items'][0]['source']['database'],'message/message_0.db')
        self.assertEqual(out['database_count'],1)
    def test_wrong_key_and_tamper(self):
        with self.assertRaises(VaultError):verify_key(self.db,os.urandom(32).hex())
        content=bytearray(self.db.read_bytes());content[100]^=1;self.db.write_bytes(content)
        with self.assertRaises(VaultError):verify_key(self.db,self.key.hex())
    def test_wal_committed_only(self):
        changed=self.p/'changed.db';sqlite_fixture(changed,self.sql.replace('before','commit'))
        later=self.p/'later.db';sqlite_fixture(later,self.sql.replace('before','ignore'))
        # Both fixtures contain schema page 1 and table root page 2.
        data=changed.read_bytes();tail=later.read_bytes()
        entries=[(1,0,data[:4096]),(2,2,data[4096:8192]),(2,0,tail[4096:8192])]
        wal_file(Path(str(self.db)+'-wal'),entries,self.key,self.salt)
        refresh(self.store,offline=True)
        self.assertEqual(history(self.store,self.chat,0,2000000000,10)['items'][0]['content'],'commit')
        manifest=json.loads((self.store.current()/'manifest.json').read_text())
        self.assertEqual(manifest['databases'][0]['wal']['uncommitted_frames'],1)
    def test_big_endian_wal(self):
        page=self.plain.read_bytes()[4096:8192]
        wal_file(Path(str(self.db)+'-wal'),[(2,2,page)],self.key,self.salt,True)
        refresh(self.store,offline=True)
        self.assertEqual(history(self.store,self.chat,0,2000000000,10)['items'][0]['content'],'before')
    def test_corrupt_wal_keeps_previous(self):
        refresh(self.store,offline=True);previous=self.store.current()
        path=Path(str(self.db)+'-wal')
        wal_file(path,[(2,2,self.plain.read_bytes()[4096:8192])],self.key,self.salt)
        raw=bytearray(path.read_bytes());raw[-1]^=1;path.write_bytes(raw)
        with self.assertRaises(VaultError):refresh(self.store,offline=True)
        self.assertEqual(self.store.current(),previous)
        self.assertEqual(list((self.store.path/'staging').iterdir()),[])
    def test_missing_key_no_publish(self):
        atomic_json(self.store.path/'keys.json',{})
        with self.assertRaises(VaultError):refresh(self.store,offline=True)
        self.assertFalse((self.store.path/'current.json').exists())
    def test_live_refused(self):
        with patch('wechat_vault.snapshot.wechat_running',return_value=True):
            with self.assertRaises(VaultError):refresh(self.store)
    def test_source_change_rejected(self):
        import wechat_vault.snapshot as mod
        real=mod.signature;count=[0]
        def changed(files):
            result=real(files);count[0]+=1
            if count[0]==2:result['different']=(0,0,0,'changed')
            return result
        with patch.object(mod,'signature',side_effect=changed):
            with self.assertRaises(VaultError):refresh(self.store,offline=True)
        self.assertFalse((self.store.path/'current.json').exists())
    def test_import_verifies_and_does_not_print_key(self):
        keyfile=self.p/'import.json';keyfile.write_text(json.dumps({'message/message_0.db':self.key.hex()}))
        r=import_keys(self.store,keyfile)
        self.assertNotIn(self.key.hex(),json.dumps(r))
    def test_precise_time_and_pagination(self):
        refresh(self.store,offline=True)
        self.assertEqual(history(self.store,self.chat,0,1792080000,10)['items'],[])
        self.assertEqual(history(self.store,self.chat,1792080000,2000000000,10,1)['items'],[])
    def test_account_binding_and_no_crossing(self):
        req={'operation':'init','root':str(self.p/'vault'),'account':'test','db_dir':str(self.source)}
        self.assertTrue(execute(req)['ok'])
        req['db_dir']=str(self.p/'other');Path(req['db_dir']).mkdir();(Path(req['db_dir'])/'x.db').touch()
        self.assertFalse(execute(req)['ok'])
    def test_no_external_tool_runtime_references(self):
        code=Path(__file__).resolve().parents[1]/'scripts'
        for p in code.rglob('*.py'):
            t=p.read_text()
            self.assertNotIn('.wx-cli',t)
            self.assertNotIn('yichen',t.lower())
    def test_unknown_chat_is_error(self):
        refresh(self.store,offline=True)
        with self.assertRaises(VaultError):history(self.store,'unknown',0,2000000000,10)

if __name__=='__main__':unittest.main()
