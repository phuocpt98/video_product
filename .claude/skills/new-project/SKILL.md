---
name: new-project
description: Nhân bản studio sang một dự án mới từ ý tưởng của Người sáng lập. Copy tầng công ty (luật, đội hình, playbook, hook, skill quản trị), tạo CLAUDE.md và bộ docs khởi đầu từ template. Không copy dữ liệu hay vai trò riêng của dự án hiện tại.
argument-hint: "<đường-dẫn-thư-mục-mới> <ý tưởng ngắn>"
disable-model-invocation: true
---

# /new-project: mở dự án mới

Đầu vào: `$ARGUMENTS` (đường dẫn tuyệt đối thư mục mới + ý tưởng).

## Bước 1. Xác nhận
Hỏi Người sáng lập nếu chưa rõ:
- tên dự án
- thư mục đích (đã tồn tại chưa, có dữ liệu không, **không ghi đè**)
- gói ngành nào cần mang theo (xem `.claude/agents/packs/`)

## Bước 2. Copy tầng công ty
Từ repo hiện tại sang `<dich>/`:
```
.claude/company/                 (toàn bộ)
.claude/agents/company/          (toàn bộ)
.claude/agents/packs/<pack>/     (chỉ gói đã chọn)
.claude/skills/hire-role/  .claude/skills/retire-role/  .claude/skills/new-project/  .claude/skills/record-lesson/
```
**KHÔNG copy:**
- `.claude/agents/project/`
- `.claude/agent-memory/`
- `.claude/settings.local.json`
- `docs/` của dự án cũ, `CLAUDE.md` cũ
- skill riêng của dự án cũ

## Bước 3. Tạo tầng dự án từ template
- `<dich>/CLAUDE.md` ← `.claude/company/templates/project-CLAUDE.md`:
  - điền tên, mô tả, ràng buộc
  - bản đồ thư mục khởi đầu chỉ gồm những gì chắc chắn cần
- `<dich>/.claude/settings.json` ← `templates/settings.json`
- `<dich>/.gitignore` ← `templates/gitignore`
- `<dich>/docs/README.md`, `progress.md`, `decisions.md` ← `templates/docs/`. Ghi ý tưởng ban đầu vào `decisions.md` mục chờ chốt.
- Thay mọi placeholder `<…>`, kể cả ngày `<dd/mm/yyyy>`. Kiểm bằng `grep -rn "<dd/mm/yyyy>\|<ten-du-an>" <dich>/CLAUDE.md <dich>/docs`, kết quả phải rỗng.

## Bước 4. Kiểm chứng
- Chạy hook thử, kết quả mong đợi `0` rồi `2`:
  ```bash
  H=<dich>/.claude/company/hooks/check_file_placement.py
  for f in docs/progress.md random_dir/x.py; do
    echo "{\"tool_input\":{\"file_path\":\"<dich>/$f\"}}" | CLAUDE_PROJECT_DIR=<dich> python3 $H; echo $?
  done
  ```
- Liệt kê cây thư mục `.claude/` và `docs/` của dự án mới.
- Đề xuất `git init` (hỏi trước).

## Bước 5. Bước tiếp theo đề xuất
Mở phiên Claude Code trong `<dich>`, gọi `product-lead` để biến ý tưởng thành mục tiêu và phạm vi MVP.

## Ghi chú về cập nhật tầng công ty
- Tầng công ty ở các dự án là **bản copy**.
- Khi sửa luật hay vai trò lõi ở một dự án, ghi vào `.claude/company/lessons.md` để mang sang dự án khác.
- Khi có từ 3 dự án trở lên, cân nhắc tách tầng công ty thành **plugin Claude Code riêng** để mọi dự án dùng chung một nguồn.
