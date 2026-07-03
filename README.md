# Dynatrace Plugin for Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Dify Plugin SDK](https://img.shields.io/badge/Dify-Plugin%20SDK-blue)](https://docs.dify.ai/plugins)

## Overview

The **Dynatrace Plugin for Dify** is a Dify Plugin SDK extension that allows AI agents and workflows to interact directly with a Dynatrace environment. It exposes Dynatrace API v2 capabilities — such as querying active problems and metric timeseries — as native Dify tools, enabling intelligent incident triage, observability-driven automation, and conversational operations.

## Features (MVP)

- **List Active Problems** — Retrieve all open problems from your Dynatrace environment, with optional filtering by status, impact level, entity, or management zone.
- **Get Problem Details** — Fetch full details of a specific problem by its Problem ID, including root cause, impacted entities, and timeline.
- **Query Metric Timeseries** — Query any metric available in Dynatrace Metrics API v2 with configurable resolution, timeframe, and entity selectors.

> These tools are the **read path** — they let Dify *query* Dynatrace (problems, metrics). Instrumenting Dify's own workflows and sending that telemetry *to* Dynatrace is a separate, future piece — see **Dynatrace Observability Suite** under Roadmap.

## Requirements

- **Dify** v1.0.0 or higher
- A **Dynatrace SaaS or Managed** environment (e.g. `https://abc12345.live.dynatrace.com`)
- A Dynatrace **API Token** with the scopes required by the tools you plan to use:

  | Scope | Required for |
  |-------|--------------|
  | `metrics.read` | Credential validation (`GET /api/v2/metrics`) **and** Query Metric |
  | `problems.read` | Get Problems **and** Get Problem Details |

> Credential validation calls `GET /api/v2/metrics` (a stable metadata endpoint
> present on every tenant) to confirm the token is valid, so `metrics.read` must
> be granted even if you only plan to use the problem-related tools.

## Configuration

When adding this plugin to your Dify workspace, you will be prompted to configure the following provider credentials:

| Field | Description | Example |
|-------|-------------|---------|
| **Environment URL** | The base URL of your Dynatrace environment, without trailing slash. | `https://abc12345.live.dynatrace.com` |
| **API Token** | A Dynatrace API token with the required scopes. | `dt0c01.XXXXXXXX...` |

These credentials are stored securely in Dify and are never exposed to end users.

## Troubleshooting

| Error | Meaning |
|-------|---------|
| `401` | API Token is invalid, expired, or revoked. |
| `403` | Token is missing a required scope — the message names the exact scope for the tool that failed (see scope table above). |
| `404` | Wrong Environment URL/host, or the requested resource (e.g. a `problemId`) doesn't exist. |
| `5xx` / `429` | Dynatrace API is temporarily unavailable or rate-limiting; the plugin retries automatically before surfacing this. |

## Testing & Validation

### Level A — Plugin Validation in Dify

- Install the `.difypkg` (or run in debug mode) in a Dify workspace.
- Create a new Dynatrace provider authorization, filling in Environment URL and API
  Token.
- Save the credentials — this triggers `GET /api/v2/metrics`, which requires
  `metrics.read` (see scope table in Requirements).
- Intentionally test the failure paths to confirm the messages: wrong token (401),
  token without `metrics.read` (403), wrong URL/host (404) — see the Troubleshooting
  table above for what each one means.
- Expected success: the authorization saves without error.

### Level B — Direct Dynatrace API Validation

- `curl` `GET /api/v2/metrics?pageSize=1` with the `Authorization: Api-Token ...`
  header — confirms the token is valid, `metrics.read` is present, and the host is
  reachable, outside of Dify.
- `curl` `GET /api/v2/metrics/query?metricSelector=builtin:host.cpu.usage:avg&from=now-1h`
  with the same token — confirms you can actually query a builtin metric, not just list
  metadata (this is what the Query Metric tool does).
- (Optional) `curl` `GET /api/v2/problems?from=now-2h` — confirms `problems.read`
  separately, since Level A validation doesn't exercise this scope.
- Diagnosis: if Level A fails but Level B succeeds, the problem is in the plugin/URL
  configuration used in Dify, not the token. If Level B itself fails, the problem is
  external to the plugin (Dynatrace/network/token) — see the Troubleshooting table
  above for what the returned HTTP status means.

### Level C — End-to-End Validation via a Dify App/Workflow

- Create a simple app/workflow in Dify (Chatflow or Agent) with the 3 Dynatrace tools
  attached.
- Ask a simple question that should trigger each tool (e.g. "what problems are open
  right now?", "what's the CPU usage for host X in the last hour?").
- Confirm in the Dify execution log/trace that the tool was actually called and
  returned the expected JSON/text message.
- Important: if the LLM doesn't call the tool, calls it with the wrong parameters, or
  misinterprets the returned result, that's a prompt/model issue, not a plugin bug —
  the plugin's responsibility ends at "tool invoked with valid parameters → correct API
  call → correct response returned" (Levels A and B). Level C validates the integration
  experience, not the plugin's correctness.

## Development

### Local Debugging

1. Copy `.env.example` to `.env` and fill in your Dify remote debugging key and host:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the plugin in debug mode using the Dify Plugin SDK CLI, which connects to your Dify instance via the remote debugging key defined in `.env`.

### Tests

A minimal, network-free smoke test checks import integrity, error handling, URL
construction, and that the tool YAMLs are parseable — catching provider↔client
mismatches before packaging:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

### Packaging

To produce a distributable plugin package:
```bash
dify plugin package ./dynatrace-dify-plugin
```
This generates a `.difypkg` file that can be uploaded directly to any Dify workspace.

## Roadmap

### Dynatrace Observability Suite

- **Two complementary halves.** This plugin is the **read path** — Dify apps *read* from Dynatrace via tools. A separate future piece is the **write / emit path** — Dify's own workflow telemetry *flowing into* Dynatrace.
- **Dynatrace Tools plugin (this repo).** The read path: the metric and problem tools documented above, installed from the Dify Marketplace as a `.difypkg`.
- **Dynatrace Telemetry / OTel bridge (future, separate).** The write path: instrumentation of Dify's own workflows / nodes / tool calls, exported as traces and metrics to Dynatrace via **OTLP / OpenTelemetry**. It lives at the infrastructure level (not as a tool) and uses a **separate token with ingest scopes** (`metrics.ingest`, `logs.ingest`, `openTelemetryTrace.ingest`) — distinct from the read-only scopes (`metrics.read`, `problems.read`) this plugin uses.
- **Scope of this repo is unchanged.** Infra/config details for the Telemetry piece are intentionally out of scope here and will ship as a separate artifact; this repo stays read-only tools.

- **Free tier** — Published on the official [Dify Marketplace](https://marketplace.dify.ai) with the MVP tools (list problems, get problem details, query metrics).
- **Advanced / Enterprise tier** — An extended version featuring incident-response automation workflows, bi-directional n8n integration for enterprise orchestration, alert correlation, and custom SLO monitoring. Available under a commercial license.

## Privacy

See [PRIVACY.md](PRIVACY.md) for information on data handling.

## License

This project is licensed under the [MIT License](LICENSE).
