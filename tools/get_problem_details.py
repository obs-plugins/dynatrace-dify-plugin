from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dt_client import DynatraceClient, DynatraceError


class GetProblemDetailsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        problem_id = (tool_parameters.get("problem_id") or "").strip()
        if not problem_id:
            yield self.create_text_message("O parâmetro 'problem_id' é obrigatório.")
            return

        creds = self.runtime.credentials
        client = DynatraceClient(creds["dynatrace_base_url"], creds["dynatrace_api_token"])

        try:
            p = client.get(f"problems/{problem_id}")
        except DynatraceError as exc:
            yield self.create_text_message(f"Dynatrace: {exc}")
            return

        details = {
            "problemId": p.get("problemId"),
            "displayId": p.get("displayId"),
            "title": p.get("title"),
            "severityLevel": p.get("severityLevel"),
            "status": p.get("status"),
            "impactLevel": p.get("impactLevel"),
            "startTime": p.get("startTime"),
            "endTime": p.get("endTime"),
            "rootCauseEntity": (p.get("rootCauseEntity") or {}).get("name"),
            "affectedEntities": [
                {"name": e.get("name"), "type": (e.get("entityId") or {}).get("type")}
                for e in p.get("affectedEntities", [])
            ],
            "impactedEntities": [
                e.get("name") for e in p.get("impactedEntities", []) if e.get("name")
            ],
            "evidenceCount": len((p.get("evidenceDetails") or {}).get("details", [])),
        }

        yield self.create_json_message(details)
        yield self.create_text_message(
            f"{details['displayId']} — {details['title']} [{details['status']}]"
        )
