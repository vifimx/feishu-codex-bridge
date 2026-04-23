#!/usr/bin/env python3
"""Local Feishu/Lark to Codex bridge.

The bridge intentionally stays local-first:
- Lark transport is the official lark-cli.
- Codex execution is the local codex CLI.
- State is plain JSON/JSONL under the configured state_dir.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import http.server
import json
import mimetypes
import os
import queue
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from urllib import request as urlrequest


ROOT = Path(__file__).resolve().parent
DASHBOARD_DIR = ROOT / "dashboard"
CODEX_HOME = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
DEFAULT_CONFIG = ROOT / "bridge.config.json"

CONFIG_WRITE_ALLOWLIST = {
    "private.default_workspace",
    "private.codex_sandbox",
    "private.codex_timeout_sec",
    "private.codex_model",
    "private.poll_interval_sec",
    "private.treat_all_text_as_codex",
    "public.allow_codex",
    "public.treat_all_text_as_codex",
    "jobs.max_concurrent",
    "reply.max_chars",
    "reply.upload_full_output_file",
    "multimodal.download_incoming",
    "multimodal.download_timeout_sec",
    "routing.accept_any_target",
    "routing.dispatch_to_peers",
    "routing.prefer_local_when_capable",
    "health_server.enabled",
    "health_server.host",
    "health_server.port",
    "dashboard.allow_config_write",
    "dashboard.auto_refresh_sec",
    "peers.enabled",
    "peers.nodes",
    "access.trusted_sender_open_ids",
    "access.limited_sender_open_ids",
    "access.limited_allowed_commands",
    "access.limited_allowed_task_ids",
    "access.enable_preset_intent_matching",
    "preset_tasks",
    "workspaces",
}


def utcnow() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def parse_ts(value: str | None) -> float:
    if not value:
        return time.time()
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return time.time()


def json_loads_maybe(value: Any) -> Any:
    if isinstance(value, (dict, list)) or value is None:
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return ""
    try:
        return json.loads(text)
    except Exception:
        return value


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def sanitize_file_name(value: str, fallback: str) -> str:
    name = (value or fallback or "artifact").strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:160] or fallback or "artifact"


def shorten(value: str, limit: int = 120) -> str:
    value = value or ""
    if len(value) <= limit:
        return value
    return value[: limit - 12] + " [truncated]"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Command not found: {name}")
    if path.lower().endswith(".ps1"):
        candidate = str(Path(path).with_suffix(".cmd"))
        if Path(candidate).exists():
            return candidate
    return path


class Bridge:
    def __init__(self, config_path: Path, dry_run: bool = False, pid_name: str | None = "bridge.pid"):
        self.config_path = config_path
        self.config = self.load_config(config_path)
        self.dry_run = dry_run
        self.machine_id = str(self.config.get("machine_id") or os.environ.get("COMPUTERNAME") or "local-codex")
        self.log_dir = Path(self.config["log_dir"]).expanduser()
        self.state_dir = Path(self.config["state_dir"]).expanduser()
        self.jobs_dir = self.state_dir / "jobs"
        self.artifacts_dir = self.state_dir / "artifacts"
        self.processed_path = self.state_dir / "processed-message-ids.txt"
        self.stop_event = threading.Event()
        self.lark_cli = resolve_command("lark-cli")
        self.codex_cli = resolve_command("codex")
        ensure_dir(self.log_dir)
        ensure_dir(self.state_dir)
        ensure_dir(self.jobs_dir)
        ensure_dir(self.artifacts_dir)
        if pid_name:
            self.write_pid(pid_name)

    @staticmethod
    def load_config(config_path: Path) -> dict[str, Any]:
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        data = json.loads(config_path.read_text(encoding="utf-8"))
        for key in ("machine_id", "log_dir", "state_dir"):
            if not data.get(key):
                raise ValueError(f"Config missing {key}")
        return data

    def write_pid(self, file_name: str = "bridge.pid") -> None:
        (self.state_dir / file_name).write_text(str(os.getpid()), encoding="ascii")

    def log(self, level: str, message: str, **data: Any) -> None:
        entry = {
            "ts": utcnow(),
            "level": level,
            "message": message,
            "machine_id": self.machine_id,
            "data": data,
        }
        path = self.log_dir / f"bridge-{dt.datetime.now().strftime('%Y%m%d')}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    def append_job_event(self, job_id: str, event: str, **data: Any) -> None:
        entry = {"ts": utcnow(), "job_id": job_id, "event": event, "data": data}
        with (self.jobs_dir / "jobs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    def mark_processed(self, message_id: str) -> bool:
        if not message_id:
            return False
        if self.processed_path.exists():
            ids = self.processed_path.read_text(encoding="utf-8", errors="replace").splitlines()
        else:
            ids = []
        if message_id in ids:
            return False
        ids.append(message_id)
        self.processed_path.write_text("\n".join(ids[-5000:]) + "\n", encoding="utf-8")
        return True

    def env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("LARK_CLI_NO_PROXY", "1")
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")
        return env

    def run_lark(self, args: list[str], timeout: int = 60, cwd: Path | None = None) -> str:
        cmd = [self.lark_cli] + args
        self.log("debug", "run lark-cli", args=args, cwd=str(cwd) if cwd else None)
        proc = subprocess.run(
            cmd,
            input=None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            env=self.env(),
        )
        out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        if proc.returncode != 0:
            raise RuntimeError(out.strip() or f"lark-cli exited with {proc.returncode}")
        return out

    def limit_reply(self, text: str) -> str:
        max_chars = int(self.config.get("reply", {}).get("max_chars", 3500))
        value = (text or "(no output)").strip()
        if len(value) <= max_chars:
            return value
        return value[: max_chars - 80].rstrip() + "\n\n[truncated; full output is stored in bridge job state]"

    def reply_text(self, message_id: str, text: str, idempotency_key: str | None = None) -> None:
        body = self.limit_reply(text)
        if self.dry_run:
            self.log("info", "dry-run reply", message_id=message_id, text=body)
            return
        args = ["im", "+messages-reply", "--as", "bot", "--message-id", message_id, "--text", body]
        if idempotency_key:
            args += ["--idempotency-key", idempotency_key[:64]]
        self.run_lark(args, timeout=60)

    def send_text(self, chat_id: str, text: str, idempotency_key: str | None = None) -> None:
        body = self.limit_reply(text)
        if self.dry_run:
            self.log("info", "dry-run send", chat_id=chat_id, text=body)
            return
        args = ["im", "+messages-send", "--as", "bot", "--chat-id", chat_id, "--text", body]
        if idempotency_key:
            args += ["--idempotency-key", idempotency_key[:64]]
        self.run_lark(args, timeout=60)

    def send_file(self, chat_id: str, message_id: str | None, path: Path, prefer_reply: bool, idempotency_key: str) -> None:
        if self.dry_run:
            self.log("info", "dry-run send file", chat_id=chat_id, message_id=message_id, path=str(path))
            return
        if prefer_reply and message_id:
            args = ["im", "+messages-reply", "--as", "bot", "--message-id", message_id, "--file", str(path)]
        else:
            args = ["im", "+messages-send", "--as", "bot", "--chat-id", chat_id, "--file", str(path)]
        args += ["--idempotency-key", idempotency_key[:64]]
        self.run_lark(args, timeout=180)

    def send_response(
        self,
        chat_id: str,
        message_id: str | None,
        text: str,
        prefer_reply: bool,
        idempotency_key: str | None = None,
    ) -> None:
        if prefer_reply and message_id:
            self.reply_text(message_id, text, idempotency_key=idempotency_key)
        else:
            self.send_text(chat_id, text, idempotency_key=idempotency_key)

    def extract_text(self, msg_type: str, content: Any) -> str:
        parsed = json_loads_maybe(content)
        if isinstance(parsed, str):
            return parsed
        if not isinstance(parsed, dict):
            return safe_text(parsed)
        if msg_type == "text":
            return str(parsed.get("text") or "")
        if msg_type == "post":
            return self.flatten_post(parsed)
        if msg_type == "image":
            return "[image]"
        if msg_type in ("file", "audio", "media", "video"):
            return f"[{msg_type}: {parsed.get('file_name') or parsed.get('file_key') or 'resource'}]"
        if msg_type == "interactive":
            return "[interactive card]\n" + safe_text(parsed)
        return safe_text(parsed)

    @staticmethod
    def flatten_post(parsed: dict[str, Any]) -> str:
        zh = parsed.get("zh_cn") or parsed.get("en_us") or parsed
        title = zh.get("title") if isinstance(zh, dict) else None
        chunks: list[str] = []
        if title:
            chunks.append(str(title))
        content = zh.get("content") if isinstance(zh, dict) else None
        for row in content or []:
            row_text = []
            for item in row or []:
                if not isinstance(item, dict):
                    continue
                text = item.get("text") or item.get("name") or item.get("href") or ""
                if text:
                    row_text.append(str(text))
            if row_text:
                chunks.append("".join(row_text))
        return "\n".join(chunks) if chunks else safe_text(parsed)

    def extract_resources(self, msg_type: str, content: Any) -> list[dict[str, str]]:
        parsed = json_loads_maybe(content)
        if not isinstance(parsed, dict):
            return []
        resources: list[dict[str, str]] = []
        if msg_type == "image" and parsed.get("image_key"):
            resources.append({"type": "image", "file_key": str(parsed["image_key"]), "name": str(parsed.get("image_key"))})
        if msg_type in ("file", "audio", "video") and parsed.get("file_key"):
            resources.append({
                "type": "file",
                "file_key": str(parsed["file_key"]),
                "name": str(parsed.get("file_name") or parsed.get("file_key")),
            })
        if msg_type == "media":
            if parsed.get("file_key"):
                resources.append({
                    "type": "file",
                    "file_key": str(parsed["file_key"]),
                    "name": str(parsed.get("file_name") or parsed.get("file_key")),
                })
            if parsed.get("image_key"):
                resources.append({"type": "image", "file_key": str(parsed["image_key"]), "name": str(parsed.get("image_key"))})
        return resources

    def download_resources(self, message_id: str, msg_type: str, content: Any, job_id: str | None = None) -> list[dict[str, Any]]:
        cfg = self.config.get("multimodal", {})
        if not cfg.get("download_incoming", True):
            return []
        resources = self.extract_resources(msg_type, content)
        if not resources:
            return []
        base = self.artifacts_dir / (job_id or sanitize_file_name(message_id, "message"))
        ensure_dir(base)
        saved: list[dict[str, Any]] = []
        for idx, res in enumerate(resources, 1):
            file_name = sanitize_file_name(res.get("name", ""), f"{idx}-{res['file_key']}")
            output_name = f"{idx}-{file_name}"
            try:
                args = [
                    "im",
                    "+messages-resources-download",
                    "--as",
                    "bot",
                    "--message-id",
                    message_id,
                    "--file-key",
                    res["file_key"],
                    "--type",
                    res["type"],
                    "--output",
                    output_name,
                ]
                out = self.run_lark(args, timeout=int(cfg.get("download_timeout_sec", 300)), cwd=base)
                actual = base / output_name
                if not actual.exists():
                    matches = list(base.glob(output_name + "*"))
                    actual = matches[0] if matches else actual
                saved.append({
                    "type": res["type"],
                    "file_key": res["file_key"],
                    "path": str(actual),
                    "download_output": shorten(out, 240),
                })
            except Exception as exc:
                saved.append({"type": res["type"], "file_key": res["file_key"], "error": str(exc)})
                self.log("error", "resource download failed", message_id=message_id, resource=res, error=str(exc))
        return saved

    def normalize_message(self, raw: dict[str, Any]) -> dict[str, Any]:
        msg_type = str(raw.get("message_type") or raw.get("msg_type") or raw.get("type") or "text")
        content = raw.get("content") if "content" in raw else raw.get("message", {}).get("content")
        message_id = str(raw.get("message_id") or raw.get("message", {}).get("message_id") or "")
        chat_id = str(raw.get("chat_id") or raw.get("message", {}).get("chat_id") or raw.get("chat", {}).get("chat_id") or "")
        chat_type = str(raw.get("chat_type") or raw.get("message", {}).get("chat_type") or "")
        if not chat_type:
            chat_type = "p2p" if chat_id in set(map(str, self.config.get("private", {}).get("allowed_chat_ids", []))) else "group"
        sender = (
            raw.get("sender_id")
            or raw.get("operator_id")
            or raw.get("sender", {}).get("id")
            or raw.get("sender", {}).get("sender_id")
            or raw.get("message", {}).get("sender", {}).get("id")
            or ""
        )
        return {
            "message_id": message_id,
            "chat_id": chat_id,
            "chat_type": chat_type,
            "sender_id": str(sender),
            "msg_type": msg_type,
            "content": content,
            "text": self.extract_text(msg_type, content).strip(),
            "raw": raw,
        }

    def normalize_command_text(self, text: str) -> str:
        text = (text or "").strip()
        return re.sub(r"^\s*@\S+\s+", "", text).strip()

    @staticmethod
    def contains(items: Any, value: str) -> bool:
        return any(str(item) == value for item in (items or []))

    def access_config(self) -> dict[str, Any]:
        return self.config.get("access", {}) or {}

    def trusted_sender_ids(self) -> list[str]:
        access = self.access_config()
        ids: list[str] = []
        ids.extend(str(item) for item in access.get("trusted_sender_open_ids", []) or [])
        # Backward compatibility: existing bridge configs treated these as full-access operators.
        ids.extend(str(item) for item in self.config.get("authorized_sender_open_ids", []) or [])
        if "access" not in self.config:
            ids.extend(str(item) for item in self.config.get("private", {}).get("allowed_sender_open_ids", []) or [])
            ids.extend(str(item) for item in self.config.get("public", {}).get("allowed_sender_open_ids", []) or [])
        return list(dict.fromkeys(ids))

    def limited_sender_ids(self) -> list[str]:
        return [str(item) for item in self.access_config().get("limited_sender_open_ids", []) or []]

    def sender_access_level(self, sender: str) -> str:
        if self.contains(self.trusted_sender_ids(), sender):
            return "trusted"
        if self.contains(self.limited_sender_ids(), sender):
            return "limited"
        return "none"

    def chat_route_allowed(self, chat_type: str, chat_id: str) -> bool:
        pub = self.config.get("public", {})
        priv = self.config.get("private", {})
        if chat_type == "p2p":
            return bool(priv.get("enabled") and self.contains(priv.get("allowed_chat_ids"), chat_id))
        return bool(pub.get("enabled") and self.contains(pub.get("allowed_chat_ids"), chat_id))

    def command_allowed_for_sender(self, sender: str, name: str) -> bool:
        level = self.sender_access_level(sender)
        if level == "trusted":
            return True
        if level != "limited":
            return False
        allowed = self.access_config().get(
            "limited_allowed_commands",
            ["help", "status", "history", "capabilities", "peers"],
        )
        return self.contains(allowed, name)

    def preset_tasks(self) -> dict[str, Any]:
        tasks = self.config.get("preset_tasks", {}) or {}
        return tasks if isinstance(tasks, dict) else {}

    def task_allowed_for_sender(self, sender: str, chat_id: str, task_id: str) -> bool:
        task = self.preset_tasks().get(task_id)
        if not isinstance(task, dict) or not task.get("enabled", True):
            return False
        task_chat_ids = task.get("allowed_chat_ids") or []
        if task_chat_ids and not self.contains(task_chat_ids, chat_id):
            return False
        task_sender_ids = task.get("allowed_sender_open_ids") or []
        if task_sender_ids and not self.contains(task_sender_ids, sender):
            return False
        level = self.sender_access_level(sender)
        if level == "trusted":
            return True
        if level != "limited":
            return False
        allowed_tasks = self.access_config().get("limited_allowed_task_ids", [])
        return self.contains(allowed_tasks, task_id)

    def match_preset_task(self, text: str) -> tuple[str | None, dict[str, Any] | None, str]:
        cleaned = (text or "").strip()
        if not cleaned:
            return None, None, ""
        explicit = re.match(r"^\s*/task\s+(?P<task>[\w.-]+)(?:\s+(?P<body>[\s\S]*))?$", cleaned)
        if explicit:
            task_id = explicit.group("task")
            task = self.preset_tasks().get(task_id)
            return (task_id, task, (explicit.group("body") or "").strip()) if isinstance(task, dict) else (None, None, cleaned)
        cmd = re.match(r"^\s*/cmd\s+(?P<task>[\w.-]+)(?:\s+(?P<body>[\s\S]*))?$", cleaned)
        if cmd:
            task_id = cmd.group("task")
            task = self.preset_tasks().get(task_id)
            return (task_id, task, (cmd.group("body") or "").strip()) if isinstance(task, dict) else (None, None, cleaned)
        if not self.access_config().get("enable_preset_intent_matching", True):
            return None, None, cleaned
        lowered = cleaned.lower()
        for task_id, task in self.preset_tasks().items():
            if not isinstance(task, dict) or not task.get("enabled", True):
                continue
            aliases = [task_id]
            aliases.extend(str(item) for item in task.get("aliases", []) or [])
            for alias in aliases:
                alias_text = str(alias).strip()
                if alias_text and alias_text.lower() in lowered:
                    return task_id, task, cleaned
        return None, None, cleaned

    def allowed_for_cmd(self, chat_type: str, chat_id: str, sender: str) -> bool:
        return self.chat_route_allowed(chat_type, chat_id) and self.sender_access_level(sender) in ("trusted", "limited")

    def allowed_for_codex(self, chat_type: str, chat_id: str, sender: str) -> bool:
        if self.sender_access_level(sender) != "trusted":
            return False
        pub = self.config.get("public", {})
        if chat_type == "p2p":
            return self.chat_route_allowed(chat_type, chat_id)
        return bool(pub.get("allow_codex") and self.chat_route_allowed(chat_type, chat_id))

    def invoke_fixed_command(self, name: str) -> str:
        commands = self.config.get("public", {}).get("commands", {}) or {}
        if name not in commands:
            return f"Unknown command: {name}"
        item = commands[name]
        if item.get("text"):
            return str(item["text"])
        args = [str(a) for a in item.get("args", [])]
        executable = resolve_command(str(item["executable"]))
        timeout = int(item.get("timeout_sec", 300))
        proc = subprocess.run(
            [executable] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=self.env(),
        )
        out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        if proc.returncode != 0:
            return out.strip() or f"{name} exited with {proc.returncode}"
        return out.strip() or "(no output)"

    def built_in_command(self, name: str, rest: str = "") -> str | None:
        key = name.lower()
        if key in ("help", "?"):
            return self.help_text()
        if key in ("status", "jobs"):
            return self.format_status(rest.strip() or None)
        if key in ("history", "recent"):
            return self.format_history()
        if key in ("capabilities", "caps"):
            return json.dumps(self.capabilities(), ensure_ascii=False, indent=2)
        if key in ("peers", "peer"):
            return self.format_peers()
        return None

    def help_text(self) -> str:
        return "\n".join(
            [
                f"machine_id={self.machine_id}",
                "Commands:",
                "/codex-id",
                "/cmd help",
                "/cmd status [job_id]",
                "/cmd history",
                "/cmd capabilities",
                "/cmd peers",
                "/cmd doctor",
                "/cmd auth",
                "/cmd <preset_task> [input]",
                "/task <preset_task> [input]",
                "/codex [@machine_id] [workspace=name] <prompt>",
                "Limited users can only run commands and preset tasks allowed by access.* config.",
                "Text replies use exact UTF-8 plain text. Image/file messages are downloaded to the job artifact directory when possible.",
            ]
        )

    def capabilities(self) -> dict[str, Any]:
        active = [j for j in self.read_jobs() if j.get("status") in ("queued", "running")]
        return {
            "machine_id": self.machine_id,
            "version": self.config.get("protocol_version", "2"),
            "codex_cli": self.codex_cli,
            "lark_cli": self.lark_cli,
            "workspaces": sorted((self.config.get("workspaces") or {}).keys()),
            "skills": self.config.get("capabilities", {}).get("skills", []),
            "modalities": self.config.get("capabilities", {}).get("modalities", ["text", "image", "file"]),
            "active_jobs": len(active),
            "max_concurrent_jobs": int(self.config.get("jobs", {}).get("max_concurrent", 1)),
            "routing": self.config.get("routing", {}),
            "access": {
                "trusted_count": len(self.trusted_sender_ids()),
                "limited_count": len(self.limited_sender_ids()),
                "limited_allowed_commands": self.access_config().get("limited_allowed_commands", []),
                "limited_allowed_task_ids": self.access_config().get("limited_allowed_task_ids", []),
            },
            "preset_tasks": [
                {"id": task_id, "description": task.get("description", ""), "enabled": task.get("enabled", True)}
                for task_id, task in self.preset_tasks().items()
                if isinstance(task, dict)
            ],
        }

    def read_jobs(self) -> list[dict[str, Any]]:
        jobs = []
        for path in self.jobs_dir.glob("job-*.json"):
            try:
                jobs.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        jobs.sort(key=lambda j: str(j.get("created_at", "")), reverse=True)
        return jobs

    def format_status(self, job_id: str | None = None) -> str:
        jobs = self.read_jobs()
        if job_id:
            job = next((j for j in jobs if str(j.get("job_id")) == job_id), None)
            if not job:
                return f"Job not found: {job_id}"
            lines = [
                f"job_id={job.get('job_id')}",
                f"status={job.get('status')}",
                f"workspace={job.get('workspace')}",
                f"created_at={job.get('created_at')}",
                f"updated_at={job.get('updated_at')}",
                f"codex_deeplink={job.get('codex_deeplink') or ''}",
                f"output={job.get('output_file') or ''}",
                f"error={job.get('error') or ''}",
            ]
            return "\n".join(lines)
        active = [j for j in jobs if j.get("status") in ("queued", "running")]
        recent = jobs[:8]
        lines = [f"active_jobs={len(active)}"]
        for job in recent:
            lines.append(
                f"{job.get('job_id')} {job.get('status')} workspace={job.get('workspace')} "
                f"updated={job.get('updated_at')} prompt={shorten(str(job.get('prompt','')), 64)}"
            )
        return "\n".join(lines)

    def format_history(self) -> str:
        jobs = [j for j in self.read_jobs() if j.get("status") in ("completed", "failed", "timed_out")]
        if not jobs:
            return "No completed bridge jobs yet."
        return "\n".join(
            f"{j.get('job_id')} {j.get('status')} workspace={j.get('workspace')} "
            f"deeplink={j.get('codex_deeplink') or ''} prompt={shorten(str(j.get('prompt','')), 72)}"
            for j in jobs[:10]
        )

    def format_peers(self) -> str:
        peers_cfg = self.config.get("peers", {})
        peers = peers_cfg.get("nodes", []) or []
        if not peers:
            return "No peers configured. Add peers.nodes entries with name, url, capabilities, and enabled=true."
        lines = []
        for peer in peers:
            name = str(peer.get("name") or peer.get("url") or "peer")
            enabled = bool(peer.get("enabled", peers_cfg.get("enabled", False)))
            status = "disabled"
            detail = ""
            if enabled and peer.get("url"):
                try:
                    with urlrequest.urlopen(str(peer["url"]).rstrip("/") + "/health", timeout=2) as resp:
                        detail = resp.read().decode("utf-8", errors="replace")[:500]
                        status = f"ok:{resp.status}"
                except Exception as exc:
                    status = "down"
                    detail = str(exc)
            lines.append(f"{name} {status} {shorten(detail, 160)}")
        return "\n".join(lines)

    def summarize_job(self, job: dict[str, Any]) -> dict[str, Any]:
        attachments = job.get("attachments") or []
        return {
            "job_id": job.get("job_id"),
            "status": job.get("status"),
            "job_kind": job.get("job_kind", "codex"),
            "task_id": job.get("task_id"),
            "workspace": job.get("workspace"),
            "created_at": job.get("created_at"),
            "updated_at": job.get("updated_at"),
            "started_at": job.get("started_at"),
            "finished_at": job.get("finished_at"),
            "prompt_prefix": shorten(str(job.get("prompt") or ""), 180),
            "attachment_count": len(attachments),
            "codex_deeplink": job.get("codex_deeplink"),
            "codex_session_path": job.get("codex_session_path"),
            "output_file": job.get("output_file"),
            "error": shorten(str(job.get("error") or ""), 240),
            "source": job.get("source") or {},
        }

    def dashboard_status(self) -> dict[str, Any]:
        jobs = self.read_jobs()
        counts: dict[str, int] = {}
        for job in jobs:
            status = str(job.get("status") or "unknown")
            counts[status] = counts.get(status, 0) + 1
        active = [j for j in jobs if j.get("status") in ("queued", "running")]
        pid_files = {}
        for name in ("bridge.pid", "dashboard.pid"):
            path = self.state_dir / name
            pid_files[name] = path.read_text(encoding="ascii", errors="replace").strip() if path.exists() else ""
        return {
            "status": "ok",
            "now": utcnow(),
            "config_path": str(self.config_path),
            "log_dir": str(self.log_dir),
            "state_dir": str(self.state_dir),
            "pid": os.getpid(),
            "pid_files": pid_files,
            "capabilities": self.capabilities(),
            "job_counts": counts,
            "active_jobs": [self.summarize_job(j) for j in active],
            "recent_jobs": [self.summarize_job(j) for j in jobs[:10]],
            "dashboard": self.config.get("dashboard", {}),
            "health_server": self.config.get("health_server", {}),
        }

    def read_recent_logs(self, limit: int = 120) -> list[dict[str, Any]]:
        files = sorted(self.log_dir.glob("bridge-*.jsonl"), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
        lines: list[str] = []
        for path in files[:3]:
            try:
                lines.extend(path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:])
            except Exception:
                continue
            if len(lines) >= limit:
                break
        result = []
        for line in lines[-limit:]:
            try:
                result.append(json.loads(line))
            except Exception:
                result.append({"ts": "", "level": "raw", "message": line, "data": {}})
        return result

    def editable_config(self) -> dict[str, Any]:
        return {
            "config": self.config,
            "allow_config_write": bool(self.config.get("dashboard", {}).get("allow_config_write", False)),
            "write_allowlist": sorted(CONFIG_WRITE_ALLOWLIST),
        }

    @staticmethod
    def get_dotted(data: dict[str, Any], key: str) -> Any:
        current: Any = data
        for part in key.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    @staticmethod
    def set_dotted(data: dict[str, Any], key: str, value: Any) -> None:
        current: dict[str, Any] = data
        parts = key.split(".")
        for part in parts[:-1]:
            next_value = current.get(part)
            if not isinstance(next_value, dict):
                next_value = {}
                current[part] = next_value
            current = next_value
        current[parts[-1]] = value

    def coerce_config_value(self, key: str, value: Any) -> Any:
        old = self.get_dotted(self.config, key)
        if key in ("workspaces", "preset_tasks"):
            if not isinstance(value, dict):
                raise ValueError(f"{key} must be a JSON object")
            return value
        if key in ("peers.nodes", "access.trusted_sender_open_ids", "access.limited_sender_open_ids", "access.limited_allowed_commands", "access.limited_allowed_task_ids"):
            if not isinstance(value, list):
                raise ValueError(f"{key} must be a JSON array")
            return value
        if isinstance(old, bool):
            return bool(value)
        if isinstance(old, int) and not isinstance(old, bool):
            return int(value)
        if isinstance(old, list):
            if not isinstance(value, list):
                raise ValueError(f"{key} must be a JSON array")
            return value
        if isinstance(old, dict):
            if not isinstance(value, dict):
                raise ValueError(f"{key} must be a JSON object")
            return value
        return "" if value is None else str(value)

    @staticmethod
    def is_loopback(address: str) -> bool:
        return address in ("127.0.0.1", "::1", "localhost") or address.startswith("127.")

    def update_config(self, updates: dict[str, Any], client_address: str) -> dict[str, Any]:
        if not self.config.get("dashboard", {}).get("allow_config_write", False):
            raise PermissionError("Config writes are disabled. Set dashboard.allow_config_write=true in bridge.config.json.")
        if not self.is_loopback(client_address):
            raise PermissionError("Config writes are only accepted from loopback clients.")
        if not updates:
            return {"changed": [], "restart_recommended": False}
        new_config = json.loads(json.dumps(self.config, ensure_ascii=False))
        changed = []
        for key, value in updates.items():
            if key not in CONFIG_WRITE_ALLOWLIST:
                raise ValueError(f"Config key is not editable from dashboard: {key}")
            coerced = self.coerce_config_value(key, value)
            if self.get_dotted(new_config, key) != coerced:
                self.set_dotted(new_config, key, coerced)
                changed.append(key)
        if not changed:
            return {"changed": [], "restart_recommended": False}
        backup = self.config_path.with_suffix(self.config_path.suffix + "." + dt.datetime.now().strftime("%Y%m%d-%H%M%S") + ".bak")
        backup.write_text(json.dumps(self.config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.config_path.write_text(json.dumps(new_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.config = new_config
        self.machine_id = str(self.config.get("machine_id") or self.machine_id)
        self.log("info", "dashboard updated config", changed=changed, backup=str(backup))
        restart_recommended = any(key.startswith(("health_server.", "dashboard.", "private.poll_interval_sec")) for key in changed)
        return {"changed": changed, "backup": str(backup), "restart_recommended": restart_recommended}

    def should_accept_target(self, target: str | None) -> bool:
        if not target:
            return True
        if target == self.machine_id:
            return True
        if target == "any":
            routing = self.config.get("routing", {})
            return bool(routing.get("accept_any_target", False))
        return False

    def parse_codex_rest(self, rest: str) -> tuple[str, str, str]:
        workspace = str(self.config.get("private", {}).get("default_workspace") or "")
        prompt = rest.strip()
        match = re.match(r"^\s*workspace=(?P<ws>[\w.-]+)\s+(?P<body>[\s\S]+)$", prompt)
        if match:
            workspace = match.group("ws")
            prompt = match.group("body").strip()
        workspaces = self.config.get("workspaces") or {}
        if workspace not in workspaces:
            raise ValueError(f"Unknown workspace: {workspace}")
        cwd = str(workspaces[workspace])
        if not Path(cwd).exists():
            raise ValueError(f"Workspace path not found: {cwd}")
        if not prompt:
            raise ValueError("Missing prompt.")
        return workspace, cwd, prompt

    def can_start_job(self) -> tuple[bool, str]:
        max_jobs = int(self.config.get("jobs", {}).get("max_concurrent", 1))
        active = [j for j in self.read_jobs() if j.get("status") in ("queued", "running")]
        if len(active) >= max_jobs:
            return False, f"Bridge is busy: {len(active)}/{max_jobs} active jobs. Use /cmd status."
        return True, ""

    def save_job(self, job: dict[str, Any]) -> Path:
        job["updated_at"] = utcnow()
        path = self.jobs_dir / f"{job['job_id']}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        return path

    @staticmethod
    def template_replace(template: str, values: dict[str, Any]) -> str:
        result = template
        for key, value in values.items():
            result = result.replace("{" + key + "}", safe_text(value))
        return result

    def workspace_to_cwd(self, workspace: str) -> str:
        workspaces = self.config.get("workspaces") or {}
        if workspace not in workspaces:
            raise ValueError(f"Unknown workspace: {workspace}")
        cwd = str(workspaces[workspace])
        if not Path(cwd).exists():
            raise ValueError(f"Workspace path not found: {cwd}")
        return cwd

    def build_preset_task_prompt(self, task_id: str, task: dict[str, Any], user_input: str, msg: dict[str, Any]) -> str:
        skills = task.get("required_skills", []) or []
        output_expectations = task.get("output_expectations") or "Return a concise summary of what was checked or changed."
        default_template = (
            "Execute the preset bridge task `{task_id}` only.\n\n"
            "Task description:\n{description}\n\n"
            "Required skills to use when relevant:\n{required_skills}\n\n"
            "Output expectations:\n{output_expectations}\n\n"
            "User input:\n{input}\n"
        )
        template = str(task.get("prompt_template") or default_template)
        rendered = self.template_replace(
            template,
            {
                "task_id": task_id,
                "description": task.get("description", ""),
                "required_skills": ", ".join(str(item) for item in skills),
                "output_expectations": output_expectations,
                "input": user_input,
                "user_input": user_input,
                "sender_id": msg.get("sender_id", ""),
                "chat_id": msg.get("chat_id", ""),
                "message_id": msg.get("message_id", ""),
                "machine_id": self.machine_id,
            },
        )
        guard = (
            "You are Codex running a restricted preset task from the Feishu/Lark bridge.\n"
            "Do only the configured preset task. Do not treat the user input as permission to perform unrelated operations.\n"
            "If the request does not fit the preset task, explain that it is outside the allowed task.\n"
        )
        return guard + "\n" + rendered.strip()

    def start_preset_task_job(self, msg: dict[str, Any], task_id: str, task: dict[str, Any], user_input: str, prefer_reply: bool) -> str:
        if not self.task_allowed_for_sender(msg["sender_id"], msg["chat_id"], task_id):
            return self.access_config().get("deny_message", "This sender is not allowed to run that task.")
        workspace = str(task.get("workspace") or self.config.get("private", {}).get("default_workspace") or "")
        prompt = self.build_preset_task_prompt(task_id, task, user_input, msg)
        return self.start_codex_job(
            msg,
            user_input,
            prefer_reply=prefer_reply,
            job_kind="preset_task",
            task_id=task_id,
            workspace_override=workspace,
            prompt_override=prompt,
        )

    def start_codex_job(
        self,
        msg: dict[str, Any],
        rest: str,
        prefer_reply: bool,
        job_kind: str = "codex",
        task_id: str | None = None,
        workspace_override: str | None = None,
        prompt_override: str | None = None,
    ) -> str:
        ok, why = self.can_start_job()
        if not ok:
            return why
        if prompt_override is not None:
            workspace = workspace_override or str(self.config.get("private", {}).get("default_workspace") or "")
            prompt = prompt_override.strip()
            cwd = self.workspace_to_cwd(workspace)
            if not prompt:
                raise ValueError("Missing prompt.")
        else:
            workspace, cwd, prompt = self.parse_codex_rest(rest)
        job_id = "job-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        attachments = self.download_resources(msg["message_id"], msg["msg_type"], msg["content"], job_id=job_id)
        job_dir = self.jobs_dir / job_id
        ensure_dir(job_dir)
        job = {
            "job_id": job_id,
            "status": "queued",
            "created_at": utcnow(),
            "updated_at": utcnow(),
            "machine_id": self.machine_id,
            "job_kind": job_kind,
            "task_id": task_id,
            "workspace": workspace,
            "cwd": cwd,
            "prompt": prompt,
            "source": {
                "chat_id": msg["chat_id"],
                "chat_type": msg["chat_type"],
                "sender_id": msg["sender_id"],
                "message_id": msg["message_id"],
                "msg_type": msg["msg_type"],
                "prefer_reply": prefer_reply,
            },
            "attachments": attachments,
            "output_file": str(job_dir / "last-message.txt"),
            "prompt_file": str(job_dir / "prompt.txt"),
            "stdout_file": str(job_dir / "codex-stdout.log"),
            "stderr_file": str(job_dir / "codex-stderr.log"),
        }
        job_path = self.save_job(job)
        self.append_job_event(job_id, "queued", workspace=workspace, message_id=msg["message_id"])
        if self.dry_run:
            return f"Dry run: would start {job_id}"
        cmd = [
            sys.executable,
            "-u",
            str(Path(__file__).resolve()),
            "--config",
            str(self.config_path),
            "--run-job",
            str(job_path),
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            env=self.env(),
        )
        job["worker_pid"] = proc.pid
        self.save_job(job)
        self.append_job_event(job_id, "worker_started", pid=proc.pid)
        label = f"preset task {task_id}" if task_id else "Codex job"
        return (
            f"{label} started: {job_id}\n"
            f"workspace={workspace}\n"
            f"attachments={len(attachments)}\n"
            f"Use /cmd status {job_id} to inspect progress."
        )

    def build_codex_prompt(self, job: dict[str, Any]) -> str:
        constraints = self.config.get("codex_guardrails", [])
        lines = [
            "You are Codex running from a local Feishu/Lark bot bridge.",
            "Complete USER_REQUEST directly and keep the final answer suitable for a chat reply.",
            "",
            "Bridge context:",
            f"- machine_id: {self.machine_id}",
            f"- job_id: {job['job_id']}",
            f"- source_chat_id: {job.get('source', {}).get('chat_id')}",
            f"- source_message_id: {job.get('source', {}).get('message_id')}",
            f"- workspace: {job.get('workspace')}",
        ]
        if constraints:
            lines.append("")
            lines.append("Guardrails:")
            lines.extend(f"- {item}" for item in constraints)
        attachments = job.get("attachments") or []
        if attachments:
            lines.append("")
            lines.append("Input attachments downloaded by the bridge:")
            for item in attachments:
                if item.get("path"):
                    lines.append(f"- type={item.get('type')} file_key={item.get('file_key')} path={item.get('path')}")
                else:
                    lines.append(f"- type={item.get('type')} file_key={item.get('file_key')} error={item.get('error')}")
            lines.append("Use the local paths above when the task requires inspecting images or files.")
        lines.extend(["", "USER_REQUEST:", str(job.get("prompt") or "").strip()])
        return "\n".join(lines).strip() + "\n"

    def codex_args_for_job(self, job: dict[str, Any], image_paths: list[str]) -> list[str]:
        cfg = self.config.get("private", {})
        args = ["exec"]
        model = str(cfg.get("codex_model") or "").strip()
        if model:
            args += ["-m", model]
        sandbox = str(cfg.get("codex_sandbox") or "workspace-write").strip()
        if sandbox == "danger-full-access":
            args += ["--dangerously-bypass-approvals-and-sandbox"]
        else:
            args += ["--sandbox", sandbox]
        args += ["-C", str(job["cwd"]), "--output-last-message", str(job["output_file"])]
        for image in image_paths:
            args += ["--image", image]
        args += ["-"]
        return args

    def run_codex_job(self, job_path: Path) -> int:
        job = json.loads(job_path.read_text(encoding="utf-8"))
        job["status"] = "running"
        job["started_at"] = utcnow()
        job["runner_pid"] = os.getpid()
        self.save_job(job)
        self.append_job_event(job["job_id"], "running")
        prompt = self.build_codex_prompt(job)
        Path(job["prompt_file"]).write_text(prompt, encoding="utf-8")
        image_paths = [
            str(item["path"])
            for item in (job.get("attachments") or [])
            if item.get("path") and str(item.get("type")) == "image" and Path(str(item["path"])).exists()
        ]
        args = self.codex_args_for_job(job, image_paths)
        timeout = int(self.config.get("private", {}).get("codex_timeout_sec") or 900)
        start_time = time.time()
        try:
            with open(job["stdout_file"], "w", encoding="utf-8", errors="replace") as stdout, open(
                job["stderr_file"], "w", encoding="utf-8", errors="replace"
            ) as stderr:
                proc = subprocess.Popen(
                    [self.codex_cli] + args,
                    cwd=str(job["cwd"]),
                    stdin=subprocess.PIPE,
                    stdout=stdout,
                    stderr=stderr,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=self.env(),
                )
                job["codex_pid"] = proc.pid
                self.save_job(job)
                try:
                    proc.communicate(prompt, timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.communicate()
                    job["status"] = "timed_out"
                    job["error"] = f"Timed out after {timeout} seconds"
                    self.save_job(job)
                    self.append_job_event(job["job_id"], "timed_out")
                    self.notify_job_done(job, "Timed out")
                    return 124
            job["exit_code"] = proc.returncode
            session_path, deeplink = self.find_codex_session(start_time)
            job["codex_session_path"] = session_path
            job["codex_deeplink"] = deeplink
            if proc.returncode == 0:
                job["status"] = "completed"
                result = self.read_job_result(job)
                job["result_prefix"] = shorten(result, 400)
                self.save_job(job)
                self.append_job_event(job["job_id"], "completed", codex_deeplink=deeplink)
                self.notify_job_done(job, result)
                return 0
            job["status"] = "failed"
            job["error"] = self.read_file(job["stderr_file"], 2000) or self.read_file(job["stdout_file"], 2000)
            self.save_job(job)
            self.append_job_event(job["job_id"], "failed", exit_code=proc.returncode)
            self.notify_job_done(job, f"Codex job failed: {job['job_id']}\n{job.get('error')}")
            return int(proc.returncode or 1)
        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)
            self.save_job(job)
            self.append_job_event(job["job_id"], "failed", error=str(exc))
            self.notify_job_done(job, f"Codex job failed: {job['job_id']}\n{exc}")
            return 1

    @staticmethod
    def read_file(path: str, limit: int | None = None) -> str:
        p = Path(path)
        if not p.exists():
            return ""
        text = p.read_text(encoding="utf-8", errors="replace")
        return text if limit is None else text[:limit]

    def read_job_result(self, job: dict[str, Any]) -> str:
        text = self.read_file(job.get("output_file", ""))
        if text.strip():
            return text.strip()
        stdout = self.read_file(job.get("stdout_file", ""), 3000)
        stderr = self.read_file(job.get("stderr_file", ""), 3000)
        return (stdout + "\n" + stderr).strip() or "(no output)"

    def notify_job_done(self, job: dict[str, Any], result: str) -> None:
        source = job.get("source") or {}
        chat_id = str(source.get("chat_id") or "")
        message_id = str(source.get("message_id") or "")
        prefer_reply = bool(source.get("prefer_reply"))
        status = job.get("status")
        header = f"Codex job {job['job_id']} {status}"
        if job.get("codex_deeplink"):
            header += f"\n{job['codex_deeplink']}"
        body = header + "\n\n" + (result or "")
        key = f"{job['job_id']}-{status}"
        self.send_response(chat_id, message_id, body, prefer_reply=prefer_reply, idempotency_key=key)
        reply_cfg = self.config.get("reply", {})
        output_file = Path(str(job.get("output_file") or ""))
        if (
            reply_cfg.get("upload_full_output_file", True)
            and output_file.exists()
            and len((result or "")) > int(reply_cfg.get("max_chars", 3500))
        ):
            try:
                self.send_file(chat_id, message_id, output_file, prefer_reply, idempotency_key=key + "-file")
            except Exception as exc:
                self.log("error", "failed to upload full output file", job_id=job["job_id"], error=str(exc))

    def find_codex_session(self, start_time: float) -> tuple[str, str]:
        sessions = CODEX_HOME / "sessions"
        if not sessions.exists():
            return "", ""
        candidates = []
        for path in glob.glob(str(sessions / "**" / "rollout-*.jsonl"), recursive=True):
            p = Path(path)
            try:
                if p.stat().st_mtime >= start_time - 5:
                    candidates.append(p)
            except OSError:
                pass
        if not candidates:
            return "", ""
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        deeplink = ""
        try:
            first = latest.read_text(encoding="utf-8", errors="replace").splitlines()[0]
            obj = json.loads(first)
            sid = obj.get("payload", {}).get("id")
            if sid:
                deeplink = f"codex://threads/{sid}"
        except Exception:
            pass
        return str(latest), deeplink

    def handle_text_command(self, msg: dict[str, Any], prefer_reply: bool) -> None:
        text = self.normalize_command_text(msg["text"])
        if not text:
            return
        self.log(
            "info",
            "received message",
            message_id=msg["message_id"],
            chat_id=msg["chat_id"],
            chat_type=msg["chat_type"],
            sender_id=msg["sender_id"],
            msg_type=msg["msg_type"],
            text_prefix=shorten(text, 100),
        )
        if re.match(r"^\s*/codex-id\s*$", text):
            body = "\n".join(
                [
                    f"machine_id={self.machine_id}",
                    f"sender_id={msg['sender_id']}",
                    f"chat_id={msg['chat_id']}",
                    f"chat_type={msg['chat_type']}",
                ]
            )
            self.send_response(msg["chat_id"], msg["message_id"], body, prefer_reply, idempotency_key=msg["message_id"] + "-id")
            return
        match = re.match(r"^\s*/cmd\s+(?P<name>[\w.-]+)(?:\s+(?P<rest>[\s\S]*))?$", text)
        if match:
            if not self.allowed_for_cmd(msg["chat_type"], msg["chat_id"], msg["sender_id"]):
                return
            name = match.group("name")
            rest = match.group("rest") or ""
            task = self.preset_tasks().get(name)
            if isinstance(task, dict):
                answer = self.start_preset_task_job(msg, name, task, rest, prefer_reply=prefer_reply)
            elif self.command_allowed_for_sender(msg["sender_id"], name):
                answer = self.built_in_command(name, rest)
                if answer is None:
                    answer = self.invoke_fixed_command(name)
            else:
                answer = self.access_config().get("deny_message", "This sender is not allowed to run that command.")
            self.send_response(msg["chat_id"], msg["message_id"], answer, prefer_reply, idempotency_key=msg["message_id"] + "-cmd")
            return
        task_id, task, task_input = self.match_preset_task(text)
        if task_id and isinstance(task, dict):
            if not self.chat_route_allowed(msg["chat_type"], msg["chat_id"]):
                return
            answer = self.start_preset_task_job(msg, task_id, task, task_input, prefer_reply=prefer_reply)
            self.send_response(msg["chat_id"], msg["message_id"], answer, prefer_reply, idempotency_key=msg["message_id"] + "-task")
            return
        match = re.match(r"^\s*/codex\s+(?:@(?P<target>[\w.-]+)\s+)?(?P<rest>[\s\S]*)$", text)
        codex_rest = None
        target = self.machine_id
        if match:
            target = match.group("target") or self.machine_id
            codex_rest = match.group("rest")
        elif msg["chat_type"] == "p2p" and self.config.get("private", {}).get("treat_all_text_as_codex"):
            codex_rest = text
        elif msg["chat_type"] == "group" and self.config.get("public", {}).get("treat_all_text_as_codex"):
            codex_rest = text
        if codex_rest is None:
            return
        if not self.should_accept_target(target):
            return
        if not self.allowed_for_codex(msg["chat_type"], msg["chat_id"], msg["sender_id"]):
            if self.chat_route_allowed(msg["chat_type"], msg["chat_id"]) and self.sender_access_level(msg["sender_id"]) == "limited":
                self.send_response(
                    msg["chat_id"],
                    msg["message_id"],
                    self.access_config().get("deny_message", "This sender can only run approved preset tasks."),
                    prefer_reply,
                    idempotency_key=msg["message_id"] + "-deny",
                )
            return
        try:
            answer = self.start_codex_job(msg, codex_rest, prefer_reply=prefer_reply)
        except Exception as exc:
            answer = f"Could not start Codex job: {exc}"
            self.log("error", "could not start codex job", error=str(exc), message_id=msg["message_id"])
        self.send_response(msg["chat_id"], msg["message_id"], answer, prefer_reply, idempotency_key=msg["message_id"] + "-job")

    def handle_event(self, event: dict[str, Any]) -> None:
        event_type = str(event.get("type") or "")
        if event_type and event_type != "im.message.receive_v1":
            self.log("info", "received non-message event", event_type=event_type, keys=list(event.keys()))
            if event_type == "im.chat.access_event.bot_p2p_chat_entered_v1":
                self.save_onboarding_contact(event)
            return
        msg = self.normalize_message(event)
        if not msg["message_id"] or not msg["chat_id"]:
            self.log("debug", "message missing id/chat", raw=event)
            return
        if not self.mark_processed(msg["message_id"]):
            return
        if msg["msg_type"] != "text" and not self.extract_resources(msg["msg_type"], msg["content"]):
            self.log("info", "ignored unsupported message type", msg_type=msg["msg_type"], message_id=msg["message_id"])
            return
        self.handle_text_command(msg, prefer_reply=True)

    def save_onboarding_contact(self, event: dict[str, Any]) -> None:
        chat_id = str(event.get("chat_id") or "")
        if not chat_id:
            return
        path = self.state_dir / "latest-p2p-contact.json"
        data = {
            "machine_id": self.machine_id,
            "sender_id": str(event.get("operator_id") or ""),
            "chat_id": chat_id,
            "chat_type": "p2p",
            "event_id": str(event.get("event_id") or ""),
            "updated_at": utcnow(),
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if self.config.get("onboarding", {}).get("enabled", True):
            marker = self.state_dir / f"onboarding-sent-{sanitize_file_name(chat_id, 'chat')}.txt"
            if not marker.exists():
                marker.write_text(utcnow(), encoding="utf-8")
                self.send_text(chat_id, f"codex-id machine_id={self.machine_id}; sender_id={data['sender_id']}; chat_id={chat_id}; chat_type=p2p")

    def private_poller(self) -> None:
        cfg = self.config.get("private", {})
        interval = int(cfg.get("poll_interval_sec", 5))
        self.log("info", "private poller starting", interval=interval)
        while not self.stop_event.is_set():
            for chat_id in cfg.get("allowed_chat_ids", []) or []:
                try:
                    raw = self.run_lark(
                        ["im", "+chat-messages-list", "--as", "bot", "--chat-id", str(chat_id), "--page-size", "10"],
                        timeout=60,
                    )
                    result = json.loads(raw)
                    messages = (
                        result.get("data", {}).get("messages")
                        or result.get("messages")
                        or result.get("items")
                        or []
                    )
                    messages = list(reversed(messages))
                    init_file = self.state_dir / f"private-poller-initialized-{sanitize_file_name(str(chat_id), 'chat')}.txt"
                    initialized = init_file.exists()
                    for raw_msg in messages:
                        msg = self.normalize_message(raw_msg)
                        msg["chat_id"] = msg["chat_id"] or str(chat_id)
                        msg["chat_type"] = "p2p"
                        if not msg["message_id"]:
                            continue
                        is_new = self.mark_processed(msg["message_id"])
                        if not initialized or not is_new:
                            continue
                        if self.sender_access_level(msg["sender_id"]) == "none":
                            continue
                        self.handle_text_command(msg, prefer_reply=False)
                    if not initialized:
                        init_file.write_text(utcnow(), encoding="utf-8")
                        self.log("info", "private poller initialized chat", chat_id=chat_id)
                except Exception as exc:
                    self.log("error", "private poller failed", chat_id=str(chat_id), error=str(exc))
            self.stop_event.wait(interval)

    def event_loop(self) -> None:
        event_types = ",".join(
            self.config.get("event_types")
            or [
                "im.chat.access_event.bot_p2p_chat_entered_v1",
                "im.message.bot_muted_v1",
                "im.message.message_read_v1",
                "im.message.recalled_v1",
                "im.message.receive_v1",
                "p2p_chat_create",
            ]
        )
        args = ["event", "+subscribe", "--event-types", event_types, "--compact", "--quiet"]
        self.log("info", "event subscriber starting", event_types=event_types)
        if self.dry_run:
            print(f"Dry run OK. Config loaded for machine_id={self.machine_id}.")
            return
        proc = subprocess.Popen(
            [self.lark_cli] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=self.env(),
        )
        assert proc.stdout is not None

        def stderr_reader() -> None:
            assert proc.stderr is not None
            for line in proc.stderr:
                line = line.strip()
                if line:
                    self.log("warn", "event subscriber stderr", line=line)

        threading.Thread(target=stderr_reader, daemon=True).start()
        while not self.stop_event.is_set():
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    raise RuntimeError(f"lark-cli event subscriber exited with {proc.returncode}")
                time.sleep(0.2)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                self.handle_event(json.loads(line))
            except Exception as exc:
                self.log("error", "failed to handle event", error=str(exc), line=shorten(line, 1000))
        try:
            proc.terminate()
        except Exception:
            pass

    def health_handler(self):
        bridge = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def send_json(self, status: int, payload: Any) -> None:
                body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def send_dashboard_file(self, rel_path: str) -> None:
                rel = rel_path.lstrip("/") or "index.html"
                if rel == "":
                    rel = "index.html"
                path = (DASHBOARD_DIR / rel).resolve()
                try:
                    path.relative_to(DASHBOARD_DIR.resolve())
                except ValueError:
                    self.send_error(403)
                    return
                if not path.exists() or not path.is_file():
                    self.send_error(404)
                    return
                body = path.read_bytes()
                content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                if path.suffix == ".js":
                    content_type = "application/javascript; charset=utf-8"
                elif path.suffix in (".html", ".css"):
                    content_type += "; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                path = parsed.path.rstrip("/") or "/"
                query = parse_qs(parsed.query)
                try:
                    if path in ("/health", "/capabilities"):
                        payload = bridge.capabilities()
                        payload["status"] = "ok"
                        self.send_json(200, payload)
                    elif path == "/api/status":
                        self.send_json(200, bridge.dashboard_status())
                    elif path == "/api/jobs":
                        limit = int((query.get("limit") or ["50"])[0])
                        self.send_json(200, [bridge.summarize_job(j) for j in bridge.read_jobs()[:limit]])
                    elif path.startswith("/api/jobs/"):
                        job_id = path.rsplit("/", 1)[-1]
                        job = next((j for j in bridge.read_jobs() if str(j.get("job_id")) == job_id), None)
                        self.send_json(200 if job else 404, job or {"error": "job not found"})
                    elif path == "/api/logs":
                        limit = int((query.get("limit") or ["120"])[0])
                        self.send_json(200, bridge.read_recent_logs(limit=limit))
                    elif path == "/api/config":
                        self.send_json(200, bridge.editable_config())
                    elif path == "/":
                        self.send_dashboard_file("index.html")
                    else:
                        self.send_dashboard_file(parsed.path)
                except Exception as exc:
                    bridge.log("error", "dashboard GET failed", path=path, error=str(exc))
                    self.send_json(500, {"error": str(exc)})

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                path = parsed.path.rstrip("/") or "/"
                try:
                    length = int(self.headers.get("Content-Length") or "0")
                    raw = self.rfile.read(length).decode("utf-8", errors="replace") if length else "{}"
                    payload = json.loads(raw)
                    if path == "/api/config":
                        updates = payload.get("updates", payload)
                        result = bridge.update_config(updates, self.client_address[0])
                        self.send_json(200, result)
                        return
                    self.send_json(404, {"error": "not found"})
                except Exception as exc:
                    bridge.log("error", "dashboard POST failed", path=path, error=str(exc))
                    status = 403 if isinstance(exc, PermissionError) else 400
                    self.send_json(status, {"error": str(exc)})

            def log_message(self, fmt: str, *args: Any) -> None:
                bridge.log("debug", "dashboard server", request_log=fmt % args)

        return Handler

    def start_health_server(self, force: bool = False, host_override: str | None = None, port_override: int | None = None) -> tuple[str, int] | None:
        cfg = self.config.get("health_server", {})
        if not force and not cfg.get("enabled", False):
            return None
        host = host_override or str(cfg.get("host") or "127.0.0.1")
        port = int(port_override or cfg.get("port") or 8765)
        server = http.server.ThreadingHTTPServer((host, port), self.health_handler())
        self.log("info", "dashboard server starting", host=host, port=port)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return host, port

    def run(self, private_only: bool = False, no_private_poller: bool = False) -> None:
        self.log("info", "bridge starting", dry_run=self.dry_run)
        if self.dry_run:
            print(f"Dry run OK. Config loaded for machine_id={self.machine_id}.")
            return
        self.start_health_server()
        if self.config.get("private", {}).get("enabled") and not no_private_poller:
            threading.Thread(target=self.private_poller, daemon=True).start()
        if private_only:
            while not self.stop_event.is_set():
                time.sleep(1)
            return
        self.event_loop()


def install_signal_handlers(bridge: Bridge) -> None:
    def stop(signum: int, frame: Any) -> None:
        bridge.log("info", "received stop signal", signum=signum)
        bridge.stop_event.set()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--private-poller-only", action="store_true")
    parser.add_argument("--no-private-poller", action="store_true")
    parser.add_argument("--run-job")
    parser.add_argument("--dashboard-only", action="store_true")
    parser.add_argument("--dashboard-host")
    parser.add_argument("--dashboard-port", type=int)
    args = parser.parse_args()
    pid_name = None
    if not args.dry_run and not args.run_job:
        pid_name = "dashboard.pid" if args.dashboard_only else "bridge.pid"
    bridge = Bridge(Path(args.config), dry_run=args.dry_run, pid_name=pid_name)
    install_signal_handlers(bridge)
    if args.run_job:
        return bridge.run_codex_job(Path(args.run_job))
    if args.dashboard_only:
        server = bridge.start_health_server(force=True, host_override=args.dashboard_host, port_override=args.dashboard_port)
        host, port = server or ("127.0.0.1", 8765)
        print(f"Feishu Codex Bridge dashboard: http://{host}:{port}/", flush=True)
        while not bridge.stop_event.is_set():
            time.sleep(1)
        return 0
    bridge.run(private_only=args.private_poller_only, no_private_poller=args.no_private_poller)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
