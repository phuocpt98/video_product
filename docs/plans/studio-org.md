# Tổ chức phòng ban studio và tăng tốc sản xuất

Cập nhật: 28/9/2026 · Trạng thái: **đã duyệt 28/9/2026** (giữ 24 hình/giây), đang làm theo §6

## 1. Vấn đề
- **Các bước đang nối tay.** Phần chữ (`run.py`), dàn cảnh (`direct.py`), dựng (`stage.py`), nhân vật (trang tạo nhân vật, `make_parts.py`) và nền (`make_scene_sheet.py`) chạy bằng các lệnh riêng. Thiếu diễn viên hay nền thì không ai biết, trừ khi đọc dòng "Thiếu …" in ra màn hình.
- **Chậm.** Một video 10 tiếng khoảng 100 chương, mỗi chương khoảng 6 phút.

## 2. Số đo hiện tại và ước tính cho 10 tiếng video

| Khâu | Số đo | 100 chương, chạy nối tiếp | Ghi chú |
|---|---|---|---|
| Chữ: rã, viết, soát, duyệt, kiểm mạch | 5,6 phút/chương (đo lô 1, 3 luồng song song) | **khoảng 9,3 giờ** | **Nút thắt chính.** Mỗi chương gọi AI 4–6 lần, mỗi lần 1–3 phút |
| Giọng đọc VieNeu | 2–3 phút/chương | khoảng 4,2 giờ | Chạy từng chương một, máy còn nhiều nhân CPU rảnh |
| Dựng hình | 26 giây video dựng trong 6 giây (nhanh gấp 4 lần thời gian thực) | khoảng 2,5 giờ | **Không phải quay theo tốc độ thật:** hình vẽ bằng code, tiếng ghép sau |
| **Tổng nếu làm lần lượt** | | **khoảng 16 giờ** | |

## 3. Cách tăng tốc, xếp theo hiệu quả

### 3.1 Chạy gối đầu thay vì chạy lần lượt (lợi nhiều nhất, không tốn gì thêm)
Chương nào xong chữ thì đọc giọng ngay; chương nào có giọng thì dựng ngay. Ba khâu chạy song song trên các chương khác nhau, nên tổng thời gian ≈ khâu chậm nhất, **khoảng 9 giờ thay vì 16**.

### 3.2 Rút gọn khâu chữ ở chế độ viết lại nhẹ (đang dùng)
| Hiện tại | Đề xuất | Lợi |
|---|---|---|
| viết → soát → duyệt, trượt thì viết lại toàn bộ | **viết kèm tự kiểm** trong 1 lần gọi → máy kiểm (chữ Trung, tên cấm, độ dài, định dạng) → **chỉ gọi duyệt khi máy báo lỗi**, hoặc duyệt ngẫu nhiên 1/5 chương | Từ 4–6 lần gọi xuống 1–2 lần |
| sai vài câu thì viết lại cả chương | **sửa khoanh vùng:** Flash sửa đúng các câu sai (khoảng 30 giây) | Bỏ vòng viết lại 3 phút |
| mỗi lần gọi 1 chương | **gộp 2–3 chương ngắn một lần gọi** (Gemini đọc được rất dài) | Giảm thời gian khởi động agy, giữ mạch tốt hơn |
| rã chương và viết là 2 lần gọi | viết lại nhẹ thì **bỏ bước rã riêng**, người viết đọc thẳng chương gốc | Bớt 1 lần gọi |

Ước tính: **khoảng 1,5–2 phút/chương**, 100 chương còn khoảng 3 giờ. Rủi ro là chất lượng có thể giảm, nên cần thử trên 5 chương mẫu và so với bản đã duyệt trước khi áp dụng.

### 3.3 Giọng đọc: chạy 3 tiến trình song song
Máy có 10 nhân, VieNeu chạy bằng CPU. Chạy 3 chương cùng lúc thì khoảng **1,4 giờ cho 100 chương**. Cần đo RAM trước (mỗi tiến trình nạp model khoảng 1–2 GB).

### 3.4 Dựng: đã nhanh, còn vài cách nhỏ
- ~~15 hình/giây~~: Người sáng lập chốt giữ 24 hình/giây.
- Bản duyệt nhanh 720p, bản đăng 1080p.
- **Dùng lại video ngắn đã dựng** (ý của Người sáng lập): dựng đã rẻ, nên dùng lại **kịch bản cảnh mẫu** (ví dụ cảnh "tát rồi ngã", "gọi điện", "hồi tưởng") hiệu quả hơn dùng lại file video. Mẫu cảnh thay được diễn viên và nền, video dựng lại mất vài giây.

### 3.5 Tổng sau tối ưu
Gối đầu + chữ rút gọn + giọng song song: **khoảng 3–4 giờ cho 10 tiếng video**, chạy qua đêm. Hạn mức agy (khoảng 13 ảnh và lượt Gemini theo khung 5 giờ) sẽ là giới hạn mới; phần chữ cần theo dõi quota.

