import io

from PIL import Image

from frontend.ui import state


class FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def __setattr__(self, name, value):
        self[name] = value


def test_save_embed_result_records_download_without_credentials(monkeypatch):
    session_state = FakeSessionState()
    monkeypatch.setattr(state.st, "session_state", session_state)
    stego_image = Image.new("RGB", (8, 6), color=(20, 40, 60))

    state.save_embed_result(
        stego_image,
        {
            "cover_filename": "cover.png",
            "filename": "secret.txt",
            "payload_type": "Text",
            "payload_size": 12,
            "container_size": 90,
            "cover_width": 8,
            "cover_height": 6,
            "mse": 0.25,
            "psnr": 54.15,
            "password": "must-not-be-recorded",
            "stego_key": "must-not-be-recorded",
        }
    )

    history_item = session_state["embed_history"][0]
    with Image.open(io.BytesIO(history_item["image_bytes"])) as downloaded_image:
        assert downloaded_image.size == (8, 6)
        assert downloaded_image.format == "PNG"

    assert history_item["cover_filename"] == "cover.png"
    assert history_item["payload_filename"] == "secret.txt"
    assert history_item["payload_size"] == 12
    assert history_item["mse"] == 0.25
    assert history_item["psnr"] == 54.15
    assert "password" not in history_item
    assert "stego_key" not in history_item


def test_embedding_history_is_limited_and_can_be_cleared(monkeypatch):
    session_state = FakeSessionState()
    monkeypatch.setattr(state.st, "session_state", session_state)

    for index in range(state.EMBED_HISTORY_LIMIT + 2):
        state.save_embed_result(
            Image.new("RGB", (2, 2), color=(index, 0, 0)),
            {"filename": f"payload-{index}.bin", "payload_size": index}
        )

    assert len(session_state["embed_history"]) == state.EMBED_HISTORY_LIMIT
    assert session_state["embed_history"][0]["payload_filename"] == "payload-11.bin"
    assert session_state["embed_history"][-1]["payload_filename"] == "payload-2.bin"

    state.clear_embedding_history()
    assert session_state["embed_history"] == []