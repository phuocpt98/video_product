# video_reup: kênh truyện YouTube + TikTok

Cập nhật: 25/9/2026

## 0. Lối vào (đọc theo thứ tự, đã tự nạp)
- Studio, bạn là ai, luật lõi: @.claude/company/README.md và @.claude/company/constitution.md
- Mục lục tài liệu dự án: @docs/README.md
- Đầu mỗi phiên: đọc [docs/progress.md](docs/progress.md). Các file khác chỉ mở khi việc cần.
- Máy mới: làm theo [docs/setup.md](docs/setup.md) (`bash scripts/setup.sh`).

## 1. Dự án
Kênh review và kể truyện tiếng Việt (đô thị, hệ thống, trọng sinh). Pipeline biến **1 truyện chữ** thành **video FULL YouTube + clip TikTok + thumbnail**. Kế hoạch ở [docs/plans/](docs/plans/). Quyết định ở [docs/decisions.md](docs/decisions.md).

**Ràng buộc riêng của dự án:**
- Tránh chính sách "inauthentic content" của YouTube:
  - kịch bản **viết lại** theo cách 拆书 + 仿写, có lời bình người kể
  - hình ảnh **tự tạo**
  - không dùng clip, gameplay hay phim của người khác
- Chỉ dùng công cụ, giọng và trọng số **cho phép dùng thương mại**. edge-tts chỉ để thử nghiệm.
- Repo trong `tool/` phần lớn là GPL/AGPL hoặc không có giấy phép: **chỉ lấy ý tưởng**, tự viết code và prompt.
- Không lặp lỗi của repo cũ `~/Documents/project/personal/tiktok_content`: cắt clip kênh khác, chạy theo số lượng, mỗi video một script.

**Môi trường:** Mac Apple Silicon, Python 3.11+, ffmpeg (mã hoá phần cứng `h264_videotoolbox`).

## 2. Bản đồ thư mục

Nguồn duy nhất, hook đọc khối dưới đây. Ý nghĩa các đánh dấu và quy tắc thêm vị trí: [files-and-docs.md](.claude/company/playbooks/files-and-docs.md).

```
video_reup/
├── CLAUDE.md              # lối vào tầng dự án (file này)
├── README.md              # giới thiệu ngắn cho GitHub (github.com/phuocpt98/video_product)
├── .gitignore             # repo GitHub chỉ giữ cấu trúc, quy tắc, code, thư viện hình (không truyện, board, media)
├── config.yaml            # cấu hình chung của studio: thang model từng vai trò (agents:), mặc định pipeline
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
│   ├── studio/            # phòng dựng rối cắt ghép: cutout.py (cắt bảng bộ phận), stage.py (dựng cảnh → video), direct.py (dàn cảnh: nhãn AI + luật từ khoá), tagger.py (đạo diễn gắn nhãn), actions.py (hành động + hiệu ứng dùng chung), avatar.py (ghép nhân vật từ kho bộ phận), maker/index.html (trang tạo nhân vật)
│   ├── common/            # dùng chung: agy.py (gọi agy), pool.py (nhóm nguồn LLM miễn phí), llm.py (GLM), imagegen.py (tạo ảnh qua agy), tts.py (VieNeu + .srt), render.py (khung, ghép, video)
│   ├── board.py           # BẢNG VIỆC giữa các phòng: python -m src.board add-render|run|list|done
│   ├── contracts.py       # HỢP ĐỒNG DỮ LIỆU giữa các phòng/công cụ/agent (mô tả: docs/plans/protocols.md)
│   └── run.py             # python -m src.run <slug> --chapters 1-10 [--render]: dây chuyền theo lô (docs/plans/story-bible.md)
├── prompts/               # [md] prompt LLM, mỗi prompt 1 file .md, tên theo bước; roles/ = file vai trò của nhân viên agy
├── tests/                 # test_<module>.py
├── scripts/               # công cụ ngoài pipeline: setup.sh + setup_models.py (khởi tạo máy mới), agy_run.py, agy_permissions.json, record_game.py, make_thumbnail.py, make_actor.py, make_props.py, make_roster.py, make_parts.py, make_extras.py (quần chúng ghép từ kho), character_maker.py (máy chủ trang tạo nhân vật, http://localhost:8765), make_tiktok.py (đoạn mồi TikTok, --auto: AI chọn khúc theo công thức), drama_pipeline.py (1 lệnh từ mô-típ đến video), make_upload.py (gói đăng YouTube: .srt gộp, thumbnail, upload.md)
├── data/                  # [md] dữ liệu nhỏ dùng chung toàn studio: actions.yaml (luật từ khoá → biểu cảm/tư thế/đạo cụ), tracking.csv (dự kiến)
├── assets/                # (dự kiến) KHO CHUNG toàn studio, media thuộc quyền của mình. Kênh và truyện chỉ tham chiếu, không copy
│   ├── clips/             # clip nền lặp tự tạo (gameplay game_ideal…) + tags.json
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
│       ├── style_card.md  # thẻ phong cách giọng kể của kênh
│       ├── end_lines.json # kho câu chèn và câu kết của kênh
│       └── brand/         # avatar, ảnh tham chiếu linh vật, banner, logo, intro/outro
├── stories/               # [md] (dự kiến) MỖI TRUYỆN = 1 DỰ ÁN, thư mục con = slug không dấu
│   └── <slug>/
│       ├── story.yaml     # thuộc kênh nào, nguồn, trạng thái, model đã dùng, quyết định riêng của truyện
│       ├── assets/        # tài nguyên riêng của truyện: ảnh tham chiếu nhân vật…
│       ├── source/        # truyện chữ gốc (không sửa)
│       ├── chapters/      # 001.txt…
│       ├── outline/       # chapter_cards/, segments/, setting.md, character_state.md
│       ├── bible/         # SỔ TAY TRUYỆN (nhóm trưởng giữ): bible.md, characters.md, ledger.md, CHANGELOG.md, arcs/KK.md, checks/KK.md
│       ├── cast.yaml      # MỤC LỤC truyện → thư viện: nhân vật → diễn viên + trang phục, nền + từ khoá, nền mở đầu chương
│       ├── storyboard/    # NNN.yaml kịch bản cảnh do direct.py sinh (sửa tay được), stage.py dựng
│       ├── rename_map.json
│       ├── script/        # 001.txt…
│       ├── audio/
│       ├── render/        # file trung gian, xoá được
│       └── output/        # video_full.mp4, tiktok_*.mp4, thumbnail, description.txt
├── board/                 # bảng việc: tasks/<id>.yaml, events.jsonl, inbox/ (ảnh Người sáng lập trả lời việc need-image), image_queue.yaml (hàng đợi tạo ảnh theo ưu tiên, scripts/image_queue.sh chạy)
├── tool/                  # [readonly] repo tham khảo clone từ GitHub, không sửa, không import
├── tmp/                   # [md] nháp tạm, xoá bất cứ lúc nào
└── .idea/                 # cấu hình IDE, không động tới
```

## 3. Điều chỉnh cho dự án này
- **Quota:** gói Gemini Pro cá nhân (qua `agy`) dùng thoải mái và ưu tiên trước. Claude Code là gói chung của team, chỉ dùng cho việc quan trọng: điều phối, kế hoạch, duyệt. Chi tiết ở [docs/plans/agent-team.md](docs/plans/agent-team.md).
- **Duyệt nội dung** (hiến pháp §5): `content-reviewer`, chạy Opus 4.6 trên agy. Code và cấu trúc vẫn qua `qa-lead`.
