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
- Event-driven private and group message intake through `im.message.receive_v1`.
- Optional private-chat polling fallback for direct messages, disabled by default when event delivery is available.
- Allowlisted users, chats, workspaces, and fixed commands.
- Tiered access: trusted users can run free-form Codex jobs, limited users can only run approved preset tasks and commands.
- Conversation continuity: private chats and group mentions can continue the same Codex session through `codex exec resume`.
- Queueing: follow-up messages are queued while a job is running; replies to bridge job messages are treated as guidance for that conversation.
- Optional editable status messages: the bridge can update the original status reply and replace it with `最终结论` when the job finishes, falling back to a new reply if Feishu message editing is unavailable.
- Visual access directory: commands, skills, models, users, and groups can be edited from the dashboard.
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
  assets/
    feishu-codex-bridge.ico
  dashboard/
    index.html
    dashboard.css
    dashboard.js
  .github/workflows/ci.yml
  bridge.config.example.json
  feishu_codex_bridge.py
  Initialize-GitHubCli.ps1
  Initialize-LarkCli.ps1
  Open-FeishuCodexBridgeDashboard.cmd
  Open-FeishuCodexBridgeDashboard.ps1
  Set-FeishuCodexBridgeWindowsIntegration.ps1
  Start-FeishuCodexBridge.ps1
  Stop-FeishuCodexBridge.cmd
  Stop-FeishuCodexBridge.ps1
  docs/GITHUB_AUTH.md
  docs/OPEN_PLATFORM_EVENTS.md
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
- `private.polling_fallback_enabled`
- `public.allowed_sender_open_ids`
- `public.allowed_chat_ids`
- `access.identities`
- `access.user_groups`
- `access.groups`
- `commands.available`
- `skills.available`
- `models.available`
- `models.default`
- `models.fast`
- `sessions`
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

Start the bridge without serving the dashboard, useful when the dashboard-only GUI is already running:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-FeishuCodexBridge.ps1 -NoDashboardServer
```

Stop the bridge, dashboard, and active bridge-started Codex jobs:

```powershell
powershell -ExecutionPolicy Bypass -File .\Stop-FeishuCodexBridge.ps1
```

This project does not install a Windows service, Scheduled Task, or startup item by default. It runs only while one of the PowerShell launchers or a dashboard-started background bridge process is running.

## Windows Integration

The dashboard has a **Windows Integration** section for user-level shell integration:

- **Add to Start Menu** creates top-level shortcuts under the current user's Start Menu programs folder.
- The shortcuts are named **Feishu Codex Bridge Dashboard** and **Feishu Codex Bridge Stop**. They use `assets/feishu-codex-bridge.ico` as their icon and appear in Windows Search and **All apps**; Windows 11 pinned Start layout still requires manual pinning from Windows.
- **Start Dashboard on Boot** creates a current-user Scheduled Task that starts the dashboard-only process after Windows user sign-in without opening a browser.
- **Start Connection on Boot** creates a current-user Scheduled Task that starts the Feishu bridge connection after Windows user sign-in without serving another dashboard.

The same actions can be run from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action status
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action install-start-menu
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action enable-dashboard-startup
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action enable-connection-startup
```

Disable or remove them with:

```powershell
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action disable-dashboard-startup
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action disable-connection-startup
powershell -ExecutionPolicy Bypass -File .\Set-FeishuCodexBridgeWindowsIntegration.ps1 -Action remove-start-menu
```

Startup tasks are not enabled by default. They are created only by the dashboard buttons or the commands above.

## Dashboard

Start the dashboard without starting Feishu event listening:

```powershell
powershell -ExecutionPolicy Bypass -File .\Open-FeishuCodexBridgeDashboard.ps1
```

Restart the dashboard process after code updates:

```powershell
powershell -ExecutionPolicy Bypass -File .\Open-FeishuCodexBridgeDashboard.ps1 -Restart
```

Default URL:

```text
http://127.0.0.1:8765/
```

