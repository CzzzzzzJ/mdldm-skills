import contextlib, fcntl, hashlib, json, os, re, tempfile
from pathlib import Path
from .errors import require
DEFAULT_ROOT=Path.home()/'Library/Application Support/mdldm-wechat-vault'

def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.pending-')
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'w') as f:
            json.dump(obj,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def load(path):
    return json.loads(Path(path).read_text())

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

class Store:
    def __init__(self,root=None,account='default'):
        require(bool(re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',account)),'INVALID_ACCOUNT','账号代号只能使用字母数字、下划线和短横线。')
        self.root=Path(root or DEFAULT_ROOT).expanduser().absolute()
        self.path=self.root/'accounts'/account
        self.account=account
    @contextlib.contextmanager
    def locked(self):
        self.path.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(self.path/'.lock',os.O_CREAT|os.O_RDWR,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX)
            yield
        finally:os.close(fd)
    def config(self):
        require((self.path/'config.json').exists(),'NOT_INITIALIZED','请先 init --db-dir 指定自己的 db_storage。')
        return load(self.path/'config.json')
    def source(self):return Path(self.config()['db_dir']).resolve()
    def keys(self):
        p=self.path/'keys.json'
        return load(p) if p.exists() else {}
    def current(self):
        p=self.path/'current.json'
        require(p.exists(),'NO_SNAPSHOT','尚无有效快照，请先 capture-keys / import-keys，再 refresh。')
        sid=load(p)['snapshot']
        require(bool(re.fullmatch(r'[a-f0-9]{32}',sid)),'INVALID_SNAPSHOT','快照索引无效。')
        return self.path/'snapshots'/sid
