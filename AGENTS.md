---
file: AGENTS.md
description: Project instructions for coding agents
scope: repository
---

# AGENTS.md — workflow-orchestration-queue

> **Project:** Headless Agentic Orchestration Platform  
> **Repository:** intel-agency/workflow-orchestration-queue-papa89

## Project Overview

**workflow-orchestration-queue** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders. The system enables AI agents to operate as background production services, performing multi-step, specification-driven tasks without human intervention.

**Success Definition:** "Zero-Touch Construction" — a user opens a single specification issue and receives a functional, test-passed branch and PR within minutes.

### Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.12+ |
| Web Framework | FastAPI | 0.115+ |
| ASGI Server | Uvicorn | 0.34+ |
| Validation | Pydantic | 2.10+ |
| HTTP Client | HTTPX | 0.28+ |
| Package Manager | uv | 0.10+ |
| Testing | pytest | 8.3+ |
| Linting/Formatting | Ruff | 0.9+ |
| Type Checking | mypy | 1.14+ |
| Containerization | Docker, Docker Compose | - |
| AI Runtime | opencode CLI | 1.2.24+ |

---

## Setup Commands

```bash
# Install dependencies (including dev tools)
uv sync --all-extras

# Run the notifier service (FastAPI webhook receiver)
uv run uvicorn src.notifier_service:app --reload --port 8000

# Run the sentinel (polling service)
uv run python -m src.orchestrator_sentinel

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_work_item.py -v
```

### Code Quality Commands

```bash
# Lint code
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Format check (without modifying)
uv run ruff format --check src/ tests/

# Type check
uv run mypy src/
```

### Docker Commands

```bash
# Build and run all services
docker compose up --build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f
```

---

## Project Structure

```
workflow-orchestration-queue/
├── src/                           # Source code
│   ├── __init__.py
│   ├── notifier_service.py        # FastAPI webhook receiver (The Ear)
│   ├── orchestrator_sentinel.py   # Polling service (The Brain)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── work_item.py           # Unified WorkItem model
│   │   └── github_events.py       # Webhook payload schemas
│   └── queue/
│       ├── __init__.py
│       └── github_queue.py        # ITaskQueue + GitHubQueue
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_work_item.py          # WorkItem model tests
│   └── test_github_queue.py       # Queue implementation tests
├── docs/                          # Documentation
│   ├── architecture.md            # Architecture overview
│   └── api/                       # API documentation
├── scripts/                       # Utility scripts
│   ├── devcontainer-opencode.sh   # Shell-bridge dispatcher
│   ├── gh-auth.ps1                # GitHub auth helper
│   └── validate.ps1               # Validation script
├── plan_docs/                     # Planning documents (exclude from linting)
├── .github/workflows/             # CI/CD workflows
│   ├── app/                       # Application workflows
│   │   ├── build-test.yml
│   │   ├── docker.yml
│   │   └── security.yml
│   └── validate.yml               # Template validation
├── pyproject.toml                 # Project configuration
├── docker-compose.yml             # Multi-container orchestration
├── Dockerfile.sentinel            # Sentinel container
└── Dockerfile.notifier            # Notifier container
```

---

## Architecture

### 4-Pillar Architecture

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

### Components

| Pillar | File | Technology | Purpose |
|--------|------|------------|---------|
| **Ear** | `src/notifier_service.py` | FastAPI | Webhook receiver with HMAC verification |
| **State** | GitHub Issues + Labels | GitHub API | Task queue using labels as state machine |
| **Brain** | `src/orchestrator_sentinel.py` | Python async | Polling service with assign-then-verify locking |
| **Hands** | `scripts/devcontainer-opencode.sh` | DevContainer | Worker execution via opencode CLI |

### State Machine (Labels)

| Label | State | Description |
|-------|-------|-------------|
| `agent:queued` | Pending | Task validated, awaiting Sentinel |
| `agent:in-progress` | Active | Sentinel claimed, worker running |
| `agent:success` | Terminal | Task completed successfully |
| `agent:error` | Terminal | Task failed |
| `agent:infra-failure` | Sub-state | Container/build failure |
| `agent:impl-error` | Sub-state | Agent logic failure |

---

## Code Style

### General Rules