The same dashboard is also served when the bridge is running and `health_server.enabled=true`. For manual GUI control, prefer the dashboard-only launcher above, then use the **Start Connection** and **Stop Connection** buttons. In that mode the GUI stays open while the Feishu event subscriber runs as a separate background bridge process.

The dashboard supports English and Simplified Chinese. On first load it uses the browser language list and switches to Simplified Chinese when a Chinese locale is detected; after the user chooses a language, the choice is saved in browser `localStorage`.

Dashboard endpoints:

```text
GET  /                         HTML dashboard
GET  /api/status               machine, capability, pid, and job summary
GET  /api/jobs?limit=30        recent job list
GET  /api/jobs/<job_id>        full job JSON
POST /api/jobs/cleanup         loopback-only cleanup using jobs.history_limit
GET  /api/logs?limit=120       recent bridge log entries
GET  /api/config               current config and editable key allowlist
POST /api/config               loopback-only config patch for allowlisted fields
POST /api/connection/start     loopback-only start of the Feishu bridge connection
POST /api/connection/stop      loopback-only stop of the Feishu bridge connection
GET  /api/windows-integration  Start Menu and startup-task status
POST /api/windows-integration/<action>
```

Config writes are intentionally constrained:

- The server must see the client as loopback.
- `dashboard.allow_config_write` must be true.
- Only the allowlisted keys in `feishu_codex_bridge.py` can be changed.
- Every write creates a timestamped `bridge.config.json.*.bak` backup before replacing the config.
- Some changes, such as `health_server.*`, need a restart to affect the already-running server.

Process control is also loopback-only and can be disabled with `dashboard.allow_process_control=false`. Windows shell integration changes are loopback-only and can be disabled with `dashboard.allow_shell_integration=false`.

Keep the dashboard bound to `127.0.0.1`. Do not expose it on a public interface without adding an authentication layer.

## Feishu Commands

Identity and onboarding:

