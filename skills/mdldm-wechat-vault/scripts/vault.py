#!/usr/bin/env python3
import argparse,json,os
from wechat_vault.service import execute

def main():
    os.umask(0o077)
    p=argparse.ArgumentParser(description='麦当微信 Vault 0.2.0 — 独立本地实现')
    p.add_argument('--root');p.add_argument('--account',default='default')
    s=p.add_subparsers(dest='operation',required=True)
    for name in ('capabilities','discover','doctor'):s.add_parser(name)
    init=s.add_parser('init');init.add_argument('--db-dir',required=True);init.add_argument('--scope',choices=['messages','all'],default='messages')
    imp=s.add_parser('import-keys');imp.add_argument('--file',required=True)
    prep=s.add_parser('prepare-copy');prep.add_argument('--acknowledge-app-copy',action='store_true')
    cap=s.add_parser('capture-keys');group=cap.add_mutually_exclusive_group(required=True)
    group.add_argument('--pid',type=int);group.add_argument('--spawn-copy',action='store_true')
    cap.add_argument('--seconds',type=int,default=60)
    ref=s.add_parser('refresh');ref.add_argument('--offline-source',action='store_true')
    ses=s.add_parser('sessions');ses.add_argument('--limit',type=int,default=20)
    for name in ('history','material'):
        q=s.add_parser(name);q.add_argument('--chat',required=True);q.add_argument('--start',required=True);q.add_argument('--end',required=True)
        q.add_argument('--limit',type=int,default=200);q.add_argument('--offset',type=int,default=0)
        if name=='material':q.add_argument('--output',required=True)
    r=execute(vars(p.parse_args()));print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
