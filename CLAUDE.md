# video_reup: kênh truyện YouTube + TikTok

Cập nhật: 14/10/2026

## 0. Lối vào (đọc theo thứ tự, đã tự nạp)
- Studio, bạn là ai, luật lõi: @.claude/company/README.md và @.claude/company/constitution.md
- Mục lục tài liệu dự án: @docs/README.md
- Đầu mỗi phiên: đọc [docs/progress.md](docs/progress.md). Các file khác chỉ mở khi việc cần.
- **Vận hành dây chuyền (truyện → video), cài máy mới, bổ sung kho: [README.md](README.md)** (nguồn chính, viết cho mọi AI).

## 1. Dự án
Kênh kể truyện tiếng Việt (đô thị, hệ thống, trọng sinh, drama). Từ 14/10/2026 (nhánh `plan-muse`): **1 file truyện chữ → chia phần → giọng đọc + hoạt hình nền ngẫu nhiên từng phần → ghép thành 1 video hoàn chỉnh** (`python -m src.produce`). Hình KHÔNG khớp truyện, chỉ để giữ mắt; không phụ đề trên hình (chỉ .srt). Kế hoạch ở [docs/plans/](docs/plans/). Quyết định ở [docs/decisions.md](docs/decisions.md).

**Ràng buộc riêng của dự án:**
- Tránh chính sách "inauthentic content" của YouTube:
  - truyện đọc THUẦN, không viết lại, không lời bình (Người sáng lập chốt 14/10/2026, docs/decisions.md); chỉ làm sạch + loại yếu tố không phù hợp bằng `prompts/story_narration.md`. Rủi ro đã chấp nhận: truyện dịch/phóng tác vẫn có thể vi phạm bản quyền và bị coi là "inauthentic"
  - hình ảnh **tự tạo**
  - không dùng clip, gameplay hay phim của người khác
- Chỉ dùng công cụ, giọng và trọng số **cho phép dùng thương mại**. edge-tts chỉ để thử nghiệm.
- Repo trong `tool/` phần lớn là GPL/AGPL hoặc không có giấy phép: **chỉ lấy ý tưởng**, tự viết code và prompt.
- Không lặp lỗi của repo cũ `~/Documents/project/personal/tiktok_content`: cắt clip kênh khác, chạy theo số lượng, mỗi video một script.

**Môi trường:** Mac Apple Silicon (mã hoá `h264_videotoolbox`) hoặc Ubuntu (máy cloud của Muse, `libx264`), Python 3.11+, ffmpeg. Không cần màn hình.

## 2. Bản đồ thư mục

Nguồn duy nhất, hook đọc khối dưới đây. Ý nghĩa các đánh dấu và quy tắc thêm vị trí: [files-and-docs.md](.claude/company/playbooks/files-and-docs.md).

