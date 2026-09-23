from __future__ import annotations

from typing import Any

from dify_plugin.entities.invoke_message import InvokeMessage

from tools.create_avatar_session import CreateAvatarSessionTool
from tools.create_editing_session import CreateEditingSessionTool
from tools.get_live_session import GetLiveSessionTool
from tools.list_voices import ListVoicesTool


class FakeResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._data


def variable_values(messages) -> dict[str, Any]:
    return {
        message.message.variable_name: message.message.variable_value
        for message in messages
        if message.type == InvokeMessage.MessageType.VARIABLE
    }


def json_values(messages) -> list[Any]:
    return [
        message.message.json_object
        for message in messages
        if message.type == InvokeMessage.MessageType.JSON
    ]


def assert_no_text_messages(messages) -> None:
    assert all(message.type != InvokeMessage.MessageType.TEXT for message in messages)


def test_avatar_tool_passes_s2_parameters_and_emits_structured_contract(monkeypatch) -> None:
    calls = []
    response = {
        "live": {
            "id": "avatar-live",
            "status": "waiting",
            "live_duration": 7200,
            "call_mode": "video",
        },
        "rtc": {
            "app_id": "app-1",
            "channel_id": "channel-1",
            "user_id": "user-1",
            "token": "rtc-secret",
            "token_expire_at": "1780000600",
        },
    }

    def fake_request(method: str, url: str, **kwargs: Any) -> FakeResponse:
        calls.append((method, url, kwargs))
        return FakeResponse(response)

    monkeypatch.setattr("requests.request", fake_request)
    tool = CreateAvatarSessionTool.from_credentials(
        {"vidu_api_key": "vda_test", "region": "cn"}
    )
    messages = list(
        tool._invoke(
            {
                "persona": "Friendly guide",
                "image_uri": "https://example.com/avatar.png",
                "name": "Tina",
                "voice": "Cindy",
                "call_mode": "video",
                "persona_enhance": True,
            }
        )
    )

    expected = {
        "live_id": "avatar-live",
        "status": "waiting",
        "live_duration": 7200,
        "call_mode": "video",
        "rtc": {
            "app_id": "app-1",
            "channel_id": "channel-1",
            "user_id": "user-1",
            "token": "rtc-secret",
            "token_expire_at": "1780000600",
        },
    }
    assert variable_values(messages) == expected
    assert json_values(messages) == [expected]
    assert_no_text_messages(messages)
    assert calls[0][1].endswith("/live/s_avatar/realtime")
    assert calls[0][2]["json"]["avatar"]["persona_enhance"] is True


def test_editing_tool_emits_render_identity_and_control_secret_only_structurally(monkeypatch) -> None:
    response = {
        "live": {
            "id": "editing-live",
            "status": "waiting",
            "live_duration": 3600,
        },
        "rtc": {
            "app_id": "app-2",
            "channel_id": "channel-2",
            "user_id": "user-2",
            "token": "editing-rtc-secret",
            "token_expire_at": "1780000700",
        },
        "render_uid": "render-user",
        "client_secret": "control-secret",
    }
    monkeypatch.setattr(
        "requests.request", lambda *_args, **_kwargs: FakeResponse(response)
    )
    tool = CreateEditingSessionTool.from_credentials(
        {"vidu_api_key": "vda_test", "region": "global"}
    )
    messages = list(
        tool._invoke(
            {
                "image_url": "https://example.com/reference.png",
                "editing_type": "background_replacement",
            }
        )
    )

    expected = {
        "live_id": "editing-live",
        "status": "waiting",
        "live_duration": 3600,
        "render_uid": "render-user",
        "client_secret": "control-secret",
        "rtc": {
            "app_id": "app-2",
            "channel_id": "channel-2",
            "user_id": "user-2",
            "token": "editing-rtc-secret",
            "token_expire_at": "1780000700",
        },
    }
    assert variable_values(messages) == expected
    assert json_values(messages) == [expected]
    assert_no_text_messages(messages)


def test_editing_tool_stabilizes_missing_client_secret(monkeypatch) -> None:
    response = {
        "live": {"id": "editing-live", "status": "waiting", "live_duration": 3600},
        "rtc": {
            "app_id": "app-2",
            "channel_id": "channel-2",
            "user_id": "user-2",
            "token": "editing-rtc-secret",
            "token_expire_at": "1780000700",
        },
        "render_uid": "render-user",
    }
    monkeypatch.setattr(
        "requests.request", lambda *_args, **_kwargs: FakeResponse(response)
    )
    tool = CreateEditingSessionTool.from_credentials(
        {"vidu_api_key": "vda_test", "region": "cn"}
    )

    messages = list(
        tool._invoke(
            {
                "image_url": "https://example.com/reference.png",
                "editing_type": "style_transfer",
            }
        )
    )

    assert variable_values(messages)["client_secret"] == ""


def test_query_tool_emits_complete_status_and_billing_contract(monkeypatch) -> None:
    response = {
        "live": {
            "id": "live-1",
            "status": "ended",
            "live_duration": 600,
            "call_mode": "video",
            "billed_seconds": 18,
            "credits_cost": 27,
            "created_at": "created",
            "started_at": "started",
            "ended_at": "ended",
            "trace_id": "trace-1",
        }
    }
    monkeypatch.setattr(
        "requests.request", lambda *_args, **_kwargs: FakeResponse(response)
    )
    tool = GetLiveSessionTool.from_credentials(
        {"vidu_api_key": "vda_test", "region": "cn"}
    )

    messages = list(tool._invoke({"live_id": "live-1"}))

    assert variable_values(messages) == {
        "live_id": "live-1",
        "status": "ended",
        "live_duration": 600,
        "call_mode": "video",
        "billed_seconds": 18,
        "credits_cost": 27,
        "created_at": "created",
        "started_at": "started",
        "ended_at": "ended",
        "trace_id": "trace-1",
    }
    assert_no_text_messages(messages)


def test_query_tool_allows_missing_optional_fields(monkeypatch) -> None:
    monkeypatch.setattr(
        "requests.request",
        lambda *_args, **_kwargs: FakeResponse(
            {"live": {"id": "live-1", "status": "waiting"}}
        ),
    )
    tool = GetLiveSessionTool.from_credentials(
        {"vidu_api_key": "vda_test", "region": "cn"}
    )

    values = variable_values(list(tool._invoke({"live_id": "live-1"})))

    assert values["billed_seconds"] is None
    assert values["credits_cost"] is None
    assert values["created_at"] == ""
    assert values["started_at"] == ""
    assert values["ended_at"] == ""
    assert values["trace_id"] == ""


def test_voice_tool_emits_custom_voice_array(monkeypatch) -> None:
    voices = [{"voice": "my_voice", "provider": "qwen_omni"}]
    monkeypatch.setattr(
        "requests.request",
        lambda *_args, **_kwargs: FakeResponse({"voices": voices}),
    )
    tool = ListVoicesTool.from_credentials(
        {"vidu_api_key": "vda_test", "region": "global"}
    )

    messages = list(tool._invoke({}))

    assert variable_values(messages) == {"voices": voices}
    assert json_values(messages) == [{"voices": voices}]
    assert_no_text_messages(messages)
