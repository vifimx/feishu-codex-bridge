# Feishu Codex Bridge

[English](README.md) | 简体中文

Feishu Codex Bridge 是一个本地 Python 桥接器，用来把飞书/Lark 机器人消息转成 `codex exec` 任务。它适合个人或小团队在本机运行：飞书负责聊天入口，Codex CLI 负责实际执行。

当前生产运行时是 [feishu_codex_bridge.py](feishu_codex_bridge.py) 里的 Python 实现。实验性的 Kotlin/Compose 重写在达到 Python 桥接器的功能一致性之前，不作为默认发布路径。

## 页面截图

![Dashboard overview](docs/assets/dashboard-overview.png)

更多截图和重新生成方式见 [docs/SCREENSHOTS.md](docs/SCREENSHOTS.md)。

## 功能概览

- 通过官方 `lark-cli` 长连接事件流接收飞书/Lark 机器人消息。
- 通过本机 `codex exec` 执行审批过的请求。
- 支持单聊、群聊、话题跟进、运行中追加指导，以及可恢复的 Codex 会话。
- 用显式访问策略管理用户、用户组、群、工作区、可执行任务、模型和技能。
- 通过 `lark-cli` 下载支持的图片/文件/音频/视频资源；当本机 Codex CLI 支持 `--image` 时，图片可以传给 Codex。
- 提供仅本机回环可访问的 dashboard，用于查看任务、日志、能力、访问策略、进程控制和 Windows 集成。
- 运行态使用本地 JSON/JSONL 文件，方便审计和排查。

## 架构

项目默认采用 Python 架构：

```text
feishu_codex_bridge.py
  CLI 入口、桥接协调器、dashboard HTTP 服务、Lark 传输、
  任务调度、Codex 进程执行、会话和回复处理。

feishu_bridge/
  config_store.py     配置校验、类型转换、dashboard 写入白名单
  runtime_paths.py    日志/状态/任务/附件路径推导

dashboard/
  index.html          本地操作界面
  dashboard.css
  dashboard.js

tests/
  config 与桥接行为的 unittest 覆盖
```

渐进式重构方向见 [docs/PYTHON_ARCHITECTURE.md](docs/PYTHON_ARCHITECTURE.md)。当前仍保留平铺的 `feishu_codex_bridge.py` 入口，确保现有 Windows 启动脚本简单、兼容。

## 环境要求

- Windows PowerShell。
- Python 3.12 或更新版本。
- 已为飞书/Lark 应用配置好的 `lark-cli`。
- `codex` CLI 已加入 `PATH`。
- 可选：GitHub CLI (`gh`) 用于仓库维护。

## 快速开始

复制示例配置：

```powershell
Copy-Item .\bridge.config.example.json .\bridge.config.json
```

至少需要改这些本地值：

- `machine_id`
- `log_dir`
- `state_dir`
- `workspaces`
- `private.allowed_sender_open_ids`
- `private.allowed_chat_ids`
- `public.allowed_sender_open_ids`
- `public.allowed_chat_ids`
- `access.identities`
- `access.user_groups`
- `access.groups`
- `preset_tasks`

`bridge.config.json` 已被 Git 忽略，因为它通常包含本机路径、群 ID、用户 open ID 和部署选择。

不连接飞书，仅校验运行时和配置：

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-FeishuCodexBridge.ps1 -DryRun
```

启动桥接器：

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-FeishuCodexBridge.ps1
```

停止桥接器、dashboard 和由桥接器启动的 Codex 任务：

```powershell
powershell -ExecutionPolicy Bypass -File .\Stop-FeishuCodexBridge.ps1
```

## Dashboard

只启动本地 dashboard：

```powershell
powershell -ExecutionPolicy Bypass -File .\Open-FeishuCodexBridgeDashboard.ps1
```

默认地址：

```text
http://127.0.0.1:8765/
```

Dashboard 支持英文和简体中文，可查看桥接状态、近期任务、日志、本机 Codex 能力、访问策略，以及用户级 Windows 快捷方式/开机启动任务。进程控制和配置写入仅允许回环访问，也可以通过配置关闭：

