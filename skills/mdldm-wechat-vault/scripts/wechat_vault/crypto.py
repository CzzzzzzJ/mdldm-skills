"""Own SQLCipher-4 page reader: fixed 4096/80/SHA512 profile, fail closed."""
import hashlib,hmac,struct
from Crypto.Cipher import AES
from .errors import VaultError,require
PAGE=4096;RESERVE=80;BODY=PAGE-RESERVE;MAGIC=b'SQLite format 3\0'

def decode_key(value):
    try:key=bytes.fromhex(value)
    except (TypeError,ValueError):raise VaultError('INVALID_KEY','密钥格式不正确。')
    require(len(key)==32,'INVALID_KEY','需要 32 字节 raw key。')
    return key

class Codec:
    def __init__(self,key,salt):
        require(len(key)==32 and len(salt)==16,'INVALID_KEY','密钥或盐长度错误。')
        self.key=key;self.salt=salt
        self.mac_key=hashlib.pbkdf2_hmac('sha512',key,bytes(b^0x3a for b in salt),2,32)
    def page(self,data,number,wal=False):
        require(len(data)==PAGE and number>0,'PAGE_SIZE','数据库页面长度不支持。')
        # SQLCipher/WCDB variants may store page 1 in WAL with or without salt prefix.
        starts=[16,0] if wal and number==1 else [16 if number==1 else 0]
        for start in starts:
            tag=hmac.new(self.mac_key,data[start:BODY+16]+struct.pack('<I',number),'sha512').digest()
            if hmac.compare_digest(tag,data[BODY+16:]):
                plain=AES.new(self.key,AES.MODE_CBC,data[BODY:BODY+16]).decrypt(data[start:BODY])
                result=(MAGIC if start==16 else b'')+plain+bytes(RESERVE)
                if number==1:
                    require(result[:16]==MAGIC and result[16:18]==b'\x10\x00' and result[20]==80,'PROFILE_UNSUPPORTED','数据库页面布局与支持的配置不匹配。')
                return result
        raise VaultError('PAGE_AUTH_FAILED','页面认证失败：密钥无效、数据损坏或加密配置不兼容。')

def verify_key(path,value):
    with path.open('rb') as f:page=f.read(PAGE)
    codec=Codec(decode_key(value),page[:16]);codec.page(page,1)
    return codec

def decrypt_database(src,dst,value):
    codec=verify_key(src,value)
    require(src.stat().st_size%PAGE==0,'TRUNCATED_DATABASE','数据库长度不是完整页面。')
    with src.open('rb') as inp,dst.open('xb') as out:
        number=0
        while True:
            data=inp.read(PAGE)
            if not data:break
            number+=1;out.write(codec.page(data,number))
    return codec
