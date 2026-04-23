# Feishu Codex Bridge

Local bridge from Feishu/Lark bot messages to the Codex CLI.

The project is designed to stay small and auditable:

- Feishu/Lark transport uses the official `lark-cli`.
- Codex execution uses the local `codex exec` command.
- Runtime state is plain JSON/JSONL files.
- The dashboard is served from localhost by the same Python runtime.
- Real local config is intentionally ignored by git.

## Features

- Long-connection Feishu event subscriber via `lark-cli event +subscribe`.
- Optional private-chat polling fallback for direct messages.
- Allowlisted users, chats, workspaces, and fixed commands.
- Tiered access: trusted users can run free-form Codex jobs, limited users can only run approved preset tasks and commands.
- UTF-8 plain-text replies to avoid Chinese text and code block corruption.
- Multimodal intake: image/file/audio/video resources can be downloaded through `lark-cli`.
- Images are attached to `codex exec --image` when supported.
- Per-request job records with status, logs, artifacts, output file paths, and Codex session deeplinks when detectable.
- Local dashboard for status, logs, jobs, capabilities, and constrained config editing.
- Future peer-routing metadata for multi-Codex deployments, disabled by default.

## Requirements

- Windows PowerShell.
- Python 3.12 or newer.
- `lark-cli` configured for a Feishu/Lark app.
- `codex` CLI available on `PATH`.

## Project Layout

```text
.
  dashboard/
    index.html
    dashboard.css
    dashboard.js
  .github/workflows/ci.yml
  bridge.config.example.json
  feishu_codex_bridge.py
  Initialize-GitHubCli.ps1
  Initialize-LarkCli.ps1
  Open-FeishuCodexBridgeDashboard.ps1
  Start-FeishuCodexBridge.ps1
  Stop-FeishuCodexBridge.ps1
  docs/GITHUB_AUTH.md
```

## Configuration

Copy the example config and fill in local values:

```powershell
Copy-Item .\bridge.config.example.json .\bridge.config.json
```

Then edit:

- `machine_id`
- `log_dir`
- `state_dir`
- `workspaces`
- `private.allowed_sender_open_ids`
- `private.allowed_chat_ids`
- `public.allowed_sender_open_ids`
- `public.allowed_chat_ids`
- `access.trusted_sender_open_ids`
- `access.limited_sender_open_ids`
- `access.limited_allowed_commands`
- `access.limited_allowed_task_ids`
- `preset_tasks`

`bridge.config.json` is ignored by git because it normally contains local paths, chat IDs, open IDs, and deployment choices.

## GitHub Maintenance

Install and authenticate GitHub CLI:

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -Login -SetupGit
```

Create a local ignored shell-token template:

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -CreateLocalEnv
```

See [docs/GITHUB_AUTH.md](docs/GITHUB_AUTH.md) for browser login, token prompt, `GH_TOKEN`, and remote creation workflows.

## Start / Stop

Validate the runtime and config without connecting to Feishu:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-FeishuCodexBridge.ps1 -DryRun
```

Start the bridge:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-FeishuCodexBridge.ps1
```

Stop the bridge, dashboard, and active bridge-started Codex jobs:

```powershell
powershell -ExecutionPolicy Bypass -File .\Stop-FeishuCodexBridge.ps1
```

## Dashboard

Start the dashboard without starting Feishu event listening:

```powershell
powershell -ExecutionPolicy Bypass -File .\Open-FeishuCodexBridgeDashboard.ps1
```

Default URL:

```text
http://127.0.0.1:8765/
```

The same dashboard is also served when the bridge is running and `health_server.enabled=true`.

Dashboard endpoints:

```text
GET  /                         HTML dashboard
GET  /api/status               machine, capability, pid, and job summary
GET  /api/jobs?limit=30        recent job list
GET  /api/jobs/<job_id>        full job JSON
GET  /api/logs?limit=120       recent bridge log entries
GET  /api/config               current config and editable key allowlist
POST /api/config               loopback-only config patch for allowlisted fields
```

Config writes are intentionally constrained:

- The server must see the client as loopback.
- `dashboard.allow_config_write` must be true.
- Only the allowlisted keys in `feishu_codex_bridge.py` can be changed.
- Every write creates a timestamped `bridge.config.json.*.bak` backup before replacing the config.
- Some changes, such as `health_server.*`, need a restart to affect the already-running server.

