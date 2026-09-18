from pathlib import Path

from studio.adapters.musetalk_mac import MuseTalkMacAdapter, _decode_video, _encode_file


def test_base_url_normalized():
    adapter = MuseTalkMacAdapter("http://127.0.0.1:8000/")
    assert adapter.base_url == "http://127.0.0.1:8000"


def test_file_base64_round_trip(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"abc123")
    encoded = _encode_file(source)

    output = tmp_path / "out.bin"
    _decode_video(encoded, output)
    assert output.read_bytes() == b"abc123"
