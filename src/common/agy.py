"""Gọi agy (Antigravity CLI, gói Gemini Pro cá nhân) ở chế độ không tương tác, lấy câu trả lời dạng chữ.

agy không được ghi file hay chạy lệnh (chế độ -p tự từ chối); người gọi tự ghi kết quả.
"""
import json
import pathlib
import subprocess
import tempfile
import time

AGY = pathlib.Path.home() / ".local/bin/agy"
BRAIN = pathlib.Path.home() / ".gemini/antigravity-cli/brain"


def run(prompt: str, model: str, timeout: int = 1800) -> dict:
    """Trả về {text, status, usage, seconds, notices, conversation_id}. Không ném lỗi; text rỗng nghĩa là thất bại."""
    start = time.time()
    with tempfile.TemporaryDirectory() as empty:  # thư mục trống: agy không đụng được repo
        try:
            p = subprocess.run(
                [str(AGY), "-p", prompt, "--model", model, "--sandbox", "--output-format", "json",
                 "--print-timeout", f"{timeout}s"],
                cwd=empty, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout + 120)
        except subprocess.TimeoutExpired:
            return {"text": "", "status": "TIMEOUT", "usage": None, "conversation_id": None,
                    "seconds": round(time.time() - start), "rc": -1, "notices": ["quá thời gian"]}
    notices = [line for line in p.stderr.splitlines() if "logging before google.Init" not in line]
    try:
        res = json.loads(p.stdout, strict=False)  # agy trả JSON có ký tự xuống dòng chưa escape
    except json.JSONDecodeError:
        res = {"status": "BAD_JSON"}
    text = (res.get("response") or "").strip()
    # agy đôi khi để bản đầy đủ trong artifact (brain/<conversation_id>/*.md), câu trả lời chỉ là lời kể
    cid = res.get("conversation_id")
    if cid:
        arts = sorted((BRAIN / cid).glob("*.md"), key=lambda f: f.stat().st_size, reverse=True)
        if arts and arts[0].stat().st_size > len(text.encode()):
            text = arts[0].read_text(encoding="utf-8").strip()
    return {"text": text, "status": res.get("status"), "usage": res.get("usage"), "conversation_id": cid,
            "seconds": round(time.time() - start), "rc": p.returncode, "notices": notices[-3:]}


def usage() -> dict:
    """Quota còn lại theo % mỗi kho: {'Gemini Models|Five Hour': 93, ...}. Rỗng nếu không đọc được."""
    p = subprocess.run([str(AGY), "-p", "/usage", "--print-timeout", "60s"], stdin=subprocess.DEVNULL,
                       capture_output=True, text=True)
    out = {}
    for line in (p.stdout + p.stderr).splitlines():
        cols = line.split("\t")
        if len(cols) >= 3 and cols[2].endswith("%"):
            out[f"{cols[0]}|{cols[1].replace(' Limit Remaining', '')}"] = int(cols[2].rstrip("%"))
    return out
