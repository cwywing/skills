# Sample Plan: Health Endpoint

## Goal

Add a minimal health check HTTP endpoint for ops probes.

## Scope

- Implement `GET /health` returning JSON `{"ok": true}`
- Add a short note in README (or existing API docs) about the endpoint
- Keep changes minimal

## Out of scope

- Auth, metrics, fancy readiness/liveness split

## Suggested tasks

1. Implement the health route in the existing web stack
2. Add/adjust a smoke test or curl-based verification note

## Acceptance (overall)

- Calling the health endpoint returns HTTP 200 and `{"ok": true}`
- Documentation mentions how to call it
