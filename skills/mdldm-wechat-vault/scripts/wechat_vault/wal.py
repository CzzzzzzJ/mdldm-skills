"""SQLite WAL checksum validation and committed-frame replay; no source writes."""
import struct
from .crypto import PAGE
from .errors import require

def checksum(data,order,state=(0,0)):
    require(len(data)%8==0,'WAL_ALIGNMENT','WAL 校验区未对齐。')
    words=struct.unpack(order+str(len(data)//4)+'I',data);a,b=state
    for i in range(0,len(words),2):
        a=(a+words[i]+b)&0xffffffff;b=(b+words[i+1]+a)&0xffffffff
    return a,b

def replay(path,dst,codec):
    if not path.exists() or path.stat().st_size==0:return {'committed_frames':0,'uncommitted_frames':0,'status':'absent'}
    require(path.stat().st_size>=32,'WAL_TRUNCATED','WAL 头不完整。')
    frames=[];last_commit=0;db_pages=None
    with path.open('rb') as f:
        header=f.read(32);magic,version,size=struct.unpack('>III',header[:12])
        require(magic in (0x377f0682,0x377f0683) and version==3007000 and size==PAGE,'WAL_PROFILE','WAL 配置不支持。')
        order='<' if magic==0x377f0682 else '>'
        state=checksum(header[:24],order)
        require(state==struct.unpack('>II',header[24:]),'WAL_CHECKSUM','WAL 头校验失败。')
        while True:
            offset=f.tell();fh=f.read(24)
            if not fh:break
            require(len(fh)==24,'WAL_TRUNCATED','WAL 尾部帧不完整。')
            data=f.read(PAGE);require(len(data)==PAGE,'WAL_TRUNCATED','WAL 页面不完整。')
            # A stale generation may remain after WAL reset. It is not current data.
            if fh[8:16]!=header[16:24]:break
            page,commit=struct.unpack('>II',fh[:8])
            require(0<page<=10000000,'WAL_PAGE_NUMBER','WAL 页码无效。')
            state=checksum(fh[:8]+data,order,state)
            require(state==struct.unpack('>II',fh[16:]),'WAL_CHECKSUM','WAL 帧校验失败，拒绝发布快照。')
            frames.append((offset,page))
            if commit:
                require(commit<=10000000,'WAL_COMMIT_SIZE','WAL 提交大小无效。')
                last_commit=len(frames);db_pages=commit
        with dst.open('r+b') as out:
            for offset,page in frames[:last_commit]:
                f.seek(offset+24);plain=codec.page(f.read(PAGE),page,wal=True)
                if page<=db_pages:out.seek((page-1)*PAGE);out.write(plain)
            if db_pages:out.truncate(db_pages*PAGE)
    return {'committed_frames':last_commit,'uncommitted_frames':len(frames)-last_commit,'status':'checksummed_commits_only'}
