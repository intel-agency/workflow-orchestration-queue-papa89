# Architecture Overview - workflow-orchestration-queue

**Project:** workflow-orchestration-queue  
**Repository:** intel-agency/workflow-orchestration-queue-papa89  
**Last Updated:** 2026-03-29

---

## Executive Summary

workflow-orchestration-queue is a **headless agentic orchestration platform** that transforms GitHub Issues into autonomous execution orders. The system moves AI from a passive co-pilot role to a background production service capable of multi-step, specification-driven task fulfillment without human intervention.

**Core Innovation:** "Zero-Touch Construction" — a user opens a single specification issue and receives a functional, test-passed branch and PR within minutes.

---

## 4-Pillar Architecture

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

---

## Pillar 1: The Ear (Work Event Notifier)

**File:** `src/notifier_service.py`  
**Technology:** FastAPI + Uvicorn + Pydantic

### Responsibilities
- **Secure Webhook Ingestion**: Exposes `/webhooks/github` endpoint
- **HMAC Verification**: Validates `X-Hub-Signature-256` against `WEBHOOK_SECRET`
- **Intelligent Triage**: Parses issue titles/bodies for template detection
- **Queue Initialization**: Applies `agent:queued` label via GitHub API

### Key Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhooks/github` | POST | GitHub webhook receiver |
| `/health` | GET | Service health check |

---

## Pillar 2: The State (Work Queue)

**Implementation:** GitHub Issues + Labels (Markdown as a Database)

### State Machine
```
                    ┌─────────────────┐
                    │  agent:queued   │
                    └────────┬────────┘
                             │ Sentinel claims
                             ▼
                    ┌─────────────────┐
          ┌────────│agent:in-progress│◀───────┐
          │        └────────┬────────┘        │
          │                 │                 │
    Reconciliation   ┌──────┴──────┐    Re-queue
     (stale task)    │             │    (PR changes)
          │          ▼             ▼          │
          │   ┌───────────┐ ┌────────────┐    │
          └──▶│agent:     │ │agent:      │◀───┘
              │  success  │ │  error     │
              └───────────┘ └────────────┘
                    │              │
                    │         ┌────┴────┐
                    │         │         │
                    │    ┌────┴───┐ ┌───┴────┐
                    │    │agent:  │ │agent:  │
                    │    │infra-  │ │impl-   │
                    │    │failure │ │error   │
                    │    └────────┘ └────────┘
                    │
              Terminal States
```

### Label Taxonomy
| Label | State | Description |
|-------|-------|-------------|
| `agent:queued` | Pending | Task validated, awaiting Sentinel |
| `agent:in-progress` | Active | Sentinel claimed, worker running |
| `agent:success` | Terminal | Task completed successfully |
| `agent:error` | Terminal | Task failed (categorized below) |
| `agent:infra-failure` | Sub-state | Container/build failure |
| `agent:impl-error` | Sub-state | Agent logic failure |
| `agent:stalled-budget` | Sub-state | Cost threshold exceeded |

---

## Pillar 3: The Brain (Sentinel Orchestrator)

**File:** `src/orchestrator_sentinel.py`  
**Technology:** Python async service + HTTPX

### Responsibilities
- **Resilient Polling**: 60-second intervals with jittered exponential backoff
- **Task Claiming**: Assign-then-verify pattern for concurrency control
- **Shell-Bridge Dispatch**: Invokes `devcontainer-opencode.sh` for worker execution
- **Heartbeat Updates**: Posts progress comments every 5 minutes
- **Graceful Shutdown**: Handles SIGTERM/SIGINT, finishes current task

### Polling Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Poll      │────▶│   Claim     │────▶│   Execute   │
│  (60s)      │     │ (Lock)      │     │ (Worker)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
      │                   │                    │
      │                   │                    │
      ▼                   ▼                    ▼
 ┌─────────┐        ┌─────────┐         ┌─────────┐
 │Backoff  │        │ Verify  │         │Heartbeat│
 │on 403   │        │ Assign  │         │(5 min)  │
 └─────────┘        └─────────┘         └─────────┘