```json
{
  "dashboard": {
    "allow_config_write": false,
    "allow_process_control": false,
    "allow_shell_integration": false
  }
}
```

除非额外加了认证和网络保护，否则 dashboard 应保持绑定 `127.0.0.1`。

## 飞书命令

身份与引导：

```text
/id
```

内置命令：

```text
/cmd help
/cmd status
/cmd status <job_id>
/cmd history
/cmd capabilities
/cmd peers
/cmd sessions
/cmd new-session
```

可执行任务：

```text
/cmd <preset_task> [input]
/task <preset_task> [input]
/task <preset_task>:<subtask_id> [input]
```

对拥有 `allow_codex=true` 权限的用户或群开放自由 Codex 任务：

```text
/ask [@node] [workspace=name] <prompt>
/ask --new [workspace=name] <prompt>
/ask mode=fast <prompt>
/ask model=gpt-5.4 reasoning=xhigh <prompt>
/ask skills=feishu,lark-doc <prompt>
```

当 `private.treat_all_text_as_codex=true` 时，单聊里被允许的普通文本也可以作为任务。群聊一般应要求 @机器人或显式命令，除非该群权限非常明确。

## 权限模型

权限来源包括：

- `access.default_policy`
- 命中的 `access.identities`
- 命中的 `access.user_groups`
- 当前命中的 `access.groups` 群策略

群策略对当前群是权威策略。如果某个群配置存在，但发送者不在该群策略允许范围内，发送者会回落到默认策略，而不是继续继承更宽泛的个人权限。

常规流程建议使用受限的可执行任务：

```json
{
  "preset_tasks": {
    "mobile-review": {
      "enabled": true,
      "aliases": ["mobile-review", "移动端评审", "评审更新"],
      "workspace": "default",
      "required_skills": ["feishu", "lark-doc", "lark-base"],
      "prompt_template": "Handle only this approved workflow. Reject unrelated requests.\n\nUser input:\n{input}\n"
    }
  }
}
```

只给可信操作人配置 `allow_codex=true`。`unrestricted=true` 只应授予允许绕过任务、模型和技能限制的管理员。

## 事件接入

桥接器预期使用飞书/Lark 长连接事件：

```powershell
lark-cli event +subscribe --as bot --filter '^(<event_types_regex>)$' --compact --quiet
```

单聊轮询只是兜底方案。只要 `im.message.receive_v1` 正常工作，就应保持 `private.polling_fallback_enabled=false`。

应用侧检查清单见已脱敏的 [docs/OPEN_PLATFORM_EVENTS.md](docs/OPEN_PLATFORM_EVENTS.md)。

## 安全与隐私

- 不要提交 `bridge.config.json`、token 文件、日志、任务状态、附件或本地分析包。
- 保持明确的发送者、群和工作区白名单。
- Dashboard 和健康检查接口应只绑定本机回环地址。
- 普通桥接回复使用 bot 身份。
- 只有在任务确实需要用户拥有的飞书资源且 user token scope 已满足时，才使用用户身份。
- 除非明确执行管理任务，否则不要通过本项目新增开放平台权限、申请 scope、发布应用版本或修改事件订阅。
- 提交截图前必须检查内容，截图应只包含占位 ID 和示例状态。

## 仓库维护

安装并登录 GitHub CLI：

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -Login -SetupGit
```

创建本地忽略的 shell token 模板：

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -CreateLocalEnv
```

浏览器登录、token 输入、`GH_TOKEN` 和远端创建流程见 [docs/GITHUB_AUTH.md](docs/GITHUB_AUTH.md)。

## 校验

提交前建议运行：

```powershell
python -m py_compile .\feishu_codex_bridge.py
python -m unittest discover -s tests
Get-Content -Raw .\bridge.config.example.json | ConvertFrom-Json | Out-Null
foreach ($script in Get-ChildItem -Filter *.ps1) {
  $null = [scriptblock]::Create((Get-Content -Raw $script.FullName))
}
```

## License

MIT。见 [LICENSE](LICENSE)。
