# Luật viết kịch bản phim AI (Muse và công cụ video AI khác)

Cập nhật: 8/10/2026 · Rút từ phim thử `nguoi-giu-deo` (bản nháp v4: đoạn đầu đẹp, đoạn đánh nhau rời rạc) và báo cáo [research/2026-10-08-ai-action-animation.html](../research/2026-10-08-ai-action-animation.html).

**Ý chính:** cảnh hành động không cứu được ở khâu dựng. Phải thiết kế đúng từ lúc viết từng clip. Tạo clip như đạo diễn, dựng như kỹ sư.

## 1. Vì sao clip AI ghép lại trông rời rạc
- Mỗi clip là một lần dựng mới: thế giới, tỉ lệ, ánh sáng tự bịa lại.
- Cắt ở tư thế đã xong (nhân vật đứng yên) thì clip sau "khởi động lại".
- Prompt kiểu "đánh nhau dữ dội" không có hướng, va chạm, phản ứng, nên model tự điền.
- Quay chậm làm lực đánh thành lơ lửng. Cảnh 10 giây quay chậm thì lê thê.
- Hai thân thể sát nhau và cử động lớn thì tay chân, vũ khí, tỉ lệ bị méo.

## 2. Luật viết
1. **Một nhịp = một clip.** Mỗi clip chỉ một hành động có nguyên nhân và hậu quả. Phần đánh nhau chia 4 khối: áp sát → thất thế → đảo chiều → kết liễu, tổng 8–12 nhịp có đánh số.
2. **Tốc độ thật, biên độ vừa.** Không viết "slow motion" trong prompt. Cảm giác lực làm bằng đứng hình 1–2 khung (hit-stop) và âm thanh ở khâu dựng.
3. **Prompt tả vật lý, không tả khí thế.** Theo chuỗi: ai chủ động → hướng và tốc độ → trúng / đỡ / hụt → phản ứng → vị trí mới → mồi cho nhịp sau.
4. **Khoá bên màn hình.** Mỗi phe một bên suốt trận (ví dụ người bên trái, quái bên phải). Ghi rõ trong từng prompt (`on the left of frame`).
5. **Nối khung hình chỉ khi cùng góc máy.** Khung cuối clip N làm ảnh đầu vào của clip N+1 khi clip sau giữ nguyên góc và cỡ cảnh (ghi `continuing the same shot`). Đổi góc hoặc cỡ cảnh thì không nối khung, mà **cắt giữa động tác**: clip sau mở đầu khi động tác đang dở (`the action already in motion`). Đừng cắt sau khi nhân vật đã đứng yên.
6. **Mỗi prompt một kiểu máy quay**, nhiều nhất hai. Đổi cỡ cảnh khi cắt thì nhảy ít nhất gấp đôi (toàn → trung → cận).
7. **Cảnh an toàn:** một nhân vật cử động rõ; cận vũ khí, chân, mắt, đá vụn; bóng đen ngược sáng; hai nhân vật xa nhau. **Tránh:** vật lộn, nhiều người đánh nhau, đứng tụ lực hoặc nhìn nhau quá lâu.
8. **Chuẩn bị cảnh chèn từ đầu** (mắt, vũ khí, chân, đá vỡ) để che chỗ nối xấu.
9. **Không thoại nhép môi.** Lời là giọng kể đặt lên cảnh quay lưng hoặc cảnh rộng.

## 3. Bộ lọc nội dung (Muse)
- Bị chặn: máu, đâm xuyên thân thể, "hất văng", "đâm sâu vào chân". Thử 2 lần không qua thì viết lại, không cố.
- Qua được: va chạm vào **đá, kim loại, năng lượng** có hậu quả rõ (đá vỡ bắn ra, khổng lồ lùi nửa bước), bị thương thể hiện bằng **ẩn dụ** (tia sét tắt dần), cú đánh cuối bằng **ánh sáng** rồi cắt sang hậu quả.
- Khối mô tả dùng chung không gắn đạo cụ thay đổi trong phim (giáo gãy thì tách giáo ra khối riêng).

## 4. Quy trình
1. Ảnh chuẩn: 1 bảng nhân vật mỗi vai + 3–5 góc bối cảnh. Mọi lần tạo đều gắn ảnh chuẩn. Muse tạo, Người sáng lập duyệt.
2. Viết nhịp, đánh dấu cặp clip nối khung hình và điểm cắt.
3. Tạo clip **im lặng về mặt dùng**: âm Muse bỏ hoặc vặn rất nhỏ.
4. Nhịp nào hỏng thì tạo lại 1–2 bản, không làm nhiều bản cho mọi nhịp (quota tuần của Muse có hạn).
5. Dựng: cắt đầu và đuôi mỗi clip khoảng 0,5 giây, nối giữa động tác, chèn cảnh phụ khi cảnh rộng gãy.
6. Âm thanh theo bảng tiếng động: mỗi cú vung, va chạm, bước chân có một tiếng, lệch không quá 1–2 khung. Mức tham khảo: master khoảng −12 LUFS, đỉnh ≤ −1 dB, giọng kể cao hơn nền ít nhất 7 dB.
7. Lưu sau mỗi nhịp: clip giữ lại, khung cuối, prompt, ảnh tham chiếu.
