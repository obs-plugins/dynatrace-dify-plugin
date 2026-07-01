# Dynatrace Plugin for Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Dify Plugin SDK](https://img.shields.io/badge/Dify-Plugin%20SDK-blue)](https://docs.dify.ai/plugins)

## Overview

The **Dynatrace Plugin for Dify** is a Dify Plugin SDK extension that allows AI agents and workflows to interact directly with a Dynatrace environment. It exposes Dynatrace API v2 capabilities — such as querying active problems and metric timeseries — as native Dify tools, enabling intelligent incident triage, observability-driven automation, and conversational operations.

## Features (MVP)

- **List Active Problems** — Retrieve all open problems from your Dynatrace environment, with optional filtering by status, impact level, entity, or management zone.
- **Get Problem Details** — Fetch full details of a specific problem by its Problem ID, including root cause, impacted entities, and timeline.
- **Query Metric Timeseries** — Query any metric available in Dynatrace Metrics API v2 with configurable resolution, timeframe, and entity selectors.

## Requirements

- **Dify** v1.0.0 or higher
- A **Dynatrace SaaS or Managed** environment (e.g. `https://abc12345.live.dynatrace.com`)
- A Dynatrace **API Token** with the following scopes:
  - `problems.read`
  - `metrics.read`
  - `events.read`

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

### Packaging

To produce a distributable plugin package:
```bash
dify plugin package ./dynatrace-dify-plugin
```
This generates a `.difypkg` file that can be uploaded directly to any Dify workspace.

## Roadmap

- **Free tier** — Published on the official [Dify Marketplace](https://marketplace.dify.ai) with the MVP tools (list problems, get problem details, query metrics).
- **Advanced / Enterprise tier** — An extended version featuring incident-response automation workflows, bi-directional n8n integration for enterprise orchestration, alert correlation, and custom SLO monitoring. Available under a commercial license.

## Privacy

See [PRIVACY.md](PRIVACY.md) for information on data handling.

## License

This project is licensed under the [MIT License](LICENSE).
