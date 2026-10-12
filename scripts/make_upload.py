"""GÓI ĐĂNG YOUTUBE cho truyện đã ghép bản full: phụ đề .srt gộp các phần, thumbnail (make_thumbnail.py drama), upload.md
(tiêu đề, mô tả có mốc từng phần, hashtag, thẻ, cài đặt). Nội dung chữ do AI nhóm nguồn miễn phí soạn (JSON), code ghép.

python scripts/make_upload.py <slug> [--parts 6]
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


def dur(p: pathlib.Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          str(p)]))


def hms(t: float) -> str:
    return f"{int(t // 60):02d}:{int(t % 60):02d}" if t < 3600 else f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{int(t % 60):02d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--parts", type=int, default=6)
    a = ap.parse_args()
    sd, out = ROOT / "stories" / a.slug, ROOT / "stories" / a.slug / "output"
    parts = [out / f"studio_{n:03d}_1920x1080.mp4" for n in range(1, a.parts + 1)]
    full = out / f"full_{a.slug}.mp4"
    # phụ đề gộp: lệch giờ theo độ dài video từng phần
    starts, off, n, srt = [], 0.0, 0, []
    ts = lambda t: "%02d:%02d:%02d,%03d" % (t // 3600, t % 3600 // 60, int(t % 60), int(t * 1000) % 1000)
    for i, p in enumerate(parts, 1):
        starts.append(off)
        for s, e, t in direct.parse_srt(sd / "audio" / f"{i:03d}.srt"):
            n += 1
            srt.append(f"{n}\n{ts(s + off)} --> {ts(e + off)}\n{t}\n")
        off += dur(p)
    (out / f"full_{a.slug}.srt").write_text("\n".join(srt), encoding="utf-8")

    cast = yaml.safe_load((sd / "cast.yaml").read_text(encoding="utf-8"))
    ch = yaml.safe_load((ROOT / "channels/khoai-tay-review/channel.yaml").read_text(encoding="utf-8"))
    cards = "\n\n".join((sd / "outline/chapter_cards" / f"{i:03d}.md").read_text(encoding="utf-8")[:1500]
                        for i in range(1, a.parts + 1) if (sd / "outline/chapter_cards" / f"{i:03d}.md").exists())
    titles = (sd / "outline/title.md").read_text(encoding="utf-8") if (sd / "outline/title.md").exists() else ""
    q = ("Soạn gói đăng YouTube cho video truyện drama hoạt hình chibi (kênh Khoai Tây Review, giọng kể nữ). Chỉ trả JSON: "
         '{"title": "tiêu đề ≤ 95 ký tự, công thức [phe ác làm gì] + [nữ chính phản đòn] + [con số/cái kết], kết bằng '
         '| Truyện Full", "summary": "3–4 câu tóm tắt gây tò mò, không lộ kết", "parts": ["tên ngắn phần 1", …], '
         '"thumb_small": "dòng nhỏ ≤ 8 từ", "thumb_big": "dòng to 3–5 từ, cực gắt", "villains": ["tên kẻ ác 1", "tên kẻ '
         'ác 2"], "tags": ["8–12 thẻ tiếng Việt"]}. Tên nhân vật dùng đúng danh sách: ' + ", ".join(cast["characters"])
         + f". Nữ chính: {cast['lead']}. Tiêu đề gợi ý có sẵn:\n{titles}\n\nThẻ từng phần:\n{cards}")
    d = {}
    for _ in range(3):
        text, _src = pool.ask("tag", q, max_tokens=4000, json_mode=True)
        m = re.search(r"\{.*\}", text, re.S)
        try:
            d = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            d = {}
        if d.get("title") and len(d.get("parts", [])) >= a.parts:
            break
    if not d.get("title"):
        raise SystemExit("AI không soạn được gói đăng")

    # thumbnail: nữ chính cười nhếch phía trước, 2 kẻ ác sợ hãi phía sau, nền cảnh cao trào (nền mở đầu phần cuối)
    actor = lambda name: cast["characters"].get(name, {}).get("actor")
    villains = [actor(v) for v in d.get("villains", []) if actor(v) and actor(v) != actor(cast["lead"])][:2]
    fx = [":shocked:sweat", ":sad:tears"]
    bg = cast.get("chapters", {}).get(a.parts, {}).get("scene", "hotel-banquet")
    for words in (99, 5, 4, 3):                        # dòng to quá dài (> 3 dòng) thì bớt từ
        big = " ".join(d["thumb_big"].split()[:words])
        r = subprocess.run([sys.executable, "scripts/make_thumbnail.py", "drama", a.slug, d["thumb_small"], big,
                            "TRUYỆN FULL", str(out / "thumbnail.png"), "--bg", bg, "--lead", f"{actor(cast['lead'])}:smirk",
                            "--back", ",".join(v + f for v, f in zip(villains, fx))], cwd=ROOT)
        if r.returncode == 0:
            break

    tags = " ".join(ch["hashtags"]["youtube_top3"] + ch["hashtags"]["youtube_common"] + ["#truyendrama", "#truyenngan",
                                                                                          "#vamat"])
    marks = "\n".join(f"{hms(t)} Phần {i} – {name}" for i, (t, name) in enumerate(zip(starts, d["parts"]), 1))
    md = f"""# Gói đăng: {d['title']}

## YouTube
- **Video:** `{full.name}` ({hms(off)}, 1920×1080)
- **Phụ đề:** `full_{a.slug}.srt` ({n} câu), tải lên mục Phụ đề, Tiếng Việt, "Có thời gian"
- **Thumbnail:** `thumbnail.png` (1280×720)
- **Tiêu đề** ({len(d['title'])} ký tự):

```
{d['title']}
```

- **Mô tả:**

```
{d['summary']}

⏱️ Mốc truyện:
{marks}

👉 Đăng ký kênh + bật chuông 🔔 để nghe truyện mới mỗi trưa 12h.

✍️ Truyện do Khoai Tây Review sáng tác và kể lại, có lời bình của người kể. Nhân vật, tình tiết là hư cấu. Video dùng giọng đọc AI và hình ảnh hoạt hình do kênh tự tạo.

{tags}
```

- **Thẻ:** {", ".join(dict.fromkeys(x.strip().lower() for x in ["khoai tây review", "nghe truyện", "truyện audio", "truyện full"] + d.get("tags", [])))}
- **Cài đặt:** Không dành cho trẻ em · bật bình luận · danh mục Giải trí · Công khai hoặc lên lịch 12h trưa
- **Danh sách phát:** "Truyện Drama Ngắn | Nghe Liền Một Mạch"

## TikTok (đăng SAU khi YouTube đã công khai)
- File bắt đầu bằng chữ in thường trong `output/` (tên file = chú thích + hashtag), ghim bình luận "Full trên YouTube: Khoai Tây Review 🥔"
"""
    (out / "upload.md").write_text(md, encoding="utf-8")
    print("Xong gói đăng:", (out / "upload.md").relative_to(ROOT), "|", d["title"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
