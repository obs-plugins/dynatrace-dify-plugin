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
            # GET leve em /metrics: endpoint de metadados sempre presente (métricas
            # builtin existem em todo tenant), ao contrário de /problems que devolve
            # 404 em tenants sem problemas recentes. Usa o scope metrics.read, já
            # exigido pelo tool query_metric.
            client.get("metrics", params={"pageSize": 1})
        except DynatraceError as exc:
            if exc.status_code == 401:
                raise ToolProviderCredentialValidationError(
                    "API Token inválido (401). Verifica se o token está correto e ativo."
                )
            if exc.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "API Token sem permissões suficientes (403). Confirma os scopes "
                    "problems.read, metrics.read e events.read."
                )
            if exc.status_code == 404:
                raise ToolProviderCredentialValidationError(
                    "Environment URL inválida ou endpoint indisponível neste tenant (404). "
                    "Confirma o URL do ambiente Dynatrace (sem /api e sem barra final)."
                )
            raise ToolProviderCredentialValidationError(str(exc))
