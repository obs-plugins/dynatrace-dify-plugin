from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dt_client import DynatraceClient, DynatraceError

MAX_POINTS_PER_SERIES = 500


class QueryMetricTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        metric_selector = (tool_parameters.get("metric_selector") or "").strip()
        if not metric_selector:
            yield self.create_text_message("O parâmetro 'metric_selector' é obrigatório.")
            return

        creds = self.runtime.credentials
        client = DynatraceClient(creds["dynatrace_base_url"], creds["dynatrace_api_token"])

        params: dict[str, Any] = {
            "metricSelector": metric_selector,
            "from": tool_parameters.get("from") or "now-1h",
            "resolution": tool_parameters.get("resolution") or "1m",
        }
        if tool_parameters.get("to"):
            params["to"] = tool_parameters["to"]
        if tool_parameters.get("entity_selector"):
            params["entitySelector"] = tool_parameters["entity_selector"]

        try:
            # metrics/query NÃO pagina por nextPageKey (deprecated) -> pedido único
            payload = client.get("metrics/query", params)
        except DynatraceError as exc:
            yield self.create_text_message(f"Dynatrace: {exc}")
            return

        results = []
        for metric in payload.get("result", []):
            series = []
            for d in metric.get("data", []):
                ts = d.get("timestamps", [])[-MAX_POINTS_PER_SERIES:]
                vals = d.get("values", [])[-MAX_POINTS_PER_SERIES:]
                series.append(
                    {
                        "dimensions": d.get("dimensions", []),
                        "points": list(zip(ts, vals)),
                    }
                )
            results.append({"metricId": metric.get("metricId"), "series": series})

        yield self.create_json_message(
            {"resolution": payload.get("resolution"), "result": results}
        )
        yield self.create_text_message(
            f"Métrica '{metric_selector}' consultada ({params['from']}, res={params['resolution']})."
        )
