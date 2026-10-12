# Kế hoạch dựng chương 1 bằng phòng dựng rối cắt ghép

Cập nhật: 27/9/2026 · Trạng thái: **đang làm** (luồng dàn cảnh đổi sang code 27/9/2026) · Truyện: `stories/ta-that-su-khong-muon-trong-sinh/` · Công cụ: `src/studio/` (cutout.py, stage.py), `scripts/make_character.py`

## 1. Đầu vào đã có
- Kịch bản chương 1 đã duyệt và qua kiểm mạch: `script/001.txt`.
- Giọng Ngọc Huyền, tốc độ 1.12, dài khoảng 6,3 phút: `audio/001.mp3` và phụ đề theo từng câu `audio/001.srt`.
- Sổ tay truyện v3: nhân vật, bối cảnh, quy ước kể.

## 2. Diễn viên (thư viện `assets/characters/`)

| id | Vai | Xuất hiện ở chương 1 | Trạng thái |
|---|---|---|---|
| tran-han-thang-35 | Hán Thăng kiếp trước (35 tuổi, vest) | tiệc rượu, trong xe, tai nạn | đang tạo |
| truong-minh-dung | nữ khách ở tiệc (váy đỏ) | tiệc rượu, đưa danh thiếp | đang tạo |
| tran-han-thang | Hán Thăng 18 tuổi | xe buýt, trạm xe, nôn bên đường | ✅ có |
| vuong-tu-bac | bạn thân | xe buýt, trạm xe | đang tạo |
| tieu-dung-ngu | hoa khôi (chỉ được nhắc tới ở chương 1) | có thể thêm một cảnh hồi tưởng ngắn | đang tạo (dùng từ chương 2) |

Trợ lý của Hán Thăng: một câu thoại, dùng giọng người kể, không cần nhân vật.

## 3. Bối cảnh (thư viện `assets/scenes/`)

| id | Dùng cho đoạn | Trạng thái |
|---|---|---|
| hotel-banquet-night | tiệc rượu trong phòng VIP khách sạn | cần tạo |
| car-interior-night | trong xe Range Rover ban đêm, nghe nhạc, bấm lái | cần tạo |
| night-road | đường đêm; tai nạn = chớp trắng + rung + đen màn (hiệu ứng, không cần vẽ) | cần tạo |
| bus-interior-day | tỉnh dậy trên xe buýt, Tử Bác trêu | cần tạo |
| bus-stop-2002 | trạm xe, đường đất, tiệm cắt tóc, soi kính, nôn bên đường | ✅ có |

Tổng cần tạo thêm **4 nền**, khoảng 4% quota Gemini.

## 4. Luồng dựng

```
script/001.txt + audio/001.srt + sổ tay
  + cast.yaml (mục lục truyện → thư viện) + data/actions.yaml (luật từ khoá dùng chung)
  → (1) ĐẠO DIỄN BẰNG LUẬT (src/studio/direct.py, KHÔNG gọi AI, chốt 27/9/2026): sinh storyboard/001.yaml
        câu nhắc ai thì người đó diễn; câu trong ngoặc kép thì người nói nhép miệng; từ khoá → biểu cảm, tư thế,
        đạo cụ, rung, góc máy; gộp câu thành cảnh tối đa 8 giây; thiếu diễn viên/nền/đạo cụ thì bỏ qua và liệt kê
        nhân vật cao 1/4–1/2 khung hình
  → (3) DỰNG (stage.py): bản 16:9 cả chương + bản 9:16 cho video mồi 30–45 giây (đoạn đắt nhất)
  → (4) Người sáng lập xem → sửa YAML (không phải vẽ lại) → dựng lại
```

- **Ai đang nói:** câu trong ngoặc kép thì nhân vật đó nhép miệng; câu của người kể thì nhân vật diễn biểu cảm, không nhép.
- **Hội thoại hai người:** xen kẽ cảnh cận A và cận B theo từng lượt thoại, hoặc cả hai cùng khung (đứng hai bên, người nói được máy quay bám).
- **Hiệu ứng cần thêm vào stage.py:** chuyển cảnh (mờ dần, chớp trắng), lọc màu hồi tưởng, rung mạnh (tai nạn), đen màn, âm thanh (`assets/sfx/`: impact khi tai nạn, whoosh khi chuyển cảnh).

## 5. Việc cần làm

| # | Việc | Ai | Ước tính |
|---|---|---|---|
| 1 | Tạo 4 diễn viên, bạn duyệt ảnh ráp thử | agy + script, bạn duyệt | đang chạy |
| 2 | Tạo 4 nền | agy | khoảng 10 phút |
| 3 | Vai trò `director` (file prompt) + `src/studio/direct.py` (gọi agy, kiểm máy YAML) | Claude | 1 phiên |
| 4 | Thêm hiệu ứng vào stage.py (chuyển cảnh, chớp, lọc màu, âm thanh) | Claude | 1 phiên |
| 5 | Dựng chương 1: 16:9 (khoảng 6,3 phút) + clip dọc 30–45 giây | máy | khoảng 10–15 phút |
| 6 | Bạn xem, sửa YAML, dựng lại | bạn + máy | — |

## 6. Rủi ro
- **Diễn viên do AI tạo có thể lệch nét giữa các nhân vật** (mỗi người tạo riêng). Duyệt ảnh ráp thử trước khi dựng.
- **Nền và nhân vật tạo riêng** nên có thể lệch ánh sáng hay tỉ lệ. Chỉnh `height` và vị trí trong YAML.
- **Chỉ có 4 tư thế mỗi người.** Hành động đặc thù (lái xe, nôn) phải diễn bằng biểu cảm cộng nền cộng hiệu ứng. Cần thì tạo thêm tư thế (1 ảnh, khoảng 1% quota).
- Giới hạn riêng của model tạo ảnh chưa đo được. Tạo từng đợt nhỏ.
