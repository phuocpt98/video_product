# Kế hoạch lô drama 2: 3 truyện ngắn mô-típ mới

Cập nhật: 28/9/2026 · Trạng thái: **ĐỀ XUẤT, chưa sản xuất** (Người sáng lập: "lên kế hoạch thôi chưa làm")

Nguồn: [research/2026-09-28-3-truyen-nguon.md](../research/2026-09-28-3-truyen-nguon.md), [research/2026-09-28-zhihu-short-stories.md](../research/2026-09-28-zhihu-short-stories.md).

## 1. Tình trạng nguồn truyện

Researcher trên agy **không lấy được text gốc**. Zhihu và 番茄 chặn đọc tự động. Cả 3 truyện đều ghi tác giả "佚名", link chỉ là trang tìm kiếm. Dàn ý thực chất là AI dựng theo mô-típ; truyện 3 có chi tiết "gọi 113" là số của Việt Nam, bên Trung là 110.

Hai đường đi:

| Đường | Cách làm | Rủi ro bản quyền | Việc của Người sáng lập |
|---|---|---|---|
| **A (mặc định)** | Dùng 3 dàn ý dưới đây làm khung, AI viết truyện mới như lô 1 | Thấp: mô-típ, không có tác phẩm gốc | Duyệt kế hoạch |
| **B (bám truyện thật)** | Người sáng lập tự mở app hoặc web 番茄/七猫/知乎, tìm theo từ khoá ở mục 5, chép text vào `stories/<slug>/source/goc.txt`. Chạy `--ref` chế độ "giữ khung, thay thịt" | Vừa: giữ khung truyện của người khác, đã buộc đổi chi tiết | Chép text 3 truyện, khoảng 10 phút mỗi truyện |

## 2. Ba truyện

### Truyện A. Lột mặt nạ phượng hoàng nam (ưu tiên 1)

- **Slug:** `phuong-hoang-nam`
- **Mô-típ:** tiểu thư nhà giàu sắp cưới anh chàng nghèo "hiền lành". Trước cưới, cô phát hiện hắn bàn với mẹ bòn tiền hồi môn mua nhà cho em trai, và nuôi tình cũ dưới danh "em họ ở quê". Cô giả ngoan, gài hợp đồng để hắn tự đứng tên vay nợ. Đám cưới biến thành buổi vạch mặt: màn hình phát bằng chứng, chủ nợ ập tới, hắn gánh nợ, bị tố lừa đảo.
- **Vai (4–5):**
  - nữ chính (`f-evening`, `f-wedding` ở đám cưới)
  - phượng hoàng nam (`m-office`, `m-groom`)
  - mẹ chồng tham lam (`f-home`)
  - tình cũ "em họ" (`f-white-dress`)
  - chủ nợ (`m-leather`)
- **Nền:**
  - có sẵn: `villa-living-room`, `hotel-banquet` (tiệc cưới), `cafe`, `meeting-room` (ký hợp đồng), `police-station`
  - không thiếu nền nào
- **TikTok mồi:** câu sốc (tin nhắn bòn tiền), ức chế (đòi nữ chính lo hết tiệc cưới), **cao trào 1** (gài được hợp đồng vay), leo tới đám cưới. **Ngắt** đúng lúc màn hình lớn bật lên.
- **Thumbnail:** nữ chính váy cưới cười nhếch. Chú rể và mẹ chồng hoảng, bên trên chữ "ĐÁM CƯỚI HOÁ PHIÊN TOÀ".
- **Khác lô 1:** trục là **tiền và nợ**, không phải ngoại tình. Đối tượng là trai nghèo hám danh.

### Truyện B. Mẹ kế không làm nữa (ưu tiên 2)

- **Slug:** `me-ke-dinh-cong`
- **Mô-típ:** trọng sinh đúng ngày sinh nhật con riêng, nữ chính nghe lén con riêng gọi tình nhân của chồng là "mẹ". Cô bình thản rút tiền, đòi "lương bảo mẫu", nhường chỗ hầu hạ cho tình nhân. Con riêng bị tình nhân hành, quay lại xin thì bị từ chối. Chồng phá sản vì cô rút vốn.
- **Cần sửa khi viết:**
  - Con riêng để 12–15 tuổi (dùng `m-school`, `f-school`), tránh cảnh bạo hành trẻ nhỏ.
  - "Bạo hành tinh thần" chỉ kể lại, không dựng thành cảnh.
- **Vai (5):**
  - nữ chính (`f-office`)
  - chồng (`m-suit`)
  - con riêng (`m-school`)
  - tình nhân (`f-evening`, môi đỏ `mouth4`)
  - mẹ chồng (`f-lady`)
