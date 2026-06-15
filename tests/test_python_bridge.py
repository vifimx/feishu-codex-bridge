import json
import os
import subprocess
import tempfile
import unittest
import datetime as dt
from pathlib import Path
from unittest import mock

from feishu_codex_bridge import Bridge, clean_powershell_output, decode_process_bytes, looks_garbled, npm_shim_direct_node_args


def bridge_for_normalization() -> Bridge:
    bridge = Bridge.__new__(Bridge)
    bridge.config = {
        "private": {"allowed_chat_ids": []},
        "sessions": {"reply_guidance_enabled": True},
    }
    return bridge


def bare_bridge() -> Bridge:
    bridge = Bridge.__new__(Bridge)
    bridge.config = {"private": {}}
    bridge.machine_id = "local"
    bridge.local_codex_model_profile = lambda: {}
    return bridge


def bridge_for_policy() -> Bridge:
    bridge = bare_bridge()
    bridge.contact_values_for_open_id = lambda open_id: []
    bridge.config.update(
        {
            "reply": {"show_details_by_default": False, "show_progress_by_default": False},
            "models": {
                "default": {"model": "gpt-5.4", "reasoning_effort": "medium", "service_tier": "fast"},
                "fast": {"model": "gpt-5.4-mini", "reasoning_effort": "low", "service_tier": "fast"},
            },
            "access": {
                "default_policy": {"allow_codex": False, "settings": {"assistant": {"display_name": "默认助手"}}},
                "identities": {
                    "operator": {
                        "open_ids": ["ou_1"],
                        "allow_codex": True,
                        "settings": {"assistant": {"display_name": "用户助手"}},
                    }
                },
                "user_groups": {},
                "groups": {
                    "chat": {
                        "chat_ids": ["oc_1"],
                        "members": ["operator"],
                        "settings": {"models": {"default": {"model": "gpt-5.4-mini"}}, "reply": {"show_details": True}},
                    }
                },
            },
        }
    )
    return bridge


