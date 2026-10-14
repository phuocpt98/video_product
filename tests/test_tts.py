"""Test cách cắt cụm đọc giọng (cách b, chốt 14/10/2026) và làm sạch chữ. Không gọi model."""
from src.common import tts


def test_split_after_closing_quote():
    cs = [c for c, _ in tts.chunks('"Uyển Thanh, cởi váy cưới ra, nhường cho Tiểu Tuyết mặc đi." Bà Trương mở miệng, '
                                   'giọng điệu đương nhiên như thể bảo tôi nhường một quả táo.')]
    assert cs[0].endswith('mặc đi."') and cs[1].startswith("Bà Trương")


def test_short_sentences_merged_long_split():
    cs = tts.chunks("Ừ. Không! Tôi đi đây.\n" + "Một câu rất dài, " * 30 + "hết.")
    assert cs[0][0] == "Ừ. Không! Tôi đi đây."
    assert all(len(c) <= tts.MAX_CHUNK for c, _ in cs)
    assert "".join(c for c, _ in cs[1:]).count("Một câu rất dài") == 30


def test_pauses():
    cs = dict(tts.chunks("Chương 3\nAnh ta đến từ một nơi rất xa, mệt mỏi rã rời… Cô hỏi vì sao anh lại đến đây vào lúc này?\n"
                         "Không ai trả lời cô cả, căn phòng im lặng đến đáng sợ."))
    assert cs["Chương 3."] == tts.PAUSE_HEADING
    assert cs["Anh ta đến từ một nơi rất xa, mệt mỏi rã rời…"] == tts.PAUSE["…"]
    assert cs["Cô hỏi vì sao anh lại đến đây vào lúc này?"] == tts.PAUSE_PARA     # cuối đoạn
    assert cs["Không ai trả lời cô cả, căn phòng im lặng đến đáng sợ."] == tts.PAUSE_PARA


def test_clean():
    t = tts.clean("*** Chương 12 ***\n– Anh đi đi... ko đc đâu!!! 😀 xem https://x.vn [1]\n=====\nNăm 2002, 15/7, 3.000.000đ.")
    assert "*" not in t and "=" not in t and "http" not in t and "[1]" not in t and "😀" not in t
    assert "Anh đi đi… không được đâu!" in t
    assert "Năm 2002, 15/7, 3.000.000đ." in t                       # số/ngày/tiền để VieNeu tự đọc
    assert tts.chunks("*** ***\n\n") == []


def test_srt_roundtrip(tmp_path):
    f = tmp_path / "a.srt"
    tts.write_srt(f, [(0.0, 1.25, "một"), (3661.5, 3662.0, "hai")])
    assert tts.read_srt(f) == [(0.0, 1.25, "một"), (3661.5, 3662.0, "hai")]


def test_clean_keeps_real_words():
    assert tts.clean("Món bít tết rất ngon, cô bít lỗ hổng.") == "Món bít tết rất ngon, cô bít lỗ hổng."
    assert tts.clean("Washington DC. Chữ J viết hoa. J. K. Rowling.") == "Washington DC. Chữ J viết hoa. J. K. Rowling."
    assert tts.clean("Cô Trần Thị Ko-rê.") == "Cô Trần Thị Ko-rê."
    assert tts.clean("Anh ấy (25 tuổi) và tôi (28).") == "Anh ấy (25 tuổi) và tôi (28)."
    assert tts.clean("Ko sao đâu, tớ đc mà.") == "Không sao đâu, tớ được mà."
    assert tts.clean('Ông Ko (Hàn Quốc) đến. Anh Lun và chị Mk. "Ko đâu!" Thật. Ko được.') == \
        'Ông Ko (Hàn Quốc) đến. Anh Lun và chị Mk. "Không đâu!" Thật. Không được.'


def test_no_cut_inside_decimal():
    s = "Một câu rất dài " * 14 + "giá chỉ còn 3,5 triệu đồng thôi " + "và còn kéo dài nữa " * 6 + "hết."
    cs = [c for c, _ in tts.chunks(s)]
    assert any("3,5 triệu" in c for c in cs)
