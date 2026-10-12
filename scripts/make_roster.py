"""Tạo lần lượt diễn viên từ assets/actors/roster.yaml bằng make_actor.py (bộ trang phục đầu tiên). Dừng khi gặp lỗi
(thường là hết lượt ảnh 429); chạy lại sẽ bỏ qua diễn viên đã có card.yaml. Mỗi diễn viên tốn 2 ảnh.

python scripts/make_roster.py nam-18-b nu-18-a ...    # theo thứ tự đưa vào
"""
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    roster = {a["id"]: a for a in yaml.safe_load((ROOT / "assets/actors/roster.yaml").read_text(encoding="utf-8"))["actors"]}
    for aid in sys.argv[1:]:
        if (ROOT / "assets/actors" / aid / "card.yaml").exists():
            print("đã có:", aid)
            continue
        a = roster[aid]
        oid, odesc = next(iter(a["outfits"].items()))
        print("tạo:", aid, flush=True)
        r = subprocess.run([sys.executable, str(ROOT / "scripts/make_actor.py"), aid, "--look", a["look"],
                            "--gender", a.get("gender", ""), "--age", str(a.get("age", "")),
                            "--signature", a.get("signature", "confident half smirk"),
                            "--outfit", oid, "--outfit-desc", odesc], cwd=ROOT)
        if r.returncode:
            print("dừng ở:", aid)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
