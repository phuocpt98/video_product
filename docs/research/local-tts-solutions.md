# Nghiên cứu: Giải pháp Text-to-Speech (TTS) Tiếng Việt Local Siêu Nhẹ

**Ngày cập nhật:** 26/09/2026
**Mục tiêu:** Tìm kiếm mô hình AI đọc truyện tiếng Việt (TTS) đáp ứng 3 tiêu chí:
1. **Chạy Local 100%:** Cắt giảm chi phí API xuống 0đ.
2. **Mô hình "Nhẹ" (Lightweight):** Hoạt động mượt mà trên Mac Apple Silicon, không vắt kiệt RAM/CPU, không làm nóng máy khi chạy liên tục nhiều giờ.
3. **Sản xuất số lượng lớn:** Có khả năng render hàng nghìn chương truyện (hàng triệu ký tự) tự động hóa bằng script.

---

## 1. Phân tích các mô hình TTS Tiếng Việt "Nhẹ" tốt nhất hiện nay

Với hệ sinh thái mã nguồn mở cuối 2026, dưới đây là 3 ứng cử viên hàng đầu cho Apple Silicon (Mac):

### 🥇 Top 1: VieNeu-TTS (Phiên bản V3 Nano/Base)
*   **Bản chất:** Mô hình Zero-shot TTS (cho phép clone giọng bất kỳ chỉ từ 3-8 giây audio mẫu).
*   **Độ "Nhẹ":** Cung cấp phiên bản `v3 Nano` đặc biệt tối ưu cho CPU và thiết bị cá nhân. Trên Apple Silicon, nó có thể chạy cực kỳ nhanh khi bật backend Metal (`device="mps"`).
*   **Chất lượng:** Hỗ trợ âm thanh 48kHz, ngắt nghỉ tự nhiên, có khả năng thể hiện cảm xúc (phù hợp với thể loại truyện Hệ thống, Đô thị).
*   **Tính tự động hóa:** Có sẵn API tương thích chuẩn OpenAI, rất dễ tích hợp vào pipeline Python (`src/common/tts.py`).
*   **Giấy phép:** Apache 2.0 (Hoàn toàn an toàn cho việc bật kiếm tiền trên YouTube).

### 🥈 Top 2: Piper TTS
*   **Bản chất:** Engine TTS cực kỳ tối giản sử dụng kiến trúc ONNX Runtime, lập trình bằng C++.
*   **Độ "Nhẹ":** Vô địch. Piper có thể chạy mượt trên cả cấu hình Raspberry Pi. Khi chạy trên Mac M1/M2/M3, nó có thể tạo ra audio nhanh gấp hàng chục lần thời gian thực (RTF < 0.05).
*   **Chất lượng:** Giọng rõ ràng, chuẩn xác nhưng **thiếu cảm xúc**. Giọng có xu hướng hơi "đều đều", phù hợp đọc tin tức hoặc sách học thuật hơn là kể truyện dài bối cảnh kịch tính.
*   **Tính tự động hóa:** Tích hợp trực tiếp qua thư viện Python siêu gọn nhẹ hoặc CLI.

### 🥉 Top 3: v-tts (Zero-shot 74.8M parameters)
*   **Bản chất:** Một trong những mô hình Pytorch nhẹ nhất hiện tại cho tiếng Việt (~74.8 triệu tham số).
*   **Độ "Nhẹ":** Rất tiết kiệm RAM/VRAM. Dễ dàng triển khai.
*   **Chất lượng:** Clone giọng tốt, tuy nhiên hệ sinh thái cộng đồng và tính năng tự động hóa không mạnh mẽ bằng VieNeu-TTS.

---

## 2. Phương pháp & Kiến trúc Đề xuất (Để xử lý số lượng siêu lớn)

Để giải quyết bài toán render hàng triệu ký tự mỗi tháng trên máy Mac mà không làm treo máy, cần thiết kế một **Pipeline Xử lý Lô (Batch Processing)** chặt chẽ.

Tôi đề xuất lựa chọn **VieNeu-TTS (v3 Nano)** kết hợp với kiến trúc xử lý sau:

### Bước 1: Tiền xử lý văn bản (Text Normalization) - BẮT BUỘC
Mô hình AI rất dễ "vấp" khi gặp ký tự lạ, số, hoặc dấu ngắt dòng lộn xộn trong truyện chữ.
*   **Giải pháp:** Dùng thư viện như `viet-tts-toolkit` (hoặc Regex) để tiền xử lý:
    *   Biến đổi số, từ viết tắt: `100k` -> `một trăm nghìn`, `vs` -> `với`.
    *   **Chia nhỏ (Chunking):** Tuyệt đối không ném cả một chương 5.000 chữ vào Model. Hãy cắt chúng thành các câu/khối (chunk) ngắn khoảng **150 - 250 ký tự** (cắt theo dấu chấm, phẩy, xuống dòng).

### Bước 2: Tối ưu bộ nhớ (Memory Management)
*   **Lỗi thường gặp:** Script cứ tạo ra câu mới là lại khởi tạo mô hình TTS.
*   **Cách làm đúng:** Xây dựng Class `LocalTTSProvider` (dự kiến nằm ở `src/common/tts.py`), Load model TTS vào bộ nhớ RAM/GPU **DUY NHẤT 1 LẦN** khi script bắt đầu chạy (preload). Vòng lặp xử lý chỉ việc đẩy text vào model đang chờ sẵn.

### Bước 3: Render cục bộ & Nối file (Chunk & Merge)
Bản chất của làm "số lượng lớn" là chia để trị:
1.  **Render Câu:** Chạy vòng lặp qua từng chunk, tạo ra các file wav ngắn (vd: `001_00.wav`, `001_01.wav`) lưu vào thư mục trung gian `stories/<slug>/render/`.
2.  **Xử lý song song:** Tận dụng 8-12 nhân CPU của máy Mac bằng Python Multiprocessing để render song song nhiều chương truyện cùng lúc.
3.  **Hợp nhất:** Sử dụng FFmpeg để nối cực nhanh không mất chất lượng:
    `ffmpeg -f concat -safe 0 -i list.txt -c copy full_chapter.wav`

### Bước 4: Tận dụng phần cứng Apple Silicon (Hardware Acceleration)
Việc bắt buộc để chạy "nhẹ" mà siêu nhanh là ép PyTorch sử dụng nhân xử lý đồ họa (Metal) của máy tính Mac:
```python
import torch

# Cấu hình thiết bị tối ưu trên Mac
device = "mps" if torch.backends.mps.is_available() else "cpu"
model.to(device)
```

---

## 3. Kế hoạch tiếp theo (Nếu chốt giải pháp)
1. Tạo môi trường test cục bộ, clone model `VieNeu-TTS` (bản Nano).
2. Chuẩn bị 1 đoạn âm thanh **giọng nam/nữ đọc truyện cực hay** (khoảng 3-8 giây, tách sạch nhạc nền) làm "Khuôn" (Reference Audio) để nhân bản giọng đọc (Voice cloning).
3. Cho máy đọc thử 1 chương (khoảng 2500 chữ), sau đó đo lường:
    - Thời gian render thực tế mất bao lâu?
    - Nhiệt độ máy và mức độ ngốn RAM?
    - Độ truyền cảm có đạt chuẩn kênh hệ thống/đô thị không?
