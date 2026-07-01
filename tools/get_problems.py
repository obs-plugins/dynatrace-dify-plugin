import json
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class GetProblemsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Retrieve a list of active problems from Dynatrace API v2."""
        credentials = self.runtime.credentials
        environment_url = credentials.get("environment_url", "").rstrip("/")
        api_token = credentials.get("api_token", "")

        problem_selector = tool_parameters.get("problem_selector", "") or ""
        entity_selector = tool_parameters.get("entity_selector", "") or ""
        page_size = tool_parameters.get("page_size") or 50

        url = f"{environment_url}/api/v2/problems"
        headers = {
            "Authorization": f"Api-Token {api_token}",
            "Accept": "application/json; charset=utf-8",
        }
        params: dict[str, Any] = {"pageSize": int(page_size)}
        if problem_selector:
            params["problemSelector"] = problem_selector
        if entity_selector:
            params["entitySelector"] = entity_selector

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(
                f"Dynatrace API error {response.status_code}: {response.text}"
            )
            return
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Request failed: {e}")
            return

        data = response.json()
        problems = data.get("problems", [])
        total_count = data.get("totalCount", len(problems))

        if not problems:
            yield self.create_text_message("No problems found matching the given criteria.")
            return

        result = {
            "totalCount": total_count,
            "problems": [
                {
                    "problemId": p.get("problemId"),
                    "displayId": p.get("displayId"),
                    "title": p.get("title"),
                    "status": p.get("status"),
                    "impactLevel": p.get("impactLevel"),
                    "severityLevel": p.get("severityLevel"),
                    "startTime": p.get("startTime"),
                    "endTime": p.get("endTime"),
                    "affectedEntities": [
                        {"entityId": e.get("entityId", {}).get("id"), "name": e.get("name")}
                        for e in p.get("affectedEntities", [])
                    ],
                }
                for p in problems
            ],
        }

        yield self.create_text_message(json.dumps(result, indent=2))
        yield self.create_json_message(result)
