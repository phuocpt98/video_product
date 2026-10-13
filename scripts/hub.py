"""BẢNG VIỆC CHUNG giữa các máy (Claude ở máy Người sáng lập, Muse ở máy cloud, Người sáng lập): GitHub Issues của repo,
qua `gh`. Mỗi việc = 1 issue; nhãn `to:<bên>` cho biết ai đang cầm việc. Giao thức: docs/plans/collab-protocol.md.
Bảng việc nội bộ một máy (board/) vẫn là src/board.py; hub chỉ cho việc phải đổi máy.

python scripts/hub.py ensure-labels                              # tạo nhãn một lần cho repo
python scripts/hub.py list [--to muse|claude|founder] [--all]    # việc đang mở
python scripts/hub.py next --to muse                             # việc cũ nhất của bên mình, in cả nội dung (chạy đầu phiên)
python scripts/hub.py new --to muse --type need-image "tiêu đề" (--body file.md | --text "...")
python scripts/hub.py post <n> "bình luận"                       # ghi tiến độ, câu hỏi
python scripts/hub.py handoff <n> --to claude ["bình luận"]      # chuyển việc sang bên khác (đổi nhãn to:)
python scripts/hub.py done <n> ["bằng chứng"]                    # Kết luận: ĐẠT, đóng việc
python scripts/hub.py reject <n> --to muse "lỗi 1; lỗi 2"        # Kết luận: CHƯA ĐẠT, trả lại
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIDES = ("claude", "muse", "founder")
TYPES = {"need-image": "cần tạo ảnh theo prompt sẵn", "need-prompt": "cần Claude viết prompt/luật",
         "need-code": "cần Claude viết/sửa code", "bug": "lỗi khi chạy, kèm lệnh và log", "review": "cần duyệt sản phẩm",
         "need-story": "cần truyện mới hoặc nhập truyện vào dây chuyền"}
COLORS = {"to:claude": "1d76db", "to:muse": "0e8a16", "to:founder": "d93f0b"}


def gh(*args, check: bool = True) -> str:
    p = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True)
    if check and p.returncode:
        raise SystemExit(f"gh {' '.join(args[:2])}: {p.stderr.strip()[:300]}")
    return p.stdout


def issues(to: str | None = None, all_: bool = False) -> list[dict]:
    args = ["issue", "list", "--json", "number,title,labels,updatedAt,url", "--limit", "100"]
    if all_:
        args += ["--state", "all"]
    if to:
        args += ["--label", f"to:{to}"]
    return json.loads(gh(*args) or "[]")


def ensure_labels() -> None:
    have = {l["name"] for l in json.loads(gh("label", "list", "--json", "name", "--limit", "200") or "[]")}
    for name, color in COLORS.items():
        if name not in have:
            gh("label", "create", name, "--color", color, "--description", f"việc đang ở bên {name[3:]}")
    for name, desc in TYPES.items():
        if name not in have:
            gh("label", "create", name, "--color", "c5def5", "--description", desc)
    print("nhãn sẵn sàng:", ", ".join(sorted(set(COLORS) | set(TYPES))))


def cmd_list(a) -> None:
    for i in issues(a.to, a.all):
        labels = " ".join(l["name"] for l in i["labels"])
        print(f"#{i['number']:<4} {i['title'][:60]:<60} {labels}  {i['updatedAt'][:10]}")


def cmd_next(a) -> None:
    rows = sorted(issues(a.to), key=lambda i: i["number"])
    if not rows:
        print(f"không có việc nào cho {a.to}")
        return
    n = rows[0]["number"]
    print(gh("issue", "view", str(n), "--comments"))


def cmd_new(a) -> None:
    body = pathlib.Path(a.body).read_text(encoding="utf-8") if a.body else (a.text or "")
    if not body.strip():
        raise SystemExit("cần --body <file.md> hoặc --text")
    out = gh("issue", "create", "--title", a.title, "--body", body, "--label", f"to:{a.to}", "--label", a.type)
    print(out.strip())


def cmd_post(a) -> None:
    gh("issue", "comment", str(a.n), "--body", a.msg)
    print("đã ghi vào", f"#{a.n}")


def _move(n: int, to: str) -> None:
    """Đổi nhãn to:* bằng MỘT lệnh edit (nguyên tử): đọc nhãn hiện có, chỉ gỡ nhãn to:* đang có. Lỗi thì issue không đổi."""
    data = json.loads(gh("issue", "view", str(n), "--json", "labels"))
    have = [lb["name"] for lb in data.get("labels", []) if lb["name"].startswith("to:")]
    args = ["issue", "edit", str(n)]
    if f"to:{to}" not in have:
        args += ["--add-label", f"to:{to}"]
    for name in have:
        if name != f"to:{to}":
            args += ["--remove-label", name]
    if len(args) > 3:
        gh(*args)


def cmd_handoff(a) -> None:
    _move(a.n, a.to)
    gh("issue", "comment", str(a.n), "--body", f"Kết luận: CHUYỂN → {a.to}\n\n{a.msg or ''}".rstrip())
    print(f"#{a.n} → {a.to}")


def cmd_done(a) -> None:
    gh("issue", "comment", str(a.n), "--body", f"Kết luận: ĐẠT\n\n{a.msg or ''}".rstrip())
    gh("issue", "close", str(a.n))
    print(f"#{a.n} đóng")


def cmd_reject(a) -> None:
    _move(a.n, a.to)
    items = "\n".join(f"- {x.strip()}" for x in a.msg.split(";") if x.strip())
    gh("issue", "comment", str(a.n), "--body", f"Kết luận: CHƯA ĐẠT\n\n{items}")
    print(f"#{a.n} trả về {a.to}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ensure-labels")
    p = sub.add_parser("list"); p.add_argument("--to", choices=SIDES); p.add_argument("--all", action="store_true")
    p = sub.add_parser("next"); p.add_argument("--to", choices=SIDES, required=True)
    p = sub.add_parser("new"); p.add_argument("title"); p.add_argument("--to", choices=SIDES, required=True)
    p.add_argument("--type", choices=list(TYPES), required=True); p.add_argument("--body"); p.add_argument("--text")
    p = sub.add_parser("post"); p.add_argument("n", type=int); p.add_argument("msg")
    p = sub.add_parser("handoff"); p.add_argument("n", type=int); p.add_argument("--to", choices=SIDES, required=True)
    p.add_argument("msg", nargs="?")
    p = sub.add_parser("done"); p.add_argument("n", type=int); p.add_argument("msg", nargs="?")
    p = sub.add_parser("reject"); p.add_argument("n", type=int); p.add_argument("--to", choices=SIDES, required=True)
    p.add_argument("msg")
    a = ap.parse_args(argv)
    {"ensure-labels": lambda a: ensure_labels(), "list": cmd_list, "next": cmd_next, "new": cmd_new, "post": cmd_post,
     "handoff": cmd_handoff, "done": cmd_done, "reject": cmd_reject}[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
