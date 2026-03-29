# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the workflow-orchestration-queue project.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs help future developers understand the "why" behind architectural choices.

## ADR Index

| Number | Title | Status |
|--------|-------|--------|
| ADR-001 | Python as Primary Language | Accepted |
| ADR-002 | FastAPI for Web Framework | Accepted |
| ADR-003 | GitHub Issues as State Machine | Accepted |
| ADR-004 | Shell-Bridge Execution Pattern | Accepted |
| ADR-005 | Polling-First Resiliency | Accepted |

## Creating New ADRs

When making a significant architectural decision:

1. Copy `template.md` to `NNNN-title-with-dashes.md`
2. Fill in the sections
3. Submit with your PR

## Template

```markdown
# ADR-NNNN: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Context

[What is the issue we're addressing?]

## Decision

[What is the change we're proposing/have made?]

## Consequences

[What are the positive and negative effects of this decision?]
```
