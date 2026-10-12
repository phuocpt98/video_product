# <ten-du-an>: <mô tả một dòng>

Cập nhật: <dd/mm/yyyy>

## 0. Lối vào (đọc theo thứ tự, đã tự nạp)
- Studio, bạn là ai, luật lõi: @.claude/company/README.md và @.claude/company/constitution.md
- Mục lục tài liệu dự án: @docs/README.md
- Đầu mỗi phiên: đọc [docs/progress.md](docs/progress.md). Các file khác chỉ mở khi việc cần.

## 1. Dự án
<Mục tiêu, người dùng, sản phẩm đầu ra. Kế hoạch ở docs/plans/, quyết định ở docs/decisions.md.>

**Ràng buộc riêng của dự án:**
- <pháp lý, nền tảng, ngân sách, công nghệ bắt buộc…>

**Môi trường:** <máy, ngôn ngữ, công cụ>

## 2. Bản đồ thư mục

Nguồn duy nhất, hook đọc khối dưới đây. Ý nghĩa các đánh dấu và quy tắc thêm vị trí: [files-and-docs.md](.claude/company/playbooks/files-and-docs.md).

```
<ten-du-an>/
├── CLAUDE.md              # lối vào tầng dự án
├── README.md              # (dự kiến) giới thiệu dự án cho người đọc
├── requirements.txt       # (dự kiến) hoặc pyproject.toml / package.json tuỳ công nghệ
├── .gitignore
├── .env                   # (dự kiến) bí mật, không commit
├── .claude/               # [md] cấu hình studio + dự án
│   ├── settings.json
│   ├── company/           # TẦNG CÔNG TY
│   ├── agents/company/    # vai trò lõi
│   ├── agents/project/    # (dự kiến) vai trò riêng dự án
│   ├── skills/
│   └── agent-memory/      # bộ nhớ quản lý
├── docs/                  # [md] tài liệu dự án
│   ├── plans/             # (dự kiến)
│   └── research/          # (dự kiến)
├── src/                   # (dự kiến) code
├── tests/                 # (dự kiến)
└── tmp/                   # [md] nháp tạm
```

## 3. Điều chỉnh playbook công ty cho dự án này
Chưa có. Playbook công ty áp dụng nguyên.
