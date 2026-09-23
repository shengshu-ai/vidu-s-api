from __future__ import annotations

from typing import Any

import pytest
import requests

from provider.vidu_client import ViduApiError, ViduClient


def session_response(*, render_uid: str | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "live": {
            "id": "995200676634042368",
            "status": "waiting",
            "live_duration": 7200,
            "call_mode": "video",
        },
        "rtc": {
            "app_id": "app-id",
            "channel_id": "channel-id",
            "user_id": "user-id",
            "token": "rtc-secret",
            "token_expire_at": "1789000000",
        },
    }
    if render_uid is not None:
        data["render_uid"] = render_uid
    return data


def test_normalizes_api_key_and_selects_china_host() -> None:
    client = ViduClient(api_key=" vda_secret ", region=" CN ", request=lambda *_a, **_k: {})

    assert client.authorization == "Token vda_secret"
    assert client.api_base_url == "https://api.vidu.cn"


def test_preserves_token_prefix_and_selects_global_host() -> None:
    client = ViduClient(
        api_key="Token vda_secret",
        region="global",
        request=lambda *_a, **_k: {},
    )

    assert client.authorization == "Token vda_secret"
    assert client.api_base_url == "https://api.vidu.com"


@pytest.mark.parametrize("api_key", ["", "secret", "Bearer vda_secret"])
def test_rejects_invalid_api_keys(api_key: str) -> None:
    with pytest.raises(ValueError, match="VIDU API key"):
        ViduClient(api_key=api_key, region="cn")


def test_rejects_unknown_region() -> None:
    with pytest.raises(ValueError, match="region"):
        ViduClient(api_key="vda_secret", region="us")


def test_creates_avatar_session_with_s2_route_and_payload() -> None:
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def request(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        calls.append((method, url, kwargs))
        return session_response()

    client = ViduClient(api_key="vda_secret", region="cn", request=request)
    result = client.create_avatar_session(
        persona=" Friendly guide ",
        image_uri=" https://example.com/avatar.png ",
        name=" Tina ",
        voice=" Cindy ",
        call_mode="video",
        persona_enhance=True,
    )

    assert result["live"]["id"] == "995200676634042368"
    assert calls == [
        (
            "POST",
            "https://api.vidu.cn/live/s_avatar/realtime",
            {
                "headers": {
                    "Authorization": "Token vda_secret",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                "json": {
                    "call_mode": "video",
                    "character_id": "1",
                    "avatar": {
                        "persona": "Friendly guide",
                        "image_uri": "https://example.com/avatar.png",
                        "persona_enhance": True,
                        "name": "Tina",
                        "voice": "Cindy",
                    },
                },
                "timeout": 60,
            },
        )
    ]


def test_avatar_omits_empty_optional_strings() -> None:
    captured: dict[str, Any] = {}

    def request(_method: str, _url: str, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs["json"])
        return session_response()

    client = ViduClient(api_key="vda_secret", region="cn", request=request)
    client.create_avatar_session(
        persona="Guide",
        image_uri="https://example.com/avatar.png",
        name="  ",
        voice="",
        call_mode="audio",
    )

    assert captured["call_mode"] == "audio"
    assert "name" not in captured["avatar"]
    assert "voice" not in captured["avatar"]
    assert captured["avatar"]["persona_enhance"] is False


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"persona": " "}, "persona is required"),
        ({"persona": "x" * 50001}, "50000"),
        ({"image_uri": " "}, "image_uri is required"),
        ({"call_mode": "screen"}, "call_mode"),
    ],
)
def test_validates_avatar_inputs(overrides: dict[str, str], message: str) -> None:
    parameters = {
        "persona": "Guide",
        "image_uri": "https://example.com/avatar.png",
        "call_mode": "video",
    }
    parameters.update(overrides)
    client = ViduClient(api_key="vda_secret", region="cn", request=lambda *_a, **_k: {})

    with pytest.raises(ValueError, match=message):
        client.create_avatar_session(**parameters)


