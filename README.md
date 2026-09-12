# CloudScale Data Platform

A production-oriented, near-real-time data engineering project built on Azure. It demonstrates event ingestion, incremental PySpark processing, Delta Lake medallion layers, infrastructure as code, and controlled CI/CD.

> **Status:** Phase 2 complete - local synthetic order ingestion is available without Azure resources.

## Project Goal

The platform will process synthetic retail order events from ingestion to analytics-ready datasets. The implementation is intentionally incremental: every phase is independently testable, documented, and safe to run without provisioning cloud resources by default.

## Target Architecture

```text
Event producer
  -> Azure Event Hubs (Kafka-compatible)
  -> Event Hubs Capture -> ADLS Gen2 raw zone
  -> Databricks Structured Streaming -> Delta Bronze
  -> validation, deduplication, enrichment -> Delta Silver
  -> business aggregates -> Delta Gold
  -> SQL analytics consumers
```

Read the detailed design in [docs/architecture.md](docs/architecture.md).

## Engineering Principles

- Keep credentials out of source control, configuration files, and Terraform state.
- Use managed identities and Azure RBAC wherever possible; use Key Vault only for secrets that cannot use identity-based access.
- Treat Bronze data as immutable and make downstream processing idempotent.
- Validate schemas and data-quality expectations before data is promoted between layers.
- Make all Azure infrastructure reproducible with Terraform, but require explicit approval for deployment.
- Prefer local Docker/PySpark validation before Azure integration tests.

## Repository Layout

Current components:

```text
src/cloudscale_data_platform/  Shared Python configuration, event contracts, and local producers
tests/                         Unit and integration tests
docs/                          Architecture, decisions, and runbooks
docker/                        Local development images
.github/workflows/             CI/CD workflows
```

Planned future components:

```text
infra/terraform/               Terraform modules and environment composition
databricks/                    Databricks job, workflow, and notebook definitions
k8s/                           Kubernetes manifests for workloads that justify orchestration
```

## Local Development

Prerequisites: Python 3.11 and `pip`.

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest
```

The editable install command also installs or refreshes the `cloudscale-produce-orders` console script after project metadata changes.

Generate local synthetic order events:

```powershell
cloudscale-produce-orders --output data/local/raw/orders.jsonl --count 10
```

Run the producer in Docker:

```powershell
docker build -f docker/producer.Dockerfile -t cloudscale-order-producer .
docker run --rm -v ${PWD}/data:/app/data cloudscale-order-producer --count 10
```

The foundational package reads only non-secret application settings. Its defaults are safe for local development:

| Variable | Default | Purpose |
| --- | --- | --- |
| `CLOUDSCALE_ENVIRONMENT` | `local` | Deployment context: `local`, `development`, `test`, or `production` |
| `CLOUDSCALE_LOG_LEVEL` | `INFO` | Application logging threshold |
| `CLOUDSCALE_EVENT_SCHEMA_VERSION` | `1` | Positive integer event-contract version |

Do not place Azure credentials, connection strings, access keys, or tokens in these variables for committed configuration. Local secret files such as `.env` are ignored by Git. Generated local data under `data/` is also ignored.

## Delivery Roadmap

1. **Foundation** — documentation, tooling, configuration conventions, and CI quality gates.
2. **Local ingestion** — a containerized producer and Kafka-compatible local integration tests.
3. **Local Delta processing** — tested PySpark Bronze, Silver, and Gold transformations.
4. **Infrastructure as code** — Terraform modules and Azure `plan` validation, with no automatic apply.
5. **Azure streaming** — Event Hubs, ADLS, and Databricks integration.
6. **Operations** — orchestration, observability, data quality, governance, and backfill procedures.
7. **Controlled delivery** — OIDC-based CI/CD and protected environment approvals.
8. **Kubernetes extension** — only for workloads that benefit from it, after the core platform is proven.

## Azure Deployment Policy

No workflow, script, or Terraform configuration will create Azure resources without explicit approval. Future CI will validate Terraform and publish plans; applying a plan will require a protected environment and a manual approval step.

## License

MIT. See [LICENSE](LICENSE).
