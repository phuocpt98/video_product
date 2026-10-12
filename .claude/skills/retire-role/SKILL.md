---
name: retire-role
description: Cắt giảm hoặc gộp vai trò trong studio khi vai trò chồng phạm vi, không còn được dùng, hoặc Người sáng lập muốn thu gọn đội hình.
argument-hint: "<tên-vai-trò> [gộp-vào <vai-trò-khác>]"
---

# /retire-role: cắt giảm hoặc gộp vai trò

Đầu vào: `$ARGUMENTS`.

1. **Kiểm tra tác động:** `grep` tên vai trò trong `.claude/`, `docs/`, `CLAUDE.md` để tìm nơi đang nhắc tới (sơ đồ, playbook, skill, brief mẫu).
2. **Đề xuất cho Người sáng lập:**
   - bỏ hẳn, hay gộp phạm vi vào vai trò nào
   - những chỗ nào phải sửa
   - Chờ đồng ý.
3. **Thực hiện:**
   - Gộp: chuyển trách nhiệm và quyền cần giữ sang file vai trò nhận, không làm rộng thêm quyền ngoài phần được duyệt.
   - Bộ nhớ `.claude/agent-memory/<vai-tro>/` (nếu có): phần còn giá trị chuyển vào bộ nhớ vai trò nhận hoặc `docs/`, rồi xoá thư mục.
   - Xoá file vai trò. Git giữ lịch sử, không để bản `_old`. Dự án chưa có git thì hỏi Người sáng lập trước khi xoá.
   - Xoá dòng trong sổ đăng ký `org-chart.md`, sửa sơ đồ mermaid, sửa mọi chỗ nhắc tới ở bước 1.
   - Ghi quyết định vào `docs/decisions.md`.
4. **Kiểm chứng:** `grep` lại tên vai trò. Chỉ còn trong `decisions.md` và lịch sử thì đạt.
