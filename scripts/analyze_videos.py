"""NGHIÊN CỨU VIDEO của kênh khác bằng Gemini API (tính năng chính thức: đưa link YouTube cho model xem): tìm video
bằng Google Search, phân tích CẤU TRÚC (không chép lời) đoạn đầu video dài hoặc trọn video ngắn, gộp thành báo cáo.
Chỉ để học nhịp/cấu trúc; không tải video, không chép lời thoại.

python scripts/analyze_videos.py "<chủ đề tìm>" --out docs/research/<file>.md [--n 6] [--shorts] [--seconds 360]
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common.pool import _key  # noqa: E402

key = _key("GEMINI_API_KEY")
def call(model, body, timeout=300):
    req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', json.dumps(body).encode(),
        {'Content-Type':'application/json','x-goog-api-key':key})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())
def text(r):
    c=r.get('candidates',[{}])[0]
    return ''.join(p.get('text','') for p in c.get('content',{}).get('parts',[])), c.get('finishReason'), c.get('groundingMetadata',{})


def resolve(u):
    import urllib.request
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    op = urllib.request.build_opener(NoRedir)
    try:
        op.open(urllib.request.Request(u, method="HEAD"), timeout=20)
    except urllib.error.HTTPError as e:
        return e.headers.get("Location")
    return None


def find_videos(query, n=6):
    body = {"contents": [{"parts": [{"text": query}]}], "tools": [{"google_search": {}}]}
    t, f, g = text(call('gemini-2.5-flash', body))
    urls = [resolve(ch["web"]["uri"]) for ch in g.get("groundingChunks", []) if "youtube" in ch.get("web", {}).get("title", "")]
    return [u for u in urls if u and "watch" in u][:n]


ASK = """Bạn phân tích CẤU TRÚC (không chép lời) 6 phút đầu của video truyện drama này. Trả lời ngắn gọn bằng tiếng Việt:
1. Tiêu đề/kênh (nếu thấy), hình thức (audio + ảnh tĩnh / truyện tranh động / hoạt hình / người thật), có phụ đề không.
2. 30 GIÂY ĐẦU làm gì: mở bằng cao trào/cảnh sau này (flash-forward) rồi quay lại? câu hỏi? lời người kể giới thiệu kênh? tóm tắt? (tóm ý, KHÔNG chép nguyên câu)
3. Mốc thời gian (mm:ss) chuyển từ đoạn mở sang kể từ đầu (nếu có), lời chào/kêu gọi đăng ký đặt ở đâu.
4. Nhịp: bao lâu thì có mâu thuẫn đầu tiên, có đổi cảnh/hình thường xuyên không.
5. Kỹ thuật giữ chân đáng học (3–5 ý).
"""


def analyze(url, end_s=360):
    body = {"contents": [{"parts": [
        {"file_data": {"file_uri": url}, "video_metadata": {"start_offset": "0s", "end_offset": f"{end_s}s"}},
        {"text": ASK}]}],
        "generationConfig": {"media_resolution": "MEDIA_RESOLUTION_LOW"}}
    t, f, _ = text(call('gemini-2.5-flash', body, timeout=600))
    return t

SHORT_ASK = """Phân tích CẤU TRÚC (không chép lời) video ngắn này (đoạn mồi truyện drama). Tiếng Việt, ngắn gọn:
1. Dài bao lâu, hình thức, chữ lớn trên màn hình ghi ý gì.
2. Mở đầu bằng gì (cao trào? câu sốc? câu hỏi?), mấy giây đầu.
3. Có quay lại kể từ đầu không, ở giây nào.
4. KẾT ở đâu: dừng trước kết quả (gây tò mò) hay đã lộ kết; câu kêu gọi xem tiếp là gì (tóm ý).
5. 3 kỹ thuật đáng học."""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--shorts", action="store_true", help="tìm video ngắn (Shorts), xem trọn")
    ap.add_argument("--seconds", type=int, default=360)
    a = ap.parse_args()
    kind = "YouTube Shorts (dưới 3 phút)" if a.shorts else "video YouTube dài 20-60 phút"
    urls = find_videos(f"Dùng Google Search tìm {kind} tiếng Việt: {a.topic}. Nhiều lượt xem.", a.n)
    parts = [f"# Phân tích video: {a.topic} ({'Shorts' if a.shorts else 'video dài'})", "",
             f"Gemini API xem trực tiếp link YouTube ({'trọn video' if a.shorts else f'{a.seconds} giây đầu'}, độ phân "
             "giải thấp). Chỉ phân tích cấu trúc, không chép lời.", ""]
    for u in urls:
        try:
            t = analyze(u, 180 if a.shorts else a.seconds) if not a.shorts else analyze_short(u)
        except urllib.error.HTTPError as e:
            t = f"(lỗi HTTP {e.code})"
        parts += [f"## {u}", "", t.strip(), ""]
        print("xong", u, flush=True)
    pathlib.Path(ROOT / a.out).write_text("\n".join(parts), encoding="utf-8")
    print("Ghi", a.out)
    return 0


def analyze_short(url):
    body = {"contents": [{"parts": [{"file_data": {"file_uri": url}}, {"text": SHORT_ASK}]}],
            "generationConfig": {"media_resolution": "MEDIA_RESOLUTION_LOW"}}
    return text(call("gemini-2.5-flash", body, timeout=600))[0]


if __name__ == "__main__":
    raise SystemExit(main())
