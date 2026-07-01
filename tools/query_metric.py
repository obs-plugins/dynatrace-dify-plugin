# TODO: Implement query_metric tool
# Queries metric timeseries data from Dynatrace Metrics API v2

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator
import requests


class QueryMetricTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        # TODO: implement Dynatrace Metrics API v2 call
        pass