## 4. Các phòng ban

| Phòng | Việc | Ai làm | Nhận việc từ | Giao việc cho |
|---|---|---|---|---|
| **Biên kịch** | rã truyện, sổ tay, viết, duyệt, kiểm mạch | agy (Gemini) theo `run.py` | Điều phối (truyện mới) | Dựng (kịch bản đã khoá) |
| **Thiết kế nhân vật** | chọn bộ phận cho nhân vật từ sổ tay; lấy diễn viên có sẵn trong thư viện, không có thì ghép mới bằng `avatar.py` | agy đọc `assets/parts/INDEX.md` + code | Dựng (thiếu diễn viên) | Dựng (diễn viên sẵn sàng) |
| **Bối cảnh** | tìm nền trong thư viện, thiếu thì xin tạo | code + Người sáng lập hoặc agy tạo ảnh | Dựng (thiếu nền) | Dựng |
| **Dựng (studio)** | đạo diễn gắn nhãn → kịch bản cảnh → dựng video; thiếu gì thì treo việc và gửi yêu cầu | agy Flash + code | Biên kịch | Người sáng lập duyệt |
| **Tài nguyên ngoài** | việc cần Người sáng lập: tạo ảnh trên web, duyệt phong cách, đăng video | Người sáng lập | mọi phòng | phòng đã yêu cầu |
| **Kỹ thuật** | viết hành động mới, sửa lỗi code (theo danh sách chờ, làm theo lô) | Claude (Điều phối) | mọi phòng | phòng đã yêu cầu |

## 5. Kênh trao đổi: bảng việc bằng file

```
board/
├── tasks/<id>.yaml     # 1 việc = 1 file
├── events.jsonl        # nhật ký chỉ ghi thêm: ai, lúc nào, làm gì
└── inbox/              # Người sáng lập thả ảnh tạo trên web vào đây; máy tự nhận và cắt
```

Mẫu một việc:
```yaml
id: 2026-09-28-017
from: dung            # phòng gửi
to: thiet-ke          # phòng nhận
type: need-actor      # need-actor | need-scene | need-action | need-image | review | bug
story: ta-that-su-khong-muon-trong-sinh
chapter: 3
need: "Cao Gia Lương: nam 18, công tử đạo đức giả, tóc rẽ ngôi, polo hàng hiệu"
blocks: [dung-ch3]    # việc đang bị treo vì chờ việc này
status: open          # open | doing | blocked | done | rejected
log:
  - {at: "2026-09-28 10:02", by: dung, msg: "Chương 3 thiếu diễn viên Cao Gia Lương"}
```

**Luồng mẫu:** Dựng chương 3 thấy thiếu diễn viên Cao Gia Lương
→ treo việc `dung-ch3`, mở việc `need-actor` gửi Thiết kế
→ Thiết kế tìm trong mục lục diễn viên. Không có thì agy chọn bộ phận từ `assets/parts/INDEX.md` và ghép, xong ghi `done`
→ bảng việc tự mở lại `dung-ch3`, Dựng làm tiếp.

Nếu cần ảnh mới (nền, bộ đồ) thì Bối cảnh mở việc `need-image` gửi Người sáng lập, kèm prompt sẵn. Người sáng lập tạo trên web, thả ảnh vào `board/inbox/` rồi đánh dấu xong. Máy cắt ảnh và mở lại các việc đang chờ.

**Người sáng lập xem bảng việc:** một trang local cùng máy chủ với trang tạo nhân vật (`http://localhost:8765/board`). Trang có các cột Mở, Đang làm, Bị treo, Xong; bấm vào xem nhật ký, bình luận, thả ảnh. Claude đọc cùng các file này nên không cần kênh ngoài.

**Người chạy việc:** `python -m src.board run` chạy vòng lặp: lấy việc `open` của từng phòng, gọi đúng script, ghi nhật ký. Hết quota thì dừng và tự thử lại sau.

## 6. Lộ trình
1. Bảng việc: file, trang xem, người chạy việc. Nối `direct.py` để tự mở việc thiếu diễn viên và thiếu nền.
2. Phòng Thiết kế nhân vật tự động: agy chọn bộ phận từ mục lục và sổ tay.
3. Chạy gối đầu trong `run.py` và giọng đọc song song (3.1, 3.3).
4. Thử rút gọn khâu chữ trên 5 chương mẫu, so chất lượng với bản đã duyệt rồi mới áp dụng (3.2).
5. Đạo diễn gắn nhãn (đã bàn trước) và kịch bản cảnh mẫu dùng lại.

## 7. Câu hỏi cho Người sáng lập
1. Duyệt mô hình phòng ban và bảng việc bằng file + trang local (mục 4–5)?
2. Chấp nhận thử rút gọn khâu chữ (mục 3.2), dù có rủi ro chất lượng giảm, để đổi lấy tốc độ?
3. Video đăng dùng 15 hay 24 hình/giây?
