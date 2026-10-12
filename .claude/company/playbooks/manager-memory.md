# Playbook: bộ nhớ của quản lý

Cập nhật: 25/9/2026

Vai trò có `memory: project` có thư mục riêng `.claude/agent-memory/<vai-tro>/`. Mỗi lần được gọi, **200 dòng đầu của `MEMORY.md` tự nạp**. Vì vậy `MEMORY.md` phải ngắn và chỉ chứa thứ còn sống.

## Cấu trúc
```
.claude/agent-memory/<vai-tro>/
├── MEMORY.md          # ≤ 60 dòng, tự nạp mỗi lần gọi
├── notes/<chu-de>.md  # ghi chú chi tiết theo chủ đề, chỉ mở khi cần
└── archive/YYYY-MM.md # việc đã xong, KHÔNG tự nạp
```

## Mẫu `MEMORY.md`
```
# <vai-tro>: bộ nhớ làm việc
Cập nhật: dd/mm/yyyy

## Đang theo dõi (tối đa 5 việc)
- [ ] <việc> — trạng thái — bước tiếp — (chi tiết: notes/<chu-de>.md)

## Checklist việc hiện tại
- [ ] ...

## Ghi nhớ bền (tối đa 10 dòng)
- <điều luôn đúng với dự án này mà vai trò cần nhớ>
```

## Quy tắc xoay vòng
- **Việc xong:** xoá khỏi `MEMORY.md`, ghi một dòng vào `archive/YYYY-MM.md` (ngày, việc, kết quả, link).
- **`MEMORY.md` vượt 60 dòng:** gom bớt, chuyển chi tiết sang `notes/`.
- **Không chép lại** thứ đã có trong `docs/`: ghi đường dẫn thay vì nội dung.
- **Không ghi** bí mật, nội dung file dài, hay nhật ký từng bước.
- **Ghi nhớ bền** mà hoá ra đúng cho mọi dự án: đề xuất đưa lên `lessons.md` công ty.
