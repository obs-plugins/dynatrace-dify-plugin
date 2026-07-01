from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.dt_client import DynatraceClient, DynatraceError


class DynatraceProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        base_url = credentials.get("dynatrace_base_url", "").strip()
        api_token = credentials.get("dynatrace_api_token", "").strip()

        if not base_url or not api_token:
            raise ToolProviderCredentialValidationError(
                "Environment URL e API Token são obrigatórios."
            )

        client = DynatraceClient(base_url, api_token, timeout=10)
        try:
            # GET leve só para confirmar auth + scope problems.read
            client.get("problems", params={"pageSize": 1})
        except DynatraceError as exc:
            raise ToolProviderCredentialValidationError(str(exc))
