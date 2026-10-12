#!/usr/bin/env bash
# Khởi tạo dự án trên máy Mac mới. Chạy từ gốc repo: bash scripts/setup.sh
# Hướng dẫn đầy đủ (kể cả bước phải làm tay): docs/setup.md
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1. Công cụ hệ thống (Homebrew)"
command -v brew >/dev/null || { echo "Thiếu Homebrew: https://brew.sh"; exit 1; }
for f in ffmpeg yt-dlp python@3.14; do brew list --versions "$f" >/dev/null || brew install "$f"; done

echo "== 2. Môi trường Python của dự án (.venv)"
[ -d .venv ] || "$(brew --prefix python@3.14)/bin/python3.14" -m venv .venv
.venv/bin/pip install -q -r requirements.txt

echo "== 3. Model AI chạy local vào .cache/ (VieNeu-TTS, khoảng 540 MB)"
.venv/bin/python scripts/setup_models.py

echo "== 4. Bí mật"
[ -f .env ] || { cp .env.example .env; echo "Đã tạo .env từ mẫu. Tự điền key vào .env (không dán key vào chat)."; }

echo "== 5. agy (Antigravity CLI, gói Gemini Pro cá nhân)"
if [ ! -x "$HOME/.local/bin/agy" ]; then
  echo "Chưa có agy. Cài: curl -fsSL https://antigravity.google/cli/install.sh | bash, rồi chạy 'agy' một lần để đăng nhập (xem docs/setup.md)."
else
  .venv/bin/python - <<'PY'
import json, os
p = os.path.expanduser("~/.gemini/antigravity-cli/settings.json")
d = json.load(open(p)) if os.path.exists(p) else {}
rules = json.load(open("scripts/agy_permissions.json"))["allow"]
allow = d.setdefault("permissions", {}).setdefault("allow", [])
allow += [r for r in rules if r not in allow]
json.dump(d, open(p, "w"), indent=2)
print("Đã gộp", len(rules), "quyền read_url vào", p)
PY
fi

echo "== 6. Kiểm tra"
.venv/bin/python -m pytest -q
echo "Xong. Việc còn làm tay: xem docs/setup.md mục 'Làm tay'."
