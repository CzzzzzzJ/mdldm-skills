#!/bin/sh
# 用风格库的渲染器把 selftest/ 渲染成 2 秒 mp4，确认整条链路能出片。
set -e
HERE=$(cd "$(dirname "$0")/.." && pwd)
LIB=${LEMO_OPUSCAR_HOME:-$HOME/lemo-opuscar}
[ -f "$LIB/core/render/video.mjs" ] || { echo "✗ 没找到风格库：$LIB（先做第 3 步）"; exit 1; }
WORK=$(mktemp -d); cp "$HERE/selftest/index.html" "$WORK/"
OUT=$HOME/video-studio-selftest.mp4
cd "$LIB"
node core/render/video.mjs "$WORK" --fps 24 --out "$WORK/video.mp4"
ffmpeg -v error -y -i "$WORK/video.mp4" -f lavfi -i "sine=frequency=440:duration=2" -c:v copy -c:a aac -shortest "$OUT"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
echo "测试片：${OUT}  时长 ${d} 秒"
echo "SELFTEST OK"
