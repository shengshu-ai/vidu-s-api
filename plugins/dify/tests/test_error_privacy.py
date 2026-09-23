from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from dify_plugin.core.server.io_server import IOServer
from dify_plugin.core.server.serverless.request_reader import ServerlessRequestReader

from provider.vidu_s1 import ViduS1Provider
from tools.list_voices import ListVoicesTool


def execute_with_sdk_logging(invoke):
    # Exercise the SDK path that logs full exception chains in remote/serverless mode.
    reader = object.__new__(ServerlessRequestReader)
    writer = Mock()
    server = SimpleNamespace(_execute_request=lambda *_args: invoke())
    IOServer._execute_request_in_thread(server, "privacy-test", {}, reader, writer)
    return writer.stream_error_object.call_args.kwargs["data"]


@pytest.mark.parametrize("entrypoint", ["provider", "tool"])
@pytest.mark.parametrize("error_type", [requests.HTTPError, requests.Timeout])
def test_sdk_logs_hide_upstream_secrets(monkeypatch, caplog, entrypoint, error_type):
    credentials = {"vidu_api_key": "vda_private_test_key", "region": "cn"}

    def fail_request(*_args, **_kwargs):
        raise error_type("vda_private_test_key private-upstream-body")

    monkeypatch.setattr("requests.request", fail_request)
    if entrypoint == "provider":
        invoke = lambda: ViduS1Provider().validate_credentials(credentials)
    else:
        tool = ListVoicesTool.from_credentials(credentials)
        invoke = lambda: list(tool._invoke({}))

    error = execute_with_sdk_logging(invoke)

    assert error["message"]
    assert "Unexpected error occurred" in caplog.text
    for secret in ("vda_private_test_key", "private-upstream-body"):
        assert secret not in caplog.text
        assert secret not in str(error)


def test_sdk_logs_hide_malformed_credentials(monkeypatch, caplog):
    request = Mock(side_effect=AssertionError("Invalid key must fail before HTTP"))
    monkeypatch.setattr("requests.request", request)

    error = execute_with_sdk_logging(
        lambda: ViduS1Provider().validate_credentials(
            {"vidu_api_key": "vda_private_test_key\nmalformed", "region": "cn"}
        )
    )

    request.assert_not_called()
    assert error["error_type"] == "ToolProviderCredentialValidationError"
    assert "vda_private_test_key" not in caplog.text
    assert "vda_private_test_key" not in str(error)
