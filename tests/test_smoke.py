"""Smoke test de integridade — NÃO toca na rede.

Objetivo: apanhar desalinhamentos provider<->client e estrutura partida ANTES de
empacotar (importa tudo, valida DynatraceError, construção de URL e YAML das tools).
Correr da raiz do repo: python -m pytest tests/ -q
"""
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"


def test_imports_provider_and_tools():
    # Import falha se houver desalinhamento provider<->client ou nas deps do SDK.
    import provider.dynatrace  # noqa: F401
    import tools.get_problems  # noqa: F401
    import tools.get_problem_details  # noqa: F401
    import tools.query_metric  # noqa: F401


def test_dynatrace_error_status_code():
    from utils.dt_client import DynatraceError

    assert DynatraceError("erro de rede").status_code is None
    assert DynatraceError("não encontrado", 404).status_code == 404


def test_client_builds_url():
    from utils.dt_client import DynatraceClient

    # rstrip da barra final do base_url + prefixo /api/v2/
    client = DynatraceClient("https://t.live.dynatrace.com/", "tok")
    assert client._url("problems") == "https://t.live.dynatrace.com/api/v2/problems"
    # path com barra inicial não duplica a barra
    assert client._url("/problems/123") == "https://t.live.dynatrace.com/api/v2/problems/123"


def test_tool_yamls_exist_and_parse():
    for name in ("get_problems.yaml", "get_problem_details.yaml", "query_metric.yaml"):
        path = TOOLS_DIR / name
        assert path.is_file(), f"YAML da tool em falta: {name}"
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert isinstance(data, dict) and "identity" in data
