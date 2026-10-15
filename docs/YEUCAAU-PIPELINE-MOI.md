# Yêu cầu pipeline mới: truyện ngắn → ghép dài → đa nền tảng

## Bối cảnh
Pipeline hiện tại (`src/produce.py` nhánh plan-muse): 1 chương → 1 video dọc 1080x1920 → thumbnail intro 1s → up Drive → đăng Facebook tay.
Chưa có: gen nhiều chương liên tục, ghép bản dài ngang cho YouTube, đăng TikTok/YouTube tự động, dọn rác cuối pipeline.

## Yêu cầu

### 1. Gen liên tục tối đa 5 chương
- Input: 1 folder chứa tối đa 5 file .txt (mỗi file = 1 chương)
- Chạy `produce` cho từng chương liên tiếp, không cần can thiệp giữa chừng
- Mỗi chương ra 1 video dọc 1080x1920 + thumbnail intro 1s (dùng lại `scripts/make_thumbnail.py`, `scripts/add_intro.py`)
- Nếu 1 chương lỗi: retry tối đa 3 lần, log lỗi vào `log.jsonl`, tiếp tục chương sau (không dừng cả batch)

### 2. Đăng bản ngắn lên các nền tảng
Sau khi từng chương gen xong:
- **Facebook**: đăng Reel lên Page Nóng Lóng (dùng `facebook-cli`, caption theo format hiện tại)
- **TikTok**: upload qua browser session (skill `local-tiktok-post`), caption + hashtag riêng, KHÔNG copy từ Facebook
- Mỗi nền tảng giãn cách 2-3 tiếng giữa các tập (bài học: đăng dồn bị bóp reach)

### 3. Ghép bản dài ngang cho YouTube
- Ghép tất cả chương trong batch thành 1 video ngang 1920x1080
- Cách ghép: **xếp 3 khung hình dọc cạnh nhau** (mỗi khung 640x1080) thành 1 frame ngang 1920x1080 — KHÔNG dùng nền mờ blur 2 bên
- Nếu số chương không chia hết cho 3: khung thừa để trống đen hoặc lặp lại khung cuối
- Audio: nối tiếp các chương, giữ nguyên mono, không re-encode thừa
- Thêm intro chung đầu video (thumbnail tổng của cả bộ, 3s)

### 4. Đăng YouTube
- Upload bản dài qua YouTube Data API v3 (credentials đã có: `~/.youtube_oauth_env`, refresh token `~/.youtube_refresh_token`)
- Đăng dưới dạng video thường (không phải Shorts vì đã convert sang ngang)
- Tích chọn "nội dung có yếu tố AI" (giọng TTS + ảnh AI)
- Tiêu đề/mô tả/tags: viết riêng cho YouTube (SEO: tên truyện + "full" + "trọn bộ")

### 5. Up Drive + dọn rác
- Up tất cả video (bản ngắn từng chương + bản dài) lên folder Drive của truyện
- Cập nhật sheet `task_video_truyện_drama`
- Dọn rác: xóa `audio/`, `video/`, `parts/` sau khi up Drive; xóa file mp4 local sau khi đăng xong tất cả nền tảng

## Ràng buộc kỹ thuật
- Không viết lại code hiện tại nếu không cần — tái sử dụng `src/produce.py`, `scripts/add_intro.py`, `scripts/make_thumbnail.py`
- Mọi lỗi sửa ở GỐC, log đầy đủ: lỗi → nguyên nhân → cách khắc phục (ghi vào `WORKFLOW.md`)
- Test end-to-end với 1 bộ 2-3 chương trước khi bàn giao
- Branch làm việc: tạo nhánh mới từ `plan-muse`, không commit thẳng vào `plan-muse`

## Output bàn giao
1. Code pipeline mới (script hoặc mở rộng `src/produce.py`)
2. `WORKFLOW.md` cập nhật
3. Video test: 2-3 chương ngắn + 1 bản dài đã qua self-review (trích frame kiểm tra)
4. Hướng dẫn chạy 1 lệnh duy nhất cho cả pipeline
