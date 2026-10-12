"""ĐOẠN MỒI TIKTOK (khung dọc 1080×1920, 3–5 phút theo Người sáng lập 28/9): lấy phần + nhịp mồi trong outline/hook.md,
nhờ AI (pool, Gemini API) chọn dải câu phụ đề liền nhau đủ dựng lên cao trào, dựng dọc kèm chữ lớn trên đầu và câu kêu gọi xem
full ở cuối. Kịch bản cảnh lấy từ direct.py (có nhãn đạo diễn thì dùng nhãn).

python scripts/make_tiktok.py <slug> [--part N] [--start i --end j]      # --start/--end: tự chọn câu (bỏ qua AI)
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import pool  # noqa: E402
from src.studio import direct  # noqa: E402
from src.studio.stage import render  # noqa: E402

CTA = "XEM FULL TRÊN YOUTUBE: KHOAI TÂY REVIEW"
MIN_S, MAX_S = 180, 300                 # đoạn mồi 3–5 phút
BAD = re.compile(r'[/\\:*?"<>|\n\r\t]')          # ký tự tên file không cho phép


def caption(sd: pathlib.Path, big: str) -> str:
    """Mô tả TikTok = câu móc + hashtag; dùng làm TÊN FILE để TikTok tự điền mô tả khi tải lên (≤ ~240 byte UTF-8)."""
    ch = yaml.safe_load((ROOT / "channels/khoai-tay-review/channel.yaml").read_text(encoding="utf-8"))["hashtags"]
    meta = yaml.safe_load((sd / "story.yaml").read_text(encoding="utf-8"))
    tags = [t for g in meta.get("genre", []) for t in ch.get("tiktok_by_genre", {}).get(g, [])] + ch["tiktok_common"]
    tags = list(dict.fromkeys(tags))[:ch.get("tiktok_max", 5)]   # Người sáng lập 28/9/2026: TikTok tối đa 5 hashtag
    head = big[:1].upper() + big[1:].lower() if big.isupper() else big
    text = f"{head} (xem full trên kênh)"
    while tags and len((text + " " + " ".join(tags) + ".mp4").encode()) > 240:
        tags.pop()
    return BAD.sub(" ", (text + " " + " ".join(tags)).strip())


def pick(subs: list, hook: str) -> tuple[int, int]:
    lines = "\n".join(f"{i + 1}. [{a:.0f}s–{b:.0f}s] {t}" for i, (a, b, t) in enumerate(subs))
    q = (f"Đoạn mồi TikTok cần cắt: {hook}\nDưới đây là các câu (số, thời gian, lời). Chọn DẢI CÂU LIỀN NHAU dài 3–5 phút "
         "(180–300 giây) làm đoạn mồi. Bắt đầu từ câu móc/cảnh ức chế đầu tiên (BỎ các câu tóm tắt truyện hay tiết lộ "
         "kết cục ở đầu phần, bỏ lời chào kênh). Dừng ĐÚNG lúc nữ chính sắp phản đòn / kẻ ác đắc ý nhất, TRƯỚC khi lộ bất "
         "kỳ kết quả nào (ai thắng, bí mật gì); không lấy lời kêu gọi đăng ký ở cuối phần. "
         f'Chỉ trả JSON {{"start": số câu đầu, "end": số câu cuối}}.\n\n{lines}')
    text, _ = pool.ask("tag", q, max_tokens=2000, json_mode=True)
    m = re.search(r"\{.*\}", text, re.S)
    d = json.loads(m.group(0)) if m else {}
    s, e = int(d.get("start", 1)), int(d.get("end", 1))
    if not 1 <= s <= e <= len(subs):
        raise SystemExit(f"AI chọn dải câu không hợp lệ: {text[:200]}")
    return s, e


def auto_ranges(sd: pathlib.Path, parts=(1, 2, 3)) -> tuple[str, str]:
    """AI (nhóm nguồn miễn phí) chọn các khúc theo CÔNG THỨC của Người sáng lập (28/9/2026): 1–3 câu mở gây sốc → cảnh ức
    chế → TRỌN cao trào 1 (cú vả mặt đầu tiên) → leo tới sát đỉnh 2 rồi NGẮT ngay trước khi đỉnh 2 nổ. 180–300 giây."""
    subs = {p: direct.parse_srt(sd / "audio" / f"{p:03d}.srt") for p in parts if (sd / "audio" / f"{p:03d}.srt").exists()}
    lines = "\n".join(f"{p}:{i + 1} [{b - a:.0f}s] {t}" for p, ss in subs.items() for i, (a, b, t) in enumerate(ss))

    def total(ranges: str) -> float:
        tot = 0.0
        for rg in ranges.split(","):
            p, span = rg.strip().split(":")
            s, e = map(int, span.split("-"))
            ss = subs[int(p)]
            if not 1 <= s <= e <= len(ss):
                raise ValueError(f"khúc {rg} ngoài phạm vi")
            tot += ss[e - 1][1] - ss[s - 1][0]
        return tot

    note = ""
    for _ in range(3):
        q = ("Cắt đoạn mồi TikTok 180–300 giây từ các câu dưới đây (dạng 'phần:số câu [độ dài] lời'). CÔNG THỨC: "
             "(1) 1–3 câu mở đầu gây sốc; (2) vài khúc cảnh nữ chính bị ức hiếp; (3) TRỌN VẸN cao trào 1 (cú vả mặt/lật mặt "
             "đầu tiên, có cả phản ứng của kẻ ác); (4) leo tiếp tới sát đỉnh 2 và NGẮT NGAY TRƯỚC khi đỉnh 2 xảy ra, để người "
             "xem phải sang YouTube xem kết quả. Được ghép 8–16 khúc câu liền nhau, theo thứ tự thời gian. BỎ lời chào kênh, "
             "lời kêu gọi đăng ký, câu tóm tắt đầu phần lặp lại, bình luận dài dòng. Chữ lớn trên màn hình: ≤ 12 từ, gây tò "
             "mò, KHÔNG lộ ai thắng hay bí mật. Chỉ trả JSON {\"ranges\": \"1:1-3,1:12-15,…\", \"text\": \"…\"}."
             + note + "\n\n" + lines)
        text, _ = pool.ask("tag", q, max_tokens=4000, json_mode=True)
        m = re.search(r"\{.*\}", text, re.S)
        try:
            d = json.loads(m.group(0)) if m else {}
            ranges, big = re.sub(r"\s", "", str(d["ranges"])), str(d.get("text", "")).strip()
            t = total(ranges)
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            note = f"\nLần trước trả sai dạng ({e}), trả lại đúng JSON."
            continue
        if MIN_S - 15 <= t <= MAX_S + 15:
            print(f"AI chọn {len(ranges.split(','))} khúc, {t:.0f} giây: {ranges}")
            return ranges, big
        note = f"\nLần trước tổng {t:.0f} giây (cần 180–300): {'bớt' if t > MAX_S else 'thêm'} khúc."
    raise SystemExit("AI không chọn được đoạn mồi đúng 3–5 phút sau 3 lần")


def multi(a, sd: pathlib.Path, big: str) -> int:
    """Ghép nhiều khúc câu (có thể khác phần) thành 1 đoạn mồi: mỗi khúc cắt kịch bản cảnh + audio của phần đó, nối liền."""
    work = ROOT / "tmp" / f"tiktok_{a.slug}"
    work.mkdir(parents=True, exist_ok=True)
    shots, subs_out, cast, wavs, off = [], [], {}, [], 0.0
    boards = {}
    for k, rg in enumerate(a.ranges.split(",")):
        part, span = rg.strip().split(":")
        part, (s, e) = int(part), map(int, span.split("-"))
        subs = direct.parse_srt(sd / "audio" / f"{part:03d}.srt")
        if part not in boards:
            boards[part] = direct.direct(a.slug, part)[0]
        sb = boards[part]
        t0, t1 = subs[s - 1][0], subs[e - 1][1]
        wav = work / f"seg{k:02d}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0), "-i",
                        str(sd / "audio" / f"{part:03d}.mp3"), "-ar", "48000", "-ac", "1", str(wav)], check=True)
        wavs.append(wav)
        cut = lambda xs: [{**x, "start": max(x["start"], t0) - t0 + off, "end": min(x["end"], t1) - t0 + off}
                          for x in xs if x["end"] > t0 and x["start"] < t1]
        shots += cut(sb["shots"])
        subs_out += cut(sb["subs"])
        cast.update(sb["cast"])
        off += t1 - t0
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{w}'\n" for w in wavs), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), str(work / "clip.wav")],
                   check=True)
    for sh in shots:
        sh["background"] = sh["background"].replace("../../../", str(ROOT) + "/")
    sb0 = next(iter(boards.values()))
    clip = {**sb0, "audio": "clip.wav", "cast": cast, "shots": shots, "subs": subs_out,
            "overlay": {"top": big, "cta": CTA, "cta_from": max(0.0, off - 4)}}
    (work / "clip.yaml").write_text(yaml.safe_dump(clip, allow_unicode=True, sort_keys=False), encoding="utf-8")
    cap = caption(sd, big)
    out = sd / "output"
    video = out / f"{cap}.mp4"
    render(work / "clip.yaml", "1080x1920", video)
    (out / f"{cap}.txt").write_text(cap + "\n", encoding="utf-8")
    print(f"Xong: {video.relative_to(ROOT)} — {len(wavs)} khúc, {off:.0f} giây")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--part", type=int)
    ap.add_argument("--start", type=int)
    ap.add_argument("--end", type=int)
    ap.add_argument("--ranges", help="ghép nhiều khúc: 'phần:câu-câu,…' vd '1:1-2,2:32-36,3:96-98' (công thức: cao trào 1 → "
                    "leo tới đỉnh 2 → ngắt)")
    ap.add_argument("--auto", action="store_true", help="AI tự chọn khúc theo công thức từ phần 1–3 (drama)")
    ap.add_argument("--text", help="chữ lớn trên màn hình (mặc định lấy 'Câu chữ lớn' trong hook.md)")
    a = ap.parse_args()
    sd = ROOT / "stories" / a.slug
    hook = (sd / "outline/hook.md").read_text(encoding="utf-8")
    part = a.part or int(re.search(r"Phần\s*(\d+)", hook).group(1))
    big = a.text or (re.search(r"(?:Câu chữ lớn|Chữ trên màn hình):\s*(.+)", hook) or [None, ""])[1].strip().strip('"*')
    if a.auto and not a.ranges:
        a.ranges, auto_big = auto_ranges(sd)
        big = a.text or auto_big or big
    if a.ranges:
        return multi(a, sd, big)
    subs = direct.parse_srt(sd / "audio" / f"{part:03d}.srt")
    s, e = (a.start, a.end) if a.start else pick(subs, hook)
    while not a.start and subs[e - 1][1] - subs[s - 1][0] < MIN_S and (s > 1 or e < len(subs)):   # AI chọn ngắn quá: máy nới cho đủ
        if s > 1:
            s -= 1                                   # ưu tiên thêm phía trước (bối cảnh), giữ điểm dừng gây tò mò
        else:
            e += 1
    while not a.start and subs[e - 1][1] - subs[s - 1][0] > MAX_S and s < e:   # tự chọn câu thì giữ nguyên                      # dài quá: bớt phía trước
        s += 1
    t0, t1 = subs[s - 1][0], subs[e - 1][1]
    sb, _ = direct.direct(a.slug, part)
    out_dir = sd / "output"
    out_dir.mkdir(exist_ok=True)
    work = ROOT / "tmp" / f"tiktok_{a.slug}"
    work.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0), "-i",
                    str(sd / "audio" / f"{part:03d}.mp3"), str(work / "clip.wav")], check=True)
    cut = lambda xs: [{**x, "start": max(x["start"], t0) - t0, "end": min(x["end"], t1) - t0}
                      for x in xs if x["end"] > t0 and x["start"] < t1]
    clip = {**sb, "audio": "clip.wav", "shots": cut(sb["shots"]), "subs": cut(sb["subs"]),
            "overlay": {"top": big, "cta": CTA, "cta_from": max(0.0, (t1 - t0) - 4)}}
    for sh in clip["shots"]:
        sh["background"] = sh["background"].replace("../../../", str(ROOT) + "/")
    (work / "clip.yaml").write_text(yaml.safe_dump(clip, allow_unicode=True, sort_keys=False), encoding="utf-8")
    cap = caption(sd, big)
    video = out_dir / f"{cap}.mp4"                     # tên file = mô tả + hashtag → TikTok tự điền khi tải lên
    render(work / "clip.yaml", "1080x1920", video)
    (out_dir / f"{cap}.txt").write_text(cap + "\n", encoding="utf-8")
    print(f"Xong: {video.relative_to(ROOT)} — phần {part}, câu {s}–{e}, {t1 - t0:.0f} giây")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
