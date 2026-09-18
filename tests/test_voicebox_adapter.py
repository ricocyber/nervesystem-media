from studio.adapters.voicebox import VoiceboxAdapter


def test_voicebox_base_url_is_normalized():
    adapter = VoiceboxAdapter("http://127.0.0.1:17493/")
    assert adapter.base_url == "http://127.0.0.1:17493"
