from __future__ import annotations

from typing import Any, Callable
from urllib.parse import quote

import requests


RequestFn = Callable[..., dict[str, Any]]


class ViduApiError(RuntimeError):
    """A sanitized Vidu API failure safe to expose through Dify."""


class ViduClient:
    """REST client for the short-lived operations exposed by the S2 plugin."""

    REGION_HOSTS = {
        "cn": "https://api.vidu.cn",
        "global": "https://api.vidu.com",
    }
    EDITING_TYPES = {
        "style_transfer",
        "virtual_tryon",
        "subject_replacement",
        "background_replacement",
    }

    def __init__(
        self,
        *,
        api_key: str,
        region: str,
        request: RequestFn | None = None,
    ) -> None:
        self.authorization = self._normalize_api_key(api_key)
        self.api_base_url = self._api_base_url(region)
        self._request = request or self._request_json

    def create_avatar_session(
        self,
        *,
        persona: str,
        image_uri: str,
        name: str = "",
        voice: str = "",
        call_mode: str = "video",
        persona_enhance: bool = False,
    ) -> dict[str, Any]:
        normalized_persona = persona.strip()
        normalized_image_uri = image_uri.strip()
        normalized_call_mode = call_mode.strip().lower()
        if not normalized_persona:
            raise ValueError("persona is required")
        if len(normalized_persona) > 50_000:
            raise ValueError("persona must not exceed 50000 characters")
        if not normalized_image_uri:
            raise ValueError("image_uri is required")
        if normalized_call_mode not in {"audio", "video"}:
            raise ValueError("call_mode must be 'audio' or 'video'")

        avatar: dict[str, Any] = {
            "persona": normalized_persona,
            "image_uri": normalized_image_uri,
            "persona_enhance": bool(persona_enhance),
        }
        if name.strip():
            avatar["name"] = name.strip()
        if voice.strip():
            avatar["voice"] = voice.strip()

        data = self._request(
            "POST",
            f"{self.api_base_url}/live/s_avatar/realtime",
            headers=self._headers(),
            json={
                "call_mode": normalized_call_mode,
                "character_id": "1",
                "avatar": avatar,
            },
            timeout=60,
        )
        self._validate_session_response(data)
        return data

    def create_editing_session(
        self,
        *,
        image_url: str,
        editing_type: str = "style_transfer",
    ) -> dict[str, Any]:
        normalized_image_url = image_url.strip()
        normalized_editing_type = editing_type.strip().lower()
        if not normalized_image_url:
            raise ValueError("image_url is required")
        if normalized_editing_type not in self.EDITING_TYPES:
            raise ValueError("editing_type is not supported")

        data = self._request(
            "POST",
            f"{self.api_base_url}/live/s_editing/realtime",
            headers=self._headers(),
            json={
                "image_url": normalized_image_url,
                "editing_type": normalized_editing_type,
            },
            timeout=60,
        )
        self._validate_session_response(data)
        if not isinstance(data.get("render_uid"), str) or not data["render_uid"]:
            raise ValueError("Vidu response missing render_uid")
        return data

    def get_live_session(self, live_id: str) -> dict[str, Any]:
        normalized_live_id = live_id.strip()
        if not normalized_live_id:
            raise ValueError("live_id is required")
        return self._request(
            "GET",
            f"{self.api_base_url}/live/v1/lives/{quote(normalized_live_id, safe='')}",
            headers=self._headers(),
            timeout=30,
        )

    def list_voices(self, *, timeout: float = 30) -> dict[str, Any]:
        return self._request(
            "GET",
            f"{self.api_base_url}/live/v1/voices",
            headers=self._headers(),
            timeout=timeout,
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": self.authorization,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def _api_base_url(cls, region: str) -> str:
        normalized = region.strip().lower()
        try:
            return cls.REGION_HOSTS[normalized]
        except KeyError as exc:
            raise ValueError("region must be 'cn' or 'global'") from exc

    @staticmethod
    def _normalize_api_key(api_key: str) -> str:
        key = api_key.strip()
        if key.startswith("Token vda_"):
            return key
        if key.startswith("vda_"):
            return f"Token {key}"
        raise ValueError('VIDU API key must look like "vda_xxx" or "Token vda_xxx".')

    @staticmethod
    def _validate_session_response(data: dict[str, Any]) -> None:
        live = data.get("live")
        if not isinstance(live, dict):
            raise ValueError("Vidu response missing live")
        for field in ("id", "status"):
            if not isinstance(live.get(field), str) or not live[field]:
                raise ValueError(f"Vidu response missing live.{field}")
        duration = live.get("live_duration")
        if isinstance(duration, bool) or not isinstance(duration, int) or duration <= 0:
            raise ValueError("Vidu response has invalid live.live_duration")

        rtc = data.get("rtc")
        if not isinstance(rtc, dict):
            raise ValueError("Vidu response missing rtc")
        for field in ("app_id", "channel_id", "user_id", "token", "token_expire_at"):
            if rtc.get(field) in (None, ""):
                raise ValueError(f"Vidu response missing rtc.{field}")

    @staticmethod
    def _request_json(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            raise
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            suffix = f" with HTTP {status}" if status else ""
            raise ViduApiError(f"Vidu API request failed{suffix}.") from exc
        except ValueError as exc:
            raise ViduApiError("Vidu API returned invalid JSON.") from exc

        if not isinstance(data, dict):
            raise ViduApiError("Vidu API returned an invalid response.")
        return data
