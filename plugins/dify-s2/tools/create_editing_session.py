from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.common import client_from_runtime, compact_editing_response


class CreateEditingSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_runtime(self.runtime.credentials)
        data = client.create_editing_session(
            image_url=tool_parameters["image_url"],
            editing_type=tool_parameters.get("editing_type", "style_transfer"),
        )
        result = compact_editing_response(data)

        for key in (
            "live_id",
            "status",
            "live_duration",
            "render_uid",
            "client_secret",
            "rtc",
        ):
            yield self.create_variable_message(key, result[key])
        yield self.create_json_message(result)
