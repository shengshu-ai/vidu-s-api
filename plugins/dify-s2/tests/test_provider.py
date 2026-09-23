from __future__ import annotations

import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from provider.vidu_client import ViduApiError
from provider.vidu_s2 import ViduS2Provider


def test_provider_validates_credentials_with_read_only_voice_lookup(monkeypatch) -> None:
    calls = []

    class FakeClient:
        def __init__(self, *, api_key: str, region: str) -> None:
            calls.append(("init", api_key, region))

        def list_voices(self, *, timeout: float = 30):
            calls.append(("list_voices", timeout))
            return {"voices": []}

    monkeypatch.setattr("provider.vidu_s2.ViduClient", FakeClient)

    ViduS2Provider().validate_credentials(
        {"vidu_api_key": "vda_test", "region": "global"}
    )

    assert calls == [
        ("init", "vda_test", "global"),
        ("list_voices", 10),
    ]


def test_provider_maps_invalid_credentials_to_safe_errors(monkeypatch) -> None:
    cases = [
        (ValueError("Token vda_test"), "VIDU API key"),
        (requests.Timeout("vda_test"), "timed out"),
        (ViduApiError("private upstream body"), "rejected"),
        (requests.ConnectionError("vda_test"), "rejected"),
        (RuntimeError("client_secret"), "validation failed"),
    ]

    for error, expected in cases:
        class FailingClient:
            def __init__(self, **_kwargs) -> None:
                if isinstance(error, ValueError):
                    raise error

            def list_voices(self, **_kwargs):
                raise error

        monkeypatch.setattr("provider.vidu_s2.ViduClient", FailingClient)

        try:
            ViduS2Provider().validate_credentials(
                {"vidu_api_key": "vda_test", "region": "cn"}
            )
        except ToolProviderCredentialValidationError as exc:
            message = str(exc)
            assert expected in message
            assert "vda_test" not in message
            assert "private upstream body" not in message
            assert "client_secret" not in message
        else:
            raise AssertionError("Expected credential validation to fail")
