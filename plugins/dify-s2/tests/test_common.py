from __future__ import annotations

from tools.common import (
    client_from_runtime,
    compact_avatar_response,
    compact_editing_response,
    compact_live_query,
)


def session_data() -> dict:
    return {
        "live": {
            "id": "live-1",
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


def test_client_from_runtime_preserves_provider_credentials() -> None:
    client = client_from_runtime({"vidu_api_key": "vda_test", "region": "global"})

    assert client.authorization == "Token vda_test"
    assert client.api_base_url == "https://api.vidu.com"


def test_compacts_avatar_response_to_stable_contract() -> None:
    assert compact_avatar_response(session_data()) == {
        "live_id": "live-1",
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


def test_compacts_editing_response_with_optional_client_secret() -> None:
    data = session_data()
    data.update({"render_uid": "render-user", "client_secret": "control-secret"})

    assert compact_editing_response(data) == {
        "live_id": "live-1",
        "status": "waiting",
        "live_duration": 7200,
        "render_uid": "render-user",
        "client_secret": "control-secret",
        "rtc": {
            "app_id": "app-1",
            "channel_id": "channel-1",
            "user_id": "user-1",
            "token": "rtc-secret",
            "token_expire_at": "1780000600",
        },
    }

    data.pop("client_secret")
    assert compact_editing_response(data)["client_secret"] == ""


def test_compacts_live_query_with_nullable_optional_fields() -> None:
    result = compact_live_query(
        {
            "live": {
                "id": "live-1",
                "status": "ended",
                "live_duration": 600,
                "call_mode": "video",
                "billed_seconds": 18,
                "credits_cost": 27,
                "created_at": "2026-09-16T10:00:00Z",
                "trace_id": "trace-1",
            }
        },
        "fallback-id",
    )

    assert result == {
        "live_id": "live-1",
        "status": "ended",
        "live_duration": 600,
        "call_mode": "video",
        "billed_seconds": 18,
        "credits_cost": 27,
        "created_at": "2026-09-16T10:00:00Z",
        "started_at": "",
        "ended_at": "",
        "trace_id": "trace-1",
    }
