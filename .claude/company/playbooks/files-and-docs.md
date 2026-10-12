# Playbook: đặt file và tài liệu

Cập nhật: 25/9/2026

## Đặt file
1. **Bản đồ thư mục** nằm trong `CLAUDE.md` của dự án (mục "Bản đồ thư mục"). Đây là nguồn duy nhất.
2. **Trước khi tạo file:** tìm vị trí trong bản đồ.
   - Không có chỗ thì hỏi Người sáng lập.
   - Sau đó thêm dòng mới vào bản đồ, kèm ngày, rồi mới tạo file.
3. **Hook `check_file_placement.py`** đọc chính bản đồ đó và tự chặn:
   - thư mục hoặc file gốc không có trong bản đồ
   - tên kiểu nhân bản (`_v2`, `_final`, `_backup`, `_copy`, `_old`…)
   - `.md` nằm ngoài thư mục được đánh dấu `[md]`
   - ghi vào thư mục đánh dấu `[readonly]`
   - tên file hoặc thư mục có ký tự ngoài ASCII
4. **Đánh dấu trong bản đồ** (viết trong phần chú thích sau `#`):
   - `[md]`: được chứa file `.md`
   - `[readonly]`: chỉ đọc
   - `(dự kiến)`: chưa tạo, chỉ tạo khi cần
5. **Nháp** để trong `tmp/`. Thử thành công thì đưa vào đúng module rồi xoá nháp.
6. **Không script dùng một lần** trong thư mục code.

## Đặt tên
- **Tên file và thư mục bằng tiếng Anh**, chữ thường, không dấu. Nội dung viết tiếng Việt.
- `.md`: gạch ngang, ví dụ `technical.md`, `ai-services.md`.
- Code và dữ liệu: gạch dưới, ví dụ `step_03_rewrite.py`, `rename_map.json`.
- Số thứ tự đệm 0: `001.txt`, `step_01_…`.
- Tên vai trò và skill: tiếng Anh gạch ngang, ví dụ `qa-lead`, `hire-role`.

## Tài liệu dự án (`docs/`)

| File / thư mục | Vai trò |
|---|---|
| `docs/README.md` | Mục lục: mỗi tài liệu một dòng, kèm "khi nào đọc" |
| `docs/progress.md` | Đang làm, tiếp theo, đã xong (≤15 việc gần nhất) |
| `docs/decisions.md` | Quyết định đã chốt (kèm ngày) và câu hỏi chờ Người sáng lập. **Nguồn đúng cao nhất của dự án** |
| `docs/plans/` | Kế hoạch sản phẩm và kỹ thuật |
| `docs/research/` | Nghiên cứu: đối thủ, công nghệ, dịch vụ. Có nguồn và ngày |

## Quy tắc viết và dọn
- Đầu mỗi tài liệu có `Cập nhật: dd/mm/yyyy`. Sửa nội dung thì cập nhật ngày.
- **Một chủ đề, một tài liệu.** Có sẵn thì sửa, không viết file mới chồng lên.
- Thêm, xoá hoặc đổi tên tài liệu thì **cập nhật `docs/README.md` trong cùng lượt**.
- **Mâu thuẫn:** sửa ngay. Thứ tự tin: `decisions.md` → `plans/` → `research/`.
- **Lỗi thời:** sửa lại, hoặc xoá hẳn và gỡ khỏi mục lục. Không giữ bản "cũ", vì git giữ lịch sử. **Dự án chưa có git thì hỏi Người sáng lập trước khi xoá** (hoặc đề xuất `git init`).
- Ưu tiên bảng và gạch đầu dòng. Link giữa tài liệu dùng đường dẫn tương đối.
- Tài liệu viết thành file `.md` cục bộ, không tạo tài liệu online trừ khi Người sáng lập yêu cầu.
