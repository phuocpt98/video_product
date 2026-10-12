> **Ghi chú của Điều phối (27/9/2026):** báo cáo do `researcher` (Gemini 3.1 Pro) làm, chưa duyệt chéo. Đoạn trích chính sách YouTube khớp với hiểu biết của Điều phối nhưng chưa mở trang để kiểm lại nguyên văn.

Dưới đây là báo cáo nghiên cứu về việc xây dựng thư viện hình ảnh tái sử dụng cho kênh YouTube motion comic/kể truyện dựa trên các công cụ AI và FFmpeg.

### 1. Tóm tắt (5 ý chính)
1. **Chính sách YouTube:** Từ 7/2025, thuật ngữ "Repetitious content" chuyển thành "Inauthentic content". Các kênh chỉ làm video dạng slideshow tĩnh + giọng đọc AI (không có bình luận/sáng tạo thêm) rất dễ bị tước tính năng kiếm tiền vì bị coi là sản xuất hàng loạt (mass-produced).
2. **Quản lý & Tự động hoá qua Repo AI:** Các framework như *ViMax* hay *MoneyPrinterTurbo* sử dụng cấu trúc Multi-Agent và LLM để tự động phân tích câu chuyện (Novel2Video), tự động chọn keyword/tag rồi lấy hình/clip tương ứng. *StoryDiffusion* (ComfyUI) là đột phá nhất cho việc giữ khuôn mặt nhân vật mà không cần train LoRA.
3. **Biến thể hình ảnh bằng FFmpeg:** Hiệu ứng Ken Burns (pan/zoom/crop) dễ dàng thực hiện bằng filter `zoompan` trong FFmpeg, nhưng có nhược điểm là nhìn rất "máy móc" (linear). Hiệu ứng 2.5D Parallax yêu cầu tạo bản đồ độ sâu (Depth Map) bằng AI trước, không thể làm trực tiếp bằng FFmpeg thuần túy.
4. **Cấu trúc thư viện "Prompt DNA":** Để đồng nhất, cần xây dựng các Character Sheet chuẩn (các góc mặt, biểu cảm) dựa trên một "Prompt DNA" không đổi. Kho tài nguyên cần được gắn tag (metadata) chi tiết (ví dụ: `scene_type`, `camera_angle`, `emotion`) để script tự động có thể gọi đúng cảnh (qua keyword matching hoặc CLIP embedding).
5. **Rủi ro lớn nhất:** Việc nhai lại quá ít ảnh cho một video dài 30–60 phút bằng cách lật, zoom hay crop vẫn bị thuật toán và người duyệt của YouTube nhận diện là lặp lại hình ảnh (slideshow lười biếng). Mật độ khung hình thị giác cần đủ biến đổi để giữ chân người xem.

---

### 2. Phân tích & Bảng so sánh các công cụ / Repo GitHub

| Repo / Công cụ | Chức năng chính & Cơ chế | Điểm đáng học & Cách quản lý | Giấy phép (License) |
| :--- | :--- | :--- | :--- |
| **ViMax** (HKUDS) | Multi-agent framework chuyên chuyển từ tiểu thuyết sang video (Novel2Video). | Giữ nhất quán cốt truyện dài bằng LLM Director. Chia prompt theo từng câu thoại. | Open-source (MIT/Apache - tùy module) |
| **MoneyPrinterTurbo** | Pipeline tự động hóa hoàn toàn: LLM script -> Search stock video -> TTS -> FFmpeg ghép. | Cách tự động ghép file bằng FFmpeg, căn chỉnh subtitle khớp audio. | Open-source |
| **StoryDiffusion** | Giữ nhất quán khuôn mặt, trang phục (Consistent Self-Attention) qua nhiều frame/ảnh. | Tích hợp vào **ComfyUI** (workflow `storydiffusion_workflow.json`), tạo Character Sheet hoàn hảo mà không cần train LoRA. | Open-source (Phi thương mại cho bản gốc) |
| **NarratoAI** | Tự động hóa tóm tắt phim/truyện. | Cách chia tag, dùng LLM để mapping nội dung với hình ảnh/video đầu vào. | Open-source |
| **Pixelle-Video** | Engine tạo video ngắn của Alibaba. | Kiến trúc modular, cách tổ chức thư mục tài nguyên âm thanh/hình ảnh. | Open-source |
| **Flowkit** | (Nhiều repo trùng tên, đáng chú ý có bộ công cụ automation) | Pipeline tự động hóa luồng làm việc. | Đa dạng |

