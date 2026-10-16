#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo '需要先安装 Python 3.10+：https://www.python.org/downloads/macos/'
  exit 1
fi
exec python3 scripts/bootstrap.py
