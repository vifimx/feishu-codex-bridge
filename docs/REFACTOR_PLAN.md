# Feishu Codex Bridge Refactor Plan

This bridge has grown past the point where a single Python file is easy to change safely. Since local compatibility is not a requirement, the next architecture should optimize for clear ownership, small modules, and explicit state transitions.

## Goals

- Keep the runtime local-first and easy to audit.
- Make message routing, access control, job execution, sessions, and dashboard API independently testable.
- Replace implicit dict mutation with typed config/state objects.
- Make new conversation modes and Feishu transport features additive instead of cross-cutting edits.
- Keep dashboard writes constrained and explicit.

## Proposed Layout

```text
feishu_codex_bridge/
  app.py                    # CLI entrypoint and process wiring
  config.py                 # config schema, validation, dashboard write allowlist
  logging.py                # JSONL logs and redaction helpers
  access.py                 # identities, groups, contact resolution, policy merge
  transport/
    lark.py                 # lark-cli calls, message send/reply/update/download
    events.py               # event subscription and polling adapters
  conversations.py          # continuous/topic session keys and conversation store
  jobs/
    store.py                # job JSON files, reconciliation, cleanup
    scheduler.py            # queueing, per-conversation serialization
    runner.py               # codex exec invocation and session detection
    prompt.py               # prompt assembly and attachment context
  commands.py               # /cmd, /ask, preset task parsing
  dashboard/
    api.py                  # HTTP API handlers
    static/                 # current HTML/CSS/JS
  windows.py                # Start Menu and Scheduled Task integration
  tests/
```

## State Model

- `Config`: validated config object with defaults applied on load.
- `IncomingMessage`: normalized Feishu event/polling message.
- `AccessPolicy`: resolved sender/chat permissions.
- `Conversation`: `key`, `mode`, `topic_ids`, `session_id`, `last_job_id`.
- `Job`: explicit status enum, source message, conversation key, codex options, artifacts.
- `RouteDecision`: command, preset task, codex job, guidance, ignored, denied.

## Message Flow

```text
raw Feishu event
  -> normalize IncomingMessage
  -> dedupe message id
  -> resolve AccessPolicy
  -> parse RouteDecision
  -> resolve Conversation
  -> create Job or send command reply
  -> scheduler starts eligible jobs
  -> runner updates Job
  -> transport updates status card/final reply
  -> conversation store records Codex session
```

## Why This Helps AI Edits

- A future change to topic mode should mostly touch `conversations.py` and scheduler tests.
- A future change to Feishu cards should mostly touch `transport/lark.py`.
- A future change to permissions should mostly touch `access.py`.
- Dashboard write behavior becomes config-schema driven instead of scattered allowlist edits.
- Tests can cover routing and persistence without starting lark-cli or codex.

## Suggested Migration

1. Add package skeleton and pure dataclasses without changing behavior.
2. Move config loading/coercion into `config.py`.
3. Move access policy and contact cache into `access.py` with unit tests.
4. Move conversation key logic into `conversations.py` with continuous/topic tests.
5. Move job store/scheduler/runner into `jobs/`.
6. Move lark-cli send/reply/update/download into `transport/lark.py`.
7. Replace the old monolithic entrypoint with `app.py`.
8. Delete old compatibility shims once dry-run and dashboard tests pass.

