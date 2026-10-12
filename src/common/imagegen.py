"""Tạo 1 ảnh bằng agy (công cụ generate_image của gói Gemini Pro), có ảnh tham chiếu, thử lại khi lỗi. Mỗi ảnh tốn
khoảng 1% quota Gemini khung 5 giờ; model ảnh còn giới hạn riêng khoảng 13 ảnh/đợt (lỗi 429 khi hết)."""
import glob
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGY = pathlib.Path.home() / ".local/bin/agy"
BRAIN = pathlib.Path.home() / ".gemini/antigravity-cli/brain"


def gen(prompt: str, refs: list[pathlib.Path], out: pathlib.Path, tries: int = 2) -> None:
    if out.exists():
        return
    for i in range(tries):  # model ảnh đôi khi chậm hoặc quá tải: thử lại
        try:
            return _gen(prompt, refs, out)
        except RuntimeError as e:
            print(f"lần {i + 1} lỗi: {str(e)[:160]}")
    raise RuntimeError(f"không tạo được {out.name} sau {tries} lần")


def _gen(prompt: str, refs: list[pathlib.Path], out: pathlib.Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        for r in refs:
            shutil.copy(r, pathlib.Path(tmp) / r.name)
        see = (f"Xem các ảnh {', '.join(r.name for r in refs)} trong thư mục hiện tại và dùng chúng làm ảnh tham chiếu. "
               if refs else "")
        p = subprocess.run([str(AGY), "-p", see + "Dùng generate_image tạo đúng 1 ảnh tỉ lệ 16:9. Prompt ảnh: " + prompt +
                            " Không chạy lệnh shell; chỉ được gọi subagent image-generator (agy tạo ảnh qua nó)."
                            " Tạo xong trả lời đường dẫn file ảnh.",
                            "--model", "gemini-3.8-flash-medium", "--sandbox", "--output-format", "json",
                            "--print-timeout", "600s"], cwd=tmp, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    res = json.loads(p.stdout or "{}", strict=False)
    files = sorted(glob.glob(str(BRAIN / str(res.get("conversation_id")) / "*.[jp][pn]g")), key=os.path.getmtime)
    if not files:
        raise RuntimeError(f"agy không tạo được ảnh {out.name}: {(res.get('response') or p.stderr)[-300:]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(files[-1], out)
    print("tạo:", out.relative_to(ROOT))
