#!/bin/sh
# 体检：只检查，不改动任何东西。最后一行 MISSING= 后面是缺少的项目（空 = 系统工具齐了）。
ok() { printf '  ✓ %-10s %s\n' "$1" "$2"; }
no() { printf '  ✗ %-10s %s\n' "$1" "$2"; MISSING="$MISSING $1"; }
MISSING=""
case "$(uname -s 2>/dev/null)" in Darwin) OS=macOS ;; Linux) OS=Linux ;; MINGW*|MSYS*|CYGWIN*) OS=Windows ;; *) OS=unknown ;; esac
echo "系统：$OS $(uname -m 2>/dev/null)"
if command -v git >/dev/null 2>&1; then ok git "$(git --version | cut -d' ' -f3)"; else no git "没装"; fi
if command -v node >/dev/null 2>&1; then v=$(node -p 'process.versions.node'); if [ "${v%%.*}" -ge 20 ] 2>/dev/null; then ok node "$v"; else no node "$v，需要 20 以上"; fi; else no node "没装"; fi
if command -v ffmpeg >/dev/null 2>&1; then v=$(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3); m=$(echo "$v" | sed 's/^n//; s/[^0-9].*//')
  if [ -n "$m" ] && [ "$m" -lt 7 ] 2>/dev/null; then no ffmpeg "$v，需要 7 以上"; elif [ -z "$m" ]; then ok ffmpeg "$v（开发版，版本号看不出，按可用处理）"; else ok ffmpeg "$v"; fi
else no ffmpeg "没装"; fi
PY=""
for c in python3.12 python3.13 python3.11 python3 python; do "$c" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null && { PY=$c; break; }; done
if command -v uv >/dev/null 2>&1; then ok python "有 uv（会自动准备 Python）"; elif [ -n "$PY" ]; then ok python "$("$PY" -V 2>&1 | cut -d' ' -f2)"; else no python "需要 3.11 以上，或装 uv"; fi
case $OS in macOS) command -v brew >/dev/null 2>&1 && echo "  · 安装器    Homebrew 可用" || echo "  · 安装器    没有 Homebrew" ;; Windows) command -v winget >/dev/null 2>&1 && echo "  · 安装器    winget 可用" || echo "  · 安装器    没找到 winget" ;; esac
free=$(df -Pk "$HOME" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1048576}'); [ -n "$free" ] && { [ "$free" -ge 3 ] && echo "  · 磁盘      主目录剩余约 ${free} GB" || echo "  ! 磁盘      主目录只剩约 ${free} GB，建议留出 3 GB"; }
LIB=${LEMO_OPUSCAR_HOME:-$HOME/lemo-opuscar}
if [ -f "$LIB/core/render/video.mjs" ]; then echo "  ✓ 风格库    $LIB"; [ -d "$LIB/node_modules/playwright-core" ] && [ -x "$LIB/.venv/bin/python" -o -x "$LIB/.venv/Scripts/python.exe" ] && echo "  ✓ 渲染依赖  已安装" || echo "  ✗ 渲染依赖  还没装（第 4 步）"
else echo "  ✗ 风格库    还没下载（第 3 步）"; fi
echo "MISSING=$(echo $MISSING)"
