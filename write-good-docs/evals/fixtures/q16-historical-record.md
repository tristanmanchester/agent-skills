## ADR supplied for editing

# ADR 003: Session storage

Date: 2024-03-12
Status: Accepted

## Context

At the time of this decision, the prototype is deployed as one process. The team has no database service.

## Decision

Use in-memory session storage for the prototype.

## Consequences

It is important to note that a process restart ends all active sessions.

## Later context, not part of the ADR

A 2026 implementation uses an external database. No superseding ADR is supplied.
