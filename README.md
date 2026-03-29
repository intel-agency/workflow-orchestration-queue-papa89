# workflow-orchestration-queue

**Headless Agentic Orchestration Platform**

[![Build & Test](https://github.com/intel-agency/workflow-orchestration-queue-papa89/actions/workflows/app/build-test.yml/badge.svg)](https://github.com/intel-agency/workflow-orchestration-queue-papa89/actions/workflows/app/build-test.yml)
[![Security Scan](https://github.com/intel-agency/workflow-orchestration-queue-papa89/actions/workflows/app/security.yml/badge.svg)](https://github.com/intel-agency/workflow-orchestration-queue-papa89/actions/workflows/app/security.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

workflow-orchestration-queue is a headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders. The system moves AI from a passive co-pilot role to a background production service capable of multi-step, specification-driven task fulfillment without human intervention.

**Success Definition:** "Zero-Touch Construction" — a user opens a single specification issue and receives a functional, test-passed branch and PR within minutes.

> 📖 **Repository Summary:** See [.ai-repository-summary.md](./.ai-repository-summary.md) for a complete overview of this project.

## Features

- **Secure Webhook Ingestion** — HMAC SHA256 verification for all incoming GitHub events
- **Resilient Task Polling** — 60-second intervals with jittered exponential backoff
- **Concurrency Control** — Assign-then-verify pattern prevents race conditions
- **Shell-Bridge Execution** — Worker dispatch via devcontainer-opencode.sh
- **Automated Status Feedback** — Heartbeat comments every 5 minutes
- **Credential Scrubbing** — Automatic sanitization of secrets in public logs
- **Intelligent Triage** — Template detection for automatic issue classification
- **Graceful Shutdown** — SIGTERM/SIGINT handling with task completion

## Architecture

The system follows a 4-Pillar architecture:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    workflow-orchestration-queue                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │     EAR      │    │    STATE     │    │    BRAIN     │          │
│   │  (Notifier)  │───▶│   (Queue)    │◀───│  (Sentinel)  │          │
│   │   FastAPI    │    │ GitHub Issues│    │   Python     │          │
│   └──────────────┘    └──────────────┘    └──────┬───────┘          │
│                                                   │                  │
│                                                   ▼                  │
│                                          ┌──────────────┐            │
│                                          │    HANDS     │            │
│                                          │   (Worker)   │            │
│                                          │  DevContainer│            │
│                                          └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

See [Architecture Overview](./docs/architecture.md) for details.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for containerized execution)
- GitHub PAT with appropriate scopes

### Installation

```bash
# Clone the repository
git clone https://github.com/intel-agency/workflow-orchestration-queue-papa89.git
cd workflow-orchestration-queue-papa89

# Install dependencies
uv sync --dev

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### Running Locally

```bash
# Run the notifier service
uv run uvicorn src.notifier_service:app --reload --port 8000

# Run the sentinel (in another terminal)
uv run python -m src.orchestrator_sentinel
```

### Running with Docker

```bash
# Build and run all services
docker compose up --build

# Run in detached mode
docker compose up -d
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub PAT with repo, workflow scopes |
| `GITHUB_ORG` | Yes (Sentinel) | Target GitHub organization |
| `GITHUB_REPO` | Yes (Sentinel) | Target repository name |
| `WEBHOOK_SECRET` | Yes (Notifier) | HMAC verification key |
| `SENTINEL_BOT_LOGIN` | No | Bot account login for locking |

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_work_item.py -v
```

### Code Quality

```bash
# Lint with Ruff
uv run ruff check src/ tests/

# Format check
uv run ruff format --check src/ tests/

# Type check with mypy
uv run mypy src/
```

## Project Structure

```
workflow-orchestration-queue/
├── src/
│   ├── __init__.py
│   ├── notifier_service.py       # FastAPI webhook receiver (Ear)
│   ├── orchestrator_sentinel.py  # Polling service (Brain)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── work_item.py          # Unified WorkItem model
│   │   └── github_events.py      # Webhook payload schemas
│   └── queue/
│       ├── __init__.py
│       └── github_queue.py       # ITaskQueue + GitHubQueue
├── tests/
│   ├── conftest.py
│   ├── test_work_item.py
│   └── test_github_queue.py
├── docs/
│   ├── architecture.md
│   └── api/
├── scripts/
│   └── devcontainer-opencode.sh
├── pyproject.toml
├── Dockerfile.sentinel
├── Dockerfile.notifier
└── docker-compose.yml
```

## Documentation

- [Architecture Overview](./docs/architecture.md)
- [API Documentation](./docs/api/) (auto-generated via FastAPI)
- [Repository Summary](./.ai-repository-summary.md)

## Security

- All GitHub Actions are SHA-pinned for supply chain security
- Docker healthchecks use Python stdlib (no curl dependency)
- Credential scrubbing prevents secret leakage in logs
- HMAC verification for all webhook payloads

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

---

Built with ❤️ by the Intel Agency team
