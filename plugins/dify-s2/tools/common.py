from __future__ import annotations

from typing import Any

from provider.vidu_client import ViduClient


def client_from_runtime(credentials: dict[str, Any]) -> ViduClient:
    return ViduClient(
        api_key=credentials.get("vidu_api_key", ""),
        region=credentials.get("region", "cn"),
    )


def compact_rtc(data: dict[str, Any]) -> dict[str, Any]:
    rtc = data.get("rtc", {})
    return {
        "app_id": rtc.get("app_id", ""),
        "channel_id": rtc.get("channel_id", ""),
        "user_id": rtc.get("user_id", ""),
        "token": rtc.get("token", ""),
        "token_expire_at": rtc.get("token_expire_at", ""),
    }


def compact_avatar_response(data: dict[str, Any]) -> dict[str, Any]:
    live = data.get("live", {})
    return {
        "live_id": live.get("id", ""),
        "status": live.get("status", ""),
        "live_duration": live.get("live_duration"),
        "call_mode": live.get("call_mode", ""),
        "rtc": compact_rtc(data),
    }


def compact_editing_response(data: dict[str, Any]) -> dict[str, Any]:
    live = data.get("live", {})
    return {
        "live_id": live.get("id", ""),
        "status": live.get("status", ""),
        "live_duration": live.get("live_duration"),
        "render_uid": data.get("render_uid", ""),
        "client_secret": data.get("client_secret", ""),
        "rtc": compact_rtc(data),
    }


def compact_live_query(data: dict[str, Any], live_id: str) -> dict[str, Any]:
    live = data.get("live", {})
    return {
        "live_id": live.get("id", live_id),
        "status": live.get("status", ""),
        "live_duration": live.get("live_duration"),
        "call_mode": live.get("call_mode", ""),
        "billed_seconds": live.get("billed_seconds"),
        "credits_cost": live.get("credits_cost"),
        "created_at": live.get("created_at", ""),
        "started_at": live.get("started_at", ""),
        "ended_at": live.get("ended_at", ""),
        "trace_id": live.get("trace_id", data.get("trace_id", "")),
    }
