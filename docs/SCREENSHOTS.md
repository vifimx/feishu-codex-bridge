# Screenshots

This page keeps repository screenshots separate from live runtime data.

## Dashboard Overview

![Dashboard overview](assets/dashboard-overview.png)

The dashboard screenshot should be generated from a temporary config based on `bridge.config.example.json`, not from a real `bridge.config.json`.

Before committing a screenshot, check that it does not contain:

- real Feishu/Lark open IDs, chat IDs, app IDs, document URLs, or user names
- local user paths
- job prompts, logs, attachments, or Codex session IDs
- tokens or secrets

## Regeneration Notes

One safe workflow is:

1. Copy `bridge.config.example.json` to a temporary directory outside the repository.
2. Point `log_dir` and `state_dir` at a temporary directory.
3. Start `feishu_codex_bridge.py --dashboard-only` on a non-default local port.
4. Capture the dashboard through a headless browser.
5. Review the PNG before staging it.

Keep committed screenshots under `docs/assets/`.
