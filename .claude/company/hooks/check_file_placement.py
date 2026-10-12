#!/usr/bin/env python3
"""Hook PreToolUse (Write|Edit|NotebookEdit) của tầng công ty.

Đọc bản đồ thư mục trong CLAUDE.md của dự án (khối ``` đầu tiên dưới tiêu đề có chữ
"Bản đồ thư mục") và chặn:
  - thư mục hoặc file gốc không có trong bản đồ
  - thư mục đánh dấu [readonly]
  - file .md nằm ngoài thư mục đánh dấu [md] (file .md ở gốc phải có tên trong bản đồ)
  - tên kiểu nhân bản ở bất kỳ cấp nào: _v2, _final, _backup, _copy, _old… (trừ trong tmp/)
  - tên có ký tự ngoài ASCII (tên phải tiếng Anh, không dấu)

Thoát mã 2 kèm lý do trên stderr thì Claude Code chặn thao tác và báo lại cho Claude.
Không tìm thấy bản đồ thì cho qua, để hook không làm hỏng dự án chưa khởi tạo.
"""
import json
import os
import re
import sys
from pathlib import Path

DONG_GOC = re.compile(r"^[├└]── (\S+)(.*)$")
TEN_NHAN_BAN = re.compile(r"[_-](v\d+|final|backup|bak|copy|old)(\.|$)", re.I)


def doc_ban_do(claude_md: Path):
    """Trả về (thư mục gốc {tên: chú thích}, file gốc {tên}) hoặc None."""
    if not claude_md.exists():
        return None
    dong = claude_md.read_text(encoding="utf-8").splitlines()
    i = next((k for k, d in enumerate(dong) if d.startswith("#") and "Bản đồ thư mục" in d), None)
    if i is None:
        return None
    try:
        bat_dau = next(k for k in range(i, len(dong)) if dong[k].startswith("```"))
        ket_thuc = next(k for k in range(bat_dau + 1, len(dong)) if dong[k].startswith("```"))
    except StopIteration:
        return None
    thu_muc, tep = {}, set()
    for d in dong[bat_dau + 1:ket_thuc]:
        m = DONG_GOC.match(d)
        if not m:
            continue
        ten, chu_thich = m.group(1), m.group(2)
        if ten.endswith("/"):
            thu_muc[ten.rstrip("/")] = chu_thich
        else:
            tep.add(ten)
    return thu_muc, tep


def chan(ly_do: str) -> None:
    print(f"[check_file_placement] {ly_do} Xem bản đồ thư mục trong CLAUDE.md và "
          ".claude/company/playbooks/files-and-docs.md. Nếu cần vị trí mới: hỏi Người sáng lập, "
          "thêm vào bản đồ, rồi làm lại.", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    data = json.load(sys.stdin)
    ti = data.get("tool_input", {})
    duong_dan = ti.get("file_path") or ti.get("notebook_path")
    if not duong_dan:
        return
    goc = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    p = Path(duong_dan)
    p = (p if p.is_absolute() else goc / p).resolve()
    try:
        phan = p.relative_to(goc).parts
    except ValueError:
        return  # ngoài dự án (bộ nhớ người dùng, scratchpad…)
    ban_do = doc_ban_do(goc / "CLAUDE.md")
    if ban_do is None:
        return
    thu_muc, tep = ban_do

    if not all(s.isascii() for s in phan):
        chan(f"Tên '{'/'.join(phan)}' có ký tự ngoài ASCII. Tên file và thư mục phải tiếng Anh, không dấu.")
    if len(phan) == 1:
        if p.name not in tep:
            chan(f"File gốc '{p.name}' không có trong bản đồ thư mục.")
        return
    dau = phan[0]
    if dau not in thu_muc:
        chan(f"Thư mục gốc '{dau}/' không có trong bản đồ thư mục.")
    chu_thich = thu_muc[dau]
    if "[readonly]" in chu_thich:
        chan(f"'{dau}/' được đánh dấu [readonly], chỉ đọc.")
    ten_nhan_ban = [s for s in phan if TEN_NHAN_BAN.search(s)]
    if dau != "tmp" and ten_nhan_ban:
        chan(f"Tên '{ten_nhan_ban[0]}' giống bản nhân bản (_v2/_final/_backup…). Sửa tại chỗ bản gốc.")
    if p.suffix == ".md" and "[md]" not in chu_thich:
        chan(f"'{dau}/' không được đánh dấu [md] nên không chứa file .md. Tài liệu để trong docs/.")


if __name__ == "__main__":
    main()