- **Line length:** 100 characters max (configured in pyproject.toml)
- **Python version:** 3.12+ (use modern syntax)
- **Type hints:** Required for all functions (enforced by mypy strict mode)
- **Imports:** Sorted by isort (via Ruff)

### Ruff Rules (from pyproject.toml)

```
E    - pycodestyle errors
W    - pycodestyle warnings
F    - Pyflakes
I    - isort
B    - flake8-bugbear
C4   - flake8-comprehensions
UP   - pyupgrade
ARG  - flake8-unused-arguments
SIM  - flake8-simplify
```

### Key Conventions

1. **Use modern Python syntax:**
   - Use `list[X]` instead of `List[X]`
   - Use `X | None` instead of `Optional[X]`
   - Use `enum.StrEnum` instead of `str, Enum`

2. **Async patterns:**
   - Use `asyncio` for all I/O operations
   - Use `httpx` for async HTTP calls
   - Use `pytest-asyncio` for async tests

3. **No hardcoded secrets:**
   - All credentials via environment variables
   - Use synthetic values in tests: `FAKE-KEY-FOR-TESTING-00000000`
   - Never use real prefixes (`sk-`, `ghp_`, `ghs_`, `AKIA`)

4. **GitHub Actions SHA pinning:**
   - All actions pinned to full commit SHA
   - Format: `uses: owner/action@<full-40-char-SHA> # vX.Y.Z`

---

## Testing Instructions

### Test Structure

- Tests live in `tests/` directory
- Use `conftest.py` for shared fixtures
- Test files named `test_*.py`
- Async tests supported via `pytest-asyncio`

### Running Tests

```bash
# All tests
uv run pytest

# With coverage (80% minimum required)
uv run pytest --cov=src --cov-report=term-missing

# Verbose output
uv run pytest -v

# Specific test file
uv run pytest tests/test_work_item.py

# Specific test
uv run pytest tests/test_work_item.py::TestScrubSecrets::test_scrub_github_pat
```

### Test Conventions

- Use `AsyncMock` for async function mocking
- Use `patch` for module-level mocking
- Always add or update tests for changed code
- Coverage threshold: 80% (configured in pyproject.toml)

---

## Configuration

### Required Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | All | GitHub PAT with repo, workflow scopes |
| `GITHUB_ORG` | Sentinel | Target organization |
| `GITHUB_REPO` | Sentinel | Target repository |
| `WEBHOOK_SECRET` | Notifier | HMAC verification key |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTINEL_BOT_LOGIN` | - | Bot account for distributed locking |

### Configuration Files

- `pyproject.toml` — Project metadata, dependencies, tool configs
- `.python-version` — Python version pin
- `docker-compose.yml` — Container orchestration

---

## PR and Commit Guidelines

### Before Committing

1. **Run linting:** `uv run ruff check src/ tests/`
2. **Run formatting:** `uv run ruff format src/ tests/`
3. **Run type check:** `uv run mypy src/`
4. **Run tests:** `uv run pytest --cov=src`
5. **Fix all issues before pushing**

### Commit Message Format

```
<type>: <short description>

