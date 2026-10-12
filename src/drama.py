"""TRUYỆN TỰ VIẾT (drama ngắn 30–60 phút): nhóm trưởng (agy, Gemini Pro) nhận MÔ-TÍP + DÀN Ý THAM KHẢO (bóc cấp cao từ
truyện đang có, kiểu 拆书 + 仿写) và viết TRUYỆN MỚI: sổ tay (bible, nhân vật, sổ dữ kiện, đề cương) + thẻ từng phần theo
đúng định dạng run.py dùng, đánh dấu phần có đoạn mồi TikTok. Sau đó `python -m src.run <slug> --chapters 1-N` viết
kịch bản từng phần, đọc giọng như truyện thường (không đọc truyện gốc vì rewrite: deep).

python -m src.drama new <slug> --motif "<mô-típ>" [--ref docs/research/...md | stories/<slug>/source/goc.txt] [--parts 6] [--minutes 5]
--ref có thể là cả truyện nguồn tải về (lưu ở stories/<slug>/source/, không sửa): chỉ làm tài liệu, truyện viết ra là truyện mới.
Không chép lời, không giữ tên/chi tiết đặc trưng của truyện tham khảo: chỉ học khung tình tiết.
"""
import argparse
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def prompt(motif: str, ref: str, parts: int, minutes: int) -> str:
    return f"""Nhiệm vụ: VIẾT TRUYỆN DRAMA NGẮN MỚI cho kênh kể chuyện hoạt hình (người kể giọng nữ, tiếng Việt), dài khoảng
{parts * minutes} phút, chia {parts} PHẦN (mỗi phần ~{minutes} phút đọc, ~{minutes * 230} từ khi viết thành kịch bản).

Mô-típ: {motif}

Yêu cầu nội dung:
- Truyện HOÀN TOÀN MỚI: đặt tên nhân vật mới (tên Hán Việt kiểu truyện Trung, bối cảnh thành phố Trung Quốc hiện đại),
  tình tiết và chiêu trò viết khác đi. Dàn ý tham khảo bên dưới CHỈ để học khung nhịp; không giữ tên, câu thoại, chi tiết
  đặc trưng của nó.
- Nhịp "sảng văn": phần 1 vào thẳng lúc bị ức hiếp (không kể xuất thân dài); cuối phần 2 có cú vả mặt nhỏ đầu tiên; giữa
  truyện kẻ ác dồn ép, nữ chính âm thầm giăng lưới; phần cuối lật mặt trước đám đông, kẻ ác trả giá, kết sảng khoái.
- Mỗi phần kết bằng một móc câu.
- Thẻ phần 1 có thêm mục "## Mở đầu 30 giây": 2–3 câu đầu giữ chân người nghe (cảnh đắt nhất kể vượt lên trước, hoặc câu
  sốc, hoặc câu hỏi), chưa chào kênh.
- Chọn đoạn MỒI TIKTOK (3–5 phút) theo công thức: 1–2 câu mở đầu → CAO TRÀO 1 trọn vẹn (cú vả mặt nhỏ đầu tiên,
  thường cuối phần 2) → leo tiếp tới sát ĐỈNH 2 và NGẮT ngay trước khi đỉnh 2 nổ (người xem phải sang YouTube để biết kết
  quả/hậu quả). Có thể ghép nhiều khúc từ phần 1–3. Tuyệt đối không lấy từ phần cuối (lộ kết).
- Nhân vật ít (4–7 vai), mỗi vai có ngoại hình ngắn (để phòng Thiết kế ghép diễn viên chibi) và bối cảnh chính (để chọn nền:
  phòng khách, phòng ngủ, văn phòng, phòng giám đốc, nhà hàng, quán bar, phố, bệnh viện…).

Trả về các file theo đúng định dạng nhiều file:
- bible.md, characters.md, ledger.md, arc.md (đề cương cả truyện: coi là lô 1), rename_map.json (JSON:
  {{"_note": "...", "characters": {{"<tên>": "<tên>"}}, "places": {{}}, "terms": {{}}, "banned": {{}}}}), changes.md
- card_01.md … card_{parts:02d}.md: thẻ từng phần, mỗi thẻ bắt đầu bằng dòng "# Thẻ chương N" và có mục "## Diễn biến"
  (10–16 nhịp đánh số, mỗi nhịp 1–2 câu, có thoại chính trong ngoặc kép), "## Nhân vật xuất hiện", "## Bối cảnh",
  "## Móc câu cuối phần". Thẻ dài ít nhất 1500 ký tự.
- cast.yaml: mục lục truyện → thư viện, YAML đúng dạng:
  lead: <tên nữ chính>
  characters: {{<tên>: {{actor: {{slug}}-<vai không dấu, vd vo, chong, tieu-tam>, outfit: "", names: [<cách gọi khác>],
                note: "<giới, tuổi, ngoại hình, trang phục 1 dòng>"}}}}
  scenes: {{<id nền trong danh sách dưới>: [<3–6 từ khoá tiếng Việt xuất hiện trong lời kể khi ở nơi đó>]}}
  chapters: {{1: {{scene: <id nền mở đầu phần 1>}}, 2: ..., ...}}
  Danh sách nền được phép (chỉ chọn trong này): {{scenes}}
- hook.md: dòng đầu "Phần N" (phần chứa cao trào 1, phải là 1 hoặc 2); dòng "Cao trào 1: phần X nhịp a–b"; dòng
  "Đỉnh 2 (ngắt trước): phần Y nhịp c–d"; 2–3 câu tóm tắt; dòng
  "Câu chữ lớn: ..." (≤ 12 từ) gây ức chế/tò mò nhưng KHÔNG LỘ KẾT QUẢ (không nói ai thắng, không nói bí mật).
- title.md: 5 tiêu đề video tiếng Việt câu view (không giật tít sai sự thật), 1 dòng mô tả truyện.

Tài liệu tham khảo: dàn ý hoặc CẢ TRUYỆN NGUỒN (thường tiếng Trung). Cách dùng "giữ khung, thay thịt": được giữ mạch tình
tiết, các cú lật và điểm sảng; PHẢI thay toàn bộ tên người và nơi chốn, nghề nghiệp, chi tiết đặc trưng (đồ vật, sự kiện gây
mâu thuẫn), và TỰ VIẾT MỚI mọi lời kể, lời thoại (không dịch câu nào). Thêm ít nhất 2 tình tiết mới của riêng mình.
{ref or "(không có — tự dựng theo mô-típ)"}
"""