```text
/id
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

Explicit tasks:

```text
/ask [@node] [workspace=name] <prompt>
```

Private chat can treat all allowlisted text as tasks when `private.treat_all_text_as_codex=true`.

Conversation control:

```text
/cmd sessions
/cmd new-session
/ask --new [workspace=name] <prompt>
```

Model and skill options:

```text
/ask mode=fast <prompt>
/ask model=gpt-5.4 reasoning=xhigh <prompt>
/ask skills=feishu,lark-doc <prompt>
```

When `sessions.enabled=true`, the bridge stores a conversation record per private chat and per group chat by default. After a job completes, the next private message or group mention resumes the same session. A reply to a bridge status/final message is attached to that job's conversation and is queued as guidance if the job is still running. Use `/cmd new-session` or `/ask --new` to start fresh.

The default interaction model is continuous: normal follow-up messages stay in the current bridge conversation. During a running job, replying to its card is treated as additional guidance for that conversation, updates the same card, and is processed as a same-card continuation after the current run finishes. Sending a new chat message while a job is running creates a separate queued follow-up card. Use `/cmd new-session` when the next request should start from a clean context.

When `reply.edit_status_message=true`, the bridge posts job status as an interactive Feishu card, then edits that same card as the job moves from queued to running to finished. The final edited card uses the `最终结论` label. If Feishu rejects card editing, the bridge logs the failure and sends a normal final text reply instead. User-facing cards use neutral wording such as `已收到消息`, `正在处理`, and `处理完成`.

Detailed parameters such as job IDs, model names, workspaces, conversation keys, and session links are hidden by default when `reply.show_details_by_default=false`. Grant `show_details=true` on a specific identity, user group, or chat group to expose those details for operators. Execution progress such as command/tool events and short output summaries is controlled separately by `show_progress`; hidden model reasoning is not exposed.

## Event Delivery

The bridge is intended to receive private and group messages through Feishu/Lark long-connection events rather than polling. The required app-side setup is:

- Bot capability enabled.
- Event delivery method set to long connection.
- `im.message.receive_v1` subscribed and published.
- Bot/app permissions that allow receiving user private messages sent to the bot and the required group-message mode.

The runtime subscribes with:

```powershell
lark-cli event +subscribe --as bot --event-types <configured event_types> --compact --quiet
```

Private chat polling is only a fallback. Keep `private.polling_fallback_enabled=false` when `im.message.receive_v1` is working. Enable it only if event delivery is unavailable and the bot has the list-message permission needed by `im +chat-messages-list`.

The current app event-page check is recorded in [docs/OPEN_PLATFORM_EVENTS.md](docs/OPEN_PLATFORM_EVENTS.md). As of 2026-04-23, the page shows long connection enabled, `im.message.receive_v1` added, and the private-message permission `读取用户发给机器人的单聊消息` already enabled.

Group chat can do the same when `public.treat_all_text_as_codex=true`; keep this false for noisy groups.

## Access Model

The bridge uses an access directory instead of only raw ID lists. An identity can include memorable labels, aliases, names, emails, and one or more Feishu identifiers. Runtime authorization always matches explicit Feishu IDs from incoming events, normally `open_id`. If `access.resolve_contacts_enabled=true` and the current app has contact scopes, the bridge also resolves the sender's contact profile and can match configured `names`, `emails`, `mobiles`, and `aliases`. If contact resolution is unavailable, readable names and emails still help dashboard search but do not replace `open_ids`.

```json
"access": {
  "identities": {
    "admin": {
      "label": "Admin User",
      "open_ids": ["ou_admin_xxx"],
      "emails": ["admin@example.com"],
      "aliases": ["admin", "Alice Zhang"],
      "allow_codex": true,
      "unrestricted": true,
      "commands": ["*"],
      "tasks": ["*"],
      "skills": ["*"],
      "models": ["*"]
    }
  },
  "user_groups": {
    "review-team": {
      "label": "Review Team",
      "enabled": true,
      "members": ["reviewer"],
      "commands": ["help", "status", "sessions"],
      "tasks": ["review-update"],
      "skills": ["feishu", "lark-doc"],
      "models": ["gpt-5.4-mini"]
    }
  },
  "groups": {
    "botx-test": {
      "label": "botx test group",
      "chat_ids": ["oc_group_xxx"],
      "members": ["admin"],
      "allow_codex": true,
      "commands": ["help", "status", "new-session"],
      "tasks": ["review-update"],
      "skills": ["feishu", "lark-doc"],
      "models": ["gpt-5.4", "gpt-5.4-mini"]
    }
  }
}
```

Permissions are additive across the matching identity, all matching custom user groups, and the current chat group. `unrestricted=true` or `["*"]` grants the full configured set. A user group or chat group can grant permissions to specific `members` by identity key, raw sender id, or to everyone when `members` is empty or contains `"*"`.

Constrained users should omit `allow_codex` and grant only specific `commands`, `tasks`, `skills`, and `models`. Their messages can only map to configured preset tasks:

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

Job records are reconciled when read by the dashboard or status API. If a queued/running job no longer has live worker or Codex PIDs and `last-message.txt` exists, it is marked `completed`; otherwise it is marked `failed` with available worker/Codex stderr.

Dashboard job history is scrollable and can be retained with:

```json
"jobs": {
  "history_limit": 50,
  "auto_cleanup_enabled": true,
  "cleanup_delete_artifacts": true
}
```

Cleanup only removes terminal jobs (`completed`, `failed`, `timed_out`, `stopped`) beyond the retention limit. Active queued/running jobs are not removed. When `cleanup_delete_artifacts=true`, the matching job working directory and downloaded artifact directory are deleted together with the job JSON.

## Security

- Keep explicit sender/chat/workspace allowlists.
- Put free-form operators in `access.identities` with explicit `allow_codex=true` or `unrestricted=true`.
- Keep constrained users restricted to explicit `commands`, `tasks`, `skills`, and `models`.
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