```

### Concurrency Control (Assign-then-Verify)
1. Attempt to assign `SENTINEL_BOT_LOGIN` to issue
2. Re-fetch issue via GitHub API
3. Verify `SENTINEL_BOT_LOGIN` is in assignees array
4. Only then proceed with label updates and execution

---

## Pillar 4: The Hands (Opencode Worker)

**Technology:** opencode CLI + DevContainer  
**Environment:** Prebuilt image from `intel-agency/workflow-orchestration-prebuild`

### Responsibilities
- **Code Generation**: Executes LLM-driven code changes
- **Test Execution**: Runs local test suites before PR submission
- **Context Awareness**: Uses vector-indexed codebase view

### Shell-Bridge Commands
| Command | Purpose | Timeout |
|---------|---------|---------|
| `devcontainer-opencode.sh up` | Provision environment | 60s |
| `devcontainer-opencode.sh start` | Start opencode server | 30s |
| `devcontainer-opencode.sh prompt` | Execute agent task | 95 min |

---

## Key Architectural Decisions (ADRs)

### ADR-07: Shell-Bridge Execution
**Decision:** Orchestrator interacts with worker exclusively via `devcontainer-opencode.sh`  
**Rationale:** Guarantees environment parity between AI and human developers  
**Benefit:** Python code stays lightweight; shell scripts handle container complexity

### ADR-08: Polling-First Resiliency
**Decision:** Polling as primary discovery; webhooks as optimization  
**Rationale:** Self-healing on restart; no lost events during downtime  
**Benefit:** System reconciles state automatically after crashes

### ADR-09: Provider-Agnostic Interface
**Decision:** `ITaskQueue` ABC with `GitHubQueue` implementation  
**Rationale:** Enables future provider swapping (Linear, Notion, Redis)  
**Note:** Kept for extensibility despite single current implementation

---

## Security Model

### Network Isolation
- Worker containers run in dedicated Docker network
- Cannot access host internal subnets
- Blocked from peer containers

### Credential Management
| Aspect | Implementation |
|--------|----------------|
| **Scoping** | GitHub App Installation Tokens (scoped permissions) |
| **Injection** | Ephemeral environment variables |
| **Cleanup** | Destroyed on container exit |
| **Scrubbing** | `scrub_secrets()` removes PATs, API keys from logs |

### Credential Scrubbing Patterns
```
ghp_*     - GitHub Personal Access Tokens
ghs_*     - GitHub Server Tokens
gho_*     - GitHub OAuth Tokens
github_pat_* - GitHub Fine-grained PATs
sk-*      - OpenAI API Keys
Bearer    - Auth headers
```

---

## Data Flow (Happy Path)

```
1. User opens issue → [Application Plan] Create X
2. Webhook hits Notifier → validates HMAC
3. Notifier triages → applies agent:queued
4. Sentinel polls → discovers queued issue
5. Sentinel claims → assign-then-verify
6. Sentinel executes → devcontainer-opencode.sh prompt
7. Worker runs → creates child issues / code
8. Sentinel finalizes → agent:success + PR link
```

---

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml                 # uv dependencies
├── uv.lock                        # Lockfile
├── src/
│   ├── notifier_service.py        # FastAPI webhook (Ear)
│   ├── orchestrator_sentinel.py   # Polling service (Brain)
│   ├── models/
│   │   ├── work_item.py           # Unified WorkItem model
│   │   └── github_events.py       # Webhook payload schemas
│   └── queue/
│       └── github_queue.py        # ITaskQueue + GitHubQueue
├── scripts/
│   ├── devcontainer-opencode.sh   # Shell-bridge dispatcher
│   ├── gh-auth.ps1                # GitHub auth sync
│   └── update-remote-indices.ps1  # Vector indexing
└── local_ai_instruction_modules/  # Markdown workflow logic
```

---

## Self-Bootstrapping Lifecycle

1. **Phase 0 (Seed)**: Manual clone from template repo
2. **Phase 1 (MVP)**: Sentinel becomes operational
3. **Phase 2 (Enhance)**: System builds its own webhook layer
4. **Phase 3 (Evolve)**: AI manages its own development

---

## Constraints & Standards

- **GitHub Actions**: SHA-pinned (no version tags)
- **Docker Healthchecks**: Python stdlib only (no curl)
- **Resource Limits**: 2 CPUs / 4GB RAM per worker
- **Subprocess Timeout**: 95 min max (with inner 90 min watchdog)