- **Nền:** `villa-living-room`, `rich-bedroom`, `meeting-room` (thay văn phòng công chứng), `courtroom`, `company-lobby`. Có đủ.
- **TikTok mồi:** câu sốc (con riêng gọi tình nhân là mẹ), **cao trào 1** (tung bằng chứng ngoại tình giữa bữa tiệc), leo tới tình nhân dọn vào nhà. **Ngắt** trước khi con riêng quay lại cầu xin.
- **Khác lô 1:** trục là **tình mẫu tử giả, người phụ nữ bị coi là bảo mẫu**. Tránh lặp "vợ trị chồng" của vo-cao-tay: không cho nữ chính lật công ty, chỉ rút vốn.

### Truyện C. Từ chối làm "phù đệ ma" (ưu tiên 3)

- **Slug:** `phu-de-ma`
- **Mô-típ:** bố mẹ và em trai phá nhà tân hôn, ép nữ chính bán nhà lấy tiền cưới vợ cho em. Cô báo công an, đòi bồi thường. Em trai đập "xe của chị" trong hầm để xả giận, hoá ra là siêu xe mượn của sếp. Em bị bắt. Bố mẹ quỳ xin, cô đưa giấy cắt quan hệ đã công chứng.
- **Cần sửa khi viết:**
  - Số cảnh sát là 110 (bối cảnh Trung Quốc).
  - **Không trọng sinh.** Phải khác hẳn trong-sinh-vo-on (cùng họ trọng nam khinh nữ): ở đây nữ chính đấu bằng pháp luật hiện đại.
- **Vai (4):**
  - nữ chính (`f-office`)
  - em trai (`m-hoodie`)
  - mẹ đẻ (`f-home`)
  - bố đẻ (`m-oldman`)
  - sếp (`m-suit`), tuỳ chọn
- **Nền:**
  - có sẵn: `home-living-room` (nhà tân hôn), `police-station`, `open-office`, `courtroom`
  - **thiếu:** hầm để xe (tạm dùng `residential-alley` hoặc `city-street-night`)
  - **thiếu:** siêu xe. Lớp xe cộ chưa có code; tạm để lời kể nói, hình dùng `car-roadside-night`.
- **TikTok mồi:** câu sốc (phá nhà tân hôn, cú tát), **cao trào 1** (tại đồn công an đòi bồi thường), leo tới lúc em trai cầm gậy xuống hầm xe. **Ngắt** trước khi lộ đó là siêu xe của sếp.
- **Nên làm sau:** khi có lớp xe cộ và nền hầm xe (xem `board/image_queue.yaml`) thì cú lật đập xe mới có hình.

## 3. Lệnh chạy (khi Người sáng lập duyệt)

```
python scripts/drama_pipeline.py <slug> --motif "<mô-típ 1 đoạn ở mục 2>" [--ref stories/<slug>/source/goc.txt] --parts 6 --full
```

- Chạy từng truyện một: agy dùng chung quota, chạy song song dễ hết lượt giữa chừng.
- Mỗi truyện ra: bản full khoảng 25 phút (giọng 1,34×), TikTok 3–5 phút, `.srt`, thumbnail, `upload.md`.
- Trước khi chạy, cập nhật `cast.yaml` sau bước tạo truyện: chọn nền mới (biệt thự, tiệc cưới…) thay nền bình dân. Nhớ bài học thien-kim-that.

## 4. Thời gian và chi phí (theo số đo lô 1)

| Hạng mục | Mỗi truyện | Cả 3 truyện |
|---|---|---|
| Máy chạy | 45–60 phút | khoảng 3 giờ nếu không hết quota |
| Quota agy (Gemini) | 15–25% khung 5 giờ, 5–8% tuần | khoảng 60% khung 5 giờ, khoảng 20% tuần |
| Người sáng lập (đường A) | xem và đăng khoảng 25 phút | khoảng 75 phút |
| Thêm cho đường B | chép text khoảng 10 phút | khoảng 30 phút |
| Tiền | 0 | 0 |

## 5. Từ khoá tìm truyện thật (đường B)

| Truyện | Từ khoá (dán vào 番茄/七猫/知乎) |
|---|---|
| A | `凤凰男 婚礼 反转 短篇 完结`, `撕下凤凰男伪装` |
| B | `重生 后妈不干了 短篇`, `觉醒后这后妈我不当了` |
| C | `扶弟魔 反击 短篇 完结`, `拒绝扶弟魔 豪车` |

Chọn truyện dài 6.000–15.000 chữ, đã hoàn (完结), đọc miễn phí.

## 6. Cần Người sáng lập chốt

1. Đường A hay B (hoặc A cho truyện C, B cho A và B)?
2. Thứ tự A → B → C, và có đợi lớp xe cộ cho truyện C không?
3. Có cần xem trước sổ tay và đoạn mồi (`outline/hook.md`) của từng truyện trước khi chạy lồng tiếng và dựng không? Thêm khoảng 5 phút mỗi truyện, đổi lại tránh phải làm lại.
