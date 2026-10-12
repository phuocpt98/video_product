"""Chạy một vai trò trên agy với 1 brief, ghi câu trả lời ra file (việc lẻ: nghiên cứu, duyệt báo cáo).

Pipeline truyện dùng src/run.py. Lõi gọi agy ở src/common/agy.py.
python scripts/agy_run.py --role prompts/roles/<vai-tro>.md --brief <file> --out <file.md> [--model M] [--timeout 1800]
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.common import agy  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gemini-3.1-pro-high")
    ap.add_argument("--timeout", type=int, default=1800, help="giây")
    a = ap.parse_args()
    prompt = pathlib.Path(a.role).read_text(encoding="utf-8") + "\n\n## Nhiệm vụ lần này\n" + \
        pathlib.Path(a.brief).read_text(encoding="utf-8")
    r = agy.run(prompt, a.model, a.timeout)
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    log = {"time": dt.datetime.now().isoformat(timespec="seconds"), "role": a.role, "brief": a.brief, "model": a.model,
           **{k: r[k] for k in ("rc", "status", "seconds", "usage", "notices")}, "chars": len(r["text"])}
    with open(out.with_suffix(".run.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
    if not r["text"]:
        print(f"Lỗi: agy không trả nội dung ({r['status']}). {' | '.join(r['notices'][-2:])}")
        return 1
    out.write_text(r["text"] + "\n", encoding="utf-8")
    print(f"Xong: {out} ({len(r['text'])} ký tự, {r['seconds']} giây)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
