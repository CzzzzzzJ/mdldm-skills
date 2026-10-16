#!/usr/bin/env python3
import argparse, os, subprocess, sys, venv
from pathlib import Path
p=argparse.ArgumentParser(description='Install isolated generic runtime; no external WeChat tools')
p.add_argument('--venv',default=str(Path.home()/'Library/Application Support/mdldm-wechat-vault/runtime'))
a=p.parse_args()
if sys.version_info < (3,10): raise SystemExit('Python 3.10+ required')
target=Path(a.venv).expanduser().absolute()
if target.is_symlink(): raise SystemExit('Refusing symlink runtime')
os.umask(0o077)
venv.EnvBuilder(with_pip=True).create(target)
python=target/'bin/python'
subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','-r',str(Path(__file__).resolve().parents[1]/'requirements.txt')],check=True)
print('Runtime ready:',python)
print('Run this Python with scripts/vault.py; no wx-cli or other Skill required.')