@pytest.mark.parametrize(
    "editing_type",
    [
        "style_transfer",
        "virtual_tryon",
        "subject_replacement",
        "background_replacement",
    ],
)
def test_creates_editing_session_for_supported_types(editing_type: str) -> None:
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def request(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        calls.append((method, url, kwargs))
        return session_response(render_uid="render-user")

    client = ViduClient(api_key="vda_secret", region="global", request=request)
    result = client.create_editing_session(
        image_url=" https://example.com/reference.png ",
        editing_type=editing_type,
    )

    assert result["render_uid"] == "render-user"
    assert calls[0][0:2] == (
        "POST",
        "https://api.vidu.com/live/s_editing/realtime",
    )
    assert calls[0][2]["json"] == {
        "image_url": "https://example.com/reference.png",
        "editing_type": editing_type,
    }
    assert calls[0][2]["timeout"] == 60


def test_validates_editing_inputs_and_render_uid() -> None:
    client = ViduClient(api_key="vda_secret", region="cn", request=lambda *_a, **_k: {})
    with pytest.raises(ValueError, match="image_url is required"):
        client.create_editing_session(image_url=" ", editing_type="style_transfer")
    with pytest.raises(ValueError, match="editing_type"):
        client.create_editing_session(image_url="image", editing_type="unknown")

    missing_render = ViduClient(
        api_key="vda_secret",
        region="cn",
        request=lambda *_a, **_k: session_response(),
    )
    with pytest.raises(ValueError, match="render_uid"):
        missing_render.create_editing_session(
            image_url="https://example.com/reference.png",
            editing_type="style_transfer",
        )


def test_queries_encoded_live_id_and_lists_voices() -> None:
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def request(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        calls.append((method, url, kwargs))
        return {"voices": []}

    client = ViduClient(api_key="vda_secret", region="cn", request=request)
    client.get_live_session("live/id with spaces")
    client.list_voices(timeout=10)

    assert calls[0][0:2] == (
        "GET",
        "https://api.vidu.cn/live/v1/lives/live%2Fid%20with%20spaces",
    )
    assert calls[1][0:2] == (
        "GET",
        "https://api.vidu.cn/live/v1/voices",
    )
    assert calls[1][2]["timeout"] == 10


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data.pop("live"),
        lambda data: data["live"].__setitem__("id", ""),
        lambda data: data["live"].__setitem__("status", ""),
        lambda data: data["live"].__setitem__("live_duration", 0),
        lambda data: data.pop("rtc"),
        lambda data: data["rtc"].__setitem__("token", ""),
    ],
)
def test_rejects_incomplete_creation_responses(mutate) -> None:
    data = session_response()
    mutate(data)
    client = ViduClient(api_key="vda_secret", region="cn", request=lambda *_a, **_k: data)

    with pytest.raises(ValueError, match="Vidu response"):
        client.create_avatar_session(
            persona="Guide",
            image_uri="https://example.com/avatar.png",
        )


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        data: Any = None,
        json_error: Exception | None = None,
    ) -> None:
        self.status_code = status_code
        self._data = data
        self._json_error = json_error

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> Any:
        if self._json_error:
            raise self._json_error
        return self._data


def test_default_request_preserves_timeout_and_sanitizes_failures(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def timeout_request(*args: Any, **kwargs: Any) -> FakeResponse:
        captured.update({"args": args, "kwargs": kwargs})
        raise requests.Timeout("vda_secret timed out")

    monkeypatch.setattr(requests, "request", timeout_request)
    client = ViduClient(api_key="vda_secret", region="cn")
    with pytest.raises(requests.Timeout):
        client.list_voices(timeout=7)
    assert captured["kwargs"]["timeout"] == 7

    monkeypatch.setattr(
        requests,
        "request",
        lambda *_a, **_k: FakeResponse(status_code=500, data={"token": "rtc-secret"}),
    )
    with pytest.raises(ViduApiError) as http_error:
        client.list_voices()
    assert "vda_secret" not in str(http_error.value)
    assert "rtc-secret" not in str(http_error.value)

    monkeypatch.setattr(
        requests,
        "request",
        lambda *_a, **_k: FakeResponse(json_error=ValueError("client_secret")),
    )
    with pytest.raises(ViduApiError) as json_error:
        client.list_voices()
    assert "client_secret" not in str(json_error.value)

    monkeypatch.setattr(
        requests,
        "request",
        lambda *_a, **_k: FakeResponse(data=["not", "an", "object"]),
    )
    with pytest.raises(ViduApiError, match="invalid response"):
        client.list_voices()
