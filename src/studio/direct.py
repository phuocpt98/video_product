"""ĐẠO DIỄN BẰNG LUẬT (không gọi AI): phụ đề chương (audio/NNN.srt) + mục lục truyện (cast.yaml) + luật hành động
dùng chung (data/actions.yaml) → kịch bản cảnh stories/<slug>/storyboard/NNN.yaml cho stage.py dựng.

- Câu nhắc tên nhân vật nào thì nhân vật đó diễn; không nhắc ai thì giữ người đang diễn (mặc định nhân vật chính).
- Câu trong ngoặc kép là thoại: người nói nhép miệng. Người nói đoán theo câu dẫn "X nói:", lời gọi "Y, ..." (thì
  người kia nói), hoặc luân phiên. Sai vài chỗ vẫn được, không cần khớp tuyệt đối.
- Từ khoá trong câu → biểu cảm, tư thế, đạo cụ, rung, máy quay. Từ khoá tên nền → đổi nền.
- Diễn viên, nền, đạo cụ chưa có trong thư viện thì bỏ qua và liệt kê ở cuối để biết cần tạo gì.

python -m src.studio.direct <slug> <chương> [--clip a-b] [--render] [--size 1920x1080]
"""
import argparse
import pathlib
import random
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
HEIGHT = 0.3                  # chiều cao nhân vật so với khung ở zoom 1; zoom tối đa 1.6 → không quá 1/2 khung
CAMS = {"wide": [1.0, 1.1], "medium": [1.2, 1.35], "close": [1.4, 1.6], "push": [1.1, 1.6], "pull": [1.5, 1.1]}
MAX_SHOT = 8.0                # giây: cảnh dài hơn thì cắt để máy quay đổi góc


def parse_srt(path: pathlib.Path) -> list[tuple[float, float, str]]:
    def sec(t):
        h, m, s = t.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    out = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = block.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = lines[1].split("-->")
            out.append((sec(a.strip()), sec(b.strip()), " ".join(lines[2:]).strip()))
    return out


def finder(words: list[str]):
    """Regex khớp nguyên từ (tiếng Việt có dấu vẫn đúng vì \\w là Unicode)."""
    return re.compile(r"(?<!\w)(" + "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)) + r")(?!\w)",
                      re.IGNORECASE)


