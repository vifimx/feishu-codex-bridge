# Open Platform Events

Last checked: 2026-04-23

App: `cli_a928e035c478dcd6` (`mi-feishu-mcp-helper`)

Source page:

```text
https://open.feishu.cn/app/cli_a928e035c478dcd6/event
```

## Delivery Mode

The Event & Callback page shows the event subscription mode as long connection:

```text
使用长连接接收事件
```

The local bridge therefore uses:

```powershell
lark-cli event +subscribe --as bot --event-types <event_types> --compact --quiet
```

## Bridge-Relevant Events

These are the events relevant to the bridge's message intake and lifecycle handling:

| Event | Page status | Bridge use |
| --- | --- | --- |
| `im.message.receive_v1` | Added, app identity | Receives private bot-chat messages and allowlisted group messages. |
| `im.chat.access_event.bot_p2p_chat_entered_v1` | Added, app identity | Captures the user entering a bot private chat. |
| `im.message.bot_muted_v1` | Added, app identity | Tracks users muting/unmuting bot messages. |
| `im.message.message_read_v1` | Added, app identity | Optional read-status event; not required for command intake. |
| `im.message.recalled_v1` | Added, app identity | Optional recall event; useful for audit state. |
| `p2p_chat_create` | Added, app identity | Legacy first private-chat-create event. |

The page also has many unrelated document, calendar, task, and drive events enabled for broader Feishu tooling. The bridge should keep its `event_types` filtered to the events it actually handles.

## Private Message Intake

For `im.message.receive_v1`, the page shows these receive-message permissions as already enabled:

```text
读取用户发给机器人的单聊消息
获取群组中用户@机器人消息
获取群组中其他机器人和用户@当前机器人的消息
获取群组中所有消息（敏感权限）
```

That means private bot-chat messages can be received through `im.message.receive_v1`. The bridge should not run private chat polling by default.

Current bridge behavior:

```json
"private": {
  "polling_fallback_enabled": false
}
```

Only enable `private.polling_fallback_enabled=true` if long-connection event delivery is unavailable and the bot has the list-message permission needed by `lark-cli im +chat-messages-list`.
