// Own Frida collector: only candidates matching configured database salts leave the process.
'use strict';
const targets = __TARGETS__;
const seen = new Set();
function hex(p,n) {
  if (p.isNull() || n<1 || n>256) return null;
  try { return Array.from(new Uint8Array(p.readByteArray(n))).map(x=>x.toString(16).padStart(2,'0')).join(''); }
  catch (_) {return null;}
}
function offer(salt,key) {
  if (!salt || !key || !targets.includes(salt) || key.length!==64) return;
  const id=salt+key;if(seen.has(id))return;seen.add(id);
  send({kind:'candidate',salt:salt,key:key});
}
let installed=false;
function hook() {
  if(installed)return;
  for(const module of Process.enumerateModules()) {
    let exp=[];try {exp=module.enumerateExports();}catch(_){continue;}
    const symbol=exp.find(e=>e.name==='CCKeyDerivationPBKDF');
    if(!symbol)continue;
    Interceptor.attach(symbol.address,{
      onEnter(a){this.p=a[1];this.n=a[2].toInt32();this.s=a[3];this.sn=a[4].toInt32();this.out=a[7];this.on=a[8].toInt32();},
      onLeave(ret){
        if(ret.toInt32()!==0 || this.sn!==16)return;
        const salt=hex(this.s,this.sn);if(!targets.includes(salt))return;
        if(this.on===32)offer(salt,hex(this.out,32));
        if(this.n===32)offer(salt,hex(this.p,32));
        if(this.n>=66 && this.n<=100) {
          try {const text=this.p.readUtf8String(this.n);const m=text.match(/^x'([0-9a-fA-F]{64})/);if(m)offer(salt,m[1].toLowerCase());}catch(_){}
        }
      }
    });
    installed=true;send({kind:'status',value:'hook_ready'});break;
  }
}
hook();const timer=setInterval(hook,500);
// Bounded synchronous chunk reads, scheduled between chunks so hooks remain responsive.
let ranges=Process.enumerateRanges({protection:'rw-',coalesce:true});
let ri=0,offset=0,total=0;const budget=1024*1024*1024;
function step() {
  if(ri>=ranges.length || total>=budget){send({kind:'status',value:'memory_scan_finished'});setTimeout(()=>{ranges=Process.enumerateRanges({protection:'rw-',coalesce:true});ri=0;offset=0;total=0;step();},5000);return;}
  const range=ranges[ri];const size=Math.min(1024*1024,range.size-offset,budget-total);
  if(size<=0){ri++;offset=0;setImmediate(step);return;}
  try {
    const bytes=new Uint8Array(range.base.add(offset).readByteArray(size));
    for(let i=0;i+99<=bytes.length;i++) {
      if(bytes[i]!==120 || bytes[i+1]!==39 || bytes[i+98]!==39)continue;
      let text='';for(let j=2;j<98;j++)text+=String.fromCharCode(bytes[i+j]);
      if(/^[a-fA-F0-9]{96}$/.test(text))offer(text.slice(64).toLowerCase(),text.slice(0,64).toLowerCase());
    }
  }catch(_){}
  total+=size;
  if(offset+size>=range.size){ri++;offset=0;}else{offset+=size-100;}
  setImmediate(step);
}
setImmediate(step);
