# Thư viện nhân vật và thư viện cảnh (YouTube 16:9 + TikTok 9:16)

Cập nhật: 27/9/2026 · Trạng thái: **đề xuất, chờ Người sáng lập duyệt** · Nghiên cứu nền: [visual-library](../research/2026-09-27-visual-library.md) (chưa duyệt chéo), [ai-film](../research/2026-09-27-ai-film.md), [tiktok-hook-strategy.md](tiktok-hook-strategy.md)

## 1. Mục tiêu
- Thay khung hình tĩnh bằng hình **khớp nội dung từng đoạn**, nhân vật **nhất quán** xuyên suốt truyện.
- **Tạo ít, dùng lại nhiều.** Ví dụ một cảnh gọi điện 1–2 giây dùng cho cả đoạn hội thoại, mỗi lần dùng đổi khung, zoom hoặc góc để YouTube không coi là lặp.
- Một bản gốc dùng được cho **cả YouTube (16:9) lẫn TikTok (9:16)**.
- Có **mục lục** và **ghi chú chi tiết** để người và máy tìm lại được, dùng lại qua nhiều truyện.

## 2. Ràng buộc đã biết
- **Chính sách YouTube (inauthentic content, từ 7/2025):** nhắm vào "Image slideshows or scrolling text with minimal or no narrative, commentary, or educational value" và nội dung sản xuất hàng loạt không có dấu ấn con người ([support.google.com/youtube/answer/1311392](https://support.google.com/youtube/answer/1311392)). Theo kinh nghiệm cộng đồng (chưa có con số chính thức): **cứ 5–10 giây phải có một thay đổi hình ảnh**.
- **Tạo ảnh (đo ngày 27/9):** `generate_image` của agy **tạo được** (model `gemini-3.1-flash-image`), mỗi ảnh chỉ tốn khoảng 1% quota Gemini (phần chữ) và **không trừ kho Claude**. Nhưng model ảnh có **giới hạn riêng, không hiện trong `/usage`**: tối 27/9 bị báo 429 sau khoảng **13–14 ảnh**. Nên tạo mỗi đợt dưới 12 ảnh. Các nguồn còn lại: app Gemini (làm tay), Gemini API qua key miễn phí của AI Studio (tự động, có giới hạn), hoặc model chạy trên máy (chậm).
- **Máy M2 Pro 16 GB:** không chạy nổi model video. **Đã thử tạo ảnh local (27/9): Z-Image-Turbo qua mflux ra đúng nét 2D phẳng, nhưng mất khoảng 3,5–4 phút mỗi ảnh, RAM đỉnh 12,6 GB, máy nóng, nhân vật trông trẻ hơn tuổi. Người sáng lập loại phương án này; đã xoá model (32,8 GB) và gỡ mflux.**

## 3. Cấu trúc thư viện

```
assets/
├── characters/                    THƯ VIỆN NHÂN VẬT (dùng lại qua nhiều truyện)
│   ├── INDEX.md                   mục lục (script tự sinh từ các card.yaml)
│   └── <id>/                      ví dụ: tran-han-thang
│       ├── card.yaml              hồ sơ + "prompt DNA" + ghi chú
│       ├── sheet.png              character sheet 4 góc (chính diện, 3/4, nghiêng, sau lưng)
│       ├── expressions/           biểu cảm: cười, giận, sốc, buồn… (1:1)
│       └── outfits/               trang phục theo giai đoạn truyện
├── scenes/                        THƯ VIỆN CẢNH (bối cảnh + tình huống lặp lại)
│   ├── INDEX.md
│   └── <id>/                      ví dụ: phone-call-night, bus-stop-2002, classroom
│       ├── card.yaml
│       ├── master_*.png           ảnh gốc 1:1 độ phân giải cao
│       └── clips/                 clip ngắn 1–3 giây (Veo làm tay, có bản 16:9 và 9:16)
└── fx/                            hạt phim, vệt sáng, chuyển cảnh (tự tạo hoặc có giấy phép) + LICENSE.md
```

**`card.yaml` của nhân vật** (ví dụ rút gọn):
```yaml
id: tran-han-thang
name: Trần Hán Thăng            # theo bảng tên của truyện
stories: [ta-that-su-khong-muon-trong-sinh]
dna: "Chinese male 18, short slightly messy black hair, sharp confident eyes, half smirk, ..."  # prompt cố định, không sửa
style: "2D donghua, clean lineart, warm light"   # chung cả kênh
outfits: {2002-he: "white loose T-shirt, blue jeans", dai-hoc: "..."}
notes: "Mặt hay bị trẻ hoá quá khi tạo; luôn thêm 'mature eyes'."
```

**`card.yaml` của cảnh:**
```yaml
id: phone-call-night
type: dialogue            # dialogue | action | establishing | emotion | transition
tags: [phone, night, room, alone, talk]
characters: [tran-han-thang]      # trống = cảnh không có nhân vật (dùng chung mọi truyện)
safe_box: {subject: [0.30,0.15,0.70,0.95], face: [0.42,0.18,0.58,0.40]}  # vùng an toàn, tỉ lệ 0–1 trên ảnh 1:1
frames: [16:9, 9:16]              # cảnh quá rộng thì chỉ 16:9
variants_used: {ta-that-su…/001: [wide-in, close-face-pan-left]}  # để tránh lặp y hệt
license: "Tự tạo bằng Gemini, 27/9/2026"
```

## 3a. Phong cách chung của kênh (Người sáng lập chốt 27/9/2026)
- **2D nét vẽ tay, tô màu phẳng (cel), đổ bóng tối giản**, kiểu hoạt hình và manhua Trung Quốc đầu thập niên 2000. **Không 3D, không giả ảnh thật, không ánh sáng điện ảnh.**
- Lý do: nhẹ và nhanh khi dùng lại; dễ giữ nhân vật nhất quán; dễ tách lớp nhân vật và nền (parallax, thay nền); cắt, zoom, lật không lộ lỗi.
- Đoạn phong cách gắn vào **mọi** prompt (lưu ở `channels/<kênh>/channel.yaml` → `visual_style`):
  `flat 2D hand-drawn cel animation, clean black ink outlines, flat solid colors, minimal cel shading, early-2000s Chinese donghua / manhua style, simple painted background, no 3D, no photorealism, no cinematic lighting, no gradients`

## 4. Tái sử dụng mà không bị coi là lặp
- **Một ảnh gốc 1:1 cắt ra nhiều khung:** toàn cảnh, trung cảnh, cận mặt (dựa vào `safe_box`) × **ngang hoặc dọc** × **chuyển động** (zoom vào, zoom ra, lia trái, lia phải, đứng yên rung nhẹ). Tính ra khoảng 10–30 biến thể mỗi ảnh.
- **Chuyển động có gia tốc** (ease-in/out), không dùng `zoompan` tuyến tính của ffmpeg vì nhìn "máy làm". Python tính toạ độ khung theo đường cong, ffmpeg cắt và ghép.
- **Hội thoại theo kiểu phim:** cận nhân vật A ↔ cận nhân vật B (shot, reverse shot), mỗi lượt thoại đổi khung. Một đoạn nói chuyện 2 phút chỉ cần 2–3 ảnh gốc.
- **Luật chống lặp (máy kiểm):**
  - Mỗi lượt hiển thị 3–8 giây.
  - Cùng một biến thể không dùng lại trong vòng 10 phút.
  - Cùng một ảnh gốc tối đa N lần mỗi video.
  - `variants_used` ghi lại để video sau không lặp y hệt video trước.
- **Lớp phủ:** hạt phim nhẹ, vệt sáng, chuyển cảnh, để có chuyển động thật trên màn hình.
- **Nâng cấp sau:** parallax 2.5D (tách lớp theo bản đồ độ sâu) cho cảnh đứng lâu. Nhìn "xịn" nhất, nhưng cần thử xem máy 16 GB chạy nổi không.

## 5. Chỗ gắn vào dây chuyền
Thêm bước **H. Phân cảnh → chọn hình → dựng**, sau bước giọng đọc (khi đã có mốc thời gian từng câu):
1. **Phân cảnh** (agy, Gemini Pro): đọc kịch bản + phụ đề + sổ tay. Với mỗi đoạn 3–8 giây, ghi loại cảnh, nhân vật, cảm xúc, thẻ.
2. **Khớp thư viện** (script): tìm cảnh theo thẻ và nhân vật, chọn biến thể chưa dùng. Không tìm được thì đưa vào **danh sách cần tạo** (`stories/<slug>/render/need_images.md`), kèm prompt đã ghép sẵn DNA nhân vật.
3. **Tạo ảnh còn thiếu:** tự động qua API nếu có, hoặc bạn làm tay trong app Gemini theo danh sách. Người duyệt ảnh xong, script đưa ảnh vào thư viện và tự sinh `card.yaml`.
4. **Dựng hai bản:** 16:9 cho video FULL, 9:16 cho clip TikTok, từ cùng một phân cảnh.

## 6. Phản biện luồng hiện tại

| # | Vấn đề | Bằng chứng | Hướng sửa |
|---|---|---|---|
| 1 | **Chậm:** lỗi nhỏ nào cũng kéo theo viết lại cả chương, soát lại, duyệt lại | Lô 1: phần chữ mất 28 phút, cộng thêm các vòng sửa sau đó | Máy kiểm theo sổ tay (đã làm từ cấm); **sửa khoanh vùng** bằng Flash thay vì viết lại cả chương |
| 2 | **LLM duyệt bịa lỗi** | Chấm chương 3 "1.100 từ" trong khi máy đếm 2.173 | Việc máy đo được thì máy quyết; trích dẫn phải khớp nguyên văn, không khớp thì loại |
| 3 | **Không lập kế hoạch quota** theo kho | Kho Claude/GPT (dùng chung với tạo ảnh) cạn sau 1 lô | Bảng ngân sách quota mỗi kho mỗi ngày; ưu tiên Gemini; đo trước khi mở rộng |
| 4 | **Giọng đọc là bước dài nhất và chạy tuần tự** | 2–3 phút/chương, VieNeu chỉ dùng khoảng 2 nhân CPU | Chạy 2–3 chương đọc giọng song song (máy có 10–12 nhân) |
| 5 | **Hình tĩnh** dễ dính chính sách nội dung không chân thực, người xem cũng chán | Chính sách YouTube (mục 2) | Thiết kế này |
| 6 | **Phụ thuộc nguồn chương miễn phí trên Qidian** | Chương VIP cần đăng nhập | Chọn truyện ngắn đã hoàn thành, hoặc tự sáng tác (hướng d) |
| 7 | **Dây chuyền theo lô chưa qua qa-lead** | — | QA sau khi sửa theo mục 1–2 |
| 8 | **Chưa có bước nghe kiểm trước khi đăng** | — | Checklist nghe thử 3 đoạn ngẫu nhiên mỗi tập + xem thumbnail/tiêu đề |
| 9 | **Rủi ro làm quá tay trước khi có số liệu** | Chưa đăng video nào | Làm bản tối thiểu (mục 7) song song với đăng thử tập 1; chỉ mở rộng khi số liệu tốt |

## 7. Thử nghiệm đề xuất (bản tối thiểu, chỉ chương 1)
1. Tạo character sheet cho **Trần Hán Thăng** và **Tiêu Dung Ngư**, cộng **8–10 cảnh gốc** của chương 1: phòng tiệc, xe Range Rover ban đêm, tai nạn, xe buýt và trạm xe, đường đất và tiệm cắt tóc, nôn bên đường, cổng trường. Tổng khoảng 15–20 ảnh.
2. Viết phân cảnh chương 1 (khoảng 6 phút → khoảng 50–70 lượt hiển thị) và script dựng có chuyển động gia tốc.
3. Dựng **bản 16:9 chương 1** và **một clip TikTok 9:16 dài 30–45 giây** từ cùng phân cảnh.
4. Đo: số ảnh cần, thời gian tạo, thời gian dựng, cảm nhận của bạn, tốc độ trôi quota.

## 8. Cần Người sáng lập chốt
1. Duyệt cấu trúc thư viện (mục 3) và luật tái sử dụng (mục 4)?
2. **Nguồn tạo ảnh** cho thử nghiệm:
   - **(a)** bạn tạo tay trong app Gemini theo danh sách prompt mình soạn;
   - **(b)** tạo key miễn phí ở Google AI Studio để mình chạy tự động (Google được dùng dữ liệu gửi lên);
   - **(c)** chờ quota agy.
3. ~~Phong cách hình~~ → **đã chốt 27/9: 2D nét vẽ tay, tô màu phẳng, kiểu hoạt hình/manhua Trung Quốc đời cũ; không 3D, không giả ảnh thật** (xem mục 3a).
