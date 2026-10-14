# Giao thức ba bên: Claude, Muse, Người sáng lập

Cập nhật: 14/10/2026 · Người sáng lập chốt hướng 13/10/2026 (Claude xây thư viện, Muse chỉ kéo về chạy)

**Từ 14/10/2026 (nhánh `plan-muse`):** việc chính của Muse là **chạy dây chuyền** theo [README.md](../../README.md) mục 2: nhận file truyện → `python -m src.produce run <file>` → `status` → làm lại việc lỗi → báo đường dẫn `output/<slug>.mp4` kèm thời lượng. Lỗi không tự xử lý được thì mở issue `to:claude` kèm đúng câu lỗi trong `status` và đoạn cuối `log.jsonl`. Muse không sửa `src/`.

## 1. Ai làm gì

| Bên | Ở đâu | Làm | Không làm |
|---|---|---|---|
| **Claude** (Claude Code) | máy Người sáng lập, repo này | xây thư viện và dây chuyền (`src/`, `scripts/`), viết prompt (`prompts/`), viết luật và tài liệu, **duyệt** sản phẩm của Muse, gánh việc Muse làm yếu | tạo ảnh hàng loạt (quota Claude là gói chung của team) |
| **Muse** (agent trên máy cloud 2 CPU, 8 GB) | clone repo GitHub | `git pull`, tạo ảnh theo prompt máy in ra, chạy lệnh có sẵn, commit sản phẩm, báo lỗi kèm log | sửa `src/`, `prompts/`, `docs/plans/`, `.claude/`; tự nghĩ ra cách cắt ghép mới; sửa tay card.yaml |
| **agy** (Gemini Pro cá nhân) | máy Người sáng lập | tạo ảnh và chữ khối lượng lớn do Claude điều khiển | |
| **Người sáng lập** | mọi nơi | chốt hướng, duyệt hình và video cuối, trả lời việc `to:founder` | |

## 2. Kênh: GitHub Issues là bảng việc chung

- Việc phải **đổi máy** đi qua **GitHub Issues** của repo, thao tác bằng `python scripts/hub.py` (bọc `gh`, máy nào cũng cần `gh auth login` một lần).
- Một issue = một việc. Nhãn `to:claude | to:muse | to:founder` = ai đang cầm. Nhãn loại: `need-image | need-prompt | need-code | need-story | bug | review`.
- Sản phẩm (ảnh, bộ phận, card) giao bằng **PR** từ nhánh `task/<số issue>-<slug>`, mô tả PR có `Closes #<số>`.
- **Đầu mỗi phiên**, mỗi bên chạy `python scripts/hub.py next --to <mình>` và làm việc cũ nhất trước. Không có việc thì mới làm việc khác.

## 3. Dạng bình luận bắt buộc

Dòng đầu của mọi bình luận kết thúc một lượt làm: `Kết luận: ĐẠT` · `Kết luận: CHƯA ĐẠT` · `Kết luận: CHUYỂN → <bên>` · `Kết luận: HỎI`. Sau đó là bằng chứng: lệnh đã chạy, output cuối, đường dẫn file, commit. `hub.py done/reject/handoff` tự ghi đúng dạng. Không ghi "đã xong" mà không có lệnh và output.

## 4. Luồng mẫu

**A. Diễn viên mới (`need-image`)**
1. Claude: mở issue `to:muse` gồm (a) lệnh `python scripts/new_actor.py <id> --look ... --hair ... --outfit ... --outfit-desc ...`, (b) tiêu chí = validate ĐẠT + preview, (c) ghi chú ảnh nào Muse tự tạo nếu máy cloud không có agy (`--no-gen`, bỏ ảnh vào `assets/actors/<id>/source/` theo tên script in ra).
2. Muse: `git pull`, chạy lệnh. CHƯA ĐẠT thì tạo lại ảnh theo lỗi script in (không sửa tay). ĐẠT thì commit `assets/actors/<id>/` lên nhánh `task/<n>-<id>`, mở PR, `hub.py handoff <n> --to claude "<output validate>"`.
3. Claude: pull, `python -m src.studio.validate_actor <id> --preview`, xem preview. ĐẠT → merge, `hub.py done`. CHƯA ĐẠT → `hub.py reject <n> --to muse "lỗi..."`.
4. Người sáng lập chỉ xem khi Claude gắn `to:founder` (hình quan trọng: nhân vật chính, thumbnail).

**B. Truyện mới (`need-story`)**: Người sáng lập (hoặc Claude) gửi file truyện `.txt/.md/.docx` (dòng đầu là tiêu đề) qua issue `to:muse`. Muse: `git pull`, chạy `python -m src.produce run <file> --slug <slug>` theo [README.md](../../README.md) mục 2; còn việc `failed` thì đọc `status`, chạy lại `run --slug <slug>`; lỗi lặp lại thì mở `bug` `to:claude`. Xong: `hub.py handoff <n> --to founder` kèm đường dẫn `stories/<slug>/output/<slug>.mp4`, thời lượng, nội dung `upload.md` (video KHÔNG lên git; gửi file theo cách Người sáng lập dặn).

**C. Lỗi (`bug`)**: Muse mở issue `to:claude`: lệnh, 30 dòng log cuối, commit đang đứng. Claude sửa trong repo, merge, `handoff` về Muse để chạy lại. Muse **không vá code**.

**D. Thiếu prompt hoặc luật (`need-prompt`)**: như C.

## 5. Quy tắc commit
- Muse chỉ commit trong `assets/actors/`, `assets/scenes/`, `assets/props/`, `reference/` và file issue/log; mỗi PR một việc.
- Không commit media nặng (.mp4, .wav) và `stories/` (đã trong `.gitignore`).
- Claude merge PR của Muse sau khi validate; Muse không tự merge.

## 6. Việc còn thiếu để giao thức chạy trọn
- Truyện nhập sẵn (`rewrite: none`) chỉ đọc giọng, không nở văn; phần ngắn (< 600 chữ) cho video ngắn. Bước "nở văn" theo sổ tay là việc sau.
- Muse cần `gh auth login` trên máy cloud bằng tài khoản của Người sáng lập hoặc token chỉ có quyền issues + contents.