---

### 3. Giải đáp chi tiết các khía cạnh kỹ thuật & Chính sách

#### 3.1. Chính sách YouTube (Reused & Inauthentic Content)
*   **Reused Content (Nội dung sử dụng lại):** Cấm sử dụng nội dung của bên thứ 3 mà không thêm "giá trị đáng kể" (bình luận, chỉnh sửa sáng tạo). *Trích dẫn:* "Compilations of content you did not create or have no involvement with... Content uploaded to your channel that was already uploaded elsewhere."
*   **Inauthentic Content (Nội dung không xác thực - trước đây là Repetitious):** Đây là rào cản lớn nhất cho kênh kể truyện. YouTube nhắm tới nội dung sản xuất hàng loạt. *Trích dẫn:* "Image slideshows or scrolling text with minimal or no narrative, commentary, or educational value... Content generated programmatically or at scale without unique human input."
*   **Cách kênh Audiobook/Motion Comic vượt qua:** Họ phải "chứng minh sự hiện diện của con người". Bằng cách biến tấu hình ảnh liên tục, thêm hiệu ứng hạt (grain), ánh sáng (light leaks), và đặc biệt: không để 1 hình tĩnh quá lâu trên màn hình. Nếu kiếm tiền thương mại, hình ảnh tạo bằng Gemini Pro hoàn toàn hợp lệ, nhưng cách bạn **dựng (edit)** quyết định có được duyệt kiếm tiền hay không.

#### 3.2. Kỹ thuật FFmpeg tạo biến thể (1 ảnh -> nhiều clip)
*   **Pan, Zoom, Crop (Ken Burns):** Dùng filter `zoompan` trong FFmpeg.
    *   *Ví dụ Zoom center:* `ffmpeg -loop 1 -i img.jpg -vf "zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125" output.mp4`
    *   *Đánh giá:* Rất dễ lộ "máy làm" vì tốc độ zoom là tuyến tính (linear), không có gia tốc (ease-in/out) tự nhiên của con người. Để mượt hơn, phải up-scale ảnh gốc lên cực to trước khi dùng `zoompan`.
*   **Lật ngang, Đổi tốc độ, Đổi màu:** Dễ dàng làm với `-vf hflip`, `eq=brightness=...`.
*   **Parallax 2.5D (Tách lớp tạo chiều sâu):** **Không thể làm bằng FFmpeg thuần túy.**
    *   *Cách làm:* Phải chạy ảnh gốc qua AI tạo Depth Map (như *Depth Anything V2* hoặc *MiDaS*). Sau đó dùng một script Python bên ngoài (như repo `parallax-maker`) hoặc After Effects (Displacement Map) để bóp méo pixel dựa trên độ sâu, xuất ra chuỗi PNG (image sequence), rồi mới dùng FFmpeg ghép PNG thành video. Cách này nhìn **cực kỳ tự nhiên và cao cấp**.
*   **Hiệu ứng Overlay (Ánh sáng, Hạt):** Dùng FFmpeg với filter `blend` để đè một clip light-leak có sẵn lên video (chế độ Screen/Overlay) giúp che đi sự nhàm chán của ảnh tĩnh.

#### 3.3. Đề xuất Cấu trúc thư viện & Tagging
Một thư viện tối ưu cho script tự động gọi (qua JSON/YAML) nên tổ chức như sau:
*   **Cấu trúc thư mục:**
    *   `/Characters`: Mỗi nhân vật 1 thư mục. Chứa Character Sheet và tệp `prompt_dna.txt` (Ví dụ: `1boy, 25 years old, messy black hair, cyber-punk jacket, green eyes`).
    *   `/B-Roll_Scenes`: Các cảnh quay môi trường (đường phố, trời mưa, gọi điện).
    *   `/Effects`: Light leaks, film grain, chuyển cảnh.
*   **Metadata (Gắn thẻ):** Mỗi ảnh/clip đi kèm 1 file `.json`.
    *   `tags`: `["angry", "close-up", "night", "rain"]`.
    *   `usage_count`: Để script tự động né những ảnh đã dùng quá nhiều lần trong video đó.
*   **Cách lấy tự động:** Khi LLM (như Gemini) đọc câu thoại "Hắn tức giận đi dưới mưa", script sẽ query JSON tìm ảnh có tag `angry`, `rain`. Nếu muốn mượt, dùng mô hình nhúng (CLIP embedding) để so sánh vector câu văn và vector hình ảnh.