class PythonBridgeNormalizationTest(unittest.TestCase):
    def test_normalizes_wrapped_open_platform_event(self) -> None:
        bridge = bridge_for_normalization()
        raw = {
            "schema": "2.0",
            "header": {"event_type": "im.message.receive_v1", "event_id": "evt_1"},
            "event": {
                "sender": {
                    "sender_id": {"open_id": "ou_wrapped", "user_id": "u_wrapped"},
                    "sender_type": "user",
                },
                "message": {
                    "message_id": "om_wrapped",
                    "chat_id": "oc_wrapped",
                    "chat_type": "group",
                    "message_type": "text",
                    "content": '{"text":"/ask wrapped"}',
                },
            },
        }

        self.assertEqual("im.message.receive_v1", bridge.event_type(raw))
        message = bridge.normalize_message(raw)

        self.assertEqual("om_wrapped", message["message_id"])
        self.assertEqual("oc_wrapped", message["chat_id"])
        self.assertEqual("group", message["chat_type"])
        self.assertEqual("ou_wrapped", message["sender_id"])
        self.assertEqual("u_wrapped", message["sender_user_id"])
        self.assertEqual("/ask wrapped", message["text"])

    def test_enriches_topic_context_from_message_thread_replies(self) -> None:
        bridge = bridge_for_normalization()
        bridge.dry_run = False
        bridge.log = lambda *args, **kwargs: None
        bridge.run_lark = lambda *args, **kwargs: json.dumps(
            {
                "data": {
                    "messages": [
                        {
                            "message_id": "om_child",
                            "thread_id": "omt_topic",
                            "thread_replies": [
                                {"message_id": "om_root", "thread_id": "omt_topic"},
                                {"message_id": "om_child", "thread_id": "omt_topic"},
                            ],
                        }
                    ]
                }
            }
        )
        msg = {
            "message_id": "om_child",
            "chat_id": "oc_1",
            "chat_type": "p2p",
            "reply_to": "",
            "parent_id": "",
            "root_id": "",
            "thread_id": "",
        }

        enriched = bridge.enrich_reply_to(msg)

        self.assertEqual("omt_topic", enriched["thread_id"])
        self.assertEqual("om_root", enriched["root_id"])
        self.assertEqual("om_root", enriched["reply_to"])

    def test_extracts_post_text_from_snake_and_camel_locales(self) -> None:
        bridge = bridge_for_normalization()

        self.assertEqual(
            "评审更新\n第一行",
            bridge.extract_text(
                "post",
                {
                    "zh_cn": {
                        "title": "评审更新",
                        "content": [[{"tag": "text", "text": "第一行"}]],
                    },
                },
            ),
        )
        self.assertEqual(
            "Review\nLine",
            bridge.extract_text(
                "post",
                {
                    "enUs": {
                        "title": "Review",
                        "content": [[{"tag": "text", "text": "Line"}]],
                    },
                },
            ),
        )

    def test_extracts_camel_case_resource_keys(self) -> None:
        bridge = bridge_for_normalization()

        self.assertEqual(
            [{"type": "file", "file_key": "file_1", "name": "report.pdf"}],
            bridge.extract_resources("file", {"fileKey": "file_1", "fileName": "report.pdf"}),
        )
        self.assertEqual(
            [{"type": "image", "file_key": "img_1", "name": "img_1"}],
            bridge.extract_resources("image", {"imageKey": "img_1"}),
        )

    def test_extracts_resources_from_merge_forward_text(self) -> None:
        bridge = bridge_for_normalization()
        content = (
            "<forwarded_messages>\n"
            "[2026-05-07T11:13:56+08:00] ou_1:\n"
            "    [Image: img_v3_0211f_bbd1a16e-ccec-4beb-ac69-f3be80965e5g]\n"
            "[2026-05-07T11:14:11+08:00] ou_1:\n"
            '    <file key="file_v3_0011f_5a12270f-dfe8-4ea2-8026-31e24096e42g" name="feedback.zip"/>\n'
            "</forwarded_messages>"
        )

        self.assertEqual(
            [
                {"type": "image", "file_key": "img_v3_0211f_bbd1a16e-ccec-4beb-ac69-f3be80965e5g", "name": "img_v3_0211f_bbd1a16e-ccec-4beb-ac69-f3be80965e5g"},
                {"type": "file", "file_key": "file_v3_0011f_5a12270f-dfe8-4ea2-8026-31e24096e42g", "name": "feedback.zip"},
            ],
            bridge.extract_resources("merge_forward", content),
        )

    def test_reply_context_downloads_merge_forward_attachments(self) -> None:
        bridge = bridge_for_normalization()
        bridge.dry_run = False
        bridge.log = lambda *args, **kwargs: None
        bridge.config["multimodal"] = {"download_incoming": True}
        content = (
            "<forwarded_messages>\n"
            "[2026-05-07T11:13:53+08:00] ou_1:\n"
            "    1. [WUTLQ-9250](https://jira-phone.mioffice.cn/browse/WUTLQ-9250)\n"
            "[2026-05-07T11:13:56+08:00] ou_1:\n"
            "    [Image: img_v3_0211f_bbd1a16e-ccec-4beb-ac69-f3be80965e5g]\n"
            "</forwarded_messages>"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            bridge.artifacts_dir = Path(temp_dir)

            def fake_run_lark(args, timeout=None, cwd=None):
                if args[:2] == ["im", "+messages-mget"]:
                    return json.dumps(
                        {
                            "data": {
                                "messages": [
                                    {
                                        "message_id": "om_parent",
                                        "msg_type": "merge_forward",
                                        "content": content,
                                        "create_time": "2026-05-07 11:16",
                                        "sender": {"id": "ou_1"},
                                    }
                                ]
                            }
                        },
                        ensure_ascii=False,
                    )
                if args[:2] == ["im", "+messages-resources-download"]:
                    output_name = args[args.index("--output") + 1]
                    path = Path(cwd) / f"{output_name}.jpg"
                    path.write_bytes(b"image")
                    return json.dumps({"ok": True, "data": {"saved_path": str(path)}})
                self.fail(f"unexpected lark command: {args}")

            bridge.run_lark = fake_run_lark

            contexts = bridge.context_messages_for_msg({"message_id": "om_child", "reply_to": "om_parent"}, "job-1")

        self.assertEqual(1, len(contexts))
        self.assertIn("WUTLQ-9250", contexts[0]["text"])
        self.assertEqual("reply_context", contexts[0]["attachments"][0]["source"])
        self.assertEqual("om_parent", contexts[0]["attachments"][0]["message_id"])
        self.assertTrue(contexts[0]["attachments"][0]["path"].endswith(".jpg"))

    def test_codex_prompt_includes_reply_context(self) -> None:
        bridge = bridge_for_normalization()
        bridge.machine_id = "local"
        bridge.config["multimodal"] = {"context_text_max_chars": 12000}
        job = {
            "job_id": "job-1",
            "workspace": "fitness-app",
            "conversation_key": "conv",
            "conversation_mode": "topic",
            "queue_kind": "new",
            "prompt": "帮我分析一下吧",
            "source": {"chat_id": "oc_1", "message_id": "om_child"},
            "context_messages": [
                {
                    "role": "reply_to",
                    "message_id": "om_parent",
                    "msg_type": "merge_forward",
                    "sender_id": "ou_1",
                    "create_time": "2026-05-07 11:16",
                    "text": "<forwarded_messages>\nWUTLQ-9250\n</forwarded_messages>",
                    "attachments": [{"source": "reply_context", "message_id": "om_parent", "type": "image", "file_key": "img_1", "path": "C:\\tmp\\img.jpg"}],
                }
            ],
            "attachments": [{"source": "reply_context", "message_id": "om_parent", "type": "image", "file_key": "img_1", "path": "C:\\tmp\\img.jpg"}],
            "assistant": {},
            "show_details": True,
        }

        prompt = bridge.build_codex_prompt(job)

        self.assertIn("Referenced chat messages from the user's reply context", prompt)
        self.assertIn("WUTLQ-9250", prompt)
        self.assertIn("source=reply_context message_id=om_parent type=image", prompt)

    def test_dashboard_restart_control_only_for_dashboard_mode(self) -> None:
        bridge = bridge_for_normalization()
        bridge.pid_name = "dashboard.pid"
        bridge.config["dashboard"] = {"allow_process_control": True}

        self.assertTrue(bridge.dashboard_control_status()["can_restart"])

        bridge.pid_name = "bridge.pid"
        self.assertFalse(bridge.dashboard_control_status()["can_restart"])

    def test_full_restart_restarts_connection_before_dashboard(self) -> None:
        bridge = bridge_for_normalization()
        bridge.pid_name = "dashboard.pid"
        bridge.config["dashboard"] = {"allow_process_control": True}
        bridge.process_snapshot = lambda name: {"pid": 123, "running": True, "stale": False}
        calls: list[str] = []
        bridge.stop_bridge_connection = lambda client: calls.append("stop") or {"status": "stopped", "pid": 123}
        bridge.start_bridge_connection = lambda client: calls.append("start") or {"status": "started", "pid": 456}
        bridge.restart_dashboard = lambda client: calls.append("dashboard") or {"status": "restarting", "pid": 789}
        bridge.log = lambda *args, **kwargs: None

        result = bridge.restart_dashboard_and_connection("127.0.0.1")

        self.assertEqual(["stop", "start", "dashboard"], calls)
        self.assertEqual("restarting", result["status"])
        self.assertEqual(123, result["connection_stop"]["pid"])
        self.assertEqual(456, result["connection_start"]["pid"])
        self.assertEqual(789, result["dashboard"]["pid"])

    def test_cleanup_stale_bridge_connections_preserves_current_pid(self) -> None:
        bridge = bridge_for_normalization()
        bridge.read_pid = lambda name: 456
        bridge.find_bridge_processes = lambda marker: [123, 456]
        bridge.pid_is_running = lambda pid: True
        stopped: list[int] = []
        bridge.terminate_process_tree = lambda pid: stopped.append(pid)
        bridge.log = lambda *args, **kwargs: None

        self.assertEqual([123], bridge.cleanup_stale_bridge_connections())
        self.assertEqual([123], stopped)

    def test_task_installed_treats_disabled_task_as_not_installed(self) -> None:
        bridge = bare_bridge()
        bridge.windows_integration_supported = lambda: True
        bridge.run_powershell_script = lambda script, timeout=30: subprocess.CompletedProcess(
            [],
            0,
            '{"task_name":"FeishuCodexBridgeConnection","exists":true,"installed":false,"enabled":false,"state":"Disabled"}',
            "",
        )

        self.assertFalse(bridge.task_installed("FeishuCodexBridgeConnection"))

    def test_delete_startup_task_accepts_disabled_only_fallback(self) -> None:
        bridge = bare_bridge()
        bridge.log = lambda *args, **kwargs: None
        bridge.windows_integration_supported = lambda: True
        bridge.task_status = lambda task_name: {"task_name": task_name, "exists": True, "installed": True, "enabled": True}
        bridge.run_powershell_script = lambda script, timeout=30: subprocess.CompletedProcess(
            [],
            0,
            '{"installed":false,"exists":true,"enabled":false,"disabled_only":true,"task_name":"FeishuCodexBridgeConnection","message":"Scheduled task disabled. Delete failed: Access denied."}',
            "",
        )

        result = bridge.delete_startup_task("connection")

        self.assertFalse(result["installed"])
        self.assertFalse(result["enabled"])
        self.assertTrue(result["disabled_only"])

    def test_create_startup_task_uses_limited_run_level(self) -> None:
        bridge = bare_bridge()
        bridge.log = lambda *args, **kwargs: None
        bridge.windows_integration_supported = lambda: True
        scripts = []

        def fake_run_powershell_script(script, timeout=30):
            scripts.append(script)
            return subprocess.CompletedProcess(
                [],
                0,
                '{"installed":true,"enabled":true,"task_name":"FeishuCodexBridgeConnection","message":"Scheduled task registered."}',
                "",
            )

        bridge.run_powershell_script = fake_run_powershell_script

        result = bridge.create_startup_task("connection")

        self.assertTrue(result["installed"])
        self.assertIn("-RunLevel Limited", scripts[0])
        self.assertNotIn("LeastPrivilege", scripts[0])

    def test_create_startup_task_admin_uses_highest_run_level(self) -> None:
        bridge = bare_bridge()
        bridge.log = lambda *args, **kwargs: None
        bridge.windows_integration_supported = lambda: True

        with tempfile.TemporaryDirectory() as tmp:
            bridge.state_dir = Path(tmp)
            captured = {}

            def fake_run_elevated(script_path, result_path, timeout=120):
                captured["script"] = script_path.read_text(encoding="utf-8")
                return subprocess.CompletedProcess(
                    [],
                    0,
                    '{"installed":true,"exists":true,"enabled":true,"task_name":"FeishuCodexBridgeConnection","method":"scheduled_task_admin","run_level":"Highest"}',
                    "",
                )

            bridge.run_elevated_powershell_file = fake_run_elevated
            bridge.remove_startup_shortcut = lambda kind: {"removed": True, "installed": False}

            result = bridge.create_startup_task_admin("connection")

        self.assertTrue(result["installed"])
        self.assertEqual("scheduled_task_admin", result["method"])
        self.assertEqual("Highest", result["run_level"])
        self.assertTrue(result["startup_shortcut"]["removed"])
        self.assertIn("-RunLevel Highest", captured["script"])

    def test_windows_integration_admin_action_routes_to_admin_creator(self) -> None:
        bridge = bare_bridge()
        bridge.require_shell_integration = lambda client_address: None
        bridge.create_startup_task_admin = lambda kind: {"installed": True, "kind": kind}
        bridge.windows_integration_status = lambda force_refresh=False: {"supported": True}

        result = bridge.apply_windows_integration_action("enable-connection-startup-admin", "127.0.0.1")

        self.assertEqual("enable-connection-startup-admin", result["action"])
        self.assertEqual("connection", result["result"]["kind"])

    def test_windows_integration_status_hides_local_paths_when_control_disabled(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"dashboard": {"allow_shell_integration": False}}
        bridge.windows_integration_supported = lambda: True
        bridge.start_menu_status = mock.Mock(side_effect=AssertionError("should not inspect local Start Menu"))
        bridge.startup_status = mock.Mock(side_effect=AssertionError("should not inspect local startup tasks"))

        status = bridge.windows_integration_status()

        self.assertFalse(status["control_enabled"])
        self.assertEqual("disabled", status["start_menu"]["status"])
        self.assertNotIn("folder", status["start_menu"])
        self.assertEqual("disabled", status["startup"]["dashboard"]["state"])
        self.assertEqual("disabled", status["startup"]["connection"]["state"])
        bridge.start_menu_status.assert_not_called()
        bridge.startup_status.assert_not_called()

    def test_windows_integration_status_is_cached_for_dashboard_refreshes(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"dashboard": {"allow_shell_integration": True}}
        bridge.windows_integration_supported = lambda: True
        bridge.start_menu_status = mock.Mock(return_value={"installed": True, "partial": False, "status": "installed"})
        bridge.startup_status = mock.Mock(return_value={"installed": False, "exists": False, "enabled": False})

        first = bridge.windows_integration_status()
        second = bridge.windows_integration_status()

        self.assertIs(first, second)
        bridge.start_menu_status.assert_called_once()
        self.assertEqual(2, bridge.startup_status.call_count)

        bridge.windows_integration_status(force_refresh=True)

        self.assertEqual(2, bridge.start_menu_status.call_count)
        self.assertEqual(4, bridge.startup_status.call_count)

    def test_create_startup_task_falls_back_to_startup_shortcut(self) -> None:
        bridge = bare_bridge()
        bridge.log = lambda *args, **kwargs: None
        bridge.windows_integration_supported = lambda: True
        bridge.run_powershell_script = lambda script, timeout=30: subprocess.CompletedProcess([], 1, "", "Access is denied.")
        bridge.run_command = lambda args, timeout=30: subprocess.CompletedProcess(args, 1, "", "ERROR: Access is denied.")
        bridge.create_startup_shortcut = lambda kind, reason="": {
            "installed": True,
            "enabled": True,
            "exists": True,
            "method": "startup_folder",
            "path": "Startup\\Feishu Codex Bridge Connection.lnk",
            "fallback_reason": reason,
        }

        result = bridge.create_startup_task("connection")

        self.assertTrue(result["installed"])
        self.assertEqual("startup_folder", result["method"])
        self.assertIn("Access is denied", result["task_error"])

    def test_startup_status_uses_startup_shortcut_fallback(self) -> None:
        bridge = bare_bridge()
        bridge.windows_integration_supported = lambda: True
        bridge.task_status = lambda task_name: {"task_name": task_name, "exists": False, "installed": False, "enabled": False, "state": "missing"}
        bridge.startup_shortcut_status = lambda kind: {"exists": True, "installed": True, "enabled": True, "path": "Startup\\x.lnk", "method": "startup_folder"}

        status = bridge.startup_status("connection")

        self.assertTrue(status["installed"])
        self.assertTrue(status["enabled"])
        self.assertEqual("startup_folder", status["method"])

    def test_lark_json_parser_ignores_cli_page_progress(self) -> None:
        output = '{"code":0,"data":{"items":[{"chat_id":"oc_1"}]},"msg":"success"}\n[page 1] fetching...\n'

        parsed = Bridge.parse_lark_json_output(output)

        self.assertEqual("oc_1", parsed["data"]["items"][0]["chat_id"])

    def test_decodes_local_windows_command_output(self) -> None:
        raw = "错误: 没有找到进程 \"27880\"。".encode("cp936")

        self.assertEqual('错误: 没有找到进程 "27880"。', decode_process_bytes(raw))

    def test_detects_mojibake_progress_lines(self) -> None:
        self.assertTrue(looks_garbled('����: û���ҵ����� "27880"��'))
        self.assertFalse(looks_garbled('错误: 没有找到进程 "27880"。'))

    def test_cleans_powershell_clixml_errors(self) -> None:
        clixml = (
            '#< CLIXML\r\n'
            '<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">'
            '<Obj S="progress" RefId="0"><MS><PR N="Record"><AV>Preparing modules for first use.</AV></PR></MS></Obj>'
            '<S S="Error">New-ScheduledTaskPrincipal : Cannot convert value "LeastPrivilege"_x000D__x000A_</S>'
            '<S S="Error">Limited, Highest_x000D__x000A_</S>'
            '</Objs>'
        )

        cleaned = clean_powershell_output(clixml)

        self.assertIn("Cannot convert value", cleaned)
        self.assertIn("Limited, Highest", cleaned)
        self.assertNotIn("CLIXML", cleaned)
        self.assertNotIn("Preparing modules", cleaned)

    def test_resolves_npm_lark_cli_shim_to_direct_node_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shim = root / "lark-cli.cmd"
            script = root / "node_modules" / "@larksuite" / "cli" / "scripts" / "run.js"
            node = root / "node.exe"
            shim.write_text("@echo off", encoding="utf-8")
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")
            node.write_text("", encoding="utf-8")

            args = npm_shim_direct_node_args(shim, Path("node_modules") / "@larksuite" / "cli" / "scripts" / "run.js")

            self.assertEqual([str(node), str(script)], args)

    def test_run_lark_uses_direct_args_without_cmd_reparse(self) -> None:
        bridge = bare_bridge()
        bridge.lark_cli_args = ["node.exe", "run.js"]
        bridge.log = lambda *args, **kwargs: None
        bridge.env = lambda: {}

        with mock.patch("feishu_codex_bridge.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(["node.exe"], 0, "ok", "")

            output = bridge.run_lark(["api", "PATCH", "/x", "--data", 'grep -i "health\\|fitness\\|mi"'])

        self.assertEqual("ok", output)
        self.assertEqual(["node.exe", "run.js", "api", "PATCH", "/x", "--data", 'grep -i "health\\|fitness\\|mi"'], run.call_args.args[0])

    def test_discovers_bot_chats_and_members(self) -> None:
        bridge = bare_bridge()
        bridge.log = lambda *args, **kwargs: None
        calls = []

        def fake_run_lark(args, timeout=None):
            calls.append(args)
            if args[:3] == ["im", "chats", "list"]:
                return json.dumps(
                    {
                        "data": {
                            "items": [
                                {
                                    "chat_id": "oc_review",
                                    "name": "移动端技术方案评审",
                                    "external": True,
                                    "owner_id": "ou_owner",
                                }
                            ]
                        }
                    },
                    ensure_ascii=False,
                ) + "\n[page 1] fetching...\n"
            if args[:3] == ["im", "chat.members", "get"]:
                return json.dumps(
                    {
                        "data": {
                            "items": [
                                {"member_id": "ou_1", "member_id_type": "open_id", "name": "张三"},
                                {"open_id": "ou_2", "display_name": "李四"},
                            ]
                        }
                    },
                    ensure_ascii=False,
                )
            self.fail(f"unexpected lark command: {args}")

        bridge.run_lark = fake_run_lark

        result = bridge.discover_bot_chats(include_members=True, page_limit=3)

        self.assertEqual("bot", result["identity"])
        self.assertEqual(1, result["chat_count"])
        self.assertEqual(2, result["member_count"])
        self.assertEqual("oc_review", result["chats"][0]["chat_id"])
        self.assertEqual("移动端技术方案评审", result["chats"][0]["name"])
        self.assertEqual("ou_1", result["chats"][0]["members"][0]["open_id"])
        self.assertEqual("李四", result["chats"][0]["members"][1]["name"])
        self.assertTrue(any(call[:3] == ["im", "chat.members", "get"] for call in calls))

    def test_read_job_result_ignores_process_logs_when_last_message_is_empty(self) -> None:
        bridge = bare_bridge()
        job = {"output_file": "", "stdout_file": "", "stderr_file": ""}

        self.assertEqual("", bridge.read_job_result(job))

    def test_read_job_process_output_keeps_log_tail(self) -> None:
        bridge = bare_bridge()
        with tempfile.TemporaryDirectory() as tmp:
            stderr = Path(tmp) / "stderr.log"
            stderr.write_text("OpenAI Codex\n" + ("x" * 6000) + "\nremote compaction failed", encoding="utf-8")
            job = {"stderr_file": str(stderr)}

            output = bridge.read_job_process_output(job, 2000)

        self.assertIn("OpenAI Codex", output)
        self.assertIn("remote compaction failed", output)

    def test_summarizes_unsupported_model_failure(self) -> None:
        bridge = bare_bridge()
        bridge.read_job_process_output = lambda job, limit=3000: "ERROR: The 'gpt-5.5' model requires a newer version of Codex."
        job = {"codex_options": {"model": "gpt-5.5"}}

        self.assertIn("当前执行环境不支持所选模型", bridge.summarize_codex_failure(job))

    def test_summarizes_unsupported_model_failure_with_details(self) -> None:
        bridge = bare_bridge()
        bridge.read_job_process_output = lambda job, limit=3000: "ERROR: The 'gpt-5.5' model requires a newer version of Codex."
        job = {"show_details": True, "codex_options": {"model": "gpt-5.5"}}

        self.assertIn("当前 Codex CLI 不支持所选模型 `gpt-5.5`", bridge.summarize_codex_failure(job))

    def test_summarizes_compaction_failure_without_raw_internal_output(self) -> None:
        bridge = bare_bridge()
        raw = "\n".join(
            [
                "OpenAI Codex v0.115.0",
                "workdir: C:\\datacenter\\code\\fitness-app",
                "Internal bridge context:",
                "- job_id: job-1",
                "ERROR codex_core::compact_remote: remote compaction failed",
                "ERROR: Error running remote compact task",
            ]
        )
        bridge.read_job_process_output = lambda job, limit=3000: raw
        job = {"show_details": False, "codex_options": {"model": "gpt-5.4"}}

        result = bridge.summarize_codex_failure(job)

        self.assertIn("上下文压缩失败", result)
        self.assertNotIn("OpenAI Codex", result)
        self.assertNotIn("workdir", result)
        self.assertNotIn("job-1", result)

    def test_unknown_failure_hides_raw_output_without_details(self) -> None:
        bridge = bare_bridge()
        bridge.read_job_process_output = lambda job, limit=3000: "OpenAI Codex\nworkdir: C:\\repo\nsession id: abc"
        job = {"show_details": False}

        result = bridge.summarize_codex_failure(job)

        self.assertIn("执行过程中发生错误", result)
        self.assertNotIn("OpenAI Codex", result)
        self.assertNotIn("session id", result)

    def test_build_codex_prompt_uses_assistant_identity(self) -> None:
        bridge = bare_bridge()
        bridge.config.update(
            {
                "assistant": {
                    "display_name": "飞书助手",
                    "identity_prompt": "你是飞书助手。",
                    "hide_internal_identity": True,
                },
                "sessions": {"mode": "topic"},
            }
        )
        job = {
            "job_id": "job-1",
            "workspace": "default",
            "conversation_key": "topic:1",
            "conversation_mode": "topic",
            "queue_kind": "new",
            "prompt": "你是谁？",
            "show_details": False,
            "source": {"chat_id": "oc_1", "message_id": "om_1"},
        }

        prompt = bridge.build_codex_prompt(job)

        self.assertIn("你是飞书助手。", prompt)
        self.assertIn("Do not identify yourself as Codex", prompt)
        self.assertIn("Internal bridge context (for routing only; do not include this in the final answer):", prompt)
        self.assertNotIn("You are Codex running", prompt)

    def test_topic_reply_without_explicit_reply_to_finds_running_topic_job(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "private": {},
            "sessions": {"enabled": True, "mode": "topic", "reply_guidance_enabled": True},
        }
        bridge.read_conversations = lambda: {
            "p2p:oc_1:topic:omt_topic": {
                "chat_id": "oc_1",
                "topic_ids": ["omt_topic", "om_root", "om_card"],
                "updated_at": "2026-04-27T02:12:00Z",
            }
        }
        bridge.read_jobs = lambda: [
            {
                "job_id": "job-root",
                "status": "running",
                "conversation_key": "p2p:oc_1:topic:omt_topic",
                "conversation_mode": "topic",
                "queue_kind": "new",
                "status_message_id": "om_card",
                "topic_ids": ["omt_topic", "om_root", "om_card"],
                "source": {"chat_id": "oc_1", "message_id": "om_root", "thread_id": "omt_topic"},
            }
        ]
        msg = {
            "message_id": "om_child",
            "chat_id": "oc_1",
            "chat_type": "p2p",
            "reply_to": "",
            "parent_id": "",
            "root_id": "om_root",
            "thread_id": "omt_topic",
        }

        reply_job = bridge.find_reply_job_for_msg(msg)

        self.assertIsNotNone(reply_job)
        self.assertEqual("job-root", reply_job["job_id"])

    def test_access_settings_override_global_defaults(self) -> None:
        bridge = bridge_for_policy()
        msg = {"sender_id": "ou_1", "sender_open_id": "ou_1", "chat_id": "oc_1"}

        policy = bridge.policy_for(msg, "oc_1")
        profile = bridge.model_profile("default", policy["settings"])

        self.assertTrue(policy["show_details"])
        self.assertEqual("默认助手", policy["settings"]["assistant"]["display_name"])
        self.assertEqual("gpt-5.4-mini", profile["model"])

    def test_user_settings_apply_when_no_chat_group_policy_exists(self) -> None:
        bridge = bridge_for_policy()
        msg = {"sender_id": "ou_1", "sender_open_id": "ou_1", "chat_id": "oc_other"}

        policy = bridge.policy_for(msg, "oc_other")

        self.assertTrue(policy["allow_codex"])
        self.assertEqual("用户助手", policy["settings"]["assistant"]["display_name"])

    def test_empty_user_group_does_not_apply_to_everyone(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "identities": {},
                "user_groups": {
                    "template": {"enabled": True, "members": [], "allow_codex": True},
                },
                "groups": {},
            },
        }

        policy = bridge.policy_for({"sender_id": "ou_other", "sender_open_id": "ou_other"})

        self.assertFalse(policy["allow_codex"])
        self.assertEqual([], policy["user_group_keys"])

    def test_user_group_requires_explicit_all_match(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "identities": {},
                "user_groups": {
                    "all": {"enabled": True, "members": ["*"], "allow_codex": True},
                },
                "groups": {},
            },
        }

        policy = bridge.policy_for({"sender_id": "ou_other", "sender_open_id": "ou_other"})

        self.assertTrue(policy["allow_codex"])
        self.assertEqual(["all"], policy["user_group_keys"])

    def test_template_only_user_group_does_not_apply_to_members(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "identities": {"alice": {"open_ids": ["ou_alice"]}},
                "user_groups": {
                    "operator-template": {
                        "enabled": True,
                        "preset_only": True,
                        "members": ["alice"],
                        "allow_codex": True,
                    },
                },
                "groups": {},
            },
        }

        policy = bridge.policy_for({"sender_id": "ou_alice", "sender_open_id": "ou_alice"})

        self.assertFalse(policy["allow_codex"])
        self.assertEqual([], policy["user_group_keys"])

    def test_chat_group_empty_members_still_applies_to_chat(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "identities": {},
                "user_groups": {},
                "groups": {
                    "team-chat": {"enabled": True, "chat_ids": ["oc_team"], "members": [], "allow_codex": True},
                },
            },
        }

        policy = bridge.policy_for({"sender_id": "ou_any", "sender_open_id": "ou_any"}, "oc_team")

        self.assertTrue(policy["allow_codex"])
        self.assertEqual("team-chat", policy["group_key"])

    def test_chat_group_policy_ignores_user_permissions(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "reply": {"show_details_by_default": False, "show_progress_by_default": False},
            "access": {
                "default_policy": {"allow_codex": False, "tasks": []},
                "identities": {"alice": {"open_ids": ["ou_alice"], "allow_codex": True, "tasks": ["*"]}},
                "user_groups": {
                    "operators": {"enabled": True, "members": ["alice"], "allow_codex": True, "tasks": ["*"]},
                },
                "groups": {
                    "review-chat": {
                        "enabled": True,
                        "chat_ids": ["oc_review"],
                        "members": [],
                        "allow_codex": False,
                        "tasks": ["mobile-review"],
                    },
                },
            },
        }

        policy = bridge.policy_for({"sender_id": "ou_alice", "sender_open_id": "ou_alice"}, "oc_review")

        self.assertFalse(policy["allow_codex"])
        self.assertEqual(["mobile-review"], policy["tasks"])
        self.assertEqual([], policy["user_group_keys"])
        self.assertEqual("review-chat", policy["group_key"])

    def test_chat_group_membership_miss_still_blocks_user_fallback(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "reply": {"show_details_by_default": False, "show_progress_by_default": False},
            "access": {
                "default_policy": {"allow_codex": False, "tasks": []},
                "identities": {"alice": {"open_ids": ["ou_alice"], "allow_codex": True, "tasks": ["*"]}},
                "user_groups": {
                    "operators": {"enabled": True, "members": ["alice"], "allow_codex": True, "tasks": ["*"]},
                },
                "groups": {
                    "review-chat": {
                        "enabled": True,
                        "chat_ids": ["oc_review"],
                        "members": ["bob"],
                        "allow_codex": True,
                        "tasks": ["*"],
                    },
                },
            },
        }

        policy = bridge.policy_for({"sender_id": "ou_alice", "sender_open_id": "ou_alice"}, "oc_review")

        self.assertFalse(policy["allow_codex"])
        self.assertEqual([], policy["tasks"])
        self.assertEqual([], policy["user_group_keys"])
        self.assertEqual("", policy["group_key"])

    def test_group_message_can_require_bot_mention(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "assistant": {"display_name": "飞书助手"},
            "routing": {"only_respond_to_bot_mention": True, "bot_mention_ids": ["ou_bot"]},
        }

        self.assertTrue(
            bridge.should_ignore_unmentioned_group_message({"chat_type": "group", "text": "普通消息", "mentions": []})
        )
        self.assertFalse(
            bridge.should_ignore_unmentioned_group_message({"chat_type": "group", "text": "@飞书助手 处理评审", "mentions": []})
        )
        self.assertFalse(
            bridge.should_ignore_unmentioned_group_message(
                {"chat_type": "group", "text": "处理评审", "mentions": [{"id": {"open_id": "ou_bot"}}]}
            )
        )

    def test_group_policy_can_override_bot_mention_requirement(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "assistant": {"display_name": "飞书助手"},
            "routing": {"only_respond_to_bot_mention": True},
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "open-chat": {
                        "chat_ids": ["oc_open"],
                        "settings": {"routing": {"only_respond_to_bot_mention": False}},
                    }
                },
            },
        }

        self.assertFalse(
            bridge.should_ignore_unmentioned_group_message(
                {"chat_type": "group", "chat_id": "oc_open", "sender_id": "ou_1", "sender_open_id": "ou_1", "text": "普通消息", "mentions": []}
            )
        )
        self.assertTrue(
            bridge.should_ignore_unmentioned_group_message(
                {"chat_type": "group", "chat_id": "oc_other", "sender_id": "ou_1", "sender_open_id": "ou_1", "text": "普通消息", "mentions": []}
            )
        )

    def test_private_message_can_require_bot_mention(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "assistant": {"display_name": "飞书助手"},
            "routing": {"private_only_respond_to_bot_mention": True},
        }

        self.assertTrue(
            bridge.should_ignore_unmentioned_message(
                {"chat_type": "p2p", "chat_id": "oc_private", "sender_id": "ou_1", "sender_open_id": "ou_1", "text": "普通消息", "mentions": []}
            )
        )
        self.assertFalse(
            bridge.should_ignore_unmentioned_message(
                {"chat_type": "p2p", "chat_id": "oc_private", "sender_id": "ou_1", "sender_open_id": "ou_1", "text": "@飞书助手 普通消息", "mentions": []}
            )
        )

    def test_hydrated_text_mentions_satisfy_private_bot_mention_requirement(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "assistant": {"display_name": "飞书助手"},
            "routing": {"private_only_respond_to_bot_mention": True, "bot_mention_ids": ["cli_bot"]},
        }
        bridge.log = lambda *args, **kwargs: None
        bridge.run_lark = lambda *args, **kwargs: json.dumps(
            {
                "ok": True,
                "data": {
                    "messages": [
                        {
                            "message_id": "om_1",
                            "msg_type": "text",
                            "content": "<p>@mi-feishu-mcp-helper 添加到今天的技术方案</p>",
                            "mentions": [{"id": "cli_bot", "name": "mi-feishu-mcp-helper"}],
                        }
                    ]
                },
            }
        )

        msg = {
            "message_id": "om_1",
            "chat_type": "p2p",
            "chat_id": "oc_private",
            "sender_id": "ou_1",
            "sender_open_id": "ou_1",
            "msg_type": "text",
            "text": "添加到今天的技术方案",
            "mentions": [],
        }

        self.assertTrue(bridge.should_ignore_unmentioned_message(msg))
        hydrated = bridge.hydrate_message_from_lark(msg)
        self.assertFalse(bridge.should_ignore_unmentioned_message(hydrated))

    def test_hydrated_sender_allows_private_policy_override(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "assistant": {"display_name": "飞书助手"},
            "routing": {"private_only_respond_to_bot_mention": True},
            "access": {
                "default_policy": {"allow_codex": False},
                "identities": {
                    "alice": {
                        "open_ids": ["ou_alice"],
                        "settings": {"routing": {"private_only_respond_to_bot_mention": False}},
                    }
                },
            },
        }
        bridge.log = lambda *args, **kwargs: None
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.run_lark = lambda *args, **kwargs: json.dumps(
            {
                "ok": True,
                "data": {
                    "messages": [
                        {
                            "message_id": "om_1",
                            "msg_type": "text",
                            "content": "<p>普通消息</p>",
                            "sender": {"id": "ou_alice"},
                        }
                    ]
                },
            }
        )

        msg = {
            "message_id": "om_1",
            "chat_type": "p2p",
            "chat_id": "oc_private",
            "sender_id": "",
            "sender_open_id": "",
            "msg_type": "text",
            "text": "普通消息",
            "mentions": [],
        }

        self.assertTrue(bridge.should_ignore_unmentioned_message(msg))
        hydrated = bridge.hydrate_message_from_lark(msg)
        self.assertEqual("ou_alice", hydrated["sender_id"])
        self.assertFalse(bridge.should_ignore_unmentioned_message(hydrated))

    def test_event_subscriber_uses_filter_instead_of_event_type_registration(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"event_types": ["im.message.receive_v1", "im.message.recalled_v1"]}

        args, event_types = bridge.event_subscriber_args()

        self.assertEqual("im.message.receive_v1,im.message.recalled_v1", event_types)
        self.assertNotIn("--event-types", args)
        self.assertIn("--filter", args)
        event_filter = args[args.index("--filter") + 1]
        self.assertIn("im\\.message\\.receive_v1", event_filter)
        self.assertIn("im\\.message\\.recalled_v1", event_filter)

    def test_handle_event_hydrates_text_message_before_mention_filter(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "private": {"allowed_chat_ids": ["oc_private"]},
            "assistant": {"display_name": "飞书助手"},
            "routing": {"private_only_respond_to_bot_mention": True, "bot_mention_ids": ["cli_bot"]},
        }
        bridge.enrich_reply_to = lambda msg: msg
        bridge.mark_processed = lambda message_id: True
        bridge.hydrate_message_from_lark = lambda msg: {**msg, "mentions": [{"id": "cli_bot", "name": "mi-feishu-mcp-helper"}]}
        handled: list[dict[str, object]] = []
        bridge.handle_text_command = lambda msg, prefer_reply: handled.append(msg)

        bridge.handle_event(
            {
                "header": {"event_type": "im.message.receive_v1"},
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_1"}},
                    "message": {
                        "message_id": "om_1",
                        "chat_id": "oc_private",
                        "chat_type": "p2p",
                        "message_type": "text",
                        "content": '{"text":"添加到今天的技术方案"}',
                    },
                },
            }
        )

        self.assertEqual("om_1", handled[0]["message_id"])
        self.assertEqual([{"id": "cli_bot", "name": "mi-feishu-mcp-helper"}], handled[0]["mentions"])

    def test_private_forward_context_is_deferred_and_coalesced_with_comment(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "private": {
                "allowed_chat_ids": ["oc_private"],
                "coalesce_forward_comment_window_sec": 10,
            },
            "routing": {"private_only_respond_to_bot_mention": False},
            "sessions": {"reply_guidance_enabled": False},
        }
        bridge.log = lambda *args, **kwargs: None
        bridge.mark_processed = lambda message_id: True
        handled: list[dict[str, object]] = []
        bridge.handle_text_command = lambda msg, prefer_reply: handled.append(msg)

        bridge.handle_event(
            {
                "header": {"event_type": "im.message.receive_v1"},
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_1"}},
                    "message": {
                        "message_id": "om_forward",
                        "chat_id": "oc_private",
                        "chat_type": "p2p",
                        "message_type": "text",
                        "content": '{"text":"https://example.feishu.cn/wiki/DocToken"}',
                    },
                },
            }
        )
        self.assertEqual([], handled)

        bridge.handle_event(
            {
                "header": {"event_type": "im.message.receive_v1"},
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_1"}},
                    "message": {
                        "message_id": "om_comment",
                        "chat_id": "oc_private",
                        "chat_type": "p2p",
                        "message_type": "text",
                        "content": '{"text":"请添加这个"}',
                    },
                },
            }
        )

        self.assertEqual(1, len(handled))
        self.assertEqual("om_comment", handled[0]["message_id"])
        self.assertEqual("om_forward", handled[0]["reply_to"])

    def test_deferred_private_forward_context_dispatches_when_no_comment_arrives(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "private": {
                "allowed_chat_ids": ["oc_private"],
                "coalesce_forward_comment_window_sec": 10,
            },
            "routing": {"private_only_respond_to_bot_mention": False},
            "sessions": {"reply_guidance_enabled": False},
        }
        bridge.log = lambda *args, **kwargs: None
        handled: list[dict[str, object]] = []
        bridge.handle_text_command = lambda msg, prefer_reply: handled.append(msg)

        forward = {
            "message_id": "om_forward",
            "chat_id": "oc_private",
            "chat_type": "p2p",
            "sender_id": "ou_1",
            "sender_open_id": "ou_1",
            "msg_type": "text",
            "content": '{"text":"https://example.feishu.cn/wiki/DocToken"}',
            "text": "https://example.feishu.cn/wiki/DocToken",
            "mentions": [],
            "reply_to": "",
            "parent_id": "",
            "root_id": "",
            "thread_id": "",
        }

        self.assertTrue(bridge.defer_private_forward_context(forward, prefer_reply=True))
        bridge.dispatch_deferred_private_forward_context("oc_private:ou_1", "om_forward", prefer_reply=True)

        self.assertEqual(1, len(handled))
        self.assertEqual("om_forward", handled[0]["message_id"])

    def test_second_forward_context_does_not_reverse_coalesce_first_pending_message(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "private": {
                "allowed_chat_ids": ["oc_private"],
                "coalesce_forward_comment_window_sec": 10,
            },
            "routing": {"private_only_respond_to_bot_mention": False},
            "sessions": {"reply_guidance_enabled": False},
        }
        bridge.log = lambda *args, **kwargs: None
        handled: list[dict[str, object]] = []
        bridge.handle_text_command = lambda msg, prefer_reply: handled.append(msg)

        first = {
            "message_id": "om_forward_1",
            "chat_id": "oc_private",
            "chat_type": "p2p",
            "sender_id": "ou_1",
            "sender_open_id": "ou_1",
            "msg_type": "text",
            "content": '{"text":"https://example.feishu.cn/wiki/DocToken1"}',
            "text": "https://example.feishu.cn/wiki/DocToken1",
            "mentions": [],
            "reply_to": "",
            "parent_id": "",
            "root_id": "",
            "thread_id": "",
        }
        second = {**first, "message_id": "om_forward_2", "content": '{"text":"https://example.feishu.cn/wiki/DocToken2"}', "text": "https://example.feishu.cn/wiki/DocToken2"}

        self.assertTrue(bridge.defer_private_forward_context(first, prefer_reply=True))
        self.assertTrue(bridge.defer_private_forward_context(second, prefer_reply=True))

        self.assertEqual(1, len(handled))
        self.assertEqual("om_forward_1", handled[0]["message_id"])
        self.assertNotEqual("om_forward_2", handled[0].get("reply_to"))

    def test_private_forward_coalesce_can_be_enabled_by_identity_settings(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "private": {"coalesce_forward_comment_enabled": False, "coalesce_forward_comment_window_sec": 1.5},
            "access": {
                "default_policy": {"settings": {}},
                "identities": {
                    "alice": {
                        "open_ids": ["ou_alice"],
                        "settings": {
                            "private": {
                                "coalesce_forward_comment_enabled": True,
                                "coalesce_forward_comment_window_sec": 2.75,
                            }
                        },
                    }
                },
            },
        }
        msg = {
            "chat_type": "p2p",
            "chat_id": "oc_private",
            "sender_id": "ou_alice",
            "sender_open_id": "ou_alice",
            "message_id": "om_forward",
            "msg_type": "text",
            "text": "https://example.feishu.cn/wiki/DocToken",
            "content": '{"text":"https://example.feishu.cn/wiki/DocToken"}',
            "reply_to": "",
            "parent_id": "",
            "root_id": "",
            "thread_id": "",
        }

        self.assertTrue(bridge.should_defer_private_forward_context(msg))
        self.assertEqual(2.75, bridge.private_forward_comment_window_sec(msg))

    def test_private_forward_coalesce_can_be_disabled_by_chat_group_settings(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "private": {"coalesce_forward_comment_enabled": True},
            "access": {
                "default_policy": {"settings": {}},
                "groups": {
                    "no-coalesce": {
                        "chat_ids": ["oc_private"],
                        "settings": {"private": {"coalesce_forward_comment_enabled": False}},
                    }
                },
            },
        }
        msg = {
            "chat_type": "p2p",
            "chat_id": "oc_private",
            "sender_id": "ou_alice",
            "sender_open_id": "ou_alice",
            "message_id": "om_forward",
            "msg_type": "text",
            "text": "https://example.feishu.cn/wiki/DocToken",
            "content": '{"text":"https://example.feishu.cn/wiki/DocToken"}',
            "reply_to": "",
            "parent_id": "",
            "root_id": "",
            "thread_id": "",
        }

        self.assertFalse(bridge.should_defer_private_forward_context(msg))

    def test_user_policy_can_override_private_bot_mention_requirement(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "assistant": {"display_name": "飞书助手"},
            "routing": {"private_only_respond_to_bot_mention": True},
            "access": {
                "default_policy": {"allow_codex": False},
                "identities": {
                    "alice": {
                        "open_ids": ["ou_alice"],
                        "settings": {"routing": {"private_only_respond_to_bot_mention": False}},
                    }
                },
            },
        }

        self.assertFalse(
            bridge.should_ignore_unmentioned_message(
                {"chat_type": "p2p", "chat_id": "oc_private", "sender_id": "ou_alice", "sender_open_id": "ou_alice", "text": "普通消息", "mentions": []}
            )
        )
        self.assertTrue(
            bridge.should_ignore_unmentioned_message(
                {"chat_type": "p2p", "chat_id": "oc_private", "sender_id": "ou_other", "sender_open_id": "ou_other", "text": "普通消息", "mentions": []}
            )
        )

    def test_group_policy_can_accept_any_target(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "machine_id": "local",
            "routing": {"accept_any_target": False},
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "any-chat": {
                        "chat_ids": ["oc_any"],
                        "settings": {"routing": {"accept_any_target": True}},
                    }
                },
            },
        }
        msg = {"chat_id": "oc_any", "sender_id": "ou_1", "sender_open_id": "ou_1"}

        self.assertTrue(bridge.should_accept_target("any", msg))
        self.assertFalse(bridge.should_accept_target("any", {"chat_id": "oc_other", "sender_id": "ou_1", "sender_open_id": "ou_1"}))

    def test_policy_can_override_plain_text_and_preset_matching(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "public": {"treat_all_text_as_codex": False},
            "access": {
                "enable_preset_intent_matching": True,
                "default_policy": {"allow_codex": False},
                "groups": {
                    "plain-chat": {
                        "chat_ids": ["oc_plain"],
                        "settings": {
                            "public": {"treat_all_text_as_codex": True},
                            "access": {"enable_preset_intent_matching": False},
                        },
                    }
                },
            },
        }
        msg = {"chat_type": "group", "chat_id": "oc_plain", "sender_id": "ou_1", "sender_open_id": "ou_1"}

        self.assertTrue(bridge.treat_plain_text_as_codex(msg))
        self.assertFalse(bridge.preset_intent_matching_enabled(msg))

    def test_policy_session_settings_override_conversation_key(self) -> None:
        bridge = bare_bridge()
        bridge.config = {
            "sessions": {"enabled": True, "mode": "continuous"},
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "topic-chat": {
                        "chat_ids": ["oc_topic"],
                        "settings": {"sessions": {"mode": "topic", "topic_reply_in_thread": True}},
                    }
                },
            },
        }
        bridge.read_conversations = lambda: {}
        msg = {
            "chat_type": "group",
            "chat_id": "oc_topic",
            "sender_id": "ou_1",
            "sender_open_id": "ou_1",
            "message_id": "om_1",
            "root_id": "om_root",
        }
        settings = bridge.policy_settings_for_msg(msg)

        self.assertEqual("topic", bridge.session_mode(settings))
        self.assertIn(":topic:om_root", bridge.conversation_key_for_msg(msg, settings=settings))
        self.assertTrue(bridge.should_reply_in_thread(msg, prefer_reply=True, settings=settings))

    def test_policy_can_disable_media_download(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"multimodal": {"download_incoming": True}}
        bridge.run_lark = mock.Mock(return_value="")

        saved = bridge.download_resources(
            "om_1",
            "image",
            {"image_key": "img_1"},
            settings={"multimodal": {"download_incoming": False}},
        )

        self.assertEqual([], saved)
        bridge.run_lark.assert_not_called()

    def test_scheduled_task_due_window_uses_weekday_and_time(self) -> None:
        bridge = bare_bridge()
        item = {"enabled": True, "weekdays": ["mon", "wed"], "time": "18:00", "catch_up_minutes": 5}

        self.assertTrue(bridge.scheduled_task_is_due(item, dt.datetime(2026, 4, 27, 18, 2)))
        self.assertFalse(bridge.scheduled_task_is_due(item, dt.datetime(2026, 4, 27, 18, 8)))
        self.assertFalse(bridge.scheduled_task_is_due(item, dt.datetime(2026, 4, 28, 18, 2)))
        self.assertFalse(bridge.scheduled_task_is_due({"weekdays": ["mon"], "time": "18:00"}, dt.datetime(2026, 4, 27, 18, 2)))

    def test_scheduled_task_requires_explicit_chat_ids_by_default(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"public": {"allowed_chat_ids": ["oc_public"]}}

        self.assertEqual([], bridge.scheduled_task_chat_ids({}))
        self.assertEqual(["oc_public"], bridge.scheduled_task_chat_ids({"allow_public_chat_fallback": True}))
        self.assertEqual(["oc_target"], bridge.scheduled_task_chat_ids({"chat_ids": ["oc_target"]}))

    def test_preset_task_prompt_includes_configured_subtasks(self) -> None:
        bridge = bare_bridge()
        prompt = bridge.build_preset_task_prompt(
            "mobile-review",
            {
                "description": "移动端评审",
                "subtasks": ["跟踪评审结果", "新增/修改/删除评审文档"],
                "prompt_template": "允许的响应子任务:\n{subtasks}\n用户输入:\n{input}",
            },
            "请更新今天评审状态",
            {"chat_id": "oc_1", "sender_id": "ou_1", "message_id": "om_1"},
        )

        self.assertIn("1. [manual] subtask-1: 跟踪评审结果", prompt)
        self.assertIn("2. [manual] subtask-2: 新增/修改/删除评审文档", prompt)
        self.assertIn("请更新今天评审状态", prompt)

    def test_main_task_permission_allows_subtasks_with_overrides(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "tasks": ["mobile-review"],
                        "task_subtasks": {"mobile-review": ["track-review-result"]},
                        "auto_subtasks": {"mobile-review": ["overload-check"]},
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {
                    "enabled": True,
                    "subtasks": [
                        {"id": "track-review-result", "type": "manual", "enabled": True},
                        {"id": "manage-review-doc", "type": "manual", "enabled": True},
                        {"id": "overload-check", "type": "automatic", "enabled": True},
                        {"id": "submit-lock-reminder", "type": "automatic", "enabled": True},
                    ],
                }
            },
        }
        sender = {"sender_id": "ou_user", "sender_open_id": "ou_user"}

        self.assertTrue(bridge.task_allowed_for_sender(sender, "oc_review", "mobile-review", "track-review-result"))
        self.assertFalse(bridge.task_allowed_for_sender(sender, "oc_review", "mobile-review", "manage-review-doc"))
        self.assertTrue(bridge.task_allowed_for_sender(sender, "oc_review", "mobile-review", "overload-check", automatic=True))
        self.assertFalse(bridge.task_allowed_for_sender(sender, "oc_review", "mobile-review", "submit-lock-reminder", automatic=True))

    def test_task_required_skills_follow_the_task_permission(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "tasks": ["mobile-review"],
                        "skills": [],
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {
                    "enabled": True,
                    "required_skills": ["lark-doc", "lark-base"],
                }
            },
        }
        sender = {"sender_id": "ou_user", "sender_open_id": "ou_user"}

        self.assertTrue(bridge.task_allowed_for_sender(sender, "oc_review", "mobile-review"))

    def test_free_form_skill_and_model_restrictions_are_only_for_explicit_overrides(self) -> None:
        bridge = bare_bridge()
        policy = {"allow_codex": True, "skills": ["lark-doc"], "models": ["gpt-5.4"]}

        self.assertTrue(bridge.skills_allowed_for_policy(policy, []))
        self.assertTrue(bridge.skills_allowed_for_policy(policy, ["lark-doc"]))
        self.assertFalse(bridge.skills_allowed_for_policy(policy, ["lark-base"]))
        self.assertTrue(bridge.model_allowed_for_policy(policy, "gpt-5.5", explicit=False))
        self.assertTrue(bridge.model_allowed_for_policy(policy, "gpt-5.4", explicit=True))
        self.assertFalse(bridge.model_allowed_for_policy(policy, "gpt-5.5", explicit=True))

    def test_plain_text_auto_routes_when_only_one_task_is_allowed(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "enable_preset_intent_matching": True,
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "tasks": ["mobile-review"],
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {"enabled": True, "description": "移动端评审"},
            },
        }
        msg = {"sender_id": "ou_user", "sender_open_id": "ou_user", "chat_id": "oc_review", "chat_type": "group"}

        task_id, task, task_input = bridge.auto_route_single_task(msg, "这个文档能排今天评审吗")

        self.assertEqual("mobile-review", task_id)
        self.assertEqual("移动端评审", task["description"])
        self.assertEqual("这个文档能排今天评审吗", task_input)

    def test_plain_text_does_not_auto_route_when_multiple_tasks_are_allowed(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "enable_preset_intent_matching": True,
                "default_policy": {"allow_codex": False},
                "groups": {
                    "ops": {
                        "chat_ids": ["oc_ops"],
                        "tasks": ["mobile-review", "release-check"],
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {"enabled": True},
                "release-check": {"enabled": True},
            },
        }
        msg = {"sender_id": "ou_user", "sender_open_id": "ou_user", "chat_id": "oc_ops", "chat_type": "group"}

        task_id, task, task_input = bridge.auto_route_single_task(msg, "帮看一下")

        self.assertIsNone(task_id)
        self.assertIsNone(task)
        self.assertEqual("", task_input)

    def test_plain_text_auto_route_does_not_steal_free_form_users(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "enable_preset_intent_matching": True,
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "allow_codex": True,
                        "tasks": ["mobile-review"],
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {"enabled": True},
            },
        }
        msg = {"sender_id": "ou_user", "sender_open_id": "ou_user", "chat_id": "oc_review", "chat_type": "group"}

        task_id, task, task_input = bridge.auto_route_single_task(msg, "随便问一个开放问题")

        self.assertIsNone(task_id)
        self.assertIsNone(task)
        self.assertEqual("", task_input)

    def test_task_router_prompt_lists_allowed_tasks_and_virtual_tasks(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"access": {"deny_message": "暂无权限"}}

        prompt = bridge.task_router_prompt(
            {"chat_id": "oc_1", "sender_id": "ou_1", "message_id": "om_1"},
            "帮我看一下这个请求",
            [
                ("mobile-review", {"description": "移动端评审", "required_skills": ["lark-doc"]}),
                ("release-check", {"description": "发布检查"}),
            ],
            free_form_allowed=True,
            unrestricted_allowed=False,
        )

        self.assertIn("Task ID: mobile-review", prompt)
        self.assertIn("Task ID: release-check", prompt)
        self.assertIn("free-form", prompt)
        self.assertIn("virtual tasks are fallback only", prompt)
        self.assertIn("暂无权限", prompt)

    def test_example_manage_review_doc_prefers_wiki_move_before_copy(self) -> None:
        config_path = Path(__file__).resolve().parents[1] / "bridge.config.example.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        subtasks = config["preset_tasks"]["mobile-review"]["subtasks"]
        prompt = next(item["prompt"] for item in subtasks if item.get("id") == "manage-review-doc")

        self.assertIn("lark-cli wiki spaces get_node", prompt)
        self.assertIn("wiki +move --node-token", prompt)
        self.assertIn("--apply", prompt)
        self.assertIn("Creating a copy is the final fallback only", prompt)
        self.assertIn("verify the final node location before writing the tracking Base", prompt)

    def test_plain_text_single_allowed_task_still_uses_natural_router(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "private": {"default_workspace": "fitness-app"},
            "access": {
                "enable_preset_intent_matching": True,
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "tasks": ["mobile-review"],
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {
                    "enabled": True,
                    "description": "移动端评审",
                    "required_skills": ["lark-doc"],
                },
            },
        }
        msg = {
            "sender_id": "ou_user",
            "sender_open_id": "ou_user",
            "chat_id": "oc_review",
            "chat_type": "group",
            "message_id": "om_1",
        }
        captured = {}

        def fake_start_codex_job(msg_arg, prompt_arg, **kwargs):
            captured.update(kwargs)
            captured["prompt_arg"] = prompt_arg
            return {"job_id": "job_1"}

        bridge.start_codex_job = fake_start_codex_job
        bridge.start_preset_task_job = lambda *args, **kwargs: self.fail("plain text should route before preset execution")

        result = bridge.start_natural_task_router_job(msg, "请说明目前是什么模型", prefer_reply=True)

        self.assertEqual({"job_id": "job_1"}, result)
        self.assertEqual("task_router", captured["job_kind"])
        self.assertEqual("natural-task-router", captured["task_id"])
        self.assertIn("请说明目前是什么模型", captured["prompt_override"])

    def test_automatic_subtask_does_not_target_parent_task_only_groups(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "tasks": ["mobile-review"],
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {
                    "enabled": True,
                    "subtasks": [
                        {
                            "id": "overload-check",
                            "type": "automatic",
                            "enabled": True,
                            "schedule": {"weekdays": ["tue"], "time": "10:00"},
                            "action": {"input": "check overload"},
                        }
                    ],
                }
            },
        }

        items = bridge.scheduled_subtask_items()

        self.assertEqual(1, len(items))
        self.assertEqual([], items[0]["chat_ids"])

    def test_automatic_subtask_targets_groups_with_explicit_auto_permission(self) -> None:
        bridge = bare_bridge()
        bridge.contact_values_for_open_id = lambda open_id: []
        bridge.config = {
            "access": {
                "default_policy": {"allow_codex": False},
                "groups": {
                    "review": {
                        "chat_ids": ["oc_review"],
                        "tasks": ["mobile-review"],
                        "auto_subtasks": {"mobile-review": ["overload-check"]},
                    }
                },
            },
            "preset_tasks": {
                "mobile-review": {
                    "enabled": True,
                    "subtasks": [
                        {
                            "id": "overload-check",
                            "type": "automatic",
                            "enabled": True,
                            "schedule": {"weekdays": ["tue"], "time": "10:00"},
                            "action": {"input": "check overload"},
                        }
                    ],
                }
            },
        }

        items = bridge.scheduled_subtask_items()

        self.assertEqual(1, len(items))
        self.assertEqual("mobile-review", items[0]["task_id"])
        self.assertEqual("overload-check", items[0]["subtask_id"])
        self.assertEqual("preset_task", items[0]["kind"])
        self.assertEqual(["oc_review"], items[0]["chat_ids"])
        self.assertTrue(items[0]["suppress_completion_reply"])

    def test_scheduled_completion_reply_is_suppressed_by_default(self) -> None:
        bridge = bare_bridge()
        events: list[str] = []
        bridge.append_job_event = lambda job_id, event, **kwargs: events.append(event)
        bridge.update_job_status_message = lambda *args, **kwargs: self.fail("completion should be suppressed")
        bridge.send_response = lambda *args, **kwargs: self.fail("completion should be suppressed")

        bridge.notify_job_done(
            {
                "job_id": "job-scheduled",
                "status": "completed",
                "suppress_completion_reply": True,
                "source": {"chat_id": "oc_review", "message_id": "om_1"},
            },
            "已发送提醒。",
        )

        self.assertEqual(["suppressed_completion_reply"], events)

    def test_automatic_subtask_prompt_forbids_mentions_by_default(self) -> None:
        bridge = bare_bridge()
        prompt = bridge.build_preset_task_prompt(
            "mobile-review",
            {
                "description": "移动端评审",
                "subtasks": [
                    {
                        "id": "submit-lock-reminder",
                        "type": "automatic",
                        "enabled": True,
                        "description": "提醒提交",
                    }
                ],
            },
            "发送提醒",
            {"chat_id": "oc_review", "sender_id": "ou_1", "message_id": "om_1"},
            subtask_id="submit-lock-reminder",
        )

        self.assertIn("不要 @任何人", prompt)

    def test_job_private_settings_override_sandbox(self) -> None:
        bridge = bare_bridge()
        bridge.config = {"private": {"codex_sandbox": "workspace-write"}}
        job = {
            "cwd": ".",
            "output_file": "last-message.txt",
            "codex_options": {},
            "settings": {"private": {"codex_sandbox": "danger-full-access"}},
        }

        args = bridge.codex_args_for_job(job, [])

        self.assertIn("--dangerously-bypass-approvals-and-sandbox", args)
        self.assertNotIn("--sandbox", args)

    def test_final_output_ready_uses_output_last_message_channel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "last-message.txt"
            stdout = root / "codex-stdout.log"
            stderr = root / "codex-stderr.log"
            output.write_text("最终结论", encoding="utf-8")
            stdout.write_text("最终结论", encoding="utf-8")
            stderr.write_text("codex\n最终结论\ntokens used\n123", encoding="utf-8")
            old = output.stat().st_mtime - 10
            os.utime(output, (old, old))
            bridge = bare_bridge()
            job = {
                "output_file": str(output),
                "stdout_file": str(stdout),
                "stderr_file": str(stderr),
            }

            self.assertTrue(bridge.final_output_ready(job, stable_sec=3))

            now = stdout.stat().st_mtime
            os.utime(output, (now, now))
            self.assertFalse(bridge.final_output_ready(job, stable_sec=3))

    def test_progress_summary_uses_latest_tail_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stderr = root / "codex-stderr.log"
            old_lines = ["very old progress should not be shown"] + [f"filler progress {idx}" for idx in range(1200)]
            stderr.write_text("\n".join(old_lines + ['"new command"', "new result line"]), encoding="utf-8")
            bridge = bare_bridge()
            bridge.config = {"private": {}, "reply": {"progress_max_lines": 3}}
            job = {"stderr_file": str(stderr), "show_progress": True}

            progress = bridge.progress_summary_for_job(job)

            self.assertTrue(progress[0].endswith("new result line"))
            self.assertTrue(any("new command" in line for line in progress))
            self.assertFalse(any("very old progress" in line for line in progress))

    def test_progress_summary_filters_garbled_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            stderr = Path(temp_dir) / "codex-stderr.log"
            stderr.write_text('����: û���ҵ����� "27880"��\n"valid command"\nvalid output\n', encoding="utf-8")
            bridge = bare_bridge()
            bridge.config = {"private": {}, "reply": {"progress_max_lines": 4}}
            job = {"stderr_file": str(stderr), "show_progress": True}

            progress = bridge.progress_summary_for_job(job)

        self.assertTrue(any("valid output" in line for line in progress))
        self.assertFalse(any("27880" in line for line in progress))

    def test_wait_for_codex_extends_timeout_for_active_output_once(self) -> None:
        class FakeStdin:
            def write(self, value: str) -> None:
                self.value = value

            def flush(self) -> None:
                pass

            def close(self) -> None:
                pass

        class FakeProc:
            stdin = FakeStdin()
            args = ["codex", "exec"]

            def poll(self):
                return None

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stderr = root / "codex-stderr.log"
            stderr.write_text("active output", encoding="utf-8")
            bridge = bare_bridge()
            bridge.config = {
                "private": {
                    "codex_active_output_grace_sec": 1,
                    "codex_timeout_extension_sec": 1,
                }
            }
            events: list[tuple[str, dict]] = []
            bridge.save_job = lambda job: None
            bridge.append_job_event = lambda job_id, name, **kwargs: events.append((name, kwargs))
            job = {
                "job_id": "job-active-timeout",
                "stderr_file": str(stderr),
                "settings": {},
            }

            with self.assertRaises(subprocess.TimeoutExpired):
                bridge.wait_for_codex_process(FakeProc(), job, "prompt", timeout=0)

            self.assertEqual(1, job["timeout_extension_count"])
            self.assertEqual("timeout_extended_for_activity", events[0][0])

    def test_dashboard_job_detail_includes_safe_file_previews(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bridge = bare_bridge()
            bridge.jobs_dir = root / "jobs"
            bridge.artifacts_dir = root / "artifacts"
            bridge.jobs_dir.mkdir()
            bridge.artifacts_dir.mkdir()
            job_id = "job-test"
            job_dir = bridge.jobs_dir / job_id
            artifact_dir = bridge.artifacts_dir / job_id
            job_dir.mkdir()
            artifact_dir.mkdir()
            output = job_dir / "last-message.txt"
            image = artifact_dir / "1-image"
            outside = root / "outside.txt"
            output.write_text("done", encoding="utf-8")
            image.write_bytes(b"\x89PNG\r\n\x1a\n")
            outside.write_text("secret", encoding="utf-8")
            job = {
                "job_id": job_id,
                "status": "completed",
                "output_file": str(output),
                "attachments": [{"type": "image", "path": str(image), "file_key": "img_1"}],
                "stderr_file": str(outside),
            }

            detail = bridge.job_detail_payload(job)

            self.assertEqual(job_id, detail["job_id"])
            self.assertEqual("done", next(item for item in detail["files"] if item["kind"] == "output")["text_preview"])
            self.assertEqual("image/png", detail["attachment_details"][0]["content_type"])
            self.assertEqual(image.resolve(), bridge.job_file_path(job, "attachment", 0))
            self.assertIsNone(bridge.job_file_path(job, "stderr"))


if __name__ == "__main__":
    unittest.main()
