# Dịch vụ AI trả phí: video, ảnh, giọng đọc

Cập nhật: 25/9/2026 · Tỷ giá tạm tính 26.000 VND/USD · Giá có ghi "(3P)" lấy từ trang tổng hợp bên thứ ba, chưa xác minh trên trang chính thức

## 1. Kết luận

- **Hai khoản tốn nhất là TTS và video.** Với 1,5 video/ngày, trung bình 12 giờ, cần khoảng 540 giờ audio/tháng (~30 triệu ký tự).
- **TTS rẻ nhất mà hợp pháp:** tự chạy mô hình mã nguồn mở (VieNeu-TTS, xem [open-source-video-ai.md](open-source-video-ai.md)), hoặc gói lớn FPT.AI, hoặc Gemini TTS. **ElevenLabs quá đắt** cho video dài.
- **edge-tts** (đang tính dùng cho MVP) **không được phép dùng thương mại** theo Microsoft. Chỉ dùng để thử, không dùng cho video kiếm tiền.
- **Video rẻ nhất:** MiniMax H3 qua Motion Studio (~0,023 USD/giây), Vidu Q3 Turbo, Seedance Mini, Veo 3.1 Lite. **Nhân vật nhất quán tốt nhất:** Kling 3.0 Omni Elements, Vidu Q3 chế độ tham chiếu.
- **Chi phí video giảm mạnh sau tháng đầu,** khi đã có kho clip nhân vật chính để dùng lại.
- **Ước tính mỗi tháng:** gói tiết kiệm **~110–430 USD (3–11 triệu VND)**, gói chất lượng **~1.000–1.500 USD**.

## 2. Motion Studio ([tasks.datools.info](https://tasks.datools.info/))

- **Ai vận hành:** không có tên công ty hay mã số thuế, chỉ có Gmail cá nhân và nhóm Zalo. Ra mắt 14/7/2026, bản v1.3.13 (15/8/2026). Nhiều khả năng một lập trình viên làm một mình, **rủi ro ngừng dịch vụ bất cứ lúc nào**.
- **Mô hình bên dưới:**

| Tính năng | Mô hình | Ghi chú |
|---|---|---|
| Motion Control | Wan 2.2 Animate tự chạy | Ảnh nhân vật + video mẫu → nhân vật làm theo điệu nhảy. 10/15/20 giây, tối đa 704×1248, 24fps. Hợp TikTok và thời trang, không hợp làm nền kể chuyện |
| MiniMax H3 | Hailuo 3.0 | Ảnh → video, chữ → video, R2V với 1–5 ảnh tham chiếu, tối đa 20 giây, 768p. **~0,023 USD/giây**, rẻ hơn API chính hãng (~0,08 USD/giây, 3P) |
| MV Music, Tạo nhạc | Không công bố | 1 ảnh + 1 bài hát → MV hát nhép. Mô tả + lời → bài nhạc |

- **Bảng giá:**
  - H3: 180k VND/5 phút, 342k/10 phút, 972k/30 phút.
  - Motion: Lite 49k/25 video, Pro 189k/100 video.
  - Mua mã nguồn: 1,5 triệu VND, tự chạy trên GPU từ 16GB.
- **API:** có (`POST /api/v1/motion`), nhưng **chỉ cho Motion Control**, chưa có API cho H3.
- **Quyền thương mại:** **không có điều khoản cho phép dùng thương mại rõ ràng.** Quyền với sản phẩm "theo luật hiện hành".
- **Hợp với kênh:** H3 R2V (ảnh nhân vật chính → clip 10–20 giây) là lựa chọn rẻ nhất tìm được. Cần hỏi chủ dịch vụ về quyền thương mại trước khi dùng nhiều.

## 3. Dịch vụ tạo video

