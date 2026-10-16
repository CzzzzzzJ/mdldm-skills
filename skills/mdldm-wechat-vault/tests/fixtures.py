"""SQLite itself builds reserved-byte DBs; independent test encryptor creates SQLCipher profile."""
import ctypes,ctypes.util,hashlib,hmac,os,struct
from pathlib import Path
from Crypto.Cipher import AES
PAGE=4096

def sqlite_fixture(path,sql):
    lib=ctypes.CDLL(ctypes.util.find_library('sqlite3'))
    db=ctypes.c_void_p()
    lib.sqlite3_open.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_void_p)]
    lib.sqlite3_exec.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p]
    lib.sqlite3_file_control.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int,ctypes.c_void_p]
    lib.sqlite3_close.argtypes=[ctypes.c_void_p]
    assert lib.sqlite3_open(str(path).encode(),ctypes.byref(db))==0
    try:
        reserve=ctypes.c_int(80)
        assert lib.sqlite3_file_control(db,b'main',38,ctypes.byref(reserve))==0
        assert lib.sqlite3_exec(db,('PRAGMA page_size=4096; VACUUM; '+sql).encode(),None,None,None)==0
    finally:lib.sqlite3_close(db)
    assert path.read_bytes()[20]==80

def encrypted_page(data,number,key,salt,wal_full_first=False):
    offset=0 if wal_full_first else (16 if number==1 else 0)
    iv=os.urandom(16);cipher=AES.new(key,AES.MODE_CBC,iv).encrypt(data[offset:4016])
    auth_key=hashlib.pbkdf2_hmac('sha512',key,bytes(x^58 for x in salt),2,32)
    tag=hmac.new(auth_key,cipher+iv+number.to_bytes(4,'little'),hashlib.sha512).digest()
    return (salt if offset else b'')+cipher+iv+tag

def encrypt(src,dst,key,salt):
    data=src.read_bytes();dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(b''.join(encrypted_page(data[i:i+PAGE],i//PAGE+1,key,salt) for i in range(0,len(data),PAGE)))

def wal_file(path,entries,key,salt,bigendian=False):
    # Independent rolling checksum, no production module imports.
    order='big' if bigendian else 'little'
    def calc(data,state=(0,0)):
        a,b=state
        for pos in range(0,len(data),8):
            a=(a+int.from_bytes(data[pos:pos+4],order)+b)%(2**32)
            b=(b+int.from_bytes(data[pos+4:pos+8],order)+a)%(2**32)
        return a,b
    generation=os.urandom(8)
    header=struct.pack('>IIII',0x377f0683 if bigendian else 0x377f0682,3007000,4096,0)+generation
    state=calc(header);output=header+struct.pack('>II',*state)
    for pgno,commit,plain in entries:
        frame=struct.pack('>II',pgno,commit)+generation
        data=encrypted_page(plain,pgno,key,salt,wal_full_first=pgno==1)
        state=calc(frame[:8]+data,state);output+=frame+struct.pack('>II',*state)+data
    path.write_bytes(output)
