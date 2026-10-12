---
name: hire-role
description: Thêm vai trò mới vào studio, hoặc sửa vai trò có sẵn (đổi phạm vi, thêm công cụ hoặc quyền nghiệp vụ, đổi model). Dùng khi Người sáng lập muốn thêm vị trí, mở rộng quyền, hoặc khi một loại việc lặp lại chưa có vai trò phù hợp.
argument-hint: "<tên-vai-trò> <mục đích ngắn>"
---

# /hire-role: tuyển hoặc điều chỉnh vai trò

Đầu vào: `$ARGUMENTS` (tên vai trò tiếng Anh gạch ngang + mục đích).

## Bước 1. Kiểm tra trùng
- Đọc bảng "Sổ đăng ký vai trò" trong `.claude/company/org-chart.md`.
- Vai trò hiện có đã phủ ≥70% phạm vi thì **đề xuất sửa vai trò đó** thay vì thêm mới.
- Việc chỉ xảy ra một lần thì **không tuyển**: giao cho vai trò hiện có kèm brief kỹ.

## Bước 2. Xác định tầng và cấp

| Câu hỏi | Kết quả |
|---|---|
| Mọi dự án đều cần? | Tầng công ty: `.claude/agents/company/` |
| Chỉ dự án cùng ngành cần? | Gói ngành: `.claude/agents/packs/<pack>/`, tên `<pack>-<vai-tro>` |
| Chỉ dự án này cần? | Tầng dự án: `.claude/agents/project/` |
| Dựng khung, quyết định, duyệt? | Cấp Quản lý: model opus, `memory: project`, được dùng `Agent` |
| Làm, test, chạy? | Cấp Thực thi: model sonnet, hoặc haiku nếu hoàn toàn máy móc, không có bộ nhớ |

## Bước 3. Đề xuất cho Người sáng lập duyệt
Trình bày ngắn gọn:
- tên, tầng, cấp, model
- công cụ (ít nhất có thể)
- được làm, không được làm
- gọi khi nào
- quyền mới trong `.claude/settings.json` nếu cần

**Chờ đồng ý** trước khi tạo. Hiến pháp §6 yêu cầu duyệt khi thêm vai trò hoặc thêm quyền.

## Bước 4. Tạo hoặc sửa
1. Tạo file từ `.claude/company/templates/agent.md`: điền frontmatter và các mục. Viết tiếng Việt, ngắn, có mục "Không được làm".
2. Thêm hoặc sửa dòng trong bảng sổ đăng ký của `org-chart.md`, sửa sơ đồ mermaid nếu quan hệ giao việc thay đổi.
3. Nếu là thư mục mới (`packs/<pack>/`, `project/`): cập nhật bản đồ thư mục trong `CLAUDE.md` dự án.
4. Có quyền mới thì sửa `.claude/settings.json` và ghi vào `docs/decisions.md` (ngày, quyền, lý do).
5. Cập nhật dòng `Cập nhật:` của `org-chart.md`, và ghi quyết định tuyển (ngày, vai trò, lý do) vào `docs/decisions.md` mục "Đã chốt" (vì Người sáng lập đã duyệt ở Bước 3).

## Bước 5. Kiểm chứng
- Frontmatter hợp lệ: có `name`, `description`, `tools`, `model`.
- `name` khớp tên file.
- Vai trò xuất hiện trong bảng sổ đăng ký.
- Báo Người sáng lập: đã tạo gì, gọi thế nào (ví dụ "dùng agent `<ten>` để…").
- Nhắc Người sáng lập: vai trò mới có thể cần khởi động lại phiên mới được nhận.