def new(slug: str, motif: str, ref_path: str | None, parts: int, minutes: int) -> pathlib.Path:
    from src import run
    from src.common import agy
    d = ROOT / "stories" / slug
    if (d / "story.yaml").exists():
        raise SystemExit(f"Đã có truyện {slug}")
    d.mkdir(parents=True, exist_ok=True)              # có thể đã có source/ (truyện nguồn tải về)
    (d / "story.yaml").write_text(yaml.safe_dump({
        "title_vi": slug, "title_zh": "", "channel": "khoai-tay-review", "genre": ["drama"], "status": "thu-nghiem",
        "source": "original", "motif": motif, "reference": ref_path or "", "rewrite": "deep", "parts": parts,
        "bible_approved": True,          # thử nghiệm: Người sáng lập xem bản TikTok trước rồi mới duyệt cả truyện
        "pipeline": {"fast": True, "batch_size": parts, "continuity_rounds": 1}}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    ref = (ROOT / ref_path).read_text(encoding="utf-8")[:60000] if ref_path else ""   # dàn ý, hoặc cả truyện nguồn (1–3 vạn chữ)
    role = (ROOT / "prompts/roles/story-lead.md").read_text(encoding="utf-8")
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    model = cfg["agents"]["story-lead"][0]
    need = ["bible.md", "characters.md", "ledger.md", "arc.md", "rename_map.json", "hook.md", "cast.yaml"] + \
        [f"card_{i:02d}.md" for i in range(1, parts + 1)]
    files = {}
    for _ in range(2):
        scenes = ", ".join(sorted(p.parent.name for p in (ROOT / "assets/scenes").glob("*/master.jpg")))
        task = prompt(motif, ref, parts, minutes).replace("{slug}", slug).replace("{scenes}", scenes)
        text = agy.run(role + "\n\n## Nhiệm vụ lần này\n" + task, model, timeout=1800)["text"]
        files = run.split_files(text)
        if all(k in files for k in need):
            break
    missing = [k for k in need if k not in files]
    if missing:
        raise SystemExit(f"Nhóm trưởng trả thiếu file: {missing}")
    story = run.Story(slug)
    run.write_bible_files(story, files, 1, f"lập truyện tự viết từ mô-típ: {motif[:60]}")
    for i in range(1, parts + 1):
        story.p("card", i).parent.mkdir(parents=True, exist_ok=True)
        card = files[f"card_{i:02d}.md"]
        if not re.search(rf"#\s*Thẻ chương\s*{i}\b", card):
            card = f"# Thẻ chương {i}\n\n" + card
        story.p("card", i).write_text(card.strip() + "\n", encoding="utf-8")
    from src.contracts import require
    cast = yaml.safe_load(re.sub(r"^```\w*|```$", "", files["cast.yaml"].strip(), flags=re.M))
    require("cast", cast, "cast.yaml (nhóm trưởng)")
    (d / "cast.yaml").write_text(yaml.safe_dump(cast, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (d / "outline").mkdir(exist_ok=True)
    for extra in ("hook.md", "title.md"):
        if extra in files:
            (d / "outline" / extra).write_text(files[extra].strip() + "\n", encoding="utf-8")
    m = re.search(r"#\s*(?:Tiêu đề|1\.)\s*(.+)", files.get("title.md", ""))
    meta = yaml.safe_load((d / "story.yaml").read_text(encoding="utf-8"))
    if m:
        meta["title_vi"] = m.group(1).strip().strip("*")
    (d / "story.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("new")
    a1.add_argument("slug")
    a1.add_argument("--motif", required=True)
    a1.add_argument("--ref")
    a1.add_argument("--parts", type=int, default=6)
    a1.add_argument("--minutes", type=int, default=5)
    a = ap.parse_args()
    d = new(a.slug, a.motif, a.ref, a.parts, a.minutes)
    print("Xong:", d.relative_to(ROOT), "→ xem outline/hook.md, bible/; rồi: python -m src.run", a.slug,
          f"--chapters 1-{a.parts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
