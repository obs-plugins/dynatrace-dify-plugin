# CLAUDE.md — Dynatrace Plugin for Dify

Contexto para sessões de Claude Code neste repositório. Lê isto antes de mexer no código.

## O que é

Plugin de integração **Dynatrace → Dify** (Dify Plugin SDK). MVP com 3 tools que consultam
a **Dynatrace API v2** (SaaS). Autor/org: `obs-plugins`.

## Estado atual

- Estrutura de ficheiros completa e a compilar (Python + YAML válidos).
- Ainda não testado contra um tenant real nem empacotado em `.difypkg`.

## Tools do MVP

1. `dynatrace_get_problems` — lista problemas (`from`, `status`, `severity`, `page_size`) → `problemSelector`.
2. `dynatrace_get_problem_details` — detalhe por `problemId` (root cause, entidades afetadas).
3. `dynatrace_query_metric` — timeseries por `metricSelector` (`from`/`to`/`resolution`).

Cliente HTTP partilhado em `utils/dt_client.py`: auth `Api-Token`, retry/backoff (429/5xx),
paginação `nextPageKey` com cap. `metrics/query` NÃO pagina (deprecated) → pedido único.

## Autenticação

API Token (não OAuth). Duas credenciais no provider:
- `dynatrace_base_url` — campo livre (SaaS `https://{id}.live.dynatrace.com` ou Managed `.../e/{env-id}`).
- `dynatrace_api_token` — matriz de scopes por uso:
  - `metrics.read` — obrigatório na validação inicial (`GET /api/v2/metrics`) e em `dynatrace_query_metric`.
  - `problems.read` — obrigatório em `dynatrace_get_problems` e `dynatrace_get_problem_details`.
  - `events.read` não é usado por nenhum tool do MVP atual — não exigir nem documentar como obrigatório.

Ambiente de teste: **SaaS**. Managed é suportado por design (base_url livre) mas ainda não validado.

## Tarefas pendentes (por ordem)

1. **Corrigir o pin do SDK** em `requirements.txt`: o pin atual (`dify_plugin>=0.2.0,<0.3.0`)
   está desatualizado. O SDK atual é 0.7.x. Usar algo como `dify_plugin>=0.7.0,<0.8.0`
   e alinhar com a versão do Dify de destino. Confirmar imports (`ToolProvider`,
   `ToolProviderCredentialValidationError`, `Tool`, `ToolInvokeMessage`) contra essa versão.
2. Criar ambiente Python local (`uv venv` + `uv pip install -r requirements.txt`) e garantir
   que `python -m main` arranca.
3. Debug remoto: `.env` com a debug key do Dify → testar os 3 tools contra o tenant SaaS.
4. Validar `problemSelector`/`entitySelector`/`metricSelector` reais (a gramática evolui —
   confirmar no API Explorer do tenant).
5. Confirmar path do ícone (`_assets/icon.svg` vs `assets/`) antes de `dify plugin package`.
6. Empacotar `.difypkg`.

## Regras

- Autor `obs-plugins` em todo o lado (manifest, provider, tools).
- Versão avançada (automação de incidentes, n8n) é repo PRIVADO separado, licença comercial —
  NUNCA neste repo (que é MIT público).
- Comentários mínimos no código; só onde a lógica não é óbvia.
