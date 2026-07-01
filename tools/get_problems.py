from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dt_client import DynatraceClient, DynatraceError

SEVERITY_VALUES = {
    "AVAILABILITY",
    "ERROR",
    "PERFORMANCE",
    "RESOURCE_CONTENTION",
    "CUSTOM_ALERT",
    "MONITORING_UNAVAILABLE",
    "INFO",
}


class GetProblemsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        creds = self.runtime.credentials
        client = DynatraceClient(creds["dynatrace_base_url"], creds["dynatrace_api_token"])

        time_from = tool_parameters.get("from") or "now-2h"
        status = tool_parameters.get("status")  # OPEN | CLOSED
        severity = tool_parameters.get("severity")
        page_size = min(int(tool_parameters.get("page_size") or 50), 500)

        # Constrói problemSelector a partir de filtros amigáveis
        selectors: list[str] = []
        if status in ("OPEN", "CLOSED"):
            selectors.append(f'status("{status}")')
        if severity and severity in SEVERITY_VALUES:
            selectors.append(f'severityLevel("{severity}")')

        params: dict[str, Any] = {"from": time_from, "pageSize": page_size}
        if selectors:
            params["problemSelector"] = ",".join(selectors)

        try:
            problems = client.paginate(
                "problems", params, items_key="problems", max_items=page_size
            )
        except DynatraceError as exc:
            yield self.create_text_message(f"Dynatrace: {exc}")
            return

        summary = [
            {
                "problemId": p.get("problemId"),
                "displayId": p.get("displayId"),
                "title": p.get("title"),
                "severityLevel": p.get("severityLevel"),
                "status": p.get("status"),
                "impactLevel": p.get("impactLevel"),
                "startTime": p.get("startTime"),
                "affectedEntities": [
                    e.get("name") for e in p.get("affectedEntities", []) if e.get("name")
                ],
            }
            for p in problems
        ]

        yield self.create_json_message({"count": len(summary), "problems": summary})
        yield self.create_text_message(
            f"{len(summary)} problema(s) encontrado(s) (janela: {time_from})."
        )
