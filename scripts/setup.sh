#!/usr/bin/env bash
# Khởi tạo dự án trên máy mới (macOS hoặc Ubuntu). Chạy từ gốc repo: bash scripts/setup.sh
# Hướng dẫn đầy đủ: README.md
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1. Công cụ hệ thống (ffmpeg, Python 3.11+)"
if [ "$(uname)" = "Darwin" ]; then
  command -v brew >/dev/null || { echo "Thiếu Homebrew: https://brew.sh"; exit 1; }
  for f in ffmpeg python@3.14; do brew list --versions "$f" >/dev/null || brew install "$f"; done
  PY="$(brew --prefix python@3.14)/bin/python3.14"
else
  if ! command -v ffmpeg >/dev/null || ! python3 -c "import venv, ensurepip" 2>/dev/null; then
    sudo apt-get update -y && sudo apt-get install -y ffmpeg python3-venv python3-pip
  fi
  PY=""
  for c in python3.13 python3.12 python3.11 python3; do      # Ubuntu 22.04 mặc định 3.10: thử bản mới hơn nếu đã cài
    if command -v "$c" >/dev/null && "$c" -c "import sys; sys.exit(sys.version_info < (3, 11))"; then PY="$c"; break; fi
  done
  [ -n "$PY" ] || { echo "Cần Python 3.11+ (Ubuntu 24.04 có sẵn 3.12). Ubuntu 22.04: sudo apt install python3.11 python3.11-venv"; exit 1; }
  "$PY" -c "import venv, ensurepip" 2>/dev/null || sudo apt-get install -y "$(basename "$PY")-venv"
fi
"$PY" -c "import sys; assert sys.version_info >= (3, 11), 'Cần Python 3.11+'"

echo "== 2. Môi trường Python của dự án (.venv)"
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

echo "== 3. Model giọng đọc vào .cache/ (VieNeu-TTS, khoảng 540 MB)"
.venv/bin/python scripts/setup_models.py

echo "== 4. Kiểm tra"
.venv/bin/python -m pytest -q
echo "Xong. Chạy thử: .venv/bin/python -m src.produce run tests/data/sample_story.txt --slug thu-nghiem"