| Dịch vụ | Giá API/giây | Clip tối đa | Nhân vật nhất quán | Gói tháng |
|---|---|---|---|---|
| **Kling 3.0 Omni** | 0,075–0,17 USD (3P) | 15 giây, nhiều cảnh, có âm thanh | **Elements:** tối đa 4 ảnh góc → nhân vật dùng lại. Mạnh nhất | 10 / 37 / 92 / 180 USD. Có credit miễn phí hằng ngày. Có giao diện tiếng Việt |
| **Hailuo / MiniMax H3** | 0,08 (768p), 0,13 (2K) | 15 giây | R2V nhiều ảnh tham chiếu. Có trọng số mở | 14,99–199,99 USD |
| **Google Veo 3.1** | Lite 0,05–0,08; Fast 0,10–0,12; Std 0,40 | 8 giây | Ảnh tham chiếu "Ingredients" | AI Pro 19,99 USD ≈ 100 clip Lite. Có watermark SynthID |
| **Seedance 2.0/2.5** (ByteDance) | Mini 0,04–0,08; Fast 0,06–0,13; bản cao nhất 0,16–0,34 | 4–15 giây | Tham chiếu nhiều ảnh/video | Qua BytePlus hoặc fal. Jimeng cần tài khoản Trung Quốc |
| **Vidu Q3** | Turbo 0,034; Pro 0,042; Q3-Mix 0,106. Giờ thấp điểm rẻ ~50% | 16 giây | Thẻ nhân vật tham chiếu | Có |
| **Runway Gen-4.5** | 0,12 | 10 giây | Có | 12 / 28 / 76 USD |
| **Luma Ray 3** | 0,04–0,21 | 10 giây | Có | 30 / 90 / 300 USD |
| **Pika 2.5** | ~0,05 | 10 giây | Có | **Chỉ gói Pro (76 USD) được dùng thương mại** |
| **Higgsfield** | Bán lại Kling, Veo, Seedance… | — | Soul ID | 19–129 USD. Không có API |
| **Sora 2** | **Đã ngừng:** app đóng 26/4/2026, API đóng 24/9/2026 | — | — | — |

## 4. Tạo ảnh giữ nhân vật

| Mô hình | Giá | Ghi chú |
|---|---|---|
| **Nano Banana 2** (Gemini 3.1 Flash Image) | ~0,045–0,15 USD/ảnh, bản Lite ~0,034 | Tham chiếu nhiều ảnh, giữ mặt rất tốt. Có API. Dùng thương mại được |
| **Nano Banana Pro** | 0,134 USD (1K/2K), chạy lô giảm 50% | **Chữ trên ảnh đẹp nhất**, hợp thumbnail có tiêu đề |
| **GPT Image 2** | ~0,005–0,21 USD tuỳ chất lượng | Sửa theo ảnh tham chiếu |
| **FLUX Kontext / FLUX.2** | Pro 0,04, Max 0,08 USD | API dùng thương mại được. Trọng số dev thì không |
| **Midjourney V8** | 10–120 USD/tháng | `--oref` giữ nhân vật. **Không có API chính thức** |
| **Ideogram 3.0** | 0,03–0,20 USD | Tham chiếu nhân vật từ 1 ảnh |

## 5. Giọng đọc tiếng Việt (TTS)

Ước tính ~55–60 nghìn ký tự mỗi giờ audio.

| Dịch vụ | Giá | Giá 1 giờ audio | Ghi chú |
|---|---|---|---|
| **FPT.AI** | Miễn phí 100k ký tự/tháng. Gói lớn nhất 5 triệu VND/27,1 triệu ký tự | ~10–17k VND | Bảng giá rõ ràng nhất |
| **Viettel AI** | Không đọc được trang giá. Dùng thử đến 1 triệu ký tự | Chưa rõ, **cần hỏi báo giá** | Giọng Bắc/Nam, tự nhiên |
| **Vbee** | Miễn phí 3.000 ký tự/ngày. VIP ~299k VND/tháng (hạn mức chưa rõ) | Chưa rõ | Nhiều kênh truyện audio Việt đang dùng. VIP+ có clone giọng |
| **Gemini TTS** | 3.8 Flash-Lite: 6 USD/triệu token audio; Flash: 9 USD (giá ra mắt đến 31/12) | ~0,54–0,81 USD | Biểu cảm, nhiều giọng. Mới ra 23/9/2026, chưa kiểm chứng chất lượng |
| **Azure Neural** (HoaiMy, NamMinh) | 16 USD/triệu ký tự, miễn phí 500k/tháng | ~0,9–1,3 USD | Ổn định, được dùng thương mại. **Đây là bản hợp pháp của giọng edge-tts** |
| **Google Cloud Chirp 3 HD** | 30 USD/triệu ký tự | ~1,7 USD | — |
| **ElevenLabs** | API 0,05–0,10 USD/1k ký tự | 3–6 USD | Clone giọng tốt, tiếng Việt khá nhưng đôi khi lệch thanh. 30 triệu ký tự/tháng tốn 1.500–3.000 USD, quá đắt |
| **edge-tts** | Miễn phí | 0 | **Microsoft xác nhận vi phạm điều khoản khi dùng không có tài khoản Azure. Không dùng cho kênh kiếm tiền** |
| Zalo AI | Chưa công bố giá | — | Ưu tiên thấp |

## 6. Công cụ trọn gói

- **Việt Nam:**
  - Motion Studio (mục 2).
  - MagaRecap, MTH Recap Studio (tự động kịch bản, giọng, dựng cho video tóm tắt truyện/phim).
  - Các trang bán lại tài khoản Veo/Kling dùng chung: **rủi ro vi phạm điều khoản và bị khoá**.
