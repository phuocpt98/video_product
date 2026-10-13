# Vấn đề hệ nhân vật Puppet — Ghi nhận để nghiên cứu

Ngày: 2026-10-13
Người ghi: Muse (quá trình build bộ nhân vật mới cho "Ngày Cưới Đổi Dâu")

## Bối cảnh

- Repo dùng puppet renderer: đầu (head PNG) gắn lên thân (body PNG), lip-sync theo audio, blink, walk, khóc...
- User yêu cầu rebuild bộ nhân vật đẹp hơn (không chibi), chốt 6 archetype từ phim ngắn TQ.
- Đã gen 6 nhân vật full-body đẹp (loop-v2), mỗi nhân vật 5 biểu cảm (đầu).

## Vấn đề 1: Đầu mới + thân cũ = lệch tỉ lệ

**Hiện tượng:** Đầu gen theo tỉ lệ người thật (mặt 35–40% chiều cao) gắn lên thân chibi cũ → đầu to thân nhỏ, như búp bê gắn nhầm thân.

**Đã thử:** Giữ nguyên thân cũ, chỉ thay đầu. Kết quả: v2 thua v1 (bản gốc chibi đồng bộ đẹp hơn).

**Câu hỏi nghiên cứu:** Làm sao có hệ thân mới tỉ lệ người thật, đồng bộ với đầu mới? Hay phải gen lại toàn bộ (đầu + thân) cùng tỉ lệ?

## Vấn đề 2: AI không cắt được lớp giữ nguyên tọa độ

**Hiện tượng:** Dùng ảnh tổng là input, bảo AI "tách lớp 1 tóc sau giữ nguyên tọa độ" — AI vẽ lại composition mới hoàn toàn, không giữ pixel gốc.

**Đã thử 2 lần** với prompt nhấn mạnh "giữ nguyên kích thước 1280x1920 và vị trí tuyệt đối" — vẫn thất bại.

**Câu hỏi nghiên cứu:** Có cách nào dùng AI để segment (cắt mask) mà không redraw không? Hay phải dùng code (OpenCV/SAM) để cắt?

## Vấn đề 3: Ảnh tổng làm sprite trực tiếp → cứng, không động tác

**Hiện tượng:** (User chỉ ra) Dùng ảnh full-body nguyên con làm sprite thì nhân vật cứng đờ, không có walk/breathing/hair_sway vì mọi thứ đã "nướng" vào 1 ảnh.

**Câu hỏi nghiên cứu:** Làm sao vừa giữ tỉ lệ đẹp của ảnh gen, vừa tách được các bộ phận cử động độc lập (tay, đầu, tóc)? Có cần rig xương (skeletal) không, hay puppet 4 lớp hiện tại đủ?

## Vấn đề 4: Quy trình 4 lớp vs thực tế gen

**Quy trình đã chốt:**
1. Tóc sau full kín → 2. Thân từ cổ → 3. Mặt không tóc → 4. Mái khối đặc đè trán

**Khó khăn:** Mỗi lớp phải là mảnh "lego" hoàn chỉnh, kể cả phần bị lớp khác che (ví dụ: gáy bị tóc che, trán bị mái che, cổ bị đầu che). Gen từng mảnh riêng thì lệch tỉ lệ (vấn đề 1). Cắt từ ảnh tổng thì AI không giữ tọa độ (vấn đề 2).

**Câu hỏi nghiên cứu:** Workflow nào khả thi để tạo 4 lớp đồng bộ tỉ lệ? Có nên gen ảnh tổng trước rồi dùng tool segmentation (không phải AI-gen) để cắt?

## Vấn đề 5: Card.yaml thiếu trường khi tạo actor mới

**Hiện tượng:** Tạo actor mới thủ công (copy đầu + viết card.yaml) thì render lỗi liên tiếp:
- `KeyError: 'outfits'` — thiếu block outfits
- `KeyError: 'rig'` — thiếu block rig
- `KeyError: 'head_scale'` — thiếu trường trong rig

**Đã fix thủ công** bằng cách copy từ actor cũ. Nhưng đây là lỗi pipeline.

**Đề xuất:** Viết script `scripts/new_actor.py` validate đầy đủ trường bắt buộc khi tạo actor mới, báo lỗi rõ ràng thay vì KeyError giữa chừng.

## Vấn đề 6: Thay trang phục = gen lại cả người

Nếu dùng ảnh full-body (không tách lớp), mỗi bộ trang phục mới phải gen lại toàn bộ nhân vật → tốn lượt gen, khó giữ consistency khuôn mặt.

**Câu hỏi nghiên cứu:** Có cách nào tách riêng lớp trang phục để thay đồ mà không gen lại mặt/tóc không?

---

## File liên quan

- Ảnh tổng 6 nhân vật: `reference/loop-v2/media-generation-*-v2-full-*.webp`
- 4 actor v2 đã tạo (đầu mới + thân cũ, đang lệch): `assets/actors/{uyen-thanh,lieu-tuyet,ba-truong,tong-hao}-v2/`
- Thử nghiệm cắt lớp thất bại: `reference/lego-layers/uyen-thanh/`
- So sánh v1 vs v2: `~/workspace/video/kho-truyen-mau/ngay-cuoi-doi-dau/so-sanh-v1-v2/`
