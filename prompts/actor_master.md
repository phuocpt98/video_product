# Ảnh gốc toàn thân của diễn viên (chế độ `semi`: đầu to hơn người thật một chút)

Dùng cho `scripts/new_actor.py` bước 1. Thay `{look}` bằng mô tả ngoại hình trong card (tiếng Anh), `{outfit}` bằng mô tả bộ đồ. Tỉ lệ khung 9:16.

```
Character design sheet, ONE character, full body from the top of the head to the soles of the feet, standing straight,
facing the viewer, arms relaxed at the sides, feet slightly apart, 10% empty margin above the head and below the feet.
{look}. Outfit: {outfit}.
STYLE: clean modern Chinese webtoon (manhua) line art, elegant and refined; thin uniform black outlines;
FLAT solid colors only, NO shading, NO gradients, NO highlights, NO texture; pure flat white background (#FFFFFF).
PROPORTIONS: stylised but graceful, about 4.5 heads tall (head slightly larger than a real person), slim neck visible,
natural shoulders.
FACE: refined elegant features, almond-shaped eyes with delicate lashes and a small bright highlight, thin arched brows,
small straight nose drawn with a short line, soft natural lips, slim oval face, calm expression, mouth closed.
HAIR: {hair}. ALL long hair hangs BEHIND the shoulders and back, none in front of the shoulders or chest, so the
collar and shoulders are fully visible.
NO text, NO caption, NO watermark, NO labels, NO extra objects, NO second character.
```

Ghi chú:
- `{hair}` ví dụ: "long straight black hair with straight bangs" hoặc "short neat black hair, no bangs".
- Tóc dài **bắt buộc sau lưng** để lớp tóc sau tách được và nằm sau thân (vấn đề 4 trong `docs/research/2026-10-13-puppet-v2.md`).
- Màu phẳng, viền đen, nền trắng là điều kiện để `src/studio/segment.py` tách lớp bằng màu, không cần AI.
