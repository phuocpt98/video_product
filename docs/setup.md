# Cài đặt dự án trên máy mới

Cập nhật: 26/9/2026 · Dành cho Người sáng lập **và cho AI** (Claude Code) khi khởi tạo dự án ở máy khác.

## Nguyên tắc
- **Mọi thứ tải về cho dự án đều nằm trong repo** và bị git bỏ qua, nên xoá dự án là sạch:
  - `.venv/`: thư viện Python
  - `.cache/huggingface/`: model AI chạy local (biến `HF_HOME` do code tự đặt)
  - `tmp/`: file nháp
- Chỉ có **công cụ hệ thống** nằm ngoài repo, vì nhiều dự án dùng chung: Homebrew (ffmpeg, yt-dlp, Python 3.14) và agy.

## Cài tự động
Chạy từ gốc repo:

```bash
bash scripts/setup.sh
```

Script làm lần lượt:
1. Cài ffmpeg, yt-dlp, python@3.14 bằng Homebrew nếu thiếu.
2. Tạo `.venv` và cài `requirements.txt`.
3. Tải model VieNeu-TTS vào `.cache/` và sửa lỗi symlink (xem mục Lỗi đã biết).
4. Tạo `.env` từ `.env.example` nếu chưa có.
5. Gộp danh sách quyền đọc web của agy (`scripts/agy_permissions.json`) vào cấu hình agy.
6. Chạy test.

## Làm tay (AI không làm thay được)
| Việc | Cách làm |
|---|---|
| **Điền key vào `.env`** | `ZAI_API_KEY` (GLM, miễn phí): tạo ở https://z.ai/manage-apikey/apikey-list. Người sáng lập tự dán vào `.env`, **không dán key vào chat**. |
| **Cài và đăng nhập agy** | `curl -fsSL https://antigravity.google/cli/install.sh \| bash`, sau đó mở **Terminal riêng** chạy `~/.local/bin/agy`, đăng nhập bằng tài khoản Google có gói AI Pro. Ở màn điều khoản: bỏ tick chia sẻ dữ liệu (Space), Tab tới `[Done]`, Enter. Chạy lại `bash scripts/setup.sh` để gộp quyền. |
| **Duyệt MCP `glm`** | Mở `claude` từ gốc repo, chọn đồng ý khi được hỏi bật server `glm`. |

## Kiểm tra sau khi cài
```bash
.venv/bin/python -m pytest -q                               # test client GLM
~/.local/bin/agy -p "/usage" --print-timeout 60s            # quota gói Gemini Pro
.venv/bin/python -m src.board add-render ta-that-su-khong-muon-trong-sinh 1 && .venv/bin/python -m src.board run   # dựng thử chương 1
```

## Lỗi đã biết
- **VieNeu báo "External data path escapes model directory":** onnxruntime từ 1.30 từ chối file model mà HuggingFace lưu dạng symlink. Chạy lại `.venv/bin/python scripts/setup_models.py`; script chuyển symlink thành file thật.
- **edge-tts báo "No audio was received":** dịch vụ chặn khi gọi dồn dập, chờ rồi thử lại. edge-tts chỉ để thử, giọng mặc định của dự án là VieNeu.
- **agy trả về rỗng:** thiếu quyền `read_url(<tên miền>)`. Thêm tên miền vào `scripts/agy_permissions.json` rồi chạy lại `setup.sh`.
- **ffmpeg không có `drawtext` hay `subtitles`:** bản Homebrew hiện tại không kèm libass, nên chưa đốt chữ vào hình được; dùng phụ đề mềm (.srt).

## Gỡ bỏ
- Xoá thư mục repo là sạch phần của dự án.
- Công cụ hệ thống, nếu không dùng nữa: `brew uninstall ffmpeg yt-dlp`; agy thì xoá `~/.local/bin/agy` và `~/.gemini/antigravity-cli/`.