```
video_reup/
├── CLAUDE.md              # lối vào tầng dự án (file này)
├── README.md              # HƯỚNG DẪN VẬN HÀNH ĐẦY ĐỦ (cài, chạy, lỗi, bổ sung kho) cho người và mọi AI: nguồn chính
├── .gitignore             # repo GitHub chỉ giữ cấu trúc, quy tắc, code, thư viện hình (không truyện, board, media)
├── config.yaml            # tham số dây chuyền chính (mục produce:), xem README.md §2.3
├── .env                   # API key. Không commit, không in ra
├── .env.example           # mẫu biến môi trường, không chứa giá trị thật
├── requirements.txt
├── pytest.ini             # testpaths = tests, để `pytest` trần từ gốc repo không quét tool/
├── .cache/                # model AI tải về (HF_HOME), không commit; tải lại bằng scripts/setup.sh
├── .venv/                 # môi trường Python cục bộ, không commit
├── .claude/               # [md] cấu hình studio + dự án
│   ├── settings.json      # quyền + hook (dùng chung). Cài đặt cá nhân: settings.local.json
│   ├── company/           # TẦNG CÔNG TY: hiến pháp, sơ đồ tổ chức, playbooks/, templates/, hooks/, lessons.md
│   ├── agents/company/    # vai trò lõi của studio
│   ├── agents/packs/      # (dự kiến) vai trò gói ngành, ví dụ packs/media/
│   ├── agents/project/    # vai trò chỉ dự án này cần (llm-runner)
│   ├── skills/            # hire-role, retire-role, new-project, record-lesson (+ skill dự án khi cần)
│   └── agent-memory/      # bộ nhớ của quản lý, tự tạo khi quản lý được gọi
├── docs/                  # [md] tài liệu dự án, xem docs/README.md
│   ├── plans/             # kế hoạch kênh, kỹ thuật
│   └── research/          # nghiên cứu: repo, dịch vụ, công cụ
│       └── trends/        # báo cáo xu hướng thị trường (trend-scout), briefs/ là đề bài từng lượt
├── src/                   # code pipeline
│   ├── produce.py         # DÂY CHUYỀN CHÍNH: python -m src.produce run <truyện.txt|.md|.docx>: chia phần → giọng → video → làm lại lỗi → ghép (README.md)
│   ├── studio/            # hình: reel.py (HOẠT HÌNH NỀN NGẪU NHIÊN: đạo diễn random + lõi vẽ pygame không màn hình), puppet.py (ghép đầu + thân diễn viên); công cụ KHO: cutout.py (cắt bảng bộ phận), segment.py (tách lớp tóc sau/đầu/thân), validate_actor.py (kiểm diễn viên), avatar.py (ghép nhân vật từ kho bộ phận), maker/index.html (trang tạo nhân vật)
│   ├── common/            # dùng chung: tts.py (giọng VieNeu + .srt), agy.py (gọi agy), imagegen.py (tạo ảnh qua agy, để bổ sung kho)
│   └── contracts.py       # HỢP ĐỒNG DỮ LIỆU của kho (actor_card, avatar…), mô tả: docs/plans/protocols.md
├── prompts/               # [md] prompt LLM, mỗi prompt 1 file .md (story_narration = làm sạch + lọc vi phạm truyện trước khi đọc giọng; actor_master/expression/pose = tạo diễn viên semi); roles/ = file vai trò của nhân viên agy
├── tests/                 # test_<module>.py; data/ = dữ liệu mẫu cho test (sample_story.txt)
├── scripts/               # công cụ ngoài dây chuyền: setup.sh + setup_models.py (khởi tạo máy mới, Mac/Ubuntu), agy_run.py + agy_permissions.json (giao việc lẻ cho agy), BỔ SUNG KHO: new_actor.py (ảnh gốc → diễn viên), character_maker.py (trang tạo nhân vật, http://localhost:8765), make_extras.py (quần chúng ghép từ kho), make_scene_sheet.py (bảng 3 nền → assets/scenes); hub.py (bảng việc chung giữa các máy = GitHub Issues, docs/plans/collab-protocol.md)
├── assets/                # (dự kiến) KHO CHUNG toàn studio, media thuộc quyền của mình. Kênh và truyện chỉ tham chiếu, không copy
│   ├── music/             # nhạc nền + file giấy phép từng bài
│   ├── sfx/               # hiệu ứng âm thanh (tự tổng hợp hoặc có giấy phép) + LICENSE.md
│   ├── actors/            # ĐOÀN DIỄN VIÊN chibi: roster.yaml (danh sách cần tạo), INDEX.md, <id>/card.yaml, source/, parts/<trang phục>/
│   ├── parts/             # KHO BỘ PHẬN cho phòng thiết kế nhân vật: INDEX.md (mục lục cho AI), parts.yaml, heads/ eyes/ mouths/ extras/ bodies/<bộ đồ>/, source/
│   ├── props/             # THƯ VIỆN ĐẠO CỤ dán vào tay: props.yaml, <id>.png, source/ (bảng gốc)
│   ├── scenes/            # THƯ VIỆN CẢNH (nền): INDEX.md + <id>/card.yaml, master.jpg
│   ├── fonts/             # font được phép dùng thương mại + giấy phép
│   └── thumbnail_template/ # mẫu thumbnail dùng chung
├── channels/              # [md] (dự kiến) MỖI KÊNH một thư mục con = slug không dấu (khoai-tay-review…)
│   └── <channel>/
│       ├── channel.yaml   # tên, handle YouTube/TikTok, giọng TTS, màu, lịch đăng
│       └── brand/         # avatar, ảnh tham chiếu linh vật, banner, logo, intro/outro
├── stories/               # [md] MỖI TRUYỆN = 1 thư mục slug không dấu, do produce.py tạo (không lên git)
│   └── <slug>/
│       ├── tasks.json     # TRẠNG THÁI từng việc (giọng/video từng phần: todo|running|done|failed, số lần thử, lỗi)
│       ├── log.jsonl      # nhật ký từng lần chạy việc (kể cả vết lỗi)
│       ├── source/        # file truyện gốc đã nạp (không sửa)
│       ├── parts/         # NNN.txt: chữ từng phần
│       ├── audio/         # NNN.mp3 + NNN.srt; work_NNN/ = cache từng câu (xoá được)
│       ├── video/         # NNN.mp4 (hình + giọng từng phần), NNN.plan.json (seed hoạt hình)
│       └── output/        # <slug>.mp4 + <slug>.srt + upload.md (bản hoàn chỉnh để đăng)
├── board/                 # (cũ, chỉ còn trên máy Mac) bảng việc của dây chuyền cũ; không dùng nữa
├── tool/                  # [readonly] repo tham khảo clone từ GitHub, không sửa, không import
├── tmp/                   # [md] nháp tạm, xoá bất cứ lúc nào
└── .idea/                 # cấu hình IDE, không động tới
```

## 3. Điều chỉnh cho dự án này
- **Quota:** gói Gemini Pro cá nhân (qua `agy`) dùng thoải mái và ưu tiên trước. Claude Code là gói chung của team, chỉ dùng cho việc quan trọng: điều phối, kế hoạch, duyệt. Chi tiết ở [docs/plans/agent-team.md](docs/plans/agent-team.md).
- **Duyệt nội dung** (hiến pháp §5): `content-reviewer`, chạy Opus 4.6 trên agy. Code và cấu trúc vẫn qua `qa-lead`.
