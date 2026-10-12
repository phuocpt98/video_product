# Repo mã nguồn mở tạo video AI

Cập nhật: 25/9/2026 · Nguồn: GitHub API và README, kiểm tra ngày 25/9/2026, không clone · Máy dùng: Mac Apple Silicon (không có GPU NVIDIA)

## 1. Kết luận

Với định dạng của kênh (kể chuyện dài trên nền hình), **mô hình tạo video là phần ít quan trọng nhất**. Ba thứ quyết định chất lượng:
1. Giọng TTS tiếng Việt tốt.
2. Ảnh nhân vật nhất quán.
3. Dựng rẻ bằng ffmpeg: zoom/pan (Ken Burns) và chuyển cảnh mờ.

Clip chuyển động AI thật chỉ dùng ít, làm hình minh hoạ phụ (B-roll). Tạo video AI cho toàn bộ 8–20 giờ là không khả thi trên Mac.

**Dùng hoặc học ngay cho MVP** (đều chạy được trên Mac):

| # | Repo | Dùng cho | Giấy phép |
|---|---|---|---|
| 1 | [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) | **Giọng kể tiếng Việt.** v3 Turbo: 48kHz, 25 giọng, clone giọng từ 3–8 giây, chạy CPU đủ nhanh để render qua đêm, có server tương thích OpenAI. Cần thử văn dài và tên Hán Việt. Lưu ý: v4 là bản đóng, chỉ có API | Apache-2.0 |
| 2 | [mflux](https://github.com/filipstrand/mflux) + LoRA nhân vật + Qwen-Image-Edit/Kontext | Ảnh nhân vật chính và cảnh nhất quán, chạy MLX gốc trên Mac. Khoảng 20–60 ảnh mỗi giờ video | MIT |
| 3 | [stable-ts](https://github.com/jianfch/stable-ts), dự phòng [WhisperX](https://github.com/m-bain/whisperX) | **Khớp kịch bản có sẵn với audio** để ra phụ đề đúng dấu và mốc cắt cảnh | MIT / BSD-2 |
| 4 | [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | Học phần dựng và kiểu phụ đề 9:16 cho clip TikTok | MIT |
| 5 | [Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video), [AI_novel](https://github.com/tyxben/AI_novel) | **Chỉ học, không dùng:** cách lập kế hoạch kịch bản → phân cảnh → prompt ảnh, mẫu workflow ComfyUI | Apache-2.0 / MIT |

**Giai đoạn 2** (khi kênh có tiền hoặc thuê GPU):
- LTX-2 MLX hoặc Wan2.2-5B để làm kho clip chuyển động.
- LivePortrait để chân dung người kể chuyển động nhẹ khi đứng yên.
- InfiniteTalk để làm hook TikTok có khẩu hình khớp lời.

**Tránh:**
- **Trọng số không cho dùng thương mại** trên kênh kiếm tiền: F5-TTS-Vietnamese-ViVoice (CC-BY-NC-SA), viXTTS/XTTS-v2 (Coqui CPML), InstantID (model InsightFace chỉ cho nghiên cứu), FLUX.1-dev/Kontext-dev nếu không mua giấy phép.
- story-flicks (không có giấy phép).
- Code AGPL như ArcReel nếu sau này làm dịch vụ.
- SadTalker, Hallo2, StoryDiffusion: đã cũ, bị vượt.

## 2. Pipeline "kịch bản → video" trọn gói

| Repo | Sao / cập nhật / giấy phép | Ghi chú |
|---|---|---|
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | ~125,6k / 9/2026 / MIT | Chủ đề → kịch bản → TTS (edge-tts có giọng Việt) → footage kho → phụ đề → MP4. Có WebUI, API, chạy lô. Chạy Mac. Làm video ngắn, không hợp 8–20 giờ |
| [Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) | ~28,4k / 6/2026 / Apache-2.0 | Kịch bản → lập kế hoạch ảnh → tạo từng khung (ComfyUI hoặc API) → dựng. Gần định dạng "kể + ảnh AI" nhất |
| [Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | ~16k / 9/2026 / MIT (từ v1.0.8) | Tiểu thuyết → rút sự kiện chương → kịch bản → phân cảnh → thẻ nhân vật → ảnh/video. Hướng phim AI, không phải kể chuyện |
| [ArcReel](https://github.com/ArcReel/ArcReel) | ~5,2k / 9/2026 / **AGPL-3.0** | Truyện → tài sản nhân vật/cảnh/đạo cụ → phân cảnh → video, xuất sang dự án 剪映 (Jianying). Tham khảo cách giữ nhất quán bằng ảnh tham chiếu |
| [Jellyfish](https://github.com/Forget-C/Jellyfish) | ~6,5k / 7/2026 / Apache-2.0 | Sổ đăng ký nhân vật, cảnh, trang phục gắn theo cảnh quay. Thiết kế quản lý nhất quán gọn gàng |
| [AI_novel](https://github.com/tyxben/AI_novel) | ~280 / 8/2026 / MIT | Công cụ 小说推文: truyện → sách nói + ảnh AI → video ngắn. Nhỏ, sát nhu cầu nhất, dễ đọc |
| [AI-Youtube-Shorts-Generator](https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator) | ~5,1k / 9/2026 / MIT | Video dài → Whisper → LLM chọn đoạn hay → cắt 9:16. Hợp để cắt clip TikTok từ video của mình |

## 3. Mô hình tạo video chạy tại máy

| Mô hình | Chạy trên Mac? |
|---|---|
| [LTX-2](https://github.com/Lightricks/LTX-2) (giấy phép riêng, miễn phí dưới ngưỡng doanh thu) | **Lựa chọn tốt nhất cho Mac:** có bản MLX ([ltx-2-mlx](https://github.com/dgrauet/ltx-2-mlx)). Cần từ 32GB bộ nhớ |
| [Wan2.2](https://github.com/Wan-Video/Wan2.2) (Apache-2.0) | Qua [mlx-video](https://github.com/Blaizzy/mlx-video) hoặc ComfyUI. Chạy được nhưng chậm, vài phút cho mỗi clip vài giây |
| [FramePack](https://github.com/lllyasviel/FramePack) (Apache-2.0) | Có bản fork cho Mac, chậm |
| HunyuanVideo-1.5 | Không thực tế trên Mac |

**Cách dùng:** làm sẵn một kho nhỏ clip lặp 3–6 giây theo loại cảnh (thành phố đêm, văn phòng, hào quang chiến đấu) rồi dùng lại. Cần số lượng lớn thì thuê GPU (RunPod…) hoặc dùng API trả phí, xem [ai-services.md](ai-services.md).

## 4. Người kể có hình: khẩu hình và chân dung động

| Repo | Ghi chú |
|---|---|
| [LivePortrait](https://github.com/KwaiVGI/LivePortrait) | **Hỗ trợ macOS chính thức.** Điều khiển bằng video mẫu, không bằng audio. Hợp để chân dung nhân vật chớp mắt, nghiêng đầu nhẹ |
| [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) (Apache-2.0) | Audio → video nói không giới hạn độ dài. Chất lượng tốt nhất nhưng cần NVIDIA |
| MuseTalk, echomimic_v3 | Cần NVIDIA |

**Khuyến nghị:** không làm khẩu hình cho video 8–20 giờ vì quá tốn và người nghe thể loại này không đòi hỏi. Chân dung động nhẹ hoặc hình sóng âm theo giọng là đủ.

## 5. Nhân vật chính nhất quán

- **Cách thực tế:** mỗi nhân vật chính huấn luyện một **LoRA** (Flux hoặc Z-Image) từ 15–30 ảnh chọn lọc. Biến thể tư thế và cảnh làm bằng Qwen-Image-Edit hoặc Kontext.
- Giữ **một phong cách vẽ cố định** (manhua hoặc donghua anime) để che lệch nhỏ giữa các ảnh.
- **Công cụ:**
  - [mflux](https://github.com/filipstrand/mflux) (MIT, MLX cho Mac)
  - [Qwen-Image / Qwen-Image-Edit](https://github.com/QwenLM/Qwen-Image) (Apache-2.0, cho dùng thương mại)
  - [PuLID](https://github.com/ToTheBeginning/PuLID) (Apache-2.0, cần kiểm tra giấy phép model khuôn mặt đi kèm)

## 6. TTS tiếng Việt và phụ đề

| Repo | Giấy phép trọng số | Ghi chú |
|---|---|---|
| [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) | Apache-2.0 | **Lựa chọn số 1**, xem mục 1 |
| [viet-tts](https://github.com/dangvansam/viet-tts) | Apache-2.0 | Dự phòng, có clone giọng |
| F5-TTS-Vietnamese-ViVoice | **CC-BY-NC-SA** | Tự nhiên nhưng **không dùng thương mại được**. Muốn dùng phải tự huấn luyện lại từ [F5-TTS](https://github.com/SWivid/F5-TTS) (MIT) bằng dữ liệu của mình |
| viXTTS | Coqui CPML (phi thương mại) | Tránh |
| edge-tts | Không chính thức | Xem cảnh báo trong [ai-services.md](ai-services.md) §4 |

**Phụ đề:** dùng [stable-ts](https://github.com/jianfch/stable-ts) để khớp kịch bản đã biết vào audio, đúng dấu tiếng Việt hơn nhận dạng giọng nói. [WhisperX](https://github.com/m-bain/whisperX) để dự phòng.

## 7. ComfyUI và tự động hoá 小说推文

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (GPL-3.0) chạy được trên Mac. Điều khiển qua HTTP API: Pixelle-Video, Toonflow, ArcReel đều cắm vào theo cách này.
- Bộ công cụ cộng đồng AI 漫剧 (truyện tranh AI): IP-Adapter giữ phong cách, PuLID/InstantID giữ khuôn mặt, ControlNet giữ tư thế, GGUF để chạy model nén, LLM để viết prompt phân cảnh.
- Danh sách tổng hợp: [awesome-ai-media-cn](https://github.com/JuneYaooo/awesome-ai-media-cn).
