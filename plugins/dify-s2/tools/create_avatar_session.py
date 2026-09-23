from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.common import client_from_runtime, compact_avatar_response


class CreateAvatarSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = client_from_runtime(self.runtime.credentials)
        data = client.create_avatar_session(
            persona=tool_parameters["persona"],
            image_uri=tool_parameters["image_uri"],
            name=tool_parameters.get("name", ""),
            voice=tool_parameters.get("voice", ""),
            call_mode=tool_parameters.get("call_mode", "video"),
            persona_enhance=tool_parameters.get("persona_enhance", False),
        )
        result = compact_avatar_response(data)

        for key in ("live_id", "status", "live_duration", "call_mode", "rtc"):
            yield self.create_variable_message(key, result[key])
        yield self.create_json_message(result)
