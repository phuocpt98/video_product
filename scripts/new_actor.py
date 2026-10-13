"""Một lệnh từ ảnh gốc đến card diễn viên đã kiểm, chế độ `semi` (docs/research/2026-10-13-puppet-v2.md §8).

python scripts/new_actor.py <id> --look "..." --hair "..." --outfit <id bộ đồ> --outfit-desc "..."
       [--signature "confident half smirk"] [--gender nu] [--age 25-30] [--exprs a,b,..] [--poses a,b,..]
       [--master ảnh_có_sẵn] [--no-gen]
Bước nào đã có file (mới hơn nguồn) thì bỏ qua; ảnh gốc đổi (md5) thì cắt lại. --no-gen: không gọi agy, báo MỘT lượt mọi ảnh còn thiếu rồi dừng.
Chưa đạt: ghi card.rejected.yaml (kèm errors), không để card.yaml. Prompt: prompts/actor_*.md.
"""
import argparse
import hashlib
import pathlib
import re
import shutil
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import imagegen  # noqa: E402
from src.studio import segment, validate_actor  # noqa: E402

ACTORS = ROOT / "assets/actors"
EXPRS = "neutral,neutral_talk,smirk,smirk_talk,shocked,angry,sad,blink"
POSES = "hips,phone,point"


def read_prompt(name: str) -> str:
    """Khối ``` đầu tiên của prompts/<name>.md, nối dòng bằng khoảng trắng."""
    text = (ROOT / "prompts" / name).read_text(encoding="utf-8")
    m = re.search(r"```\n(.*?)```", text, re.S)
    return " ".join(m.group(1).split())


def read_table(name: str) -> dict[str, str]:
    """Bảng markdown `| khoá | giá trị |` trong prompts/<name>.md."""
    out = {}
    for line in (ROOT / "prompts" / name).read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and re.fullmatch(r"[a-z_]+", cells[0]) and cells[0] != "khoá":
            out[cells[0]] = cells[1]
    return out


def fill(tpl: str, **fields) -> str:
    for k, v in fields.items():
        tpl = tpl.replace("{" + k + "}", v)
    return tpl


