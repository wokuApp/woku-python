from __future__ import annotations

import io

import httpx
import pytest
import respx

from woku import AsyncWoku, Woku, WokuAPIError

BASE = "http://api.test"


@respx.mock
def test_image_upload_has_bytes_filename_boundary_and_one_auth_header() -> None:
    route = respx.post(f"{BASE}/v1/woku-media").mock(
        return_value=httpx.Response(
            201, json={"fileId": "f1", "filename": "test.webp", "type": "image"}
        )
    )
    stream = io.BytesIO(b"\x00\x7f\x80\xff")
    with Woku(
        api_key="sk_test",
        base_url=BASE,
        default_headers={"content-type": "application/json"},
    ) as sdk:
        result = sdk.media.upload(
            stream, filename="image.png", content_type="image/png"
        )
    request = route.calls.last.request
    assert request.headers.get_list("authorization") == ["Bearer sk_test"]
    assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'filename="image.png"' in request.content
    assert b"\x00\x7f\x80\xff" in request.content
    assert result["fileId"] == "f1"
    assert not stream.closed


@respx.mock
async def test_async_mp4_upload_and_413_mapping() -> None:
    route = respx.post(f"{BASE}/v1/woku-media").mock(
        return_value=httpx.Response(
            413, headers={"x-request-id": "media-limit"}, json={"message": "too large"}
        )
    )
    async with AsyncWoku(api_key="sk_test", base_url=BASE) as sdk:
        with pytest.raises(WokuAPIError) as error:
            await sdk.media.upload(
                b"mp4", filename="video.mp4", content_type="video/mp4"
            )
    assert error.value.status == 413
    assert error.value.code == "payload_too_large"
    assert error.value.request_id == "media-limit"
    assert route.call_count == 1


@respx.mock
def test_upload_is_not_retried_even_with_a_caller_key() -> None:
    route = respx.post(f"{BASE}/v1/woku-media").mock(
        return_value=httpx.Response(503, json={})
    )
    with Woku(api_key="sk_test", base_url=BASE) as sdk:
        with pytest.raises(WokuAPIError):
            sdk.media.upload(
                b"bytes",
                filename="image.png",
                options={"idempotency_key": "upload1", "max_retries": 3},
            )
    assert route.call_count == 1