- **Trung Quốc (小说推文):** 推文助手, 聚星文社, 文刻AI, 剪映 "图文成片", 即梦. Phần lớn cần số điện thoại hoặc thanh toán Trung Quốc.

## 7. Ước tính chi phí mỗi tháng

Giả định 1,5 video/ngày, trung bình 12 giờ (~45 video/tháng):
- mỗi video khoảng 15 clip mới 6 giây
- 20 ảnh tĩnh và 4 bản thumbnail mỗi video
- khoảng 540 giờ audio mỗi tháng

| Hạng mục | Gói tiết kiệm | USD | Gói chất lượng | USD |
|---|---|---|---|---|
| Video | Motion Studio H3 (~2,2 triệu VND), hoặc Vidu Q3 Turbo/Seedance Mini | 85–160 | Kling 3.0 Omni, Seedance 2.0 720p hoặc Veo 3.1 Fast | 400–650 |
| Ảnh, thumbnail | Nano Banana 2 API hoặc Google AI Pro | 20–40 | Midjourney + Nano Banana Pro | 150–180 |
| TTS | Tự chạy VieNeu-TTS (~0), gói FPT.AI, hoặc Gemini Flash-Lite TTS (~290) | 0–230 | Gemini Flash TTS, Vbee/FPT giọng riêng | 450–700 |
| **Tổng** | | **~110–430** | | **~1.000–1.500** |

## 8. Rủi ro YouTube và pháp lý

- **Chính sách "inauthentic content"** (đổi tên từ "repetitious content" ngày 15/7/2025, siết mạnh trong năm 2026). Kênh AI bị xoá hàng loạt thường có chung dấu hiệu: giọng AI tổng hợp, thumbnail rập khuôn, footage lặp, đăng dày.
  - "2 video AI 12 giờ/ngày trên clip AI lặp" khớp đúng dấu hiệu này.
  - Cần giá trị biên tập thật: lời bình, tóm tắt, chia chương, hình vẽ riêng, giọng thật hoặc giọng clone của chính mình cho phần mở đầu.
- **Khai báo AI:** tích "altered or synthetic content" khi có cảnh AI giống thật. Hình anime hoặc cách điệu rõ ràng, và giọng AI không nhái người thật, thường không cần khai.
- **Bản quyền là rủi ro lớn nhất.** Kể lại truyện dịch Trung Quốc (Qidian, Fanqie…) khi chưa có giấy phép là vi phạm bản quyền. Các bên giữ quyền như China Literature có gửi claim và yêu cầu gỡ. Dùng giọng AI không làm thay đổi điều đó. Cách giảm rủi ro: viết lại sâu (拆书 + 仿写), truyện có giấy phép, truyện hết bản quyền, hoặc truyện tự sáng tác.
- **Watermark:** Veo và Gemini nhúng SynthID. Gói miễn phí thường có watermark nhìn thấy được.

## Nguồn
- **Motion Studio:** [trang chủ](https://tasks.datools.info/), [membership](https://tasks.datools.info/membership), [apis](https://tasks.datools.info/apis), [rules](https://tasks.datools.info/rules), [changelog](https://tasks.datools.info/changelog)
- **Video:**
  - [giá Gemini/Veo](https://ai.google.dev/gemini-api/docs/pricing)
  - [Kling Elements](https://kling.ai/blog/kling-3-subject-binding-character-consistency)
  - [MiniMax H3](https://llm-stats.com/blog/research/minimax-h3-launch)
  - [Seedance](https://apiframe.ai/models/seedance-2.0/pricing)
  - [Vidu Q3](https://www.atlascloud.ai/models/vidu/q3-mix/reference-to-video)
  - [Sora ngừng](https://the-decoder.com/openai-sets-two-stage-sora-shutdown-with-app-closing-april-2026-and-api-following-in-september/)
- **Ảnh:** [BFL](https://bfl.ai/pricing), [Midjourney Omni Reference](https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference)
- **TTS:**
  - [FPT.AI](https://docs.fpt.ai/docs/vi/speech/documentation/tts-pricing/)
  - [Viettel AI](https://viettelai.vn/en/bang-gia)
  - [Vbee](https://help.vbee.vn/huong-dan-su-dung/thanh-toan/giao-dien-may-tinh/cac-goi-cuoc)
  - [ElevenLabs](https://elevenlabs.io/pricing)
  - [edge-tts và điều khoản Microsoft](https://learn.microsoft.com/en-us/answers/questions/2088770/are-opensource-edge-tts-free-for-commercial-use)
- **YouTube:** [chính sách kiếm tiền](https://support.google.com/youtube/answer/15447836), [khai báo AI](https://blog.youtube/news-and-events/disclosing-ai-generated-content/)