def md5(path: pathlib.Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--look", required=True)
    ap.add_argument("--hair", required=True)
    ap.add_argument("--outfit", required=True)
    ap.add_argument("--outfit-desc", required=True)
    ap.add_argument("--signature", default="confident half smirk")
    ap.add_argument("--gender", default="")
    ap.add_argument("--age", default="")
    ap.add_argument("--exprs", default=EXPRS)
    ap.add_argument("--poses", default=POSES)
    ap.add_argument("--master")
    ap.add_argument("--no-gen", action="store_true")
    a = ap.parse_args(argv)

    d = ACTORS / a.id
    src, parts = d / "source", d / "parts"
    for p in (src, parts / a.outfit):
        p.mkdir(parents=True, exist_ok=True)
    exprs = [e for e in a.exprs.split(",") if e]
    poses = [p for p in a.poses.split(",") if p and p != "relaxed"]
    expr_tbl, pose_tbl = read_table("actor_expression.md"), read_table("actor_pose.md")
    for k in exprs:
        if k != "neutral" and k not in expr_tbl:
            raise SystemExit(f"biểu cảm '{k}' không có trong prompts/actor_expression.md")
    for k in poses:
        if k not in pose_tbl:
            raise SystemExit(f"tư thế '{k}' không có trong prompts/actor_pose.md")

    def fresh(out: pathlib.Path, raw: pathlib.Path) -> bool:
        """Ảnh ra dùng lại được khi có và mới hơn (hoặc bằng) ảnh nguồn."""
        return out.exists() and (not raw.exists() or out.stat().st_mtime >= raw.stat().st_mtime)

    def make(prompt: str, refs, out: pathlib.Path) -> None:
        if not out.exists():
            imagegen.gen(prompt, refs, out, aspect="9:16")

    master = src / "master.png"
    mp = src / "measure.yaml"
    head_n, hair_back, body_r = parts / "head_neutral.png", parts / "hair_back.png", parts / a.outfit / "body_relaxed.png"
    etpl, ptpl = read_prompt("actor_expression.md"), read_prompt("actor_pose.md")
    mtpl = read_prompt("actor_master.md")
    cur = master
    try:
        if a.master:
            if not master.exists():
                shutil.copy(a.master, master)
            elif md5(pathlib.Path(a.master)) != md5(master):
                shutil.copy(a.master, master)
                print("ảnh gốc mới, cắt lại")

        if a.no_gen:                                       # gom TẤT CẢ ảnh còn thiếu rồi báo một lượt
            miss = [] if master.exists() else [master]
            for k in exprs:
                if k != "neutral" and not fresh(parts / f"head_{k}.png", src / f"expr_{k}.png") \
                        and not (src / f"expr_{k}.png").exists():
                    miss.append(src / f"expr_{k}.png")
            for k in poses:
                if not fresh(parts / a.outfit / f"body_{k}.png", src / f"pose_{k}.png") \
                        and not (src / f"pose_{k}.png").exists():
                    miss.append(src / f"pose_{k}.png")
            if miss:
                print("DỪNG: thiếu ảnh (--no-gen):")
                for f in miss:
                    print(" -", f)
                return 1
        make(fill(mtpl, look=a.look, outfit=a.outfit_desc, hair=a.hair), [], master)

        prev = yaml.safe_load(mp.read_text(encoding="utf-8")) if mp.exists() else None
        digest = md5(master)
        if (isinstance(prev, dict) and prev.get("source_md5") == digest and head_n.exists() and body_r.exists()
                and head_n.stat().st_mtime >= master.stat().st_mtime):
            measure = prev
        else:                                              # ảnh gốc đổi hoặc chưa cắt: xoá bản cũ, cắt lại từ master
            for f in [head_n, hair_back, body_r, *parts.glob("head_*.png"), *(parts / a.outfit).glob("body_*.png"),
                      d / "card.yaml"]:                    # card cũ không còn đúng với bộ phận mới
                f.unlink(missing_ok=True)
            if isinstance(prev, dict) and prev.get("source_md5") not in (None, digest):
                for f in [*src.glob("expr_*.png"), *src.glob("pose_*.png")]:   # ảnh sửa từ master cũ: mặt sẽ lệch
                    f.unlink()
                print("đã bỏ ảnh biểu cảm/tư thế sinh từ ảnh gốc cũ, cần tạo lại")
            measure = segment.cut_figure(master, parts)
            (parts / "head_front.png").replace(head_n)
            (parts / "body_relaxed.png").replace(body_r)
            measure["source_md5"] = digest
            mp.write_text(yaml.safe_dump(measure, allow_unicode=True, sort_keys=False), encoding="utf-8")
        has_back = hair_back.exists()

        for k in exprs:
            if k == "neutral":
                continue
            out, raw = parts / f"head_{k}.png", src / f"expr_{k}.png"
            if fresh(out, raw):
                continue
            make(fill(etpl, expr=fill(expr_tbl[k], signature=a.signature)), [master], raw)
            cur = raw
            segment.cut_head(raw, out, measure)
        for k in poses:
            out, raw = parts / a.outfit / f"body_{k}.png", src / f"pose_{k}.png"
            if fresh(out, raw):
                continue
            make(fill(ptpl, pose=pose_tbl[k]), [master], raw)
            cur = raw
            segment.cut_body(raw, out, measure)
        # stage đặt cằm thấp hơn đỉnh cổ overlap × chiều cao KHUNG đầu; segment kéo mẩu cổ lên 0.12 × head_h
        head_h = measure["chin_y"] - measure["head_box"][1]
        overlap = round(0.12 * head_h / measure["frame"][1], 4)
    except (ValueError, IndexError) as e:
        (d / "card.yaml").unlink(missing_ok=True)          # bộ phận có thể đã bị xoá: không để card cũ trỏ vào chỗ trống
        print(f"CHƯA ĐẠT: {cur}: {e}")
        return 1

    rig = {"mode": "semi", "head_scale": 1.0, "overlap": overlap, "chin_up": 0.0, "head_dx": 0, "neck_dx": {}}
    if has_back:
        rig["hair_back"] = "parts/hair_back.png"
    card = {"id": a.id, "kind": "actor", "made_by": "new_actor", "gender": a.gender, "age": a.age, "look": a.look,
            "signature": a.signature, "rig": rig,
            "heads": {k: f"parts/head_{k}.png" for k in exprs},
            "outfits": {a.outfit: {"desc": a.outfit_desc,
                                   "bodies": {k: f"parts/{a.outfit}/body_{k}.png" for k in ["relaxed"] + poses}}},
            "roles": [], "notes": f"Tạo bằng scripts/new_actor.py, tóc: {a.hair}"}
    (d / "card.rejected.yaml").unlink(missing_ok=True)
    (d / "card.yaml").write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")

    errs = validate_actor.validate(d)
    for w in validate_actor.warnings:
        print("cảnh báo:", w)
    if errs:
        card["errors"] = errs
        (d / "card.rejected.yaml").write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")
        (d / "card.yaml").unlink()
        print("CHƯA ĐẠT")
        for e in errs:
            print(" -", e)
        return 1
    print("ĐẠT")
    for p in validate_actor.preview(d):
        print("preview:", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
