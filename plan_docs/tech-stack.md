# Technology Stack - workflow-orchestration-queue

**Project:** workflow-orchestration-queue  
**Repository:** intel-agency/workflow-orchestration-queue-papa89  
**Last Updated:** 2026-03-29

---

## Runtime & Languages

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Primary Language** | Python | 3.12+ | Core orchestrator, webhook receiver, system logic |
| **Shell Scripts** | Bash / PowerShell Core | pwsh 7.x | CLI interactions, cross-platform automation |

---

## Web Framework & API

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async webhook receiver (The Ear) |
| **ASGI Server** | Uvicorn | Production server for FastAPI application |
| **Validation** | Pydantic v2 | Strict data validation, settings management, schemas |

---

## HTTP & Async

| Component | Technology | Purpose |
|-----------|------------|---------|
| **HTTP Client** | HTTPX (async) | Non-blocking GitHub REST API calls |
| **Async Runtime** | asyncio | Background polling, concurrent operations |

---

## Package Management

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Package Manager** | uv | 0.10.x+ | Rust-based fast dependency management |
| **Lock File** | uv.lock | — | Deterministic package versions |
| **Project Config** | pyproject.toml | — | Project metadata and dependencies |

---

## Containerization

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Container Runtime** | Docker | Worker isolation, environment consistency |
| **Dev Environment** | DevContainers | Reproducible AI worker environment |
| **Orchestration** | Docker Compose | Multi-container workflows |

---

## AI/Agent Runtime

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent CLI** | opencode CLI | AI agent runtime (v1.2.24+) |
| **LLM Providers** | ZhipuAI GLM, OpenAI, Kimi, Google Gemini | Model backends for agents |

---

## Authentication & Security

| Component | Technology | Purpose |
|-----------|------------|---------|
| **GitHub Auth** | GitHub App Installation Tokens | API authentication with scoped permissions |
| **Webhook Security** | HMAC SHA256 | Cryptographic payload verification |
| **Token Management** | Ephemeral env vars | Least-privilege credential injection |

---

## State Management

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Queue Backend** | GitHub Issues + Labels | "Markdown as a Database" state machine |
| **Label States** | agent:queued, agent:in-progress, agent:success, agent:error, agent:infra-failure | Task lifecycle tracking |

---

## Observability

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Logging** | Python logging (stdout) | Structured service logs |
| **Heartbeat** | GitHub Issue comments | User-visible progress updates |
| **API Docs** | Swagger/OpenAPI (auto-generated) | Interactive API documentation |

---

## External Dependencies

| Dependency | Required For | Notes |
|------------|--------------|-------|
| `GH_ORCHESTRATION_AGENT_TOKEN` | GitHub API operations | PAT with repo, workflow, project, read:org scopes |
| `WEBHOOK_SECRET` | Notifier service | HMAC verification key |
| `SENTINEL_BOT_LOGIN` | Task locking | Bot account login for assign-then-verify |

---

## Development Tools

| Tool | Purpose |
|------|---------|
| **gh CLI** | GitHub API interactions |
| **actionlint** | Workflow YAML validation |
| **gitleaks** | Secret scanning |
| **shellcheck** | Shell script linting |
| **pytest** | Test framework (when implemented) |

---

## Constraints & Standards

- **GitHub Actions**: Must be pinned to full commit SHA (not version tags)
- **DevContainer Image**: Prebuilt from `intel-agency/workflow-orchestration-prebuild`
- **No curl in Docker healthchecks**: Use Python stdlib instead
- **No hardcoded secrets**: All credentials via environment variables
