# Chiến lược Video Mồi TikTok (TikTok Hook Strategy) & Xây dựng IP Nhân vật

**Cập nhật:** 27/09/2026
**Mục tiêu:** Tạo các video ngắn (10-15 giây) cực kỳ cuốn hút từ 1-2 chương đầu của truyện để làm "chim mồi" kéo traffic về video YouTube dài. Sử dụng công nghệ AI Image-to-Video (I2V) để tạo ra định dạng Motion Comic/AI Film sống động, nhất quán, tối ưu chi phí 0đ.
**Tư duy cốt lõi:** Chuyển từ "Công cụ tạo video" sang "Hệ thống sản xuất phim" (Xây nhân vật trước - Làm phim sau).

---

## 1. Hệ thống "Thư viện Nhân vật" (Character Library & IP)

Thay vì mỗi video/truyện sinh ra một khuôn mặt ngẫu nhiên, kênh sẽ vận hành theo mô hình "Công ty giải trí" với các diễn viên được tái sử dụng dài hạn (Tạo IP Nhân vật).

*   **Vị trí lưu trữ:** `assets/characters/`
*   **Bí mật nhất quán (Character Sheet):** Không dùng 1 tấm ảnh chân dung đơn điệu. Mỗi "Diễn viên" phải là một **Hồ sơ nhân vật đa góc (Character Sheet)**.
    *   Tấm ảnh tham chiếu phải bao gồm 4 góc: *Chính diện - Góc nghiêng 45 độ - Góc nghiêng 90 độ - Nhìn từ sau lưng.* (Nhờ vậy AI Video hiểu được 360 độ cấu trúc tóc, quần áo, khuôn mặt của nhân vật).
    *   1 file `metadata.json` chứa thông tin (Tên ID, Giới tính, Prompt mô tả chi tiết: tóc, form mặt, trang phục cố định, tính cách).
*   **Cơ chế hoạt động:** Khi làm truyện mới, kịch bản sẽ "casting" diễn viên từ thư viện. Các bước sinh ảnh tĩnh và video sẽ bám chặt vào Character Sheet này làm "DNA bất diệt" (qua công nghệ IP-Adapter/FaceID).

---

## 2. Chiến thuật sinh Video Chuyển động (I2V) & Nguyên tắc Prompt

Sử dụng **Cấp độ 3 (AI Video Generation từ Ảnh + Prompt)** thông qua các nền tảng cho phép Gen Free mỗi ngày (Kling AI, Hailuo AI).

### 2.1. Tư duy Tách bạch: "Ai?" và "Làm gì?"
Đừng trộn lẫn miêu tả nhân vật và hành động vào chung một câu lệnh.
*   **Character Sheet (Nạp bằng Hình ảnh):** Trả lời câu hỏi *AI đang nhìn ai?* (Giữ sự nhất quán về khuôn mặt, trang phục).
*   **Video Prompt (Nạp bằng Văn bản):** Trả lời câu hỏi *Người đó đang làm gì? Góc máy ra sao?*
    *   *Ví dụ Prompt chuẩn:* "A person exactly matching the reference image. Pushes the car door open and steps out confidently, cinematic motion, camera tracking."

### 2.2. Quy tắc "Ảnh Bản Lề" (Chống lỗi biến dạng hành động)
Để AI làm các hành động tương tác vật lý (Mở cửa, bước đi, cầm kiếm) không bị lỗi:
*   **KHÔNG** đưa ảnh chân dung và bắt AI tự nghĩ ra bối cảnh/xe cộ.
*   **BẮT BUỘC** sinh ảnh tĩnh 2D ở *khoảnh khắc ngay trước khi hành động xảy ra*. (Ví dụ: Tay đã đặt lên cửa xe chuẩn bị đẩy).

---

## 3. Pipeline Tự động hóa Video Mồi (Dự kiến Code)

Lập kế hoạch trước (Story -> Character -> Scene -> Video), tuyệt đối không vừa làm vừa nghĩ prompt. Quy trình tự động hóa (`scripts/build_tiktok_hook.py`):

1.  **Lập Storyboard (Bởi LLM):** 
    *   Đọc chương 1-2, trích xuất cốt truyện.
    *   Casting diễn viên từ Thư viện.
    *   Chia nhỏ thành 3-4 cảnh (Scenes) có kịch bản hành động rõ ràng.
2.  **Audio (TTS):** Đẩy qua VieNeu-TTS (Local) đọc thoại với nhịp độ giật gân, dồn dập (1.25x - 1.5x).
3.  **Visuals (Kết hợp Ảnh + Video):** 
    *   Sinh các "Ảnh bản lề" cho từng cảnh, khóa khuôn mặt bằng Character Sheet.
    *   Gửi Ảnh + Video Prompt (chỉ chứa hành động) lên Kling AI / Hailuo AI.
4.  **Auto-Merge (Hậu kỳ bằng FFmpeg/MoviePy):**
    *   Tải clip về `stories/<slug>/render/tiktok_clips/`.
    *   Script tự động crop video (Cắt bỏ logo watermark).
    *   Nối video khớp với file Audio TTS, chèn nhạc nền Phonk / Sigma nam tính.
    *   Chèn phụ đề text to, chớp nháy ở giữa màn hình chuẩn style TikTok.

---
*Ghi chú: Bản kế hoạch này đóng vai trò định hướng kiến trúc chuẩn "AI Film". Các module kỹ thuật sẽ được thiết kế bám sát nguyên tắc giữ vững IP Nhân vật xuyên suốt dự án.*