Keep the dashboard bound to `127.0.0.1`. Do not expose it on a public interface without adding an authentication layer.

## Feishu Commands

Identity and onboarding:

```text
/codex-id
```

Built-ins:

```text
/cmd help
/cmd status
/cmd status <job_id>
/cmd history
/cmd capabilities
/cmd peers
```

Fixed commands from `bridge.config.json`:

```text
/cmd doctor
/cmd auth
```

Preset tasks:

```text
/cmd <preset_task> [input]
/task <preset_task> [input]
```

Codex jobs:

```text
/codex [@machine_id] [workspace=name] <prompt>
```

Private chat can treat all allowlisted text as Codex prompts when `private.treat_all_text_as_codex=true`.

Group chat can do the same when `public.treat_all_text_as_codex=true`; keep this false for noisy groups.

## Access Model

The bridge separates senders into two tiers:

- `access.trusted_sender_open_ids`: full bridge operators. They can run free-form `/codex`, fixed commands, and preset tasks when the chat route is allowlisted.
- `access.limited_sender_open_ids`: constrained users. They can only run `access.limited_allowed_commands` and `access.limited_allowed_task_ids`.

For backward compatibility, `authorized_sender_open_ids` is also treated as trusted.

Limited users never get a free-form Codex prompt. Their messages can only map to a configured preset task:

```json
"preset_tasks": {
  "review-update": {
    "enabled": true,
    "aliases": ["review-update", "评审更新", "更新评审"],
    "workspace": "default",
    "required_skills": ["feishu", "lark-doc", "lark-base", "lark-sheets"],
    "prompt_template": "Use the listed Feishu/Lark skills to handle only this preset task...\\n{input}\\n"
  }
}
```

Preset recognition is deterministic: explicit `/task <id>`, `/cmd <id>`, or alias matching when `access.enable_preset_intent_matching=true`. The preset prompt may instruct Codex to use existing skills to understand Feishu documents, Base records, sheets, or review content, but the task scope remains the configured preset.

## Job State

Each Codex request becomes a JSON job under:

```text
<state_dir>/jobs/job-YYYYMMDD-HHMMSS-XXXXXXXX.json
```

The job records:

- prompt, workspace, and cwd
- source chat/message/sender
- downloaded attachment paths
- status: `queued`, `running`, `completed`, `failed`, `timed_out`, or `stopped`
- worker and Codex process IDs
- output file paths
- inferred Codex session path and `codex://threads/<id>` deeplink when detectable

The runtime waits for `codex exec` to exit instead of killing it when the output file first appears. This avoids interrupting local Codex-managed child work, including subagent-style workflows if the local Codex runtime supports them.

## Security

- Keep explicit sender/chat/workspace allowlists.
- Put free-form operators in `access.trusted_sender_open_ids`; put constrained users in `access.limited_sender_open_ids`.
- Keep limited users restricted to explicit `limited_allowed_commands` and `limited_allowed_task_ids`.
- Use bot identity for bridge replies.
- Use user identity only for tasks that clearly require user-owned Feishu resources and already have valid user-token scopes.
- Do not add Open Platform permissions, request new scopes, publish app versions, or change event subscriptions from this bridge unless that is the explicit administrative task.
- Keep dashboard and health endpoints on loopback unless protected by a separate authentication and network layer.
- Keep logs enabled for auditability.

## Multi-Codex Routing

`bridge.config.example.json` includes future peer metadata:

```json
"routing": {
  "accept_any_target": false,
  "dispatch_to_peers": false,
  "prefer_local_when_capable": true
},
"peers": {
  "enabled": false,
  "nodes": []
}
```

Actual remote task dispatch is disabled by default. Do not enable it until there is an authenticated queue or signed request protocol, otherwise multiple Codex machines can duplicate work or accept untrusted prompts.

## Validation

```powershell
python -m py_compile .\feishu_codex_bridge.py
Get-Content -Raw .\bridge.config.example.json | ConvertFrom-Json | Out-Null
foreach ($script in Get-ChildItem -Filter *.ps1) {
  $null = [scriptblock]::Create((Get-Content -Raw $script.FullName))
}
```
