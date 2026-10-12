---
name: record-lesson
description: Ghi một bài học (sai lầm, cách làm hay, ràng buộc phát hiện ra) vào sổ bài học của studio, và nâng thành luật khi lặp lại. Dùng sau sự cố, sau khi Người sáng lập sửa cách làm, hoặc khi phát hiện điều nên áp dụng cho mọi dự án.
argument-hint: "<bài học ngắn>"
---

# /record-lesson: ghi và nâng cấp bài học

Đầu vào: `$ARGUMENTS`.

1. **Phân loại:**
   - Đúng cho mọi dự án: `.claude/company/lessons.md`.
   - Chỉ đúng cho dự án này: ghi vào bộ nhớ của quản lý liên quan. Nếu cần thành quy định của dự án thì thêm vào `docs/decisions.md` mục **"Đang chờ Người sáng lập chốt"**. Không tự ghi vào "Đã chốt".
2. **Tìm trùng:** đọc `lessons.md`. Đã có bài học tương tự thì **tăng "Số lần gặp"** và bổ sung dự án, không thêm dòng mới.
3. **Ghi:** thêm dòng lên đầu bảng: ngày, dự án, bài học (1 câu), áp dụng thế nào (hành động cụ thể), số lần = 1, đã thành luật = Chưa.
4. **Nâng thành luật khi số lần ≥ 2:**
   - Đề xuất câu luật và vị trí cụ thể: playbook nào hoặc mục nào của hiến pháp.
   - **Sửa hiến pháp phải được Người sáng lập duyệt.** Playbook thì Điều phối được sửa, nhưng phải báo lại.
   - Sau khi đưa vào, ghi vị trí vào cột "Đã thành luật?".
5. **Giữ gọn:** bảng dài quá 40 dòng thì gộp các bài học đã thành luật thành một dòng tóm tắt kèm link tới luật.
