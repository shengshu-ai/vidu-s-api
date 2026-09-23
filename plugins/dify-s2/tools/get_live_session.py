from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.common import client_from_runtime, compact_live_query


class GetLiveSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        live_id = tool_parameters["live_id"]
        client = client_from_runtime(self.runtime.credentials)
        result = compact_live_query(client.get_live_session(live_id), live_id)

        for key in (
            "live_id",
            "status",
            "live_duration",
            "call_mode",
            "billed_seconds",
            "credits_cost",
            "created_at",
            "started_at",
            "ended_at",
            "trace_id",
        ):
            yield self.create_variable_message(key, result[key])
        yield self.create_json_message(result)
