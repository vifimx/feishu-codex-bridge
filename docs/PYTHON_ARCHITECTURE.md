# Python Runtime Architecture

The Python runtime remains the production path for the local bridge. Keep the direct `python feishu_codex_bridge.py` launchers compatible while extracting stable seams into small importable modules.

## Current Shape

```text
feishu_codex_bridge.py
  CLI entrypoint, Bridge orchestration, dashboard HTTP handler, Lark transport,
  job scheduling, Codex process execution, session tracking, and reply handling.

feishu_bridge/
  config_store.py     config load/validate/coerce/write/backup policy
  runtime_paths.py    derived log/state/job/artifact paths
```

## Refactor Direction

Prefer small modules with explicit state ownership:

- `config_store`: JSON config loading, dotted-key updates, type coercion, write allowlist, backups.
- `access_policy`: identity/group matching and permission merging.
- `transport_lark`: `lark-cli` command boundary, message normalization, replies, resource downloads.
- `job_store`: job JSON/JSONL persistence, reconciliation, cleanup.
- `codex_runner`: prompt building, CLI argument construction, process waiting, result/session discovery.
- `dashboard_api`: HTTP routes and response shaping only.
- `windows_integration`: shortcuts, Scheduled Tasks, process-tree termination.

The main `Bridge` object should become a coordinator that wires these modules together instead of owning every behavior directly.

## Packaging Note

Keep the current flat runtime entrypoint until the Windows launch scripts are moved to an installed console entrypoint. A later `src/` layout is reasonable once installation is part of the normal workflow; until then, incremental package extraction preserves the existing local launcher behavior.
