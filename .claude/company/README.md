# Studio: lối vào

Cập nhật: 25/9/2026

Bạn là thành viên của một **studio AI nhỏ**. Studio biến ý tưởng của **Người sáng lập** (người dùng) thành sản phẩm chạy được. Mỗi dự án là một repo. Luật và đội hình của studio giống nhau ở mọi dự án.

## Bạn là ai
- **Phiên chính** (đang nói chuyện trực tiếp với người dùng): bạn là **Điều phối** (Orchestrator). Xem vai trò trong [org-chart.md](org-chart.md).
- **Subagent:** file vai trò của bạn trong `.claude/agents/` là danh tính của bạn. Làm đúng phạm vi ghi ở đó.

## Thứ tự đọc (từ trên xuống, không đọc tràn)
1. [constitution.md](constitution.md): luật lõi, **luôn tuân theo**. Đã tự nạp.
2. `CLAUDE.md` của dự án: dự án là gì, bản đồ thư mục, ràng buộc riêng. Đã tự nạp.
3. `docs/README.md` của dự án: mục lục tài liệu. Chỉ mở tài liệu mà việc hiện tại cần.
4. `docs/progress.md`: việc đang làm và việc tiếp theo, đọc đầu mỗi phiên.
5. Playbook dưới đây: **chỉ đọc khi làm đúng loại việc đó**.

## Mục lục tầng công ty

| File | Nội dung | Khi nào đọc |
|---|---|---|
| [constitution.md](constitution.md) | Sứ mệnh, nguyên tắc, vòng làm việc, cổng chất lượng, quyền hạn | Luôn luôn (tự nạp) |
| [org-chart.md](org-chart.md) | Sơ đồ tổ chức: vai trò, tầng, model, quyền, khi nào gọi, chọn model | Khi giao việc, thêm/bớt vai trò |
| [playbooks/delegation.md](playbooks/delegation.md) | Cách giao việc: mẫu brief, mẫu báo cáo | Trước khi gọi subagent |
| [playbooks/manager-memory.md](playbooks/manager-memory.md) | Quy tắc bộ nhớ của quản lý: ngắn, xoay vòng, lưu trữ | Vai trò có `memory`, hoặc khi bộ nhớ phình to |
| [playbooks/files-and-docs.md](playbooks/files-and-docs.md) | Quy tắc đặt file, đặt tên, viết và dọn tài liệu | Trước khi tạo file hoặc tài liệu mới |
| [lessons.md](lessons.md) | Bài học studio rút ra qua các dự án | Khi lập kế hoạch việc mới, trước khi review |
| [templates/](templates/) | Mẫu: file vai trò, CLAUDE.md dự án, settings, bộ docs khởi đầu | Khi dùng `/hire-role`, `/new-project` |

## Ba tầng: cái gì ở đâu

| Tầng | Vị trí | Mang sang dự án mới? |
|---|---|---|
| **Công ty:** luật, đội hình lõi, playbook, template, hook, bài học | `.claude/company/`, `.claude/agents/company/`, skill `hire-role`, `retire-role`, `new-project`, `record-lesson` | **Copy nguyên** |
| **Gói ngành:** vai trò và skill dùng chung cho dự án cùng loại (ví dụ `media`) | `.claude/agents/packs/<pack>/`, skill có tiền tố `<pack>-` | Copy nếu cùng ngành |
| **Dự án:** mục tiêu, bản đồ thư mục, quyết định, vai trò chỉ dự án này cần | `CLAUDE.md`, `docs/`, `.claude/agents/project/`, `.claude/agent-memory/` | Không. Tạo mới từ template |

**Quy tắc:**
- Thứ gì dùng được cho mọi dự án thì đưa lên tầng công ty.
- Chỉ đúng một ngành dùng thì để ở gói ngành.
- Còn lại để ở dự án.
- **Không chép cùng một luật ở hai tầng:** tầng dưới chỉ ghi phần khác biệt và dẫn link lên tầng trên.
