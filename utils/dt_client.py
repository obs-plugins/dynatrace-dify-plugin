import random
import time
from typing import Any, Iterator

import requests

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class DynatraceError(Exception):
    """Erro de nível aplicacional já com mensagem legível para o LLM."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class DynatraceClient:
    def __init__(self, base_url: str, api_token: str, timeout: int = DEFAULT_TIMEOUT):
        # base_url livre: SaaS (tenant.live.dynatrace.com) ou Managed (activegate/e/{env-id})
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Api-Token {api_token}",
                "Accept": "application/json; charset=utf-8",
            }
        )
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v2/{path.lstrip('/')}"

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        url = self._url(path)
        last_exc: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, params=params, timeout=self.timeout)
            except requests.RequestException as exc:
                last_exc = exc
                self._sleep_backoff(attempt)
                continue

            if resp.status_code in RETRYABLE_STATUS and attempt < MAX_RETRIES:
                self._sleep_backoff(attempt, retry_after=resp.headers.get("Retry-After"))
                continue

            if resp.status_code == 401:
                raise DynatraceError("Token inválido ou expirado (401).", status_code=401)
            if resp.status_code == 403:
                raise DynatraceError(
                    "Token sem scopes suficientes para este endpoint (403).", status_code=403
                )
            if resp.status_code == 404:
                raise DynatraceError("Recurso não encontrado (404).", status_code=404)
            if resp.status_code in RETRYABLE_STATUS:
                raise DynatraceError(
                    f"Dynatrace API indisponível temporariamente ({resp.status_code}). "
                    "O plugin já tentou novamente automaticamente; tenta de novo dentro "
                    "de instantes.",
                    status_code=resp.status_code,
                )
            if resp.status_code >= 400:
                raise DynatraceError(
                    f"Erro Dynatrace {resp.status_code}: {resp.text[:300]}",
                    status_code=resp.status_code,
                )

            return resp.json()

        raise DynatraceError(f"Falha de rede após {MAX_RETRIES} tentativas: {last_exc}")

    def paginate(
        self,
        path: str,
        params: dict[str, Any],
        items_key: str,
        max_pages: int = 5,
        max_items: int = 500,
    ) -> list[dict]:
        """Segue nextPageKey (problems/events). Cap defensivo: o output vai para um LLM."""
        collected: list[dict] = []
        page_params = dict(params)

        for _ in range(max_pages):
            payload = self.get(path, page_params)
            collected.extend(payload.get(items_key, []))

            if len(collected) >= max_items:
                return collected[:max_items]

            next_key = payload.get("nextPageKey")
            if not next_key:
                break
            # Regra da API: com nextPageKey, todos os outros params são omitidos.
            page_params = {"nextPageKey": next_key}

        return collected

    @staticmethod
    def _sleep_backoff(attempt: int, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                time.sleep(min(float(retry_after), 30))
                return
            except ValueError:
                pass
        # exponencial + jitter
        time.sleep(min(2 ** attempt + random.random(), 30))
