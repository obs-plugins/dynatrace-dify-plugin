import json
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class QueryMetricTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Query metric timeseries data from Dynatrace Metrics API v2."""
        credentials = self.runtime.credentials
        environment_url = credentials.get("environment_url", "").rstrip("/")
        api_token = credentials.get("api_token", "")

        metric_selector = tool_parameters.get("metric_selector", "").strip()
        if not metric_selector:
            yield self.create_text_message("Metric selector is required.")
            return

        from_time = tool_parameters.get("from", "") or "now-1h"
        to_time = tool_parameters.get("to", "") or "now"
        resolution = tool_parameters.get("resolution", "") or ""
        entity_selector = tool_parameters.get("entity_selector", "") or ""

        url = f"{environment_url}/api/v2/metrics/query"
        headers = {
            "Authorization": f"Api-Token {api_token}",
            "Accept": "application/json; charset=utf-8",
        }
        params: dict[str, Any] = {
            "metricSelector": metric_selector,
            "from": from_time,
            "to": to_time,
        }
        if resolution:
            params["resolution"] = resolution
        if entity_selector:
            params["entitySelector"] = entity_selector

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            yield self.create_text_message(
                f"Dynatrace API error {response.status_code}: {response.text}"
            )
            return
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Request failed: {e}")
            return

        data = response.json()
        resolution_result = data.get("resolution", "")
        metric_results = data.get("result", [])

        if not metric_results:
            yield self.create_text_message(
                f"No data returned for metric selector: {metric_selector}"
            )
            return

        # Build a structured result
        result = {
            "resolution": resolution_result,
            "metrics": [
                {
                    "metricId": mr.get("metricId"),
                    "data": [
                        {
                            "dimensionMap": series.get("dimensionMap", {}),
                            "timestamps": series.get("timestamps", []),
                            "values": series.get("values", []),
                        }
                        for series in mr.get("data", [])
                    ],
                }
                for mr in metric_results
            ],
        }

        yield self.create_text_message(json.dumps(result, indent=2))
        yield self.create_json_message(result)
