# Architecture Overview

> **Note:** This document provides a summary of the architecture. For detailed technical specifications, see the [plan_docs/](../plan_docs/) directory.

## System Overview

workflow-orchestration-queue is a headless agentic orchestration platform built on a 4-pillar architecture:

1. **The Ear (Notifier)** — FastAPI webhook receiver for event ingestion
2. **The State (Queue)** — GitHub Issues as distributed state machine
3. **The Brain (Sentinel)** — Background polling and dispatch service
4. **The Hands (Worker)** — opencode CLI in isolated DevContainer

## Core Components

### Notifier Service (`src/notifier_service.py`)

The Notifier is the entry point for external events:

- **Endpoints:**
  - `POST /webhooks/github` — Receives GitHub webhooks
  - `GET /health` — Health check endpoint

- **Security:**
  - HMAC SHA256 signature verification
  - Environment variable validation at startup

- **Responsibilities:**
  - Validate webhook signatures
  - Parse and triage incoming events
  - Apply initial labels (`agent:queued`)
  - Generate WorkItem manifests

### Sentinel Service (`src/orchestrator_sentinel.py`)

The Sentinel is the orchestrating brain:

- **Polling:**
  - 60-second default interval
  - Jittered exponential backoff on rate limits
  - Max backoff: 960 seconds (16 minutes)

- **Task Claiming:**
  - Assign-then-verify distributed locking
  - Concurrency-safe task acquisition

- **Execution:**
  - Shell-bridge dispatch via `devcontainer-opencode.sh`
  - 95-minute subprocess timeout safety net
  - Environment reset between tasks

- **Heartbeat:**
  - Progress comments every 5 minutes
  - Timestamp and elapsed time tracking

### Queue Interface (`src/queue/github_queue.py`)

The queue abstraction layer:

- **ITaskQueue** — Abstract interface for provider swapping
- **GitHubQueue** — GitHub Issues implementation

### Data Models (`src/models/`)

Unified models shared across components:

- **WorkItem** — Canonical task representation
- **TaskType** — PLAN, IMPLEMENT, BUGFIX
- **WorkItemStatus** — Label-mapped states

## State Machine

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
```

## Security Model

### Credential Management

| Aspect | Implementation |
|--------|----------------|
| Scoping | GitHub App Installation Tokens |
| Injection | Ephemeral environment variables |
| Cleanup | Destroyed on container exit |
| Scrubbing | `scrub_secrets()` removes PATs, API keys |

### Network Isolation

- Worker containers run in dedicated Docker network
- Cannot access host internal subnets
- Blocked from peer containers

## Key Architectural Decisions

### ADR-004: Shell-Bridge Execution

**Decision:** Orchestrator interacts with worker exclusively via `devcontainer-opencode.sh`

**Rationale:** Guarantees environment parity between AI and human developers

**Benefit:** Python code stays lightweight; shell scripts handle container complexity

### ADR-005: Polling-First Resiliency

**Decision:** Polling as primary discovery; webhooks as optimization

**Rationale:** Self-healing on restart; no lost events during downtime

**Benefit:** System reconciles state automatically after crashes

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

## Related Documentation

- [Tech Stack](../plan_docs/tech-stack.md)
- [Architecture Guide v3.2](../plan_docs/OS-APOW%20Architecture%20Guide%20v3.2.md)
- [Development Plan v4.2](../plan_docs/OS-APOW%20Development%20Plan%20v4.2.md)
