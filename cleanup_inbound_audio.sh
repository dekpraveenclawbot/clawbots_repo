#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/home/praveen/.openclaw/media/inbound"

find "$TARGET_DIR" -maxdepth 1 -type f \
  \( -iname "*.ogg" -o -iname "*.mp3" -o -iname "*.wav" -o -iname "*.m4a" -o -iname "*.aac" -o -iname "*.flac" \) \
  -mtime +1 -print -delete
