"""ĐẠO DIỄN GẮN NHÃN: AI đọc cả chương (từng câu phụ đề, đánh số) và gắn nhãn mỗi câu: nền, ai có mặt, ai nói, ai diễn,
hành động, biểu cảm, hiệu ứng, CHỈ chọn trong danh sách đóng. direct.py dùng nhãn thay cho phần đoán bằng từ khoá
(từ khoá vẫn lo đạo cụ, góc máy, quần chúng). Nhãn lỗi/thiếu câu nào thì câu đó quay về luật từ khoá.

Gọi qua nhóm nhân viên nhiều nguồn (src/common/pool.py, loại việc "tag"): Gemini API ~1 giây/lần, hết lượt thì chuyển.
Kết quả lưu stories/<slug>/storyboard/NNN.tags.yaml (có rồi thì dùng lại; xoá file để gắn lại).

python -m src.studio.tagger <slug> <chương>
"""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHUNK = 60                   # số câu mỗi lần gọi


def _vocab(cast: dict) -> dict:
    from src.studio.actions import ACTIONS, EFFECTS
    scenes = sorted({p.parent.name for p in (ROOT / "assets/scenes").glob("*/master.jpg")})
    return {"characters": {n: c.get("names", []) for n, c in cast["characters"].items()}, "scenes": scenes,
            "actions": sorted(ACTIONS), "exprs": ["neutral", "smirk", "shocked", "angry", "sad"], "fx": sorted(EFFECTS)}


def _prompt(vocab: dict, lines: list[tuple[int, str]], prev_scene: str, context: str) -> str:
    chars = "\n".join(f"- {n} (còn gọi: {', '.join(a) or '—'})" for n, a in vocab["characters"].items())
    body = "\n".join(f"{i}. {t}" for i, t in lines)
    return f"""Bạn là đạo diễn phim hoạt hình rối kể chuyện. Đọc các câu (đánh số, theo thứ tự) và gắn nhãn MỖI câu.
Trả về JSON dạng {{"tags": [{{"i": số câu, "scene": nền, "present": [...], "speaker": tên hoặc null, "actor": tên hoặc null,
"action": hành động, "expr": biểu cảm, "fx": [...]}}, ...]}} — đủ {len(lines)} phần tử, đúng số câu.

Quy tắc:
- scene: CHỈ chọn trong danh sách nền, hợp với nơi diễn ra sự việc; không đổi nơi thì giữ nền câu trước.
  Nền đang dùng trước đoạn này: {prev_scene}.
- present: tối đa 2 nhân vật THỰC SỰ đang ở hiện trường lúc đó (KHÔNG tính người chỉ được nhắc tới, nhớ lại, gọi điện
  ở xa); dùng TÊN ĐẦY ĐỦ trong danh sách nhân vật. Hồi tưởng/kiếp trước thì chỉ tính người trong cảnh hồi tưởng.
- speaker: câu thoại trong ngoặc kép → tên người nói (suy từ ngữ cảnh); lời kể → null.
- actor: nhân vật mà câu tả hành động/cảm xúc (người nói hoặc chủ ngữ); không ai → null.
- action: một trong {", ".join(vocab["actions"])}.
- expr: một trong {", ".join(vocab["exprs"])}.
- fx: 0–2 trong {", ".join(vocab["fx"])}.

Nhân vật:
{chars}

Danh sách nền: {", ".join(vocab["scenes"])}

Tóm tắt những gì đã xảy ra trước đoạn này (để hiểu ngữ cảnh): {context or "đây là đầu chương"}

Các câu:
{body}
"""


def parse(text: str, vocab: dict) -> dict[int, dict]:
    import json
    import re
    from src.contracts import check
    m = re.search(r"\{.*\}", text, re.S)
    try:
        items = json.loads(m.group(0))["tags"] if m else []
    except (ValueError, KeyError, TypeError):
        items = []
    names = set(vocab["characters"])
    out = {}
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or not isinstance(it.get("i"), int):
            continue
        def one(v, allowed):                            # chuỗi nằm trong danh sách đóng, sai kiểu → None
            return v if isinstance(v, str) and v in allowed else None

        def many(v, allowed):                           # danh sách chuỗi trong danh sách đóng, sai kiểu → []
            return [x for x in v if isinstance(x, str) and x in allowed] if isinstance(v, list) else []
        tag = {"scene": one(it.get("scene"), vocab["scenes"]), "present": many(it.get("present"), names)[:2],
               "speaker": one(it.get("speaker"), names), "actor": one(it.get("actor"), names),
               "action": one(it.get("action"), vocab["actions"]) or "idle", "expr": one(it.get("expr"), vocab["exprs"]),
               "fx": many(it.get("fx"), vocab["fx"])[:2]}
        if not check("tag", tag):
            out[it["i"]] = tag
    return out


def tag(slug: str, chapter: int, force: bool = False) -> dict[int, dict]:
    from src.common import pool
    from src.studio.direct import parse_srt
    sd = ROOT / "stories" / slug
    out = sd / "storyboard" / f"{chapter:03d}.tags.yaml"
    if out.exists() and not force:
        return {int(k): v for k, v in yaml.safe_load(out.read_text(encoding="utf-8")).items()}
    cast = yaml.safe_load((sd / "cast.yaml").read_text(encoding="utf-8"))
    vocab = _vocab(cast)
    subs = parse_srt(sd / "audio" / f"{chapter:03d}.srt")
    tags, prev = {}, cast.get("chapters", {}).get(chapter, {}).get("scene", "-")
    for k in range(0, len(subs), CHUNK):
        lines = [(i + 1, s[2]) for i, s in enumerate(subs[k:k + CHUNK], start=k)]
        context = " ".join(t for _, _, t in subs[max(0, k - 12):k])
        text, src = pool.ask("tag", _prompt(vocab, lines, prev, context), max_tokens=12000, json_mode=True)
        got = parse(text, vocab)
        tags.update(got)
        prev = next((got[i]["scene"] for i in sorted(got, reverse=True) if got[i]["scene"]), prev)
        print(f"gắn nhãn câu {k + 1}–{k + len(lines)}: {len(got)}/{len(lines)} dòng hợp lệ ({src})")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(tags, allow_unicode=True, sort_keys=True), encoding="utf-8")
    return tags


if __name__ == "__main__":
    t = tag(sys.argv[1], int(sys.argv[2]), force="--force" in sys.argv)
    print("Xong:", len(t), "câu có nhãn")
