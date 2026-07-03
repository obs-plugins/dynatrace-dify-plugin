from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.dt_client import RETRYABLE_STATUS, DynatraceClient, DynatraceError


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
            # 404 em tenants sem problemas recentes. Isto só exercita metrics.read —
            # problems.read não é testado aqui e é validado implicitamente pelos
            # tools get_problems/get_problem_details ao serem invocados.
            client.get("metrics", params={"pageSize": 1})
        except DynatraceError as exc:
            if exc.status_code == 401:
                raise ToolProviderCredentialValidationError(
                    "API Token inválido ou expirado (401). Verifica se o token está "
                    "correto e ativo."
                )
            if exc.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "API Token sem o scope metrics.read (403). Este scope é obrigatório "
                    "mesmo que só pretendas usar os tools de Problems, porque a validação "
                    "inicial usa GET /api/v2/metrics."
                )
            if exc.status_code == 404:
                raise ToolProviderCredentialValidationError(
                    "Environment URL inválida ou endpoint indisponível neste tenant (404). "
                    "Confirma o URL do ambiente Dynatrace (sem /api e sem barra final)."
                )
            if exc.status_code in RETRYABLE_STATUS:
                raise ToolProviderCredentialValidationError(
                    f"Dynatrace API indisponível temporariamente ao contactar {base_url} "
                    f"({exc.status_code}). Tenta guardar as credenciais novamente dentro "
                    "de instantes."
                )
            # status_code None = erro de rede (firewall/proxy corporativo a bloquear a
            # saída, DNS, timeout). Orienta o utilizador em vez de mostrar o erro cru.
            if exc.status_code is None:
                raise ToolProviderCredentialValidationError(
                    "Não foi possível alcançar o ambiente Dynatrace em "
                    f"{base_url}. Verifica a conectividade de rede, firewall ou proxy "
                    "de saída, e confirma que o Environment URL está correto."
                )
            raise ToolProviderCredentialValidationError(str(exc))
