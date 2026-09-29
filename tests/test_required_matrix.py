"""End-to-end quality and recovery checks for the required 5x3 matrix."""

from pathlib import Path

import pytest

from backend.image.io import validate_and_load_cover_image
from backend.pipeline import embed_pipeline, extract_pipeline


COVER_IMAGE_PATHS = tuple(sorted((
    Path(__file__).parents[1] / "test_t18_images"
).glob("*.png")))
PAYLOAD_SIZES = (32, 512, 2048)
MATRIX_CASES = [
    pytest.param(image_path, payload_size, id=f"{image_path.stem}-{payload_size}B")
    for image_path in COVER_IMAGE_PATHS
    for payload_size in PAYLOAD_SIZES
]


def test_required_matrix_contains_five_images_and_three_payload_sizes():
    assert len(COVER_IMAGE_PATHS) == 5
    assert len(PAYLOAD_SIZES) == 3
    assert len(MATRIX_CASES) == 15


@pytest.mark.parametrize(("image_path", "payload_size"), MATRIX_CASES)
def test_required_matrix_embed_extract_and_quality(image_path, payload_size):
    cover_image, image_metadata = validate_and_load_cover_image(image_path.read_bytes())
    cover_image.load()
    payload = bytes((index * 31 + payload_size) % 256 for index in range(payload_size))
    password = "matrix_test_password"
    stego_key = "matrix_test_stego_key"

    stego_image, embed_metadata = embed_pipeline(
        cover_image,
        payload,
        password,
        stego_key,
        filename=f"payload_{payload_size}.bin",
        mime_type="application/octet-stream"
    )
    recovered_payload, extract_metadata = extract_pipeline(
        stego_image,
        password,
        stego_key
    )

    assert recovered_payload == payload
    assert embed_metadata["payload_size"] == payload_size
    assert embed_metadata["mse"] is not None
    assert embed_metadata["psnr"] >= 30.0
    assert extract_metadata["plaintext_size"] == payload_size
    assert image_metadata["width"] * image_metadata["height"] > 0