def direct(slug: str, chapter: int) -> tuple[dict, dict]:
    sd = ROOT / "stories" / slug
    cast = yaml.safe_load((sd / "cast.yaml").read_text(encoding="utf-8"))
    rules = [(finder(r["when"]), r) for r in yaml.safe_load((ROOT / "data/actions.yaml").read_text(encoding="utf-8"))]
    props_file = ROOT / "assets/props/props.yaml"
    props = {k for k, v in (yaml.safe_load(props_file.read_text(encoding="utf-8")) if props_file.exists() else {}).items()
             if (ROOT / "assets/props" / v["file"]).exists()}
    missing = {"diễn viên": set(), "nền": set(), "đạo cụ": set()}

    # diễn viên có sẵn (thiếu trang phục đã chọn thì lấy bộ đầu tiên). Một nhân vật có thể có ngoại hình riêng theo
    # nền (by_scene: {hotel-banquet: {actor: nam-35-a, outfit: vest}}), ví dụ nam chính kiếp trước ở bữa tiệc
    def resolve(look: dict) -> dict | None:
        card = ROOT / "assets/actors" / look["actor"] / "card.yaml"
        if not card.exists():
            return None
        outfits = yaml.safe_load(card.read_text(encoding="utf-8"))["outfits"]
        return {"actor": look["actor"], "outfit": look.get("outfit") if look.get("outfit") in outfits else next(iter(outfits))}
    actors, looks = {}, {}
    for name, c in cast["characters"].items():
        if (r := resolve(c)):
            actors[name] = r
        for sid, look in (c.get("by_scene") or {}).items():
            looks[(name, sid)] = look
    who = {name: finder([name] + c.get("names", [])) for name, c in cast["characters"].items()}
    scenes_ok = {p.parent.name for p in (ROOT / "assets/scenes").glob("*/master.jpg")}
    scene_kw = {sid: finder(kws) for sid, kws in cast.get("scenes", {}).items()}
    # quần chúng không lấy diễn viên đã có vai trong truyện (tránh nhân vật chính đứng lẫn trong đám đông)
    story_actors = sorted({c["actor"] for c in cast["characters"].values()} |
                          {v["actor"] for c in cast["characters"].values() for v in (c.get("by_scene") or {}).values()})
    scene_crowd = {p.parent.name: (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("crowd", 0)
                   for p in (ROOT / "assets/scenes").glob("*/card.yaml")}
    lead = cast["lead"]

    first = cast.get("chapters", {}).get(chapter, {}).get("scene")
    if not scenes_ok:
        raise SystemExit("Thư viện nền assets/scenes/ đang rỗng: cần ít nhất 1 nền")
    if first not in scenes_ok:
        if first:
            missing["nền"].add(first)
        first = next((s for s in cast.get("scenes", {}) if s in scenes_ok), None) or sorted(scenes_ok)[0]
    scene, focus, speaker, partner, in_quote, lead_in = first, lead, None, None, False, None
    recent: list[str] = []            # người được nhắc gần đây, mới nhất ở cuối
    units = []
    tag_file = sd / "storyboard" / f"{chapter:03d}.tags.yaml"       # nhãn đạo diễn AI (tagger.py), nếu có
    tags = {int(k): v for k, v in (yaml.safe_load(tag_file.read_text(encoding="utf-8")) or {}).items()} \
        if tag_file.exists() else {}
    for idx, (start, end, text) in enumerate(parse_srt(sd / "audio" / f"{chapter:03d}.srt"), start=1):
        # nền
        for sid, rx in scene_kw.items():
            if rx.search(text):
                if sid in scenes_ok:
                    scene = sid
                else:
                    missing["nền"].add(sid)
                break
        # ai được nhắc, theo thứ tự xuất hiện trong câu
        hits = sorted((m.start(), n) for n, rx in who.items() for m in [rx.search(text)] if m)
        named = [n for _, n in hits]
        for n in named:
            if n in recent:
                recent.remove(n)
            recent.append(n)
        # thoại hay kể
        quoted = in_quote or any(q in text for q in '"“”')
        continued = in_quote
        if text.count('"') % 2:                               # ngoặc thẳng: số lẻ thì đổi trạng thái
            in_quote = not in_quote
        if text.count("“") > text.count("”"):
            in_quote = True
        elif text.count("”") > text.count("“"):
            in_quote = False
        if quoted:
            others = [n for n in reversed(recent) if n != speaker]
            if continued and speaker:
                pass                                                  # câu thoại nối tiếp: cùng người nói
            elif lead_in:
                speaker = lead_in                                     # "X nói:" ở câu trước
            elif named and re.match(r'^\W*' + who[named[0]].pattern + r'\s*,', text, re.IGNORECASE):
                speaker = next((n for n in reversed(recent) if n != named[0]), lead)   # "Y, ..." → người kia nói
            else:
                speaker = others[0] if others else lead               # luân phiên
            actor_now = speaker
        else:
            speaker = None
            actor_now = named[0] if named else focus
        lead_in = (named[0] if named else focus) if not quoted and text.rstrip().endswith(":") else None
        focus = actor_now
        partner = next((n for n in reversed(recent) if n != actor_now and n in actors), None) \
            if len(recent) > 1 else None
        tg = tags.get(idx)
        if tg:                          # có nhãn AI: dùng nhãn cho nền, ai có mặt, ai nói, ai diễn (từ khoá lo phần còn lại)
            if tg.get("scene") in scenes_ok:
                scene = tg["scene"]
            pres = tg.get("present") or []
            speaker = tg.get("speaker")
            quoted = speaker is not None
            actor_now = speaker or tg.get("actor") or (pres[0] if pres else None)
            partner = next((n for n in pres if n != actor_now), None)
            if actor_now:
                focus = actor_now
        # hành động theo từ khoá
        act = {}
        for rx, r in rules:
            if rx.search(text):
                for k in ("expr", "pose", "prop", "shake", "cam", "crowd"):
                    if k in r and k not in act:
                        act[k] = r[k]
        if tg and tg.get("expr"):
            act["expr"] = tg["expr"]
        if act.get("prop") and act["prop"] not in props:
            missing["đạo cụ"].add(act.pop("prop"))
        cast_now = []
        for n in [actor_now, partner]:
            if not n:
                continue
            me = n == actor_now
            key = n
            if (n, scene) in looks:                              # ngoại hình riêng của nền này
                key = f"{n}@{looks[(n, scene)]['actor']}"
                if key not in actors:
                    r = resolve(looks[(n, scene)])
                    if not r:
                        missing["diễn viên"].add(f"{n} ({looks[(n, scene)]['actor']})")
                        continue
                    actors[key] = r
            elif n not in actors:
                missing["diễn viên"].add(f"{n} ({cast['characters'].get(n, {}).get('actor', '?')})")
                continue
            cast_now.append({"who": key, "pose": act.get("pose", "relaxed") if me else "relaxed",
                             "expr": act.get("expr", "neutral") if me else "neutral",
                             **({"prop": act["prop"]} if me and act.get("prop") else {}),
                             **({"talk": True} if me and quoted else {}),
                             **({"shake": True} if me and act.get("shake") else {}),
                             **({"action": tg["action"]} if me and tg and tg.get("action") not in (None, "idle") else {}),
                             **({"fx": tg["fx"]} if me and tg and tg.get("fx") else {})})
        crowd = max(act.get("crowd", 0), scene_crowd.get(scene, 0))
        units.append({"start": start, "end": end, "scene": scene, "cast": cast_now, "cam": act.get("cam"),
                      "talk": quoted, "text": text, "crowd": crowd})

    # gộp câu liền nhau cùng trạng thái thành một cảnh (tối đa MAX_SHOT giây), rồi chọn góc máy
    rnd = random.Random(chapter)
    shots, prev_cam, prev_scene, prev_who = [], None, None, set()
    for u in units:
        key = (u["scene"], yaml.safe_dump(u["cast"]), u["crowd"])
        last = shots[-1] if shots else None
        if last and last["_key"] == key and u["end"] - last["start"] <= MAX_SHOT and not u["cam"]:
            last["end"] = u["end"]
            continue
        if u["scene"] != prev_scene:
            cam = "wide"
        elif u["cam"]:
            cam = u["cam"]
        else:
            cam = rnd.choice([c for c in (["medium", "close", "medium"] if u["talk"] else ["wide", "medium", "close"])
                              if c != prev_cam])
        names = [a["who"] for a in u["cast"]]
        xs = [0.5 + rnd.uniform(-0.08, 0.08)] if len(names) == 1 else [0.38, 0.62]
        # người đứng bên phải lật mặt nhìn sang trái; người mới xuất hiện đi vào từ trái
        acts = [{**a, "x": round(x, 3), "height": HEIGHT, **({"flip": True} if i == 1 else {}),
                 **({"enter": "left"} if a["who"] not in prev_who and u["scene"] == prev_scene else {})}
                for i, (a, x) in enumerate(zip(u["cast"], xs))]
        shots.append({"start": round(u["start"], 3), "end": round(u["end"], 3),
                      "background": f"../../../assets/scenes/{u['scene']}/master.jpg",
                      "cam": {"zoom": list(CAMS[cam])}, "actors": acts, "_key": key,
                      **({"extras": {"n": u["crowd"], "seed": sum(map(ord, u["scene"])),
                                     "exclude": story_actors}}
                         if u["crowd"] else {})})
        prev_cam, prev_scene, prev_who = cam, u["scene"], set(names)
    for i, s in enumerate(shots):          # cảnh nối liền, không hở
        s.pop("_key")
        s["end"] = shots[i + 1]["start"] if i + 1 < len(shots) else s["end"] + 1
    sb = {"audio": f"../audio/{chapter:03d}.mp3", "ground": 0.85, "feet_at": 0.8,
          "cast": {n: actors[n] for n in {a["who"] for s in shots for a in s["actors"]}},
          "shots": shots, "subs": [{"start": u["start"], "end": u["end"], "text": u["text"]} for u in units]}
    return sb, missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("chapter", type=int)
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--clip", help="chỉ dựng đoạn a-b giây để xem thử, ví dụ 60-80 (ra tmp/)")
    a = ap.parse_args()
    sb, missing = direct(a.slug, a.chapter)
    out = ROOT / "stories" / a.slug / "storyboard" / f"{a.chapter:03d}.yaml"
    if not a.clip:                                    # xem thử đoạn ngắn thì không ghi đè kịch bản cảnh của truyện
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(sb, allow_unicode=True, sort_keys=False), encoding="utf-8")
    lens = [s["end"] - s["start"] for s in sb["shots"]]
    print(f"{out.relative_to(ROOT)}: {len(lens)} cảnh, trung bình {sum(lens) / len(lens):.1f} giây, "
          f"dài nhất {max(lens):.1f} giây")
    for k, v in missing.items():
        if v:
            print(f"Thiếu {k}: {', '.join(sorted(v))}")
    if a.clip:
        import subprocess
        from src.studio.stage import render
        t0, t1 = map(float, a.clip.split("-"))
        d = ROOT / "tmp/direct_clip"
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0),
                        "-i", str(out.parent / sb["audio"]), str(d / "clip.wav")], check=True)   # audio tương đối storyboard/
        cut = lambda xs: [{**x, "start": max(x["start"], t0) - t0, "end": min(x["end"], t1) - t0}
                          for x in xs if x["end"] > t0 and x["start"] < t1]
        clip = {**sb, "audio": "clip.wav", "shots": cut(sb["shots"]), "subs": cut(sb["subs"]),
                "cast": sb["cast"]}
        for s in clip["shots"]:
            s["background"] = s["background"].replace("../../../", "../../")
        (d / "clip.yaml").write_text(yaml.safe_dump(clip, allow_unicode=True, sort_keys=False), encoding="utf-8")
        video = d / f"clip_{a.size}.mp4"
        render(d / "clip.yaml", a.size, video)
        print("Xong:", video.relative_to(ROOT))
    if a.render:
        from src.studio.stage import render
        video = ROOT / "stories" / a.slug / "output" / f"studio_{a.chapter:03d}_{a.size}.mp4"
        render(out, a.size, video)
        print("Xong:", video.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