---

### 4. Đề xuất quy trình (M2 Pro 16GB)

*   **Đề xuất chính: Workflow Kết hợp (StoryDiffusion + 2.5D Parallax)**
    *   **Lý do:** Tận dụng được sức mạnh của M2 Pro. Bạn cài ComfyUI, dùng workflow **StoryDiffusion** để tạo ra các tập Character Sheet chuẩn (đảm bảo nhân vật nhìn không bị biến dạng mặt). Đối với các ảnh cần xuất hiện lâu (ví dụ cảnh nhân vật độc thoại 5-10 giây), thay vì dùng `zoompan` của FFmpeg, hãy cho chạy qua script tạo Depth Map để làm **2.5D Parallax**. Kết quả sẽ là 1 video ngắn nhìn rất xịn, qua mặt thuật toán YouTube dễ dàng vì nó tạo ra chuyển động thật.
*   **Đề xuất dự phòng: Gemini Pro + FFmpeg Nâng cao (có easing)**
    *   **Lý do:** Nhanh và tự động hóa 100%. Dùng "Prompt DNA" cố định ép Gemini tạo ảnh (dù mặt có thể xê dịch chút ít). Tránh dùng `zoompan` mặc định. Viết một đoạn script Python nhỏ tính toán tọa độ X, Y, Zoom theo đường cong Bezier (Ease-in/out), sau đó tạo hàng loạt lệnh FFmpeg crop tĩnh ghép lại (stop-motion) hoặc frame-by-frame blending để motion tự nhiên hơn.

---

### 5. Phản biện & Rủi ro mật độ

*   **Rủi ro của phương pháp "Ít ảnh, Lặp có biến thể":**
    Đối với video 30-60 phút, việc lặp lại hình ảnh quá nhiều (dù có zoom khác góc) gây ra sự mỏi mắt cho người xem (Visual Fatigue) và khiến Watch Time tụt giảm trầm trọng. Hơn nữa, những người duyệt kênh thủ công của YouTube rất nhạy cảm với các kênh làm video theo format "radio" (1 hình tĩnh xoay quanh) nếu không có sự tương tác hình ảnh khớp với nội dung.
*   **Mật độ tối thiểu (Kinh nghiệm cộng đồng):**
    Không có con số chính thức, nhưng đối với motion comic/recap, để an toàn kiếm tiền, mật độ tối thiểu nên là **1 sự thay đổi thị giác (chuyển cảnh/đổi ảnh/hiệu ứng mạnh) mỗi 5-10 giây**. Nghĩa là 1 phút cần khoảng 6-12 clip/biến thể. Một video 30 phút cần kho thư viện ít nhất 200-300 shot hình (có thể sinh ra từ 50-100 ảnh gốc mang đi cắt cúp/parallax).

---

### 6. Điểm chưa xác minh
*   Chưa có văn bản nào của Google quy định chính xác "bao nhiêu ảnh/phút" là đạt chuẩn kiếm tiền (quyết định cuối cùng dựa trên cảm quan của reviewer xem nội dung có "giá trị nguyên bản" hay không).
*   Giấy phép thương mại (Commercial License) của bản gốc StoryDiffusion chưa rõ ràng tuyệt đối trong một số mô hình base weights, người dùng thường lách bằng cách dùng base model (SD 1.5/SDXL) đã được cấp phép thương mại.

### 7. Nguồn tham khảo (Links)
*   [YouTube Channel Monetization Policies (Inauthentic Content / Reused Content)](https://support.google.com/youtube/answer/1311392?hl=en#zippy=%2Cspam-and-deceptive-practices%2Cinauthentic-content%2Creused-content) - *Tra cứu ngày 27/09/2026*
*   [Repo HKUDS/ViMax](https://github.com/HKUDS/ViMax) - *Tra cứu ngày 27/09/2026*
*   [Repo harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) - *Tra cứu ngày 27/09/2026*
*   [StoryDiffusion (Consistent Self-Attention)](https://github.com/HVision-NKU/StoryDiffusion) - *Tra cứu ngày 27/09/2026*
*   [FFmpeg zoompan filter documentation](https://ffmpeg.org/ffmpeg-filters.html#zoompan) - *Tra cứu ngày 27/09/2026*
