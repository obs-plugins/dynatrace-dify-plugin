import json
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class GetProblemDetailsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Retrieve full details of a specific Dynatrace problem by Problem ID."""
        credentials = self.runtime.credentials
        environment_url = credentials.get("environment_url", "").rstrip("/")
        api_token = credentials.get("api_token", "")

        problem_id = tool_parameters.get("problem_id", "").strip()
        if not problem_id:
            yield self.create_text_message("Problem ID is required.")
            return

        url = f"{environment_url}/api/v2/problems/{problem_id}"
        headers = {
            "Authorization": f"Api-Token {api_token}",
            "Accept": "application/json; charset=utf-8",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 404:
                yield self.create_text_message(
                    f"Problem '{problem_id}' not found. Please check the Problem ID."
                )
            else:
                yield self.create_text_message(
                    f"Dynatrace API error {response.status_code}: {response.text}"
                )
            return
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Request failed: {e}")
            return

        problem = response.json()

        # Build a structured summary
        result = {
            "problemId": problem.get("problemId"),
            "displayId": problem.get("displayId"),
            "title": problem.get("title"),
            "status": problem.get("status"),
            "impactLevel": problem.get("impactLevel"),
            "severityLevel": problem.get("severityLevel"),
            "startTime": problem.get("startTime"),
            "endTime": problem.get("endTime"),
            "affectedEntities": [
                {"entityId": e.get("entityId", {}).get("id"), "name": e.get("name")}
                for e in problem.get("affectedEntities", [])
            ],
            "impactedEntities": [
                {"entityId": e.get("entityId", {}).get("id"), "name": e.get("name")}
                for e in problem.get("impactedEntities", [])
            ],
            "rootCauseEntity": (
                {
                    "entityId": problem.get("rootCauseEntity", {}).get("entityId", {}).get("id"),
                    "name": problem.get("rootCauseEntity", {}).get("name"),
                }
                if problem.get("rootCauseEntity")
                else None
            ),
            "managementZones": [
                {"id": mz.get("id"), "name": mz.get("name")}
                for mz in problem.get("managementZones", [])
            ],
            "evidenceDetails": {
                "totalCount": problem.get("evidenceDetails", {}).get("totalCount", 0),
                "details": [
                    {
                        "displayName": ev.get("displayName"),
                        "evidenceType": ev.get("evidenceType"),
                        "entity": {
                            "entityId": ev.get("entity", {}).get("entityId", {}).get("id"),
                            "name": ev.get("entity", {}).get("name"),
                        },
                    }
                    for ev in problem.get("evidenceDetails", {}).get("details", [])
                ],
            },
            "recentComments": {
                "totalResults": problem.get("recentComments", {}).get("totalResults", 0),
                "comments": [
                    {
                        "id": c.get("id"),
                        "content": c.get("content"),
                        "authorName": c.get("authorName"),
                        "createdAtTimestamp": c.get("createdAtTimestamp"),
                    }
                    for c in problem.get("recentComments", {}).get("comments", [])
                ],
            },
        }

        yield self.create_text_message(json.dumps(result, indent=2))
        yield self.create_json_message(result)