# Types: feat, fix, docs, style, refactor, test, chore
# Examples:
#   feat: add webhook signature verification
#   fix: handle rate limit errors in queue fetch
#   test: add tests for scrub_secrets function
```

### Branch Naming

- Feature branches: `feature/<description>`
- Bug fixes: `fix/<description>`
- Dynamic workflow: `dynamic-workflow-<type>`

---

## Common Pitfalls

### Dependency Issues

- Always use `uv sync --all-extras` to install dev dependencies
- If commands fail with "No such file or directory", dev deps are missing

### Type Checking Failures

- All functions need return type annotations
- Use `-> None` for functions that don't return a value
- Abstract methods need return type annotations

### Import Sorting

- Run `uv run ruff check --fix src/ tests/` to auto-fix import order
- Ruff's isort rules enforce import ordering

### Async Tests

- Mark async test functions with `@pytest.mark.asyncio`
- Or rely on `asyncio_mode = "auto"` in pyproject.toml

### Credential Patterns

- Never commit real API keys or tokens
- Use `scrub_secrets()` when logging potentially sensitive data
- Test fixtures use synthetic values like `FAKE-KEY-FOR-TESTING-00000000`

---

## Security Considerations

- **HMAC Verification:** All webhooks validated against `WEBHOOK_SECRET`
- **Credential Scrubbing:** Automatic sanitization of tokens/keys in logs
- **Network Isolation:** Worker containers run in isolated Docker network
- **SHA-Pinned Actions:** All GitHub Actions pinned to full commit SHA
- **Non-root Containers:** Services run as unprivileged users

---

## References

- [Architecture Overview](./docs/architecture.md)
- [Repository Summary](./.ai-repository-summary.md)
- [Architecture Guide v3.2](./plan_docs/OS-APOW%20Architecture%20Guide%20v3.2.md)
- [Development Plan v4.2](./plan_docs/OS-APOW%20Development%20Plan%20v4.2.md)

---

<!-- ═══════════════════════════════════════════════════════════════════
     MANDATORY TOOL PROTOCOLS — ALL AGENTS MUST FOLLOW
     These are NON-NEGOTIABLE requirements for every agent in this system.
     Failure to follow these protocols is a critical defect.
     ═══════════════════════════════════════════════════════════════════ -->

<instructions>
  <mandatory_tool_protocols>
    <overview>
      ALL agents — orchestrator, specialists, and subagents — MUST use the following
      MCP tools as part of their standard operating procedure. These are not optional
      suggestions; they are mandatory requirements that apply to every non-trivial task.
      Agents that skip these protocols are operating incorrectly.
    </overview>

    <protocol id="sequential_thinking" enforcement="MANDATORY">
      <title>Sequential Thinking Tool — ALWAYS USE</title>
      <tool>sequential_thinking</tool>
      <when>
        EVERY non-trivial task. This means any task that involves more than a single
        obvious action. If in doubt, use it.
      </when>
      <required_usage_points>
        <point>At task START: Use sequential thinking to analyze the request, break it into steps, identify risks, and plan the approach BEFORE taking any action.</point>
        <point>At DECISION POINTS: Use sequential thinking when choosing between alternatives, evaluating trade-offs, or making architectural decisions.</point>
        <point>When DEBUGGING: Use sequential thinking to systematically isolate root causes.</point>
        <point>Before DELEGATION: The Orchestrator MUST use sequential thinking to plan the delegation tree, determine agent assignments, and define success criteria.</point>
      </required_usage_points>
      <violation>Skipping sequential thinking on a non-trivial task is a protocol violation. If an agent completes a complex task without invoking sequential_thinking, the work should be reviewed for quality issues.</violation>
    </protocol>

    <protocol id="knowledge_graph_memory" enforcement="MANDATORY">
      <title>Knowledge Graph Memory — ALWAYS USE</title>
      <tools>
        <tool>create_entities</tool>
        <tool>create_relations</tool>
        <tool>add_observations</tool>
        <tool>delete_entities</tool>
        <tool>delete_observations</tool>
        <tool>delete_relations</tool>
        <tool>read_graph</tool>
        <tool>search_nodes</tool>
        <tool>open_nodes</tool>
      </tools>
      <required_usage_points>
        <point>At task START: Call `read_graph` or `search_nodes` to retrieve existing context about the project, user preferences, prior decisions, and known patterns BEFORE planning or acting.</point>
        <point>After SIGNIFICANT WORK: Call `create_entities`, `add_observations`, or `create_relations` to persist important findings, decisions, patterns discovered, and context for future tasks.</point>
        <point>After COMPLETING a task: Store the outcome, any lessons learned, and follow-up items in the knowledge graph.</point>
        <point>When STARTING a new workflow or assignment: Search for prior related work, decisions, and context.</point>
      </required_usage_points>
      <what_to_store>
        <item>Project-specific patterns and conventions discovered during work</item>
        <item>User preferences and decisions that affect future tasks</item>
        <item>Architectural decisions and their rationale</item>
        <item>Error patterns and their resolutions</item>
        <item>Cross-task context that would otherwise be lost between sessions</item>
        <item>Workflow state and progress checkpoints</item>
      </what_to_store>
      <violation>Failing to read existing memory at task start or failing to persist important findings after task completion is a protocol violation.</violation>
    </protocol>

    <protocol id="change_validation" enforcement="MANDATORY">
      <title>Change Validation Protocol — ALWAYS FOLLOW</title>
      <when>
        After ANY non-trivial change to code, configuration, workflows, or infrastructure.
        This includes: logic changes, behavior changes, refactors, dependency updates,
        config changes, multi-file edits, workflow modifications.
      </when>
      <required_steps>
        <step order="1">Run linting: `uv run ruff check src/ tests/`</step>
        <step order="2">Run type checking: `uv run mypy src/`</step>
        <step order="3">Run tests: `uv run pytest --cov=src`</step>
        <step order="4">Fix ALL failures — do not skip, suppress, or ignore errors.</step>
        <step order="5">Re-run validation until ALL checks pass clean.</step>
        <step order="6">Only THEN proceed to commit and push.</step>
      </required_steps>
      <validation_commands>
        <command purpose="lint">uv run ruff check src/ tests/</command>
        <command purpose="format">uv run ruff format --check src/ tests/</command>
        <command purpose="type check">uv run mypy src/</command>
        <command purpose="test">uv run pytest --cov=src</command>
        <command purpose="full validation">uv run ruff check src/ tests/ && uv run mypy src/ && uv run pytest --cov=src</command>
      </validation_commands>
      <post_push>
        After push, monitor CI: `gh run list --limit 5`, `gh run watch &lt;id&gt;`, `gh run view &lt;id&gt; --log-failed`.
        If CI fails, STOP feature work, triage, fix, re-verify, push. Do NOT mark work complete while CI is red.
      </post_push>
      <violation>Committing or pushing code without running validation is a protocol violation. Marking a task complete while CI is failing is a protocol violation.</violation>
    </protocol>

    <agent_checklist>
      <!-- Agents: verify you have completed these items on every non-trivial task -->
      <item>☐ Called sequential_thinking at task start to plan approach</item>
      <item>☐ Called read_graph / search_nodes to retrieve prior context</item>
      <item>☐ Used sequential_thinking at key decision points during work</item>
      <item>☐ Ran validation (lint, type check, tests) before commit/push</item>
      <item>☐ Fixed all validation failures and re-verified clean</item>
      <item>☐ Persisted important findings to knowledge graph memory</item>
      <item>☐ Monitored CI after push and confirmed green</item>
    </agent_checklist>
  </mandatory_tool_protocols>

  <agent_specific_guardrails>
    <rule>The Orchestrator agent delegates to specialists via the `task` tool — never writes code directly.</rule>
    <rule>The Orchestrator MUST invoke `sequential_thinking` before planning any delegation and `read_graph` before every new task to load prior project context.</rule>
    <rule>ALL agents MUST follow the mandatory_tool_protocols defined above — sequential thinking, memory, and change validation are not optional.</rule>
    <rule>Use `scrub_secrets()` when logging any data that might contain credentials.</rule>
    <rule>Never commit real API keys, tokens, or secrets. Use synthetic values in tests.</rule>
  </agent_specific_guardrails>

  <tool_use_instructions>
    <instruction id="sequential_thinking_default_usage" enforcement="MANDATORY">
      <applyTo>*</applyTo>
      <title>Sequential Thinking — MANDATORY for all non-trivial tasks</title>
      <tools><tool>sequential_thinking</tool></tools>
      <guidance>
        **MUST USE** for all non-trivial requests. This is a mandatory protocol, not a suggestion.
        See `mandatory_tool_protocols.sequential_thinking` for full requirements.
        Invoke at: task start (planning), decision points, debugging, and before delegation.
        Skipping this tool on complex tasks is a protocol violation.
      </guidance>
    </instruction>
    <instruction id="memory_default_usage" enforcement="MANDATORY">
      <applyTo>*</applyTo>
      <title>Knowledge Graph Memory — MANDATORY for all non-trivial tasks</title>
      <tools><tool>create_entities</tool><tool>create_relations</tool><tool>add_observations</tool><tool>delete_entities</tool><tool>delete_observations</tool><tool>delete_relations</tool><tool>read_graph</tool><tool>search_nodes</tool><tool>open_nodes</tool></tools>
      <guidance>
        **MUST USE** for all non-trivial requests. This is a mandatory protocol, not a suggestion.
        See `mandatory_tool_protocols.knowledge_graph_memory` for full requirements.
        Invoke at: task start (read_graph/search_nodes), after significant work (create_entities/add_observations),
        and after task completion (persist outcomes and lessons learned).
        Skipping memory operations is a protocol violation.
      </guidance>
    </instruction>
  </tool_use_instructions>
</instructions>
