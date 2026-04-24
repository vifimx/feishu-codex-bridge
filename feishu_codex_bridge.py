#!/usr/bin/env python3
"""Local Feishu/Lark to Codex bridge.

The bridge intentionally stays local-first:
- Lark transport is the official lark-cli.
- Codex execution is the local codex CLI.
- State is plain JSON/JSONL under the configured state_dir.
"""

from __future__ import annotations

import argparse
import base64
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
import tomllib
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from urllib import request as urlrequest


ROOT = Path(__file__).resolve().parent
DASHBOARD_DIR = ROOT / "dashboard"
ASSETS_DIR = ROOT / "assets"
START_MENU_ICON = ASSETS_DIR / "feishu-codex-bridge.ico"
DEFAULT_CODEX_HOME = Path(os.path.expandvars(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))).expanduser()
DEFAULT_CONFIG = ROOT / "bridge.config.json"
STARTUP_TASKS = {
    "dashboard": "FeishuCodexBridgeDashboard",
    "connection": "FeishuCodexBridgeConnection",
}
WINDOWS_INTEGRATION_ACTIONS = {
    "status",
    "install-start-menu",
    "remove-start-menu",
    "enable-dashboard-startup",
    "disable-dashboard-startup",
    "enable-connection-startup",
    "disable-connection-startup",
}

CONFIG_WRITE_ALLOWLIST = {
    "codex.home_dir",
    "commands.available",
    "skills.available",
    "models.available",
    "models.default",
    "models.default.model",
    "models.default.reasoning_effort",
    "models.default.service_tier",
    "models.fast",
    "models.fast.model",
    "models.fast.reasoning_effort",
    "models.fast.service_tier",
    "sessions.enabled",
    "sessions.mode",
    "sessions.private_scope",
    "sessions.group_scope",
    "sessions.continue_after_completion",
    "sessions.queue_while_running",
    "sessions.reply_guidance_enabled",
    "sessions.topic_reply_in_thread",
    "private.default_workspace",
    "private.codex_sandbox",
    "private.codex_timeout_sec",
    "private.codex_model",
    "private.final_output_idle_grace_sec",
    "private.polling_fallback_enabled",
    "private.poll_interval_sec",
    "private.treat_all_text_as_codex",
    "public.allow_codex",
    "public.treat_all_text_as_codex",
    "jobs.max_concurrent",
    "jobs.history_limit",
    "jobs.auto_cleanup_enabled",
    "jobs.cleanup_delete_artifacts",
    "reply.max_chars",
    "reply.upload_full_output_file",
    "reply.edit_status_message",
    "reply.show_details_by_default",
    "reply.show_progress_by_default",
    "reply.progress_max_lines",
    "reply.status_update_interval_sec",
    "multimodal.download_incoming",
    "multimodal.download_timeout_sec",
    "routing.accept_any_target",
    "routing.dispatch_to_peers",
    "routing.prefer_local_when_capable",
    "health_server.enabled",
    "health_server.host",
    "health_server.port",
    "dashboard.allow_config_write",
    "dashboard.allow_process_control",
    "dashboard.allow_shell_integration",
    "dashboard.auto_refresh_sec",
    "peers.enabled",
    "peers.nodes",
    "access.default_policy",
    "access.identities",
    "access.user_groups",
    "access.groups",
    "access.enable_preset_intent_matching",
    "access.resolve_contacts_enabled",
    "access.contact_cache_ttl_sec",
    "preset_tasks",
    "workspaces",
    "event_types",
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


def strip_ansi(value: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", value or "")


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
        self.pid_name = pid_name
        self.codex_home = self.resolve_codex_home()
        self.machine_id = str(self.config.get("machine_id") or os.environ.get("COMPUTERNAME") or "local-codex")
        self.log_dir = Path(self.config["log_dir"]).expanduser()
        self.state_dir = Path(self.config["state_dir"]).expanduser()
        self.jobs_dir = self.state_dir / "jobs"
        self.artifacts_dir = self.state_dir / "artifacts"
        self.conversations_path = self.state_dir / "conversations.json"
        self.contact_cache_path = self.state_dir / "contact-cache.json"
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

    def resolve_codex_home(self) -> Path:
        cfg = self.config.get("codex", {}) if isinstance(self.config.get("codex"), dict) else {}
        configured = str(cfg.get("home_dir") or cfg.get("config_dir") or "").strip()
        if not configured:
            return DEFAULT_CODEX_HOME.expanduser()
        return Path(os.path.expandvars(configured)).expanduser()

    def write_pid(self, file_name: str = "bridge.pid") -> None:
        (self.state_dir / file_name).write_text(str(os.getpid()), encoding="ascii")

    @staticmethod
    def parse_pid(value: str | None) -> int | None:
        if not value:
            return None
        try:
            pid = int(value.strip())
        except ValueError:
            return None
        return pid if pid > 0 else None

    @staticmethod
    def pid_is_running(pid: int | None) -> bool:
        if not pid:
            return False
        if pid == os.getpid():
            return True
        if os.name == "nt":
            try:
                import ctypes

                process_query_limited_information = 0x1000
                still_active = 259
                handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, int(pid))
                if handle:
                    exit_code = ctypes.c_ulong()
                    ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return bool(ok and exit_code.value == still_active)
                return False
            except Exception:
                return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def read_pid(self, file_name: str) -> int | None:
        path = self.state_dir / file_name
        if not path.exists():
            return None
        return self.parse_pid(path.read_text(encoding="ascii", errors="replace"))

    def process_snapshot(self, file_name: str) -> dict[str, Any]:
        path = self.state_dir / file_name
        raw = path.read_text(encoding="ascii", errors="replace").strip() if path.exists() else ""
        pid = self.parse_pid(raw)
        running = self.pid_is_running(pid)
        if file_name == "bridge.pid" and not running:
            discovered = self.find_bridge_process("--no-dashboard-server")
            if discovered:
                pid = discovered
                running = True
                try:
                    path.write_text(str(pid), encoding="ascii")
                except Exception:
                    pass
        return {
            "pid": pid,
            "running": running,
            "pid_file": str(path),
            "stale": bool(raw and not running),
        }

    def runtime_mode(self) -> str:
        if self.pid_name == "dashboard.pid":
            return "dashboard-only"
        if self.pid_name == "bridge.pid":
            return "bridge-hosted"
        pid = os.getpid()
        if self.read_pid("dashboard.pid") == pid:
            return "dashboard-only"
        if self.read_pid("bridge.pid") == pid:
            return "bridge-hosted"
        return "unknown"

    def find_bridge_process(self, marker: str) -> int | None:
        if os.name != "nt":
            return None
        powershell = self.powershell_exe()
        script = (
            "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | "
            f"Where-Object {{ $_.CommandLine -like '*feishu_codex_bridge.py*' -and $_.CommandLine -like '*{marker}*' }} | "
            "Select-Object -ExpandProperty ProcessId -First 1"
        )
        try:
            result = subprocess.run(
                [powershell, "-NoProfile", "-Command", script],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=3,
                check=False,
            )
            return self.parse_pid((result.stdout or "").strip().splitlines()[0] if result.stdout.strip() else "")
        except Exception:
            return None

    def process_control_enabled(self, client_address: str) -> bool:
        if not self.is_loopback(client_address):
            return False
        dashboard_cfg = self.config.get("dashboard", {})
        return bool(dashboard_cfg.get("allow_process_control", True))

    def require_process_control(self, client_address: str) -> None:
        if not self.is_loopback(client_address):
            raise PermissionError("Process control is only accepted from loopback clients.")
        if not bool(self.config.get("dashboard", {}).get("allow_process_control", True)):
            raise PermissionError("Process control is disabled. Set dashboard.allow_process_control=true in bridge.config.json.")

    def shell_integration_enabled(self) -> bool:
        return bool(self.config.get("dashboard", {}).get("allow_shell_integration", True))

    def require_shell_integration(self, client_address: str) -> None:
        if not self.is_loopback(client_address):
            raise PermissionError("Shell integration changes are only accepted from loopback clients.")
        if not self.shell_integration_enabled():
            raise PermissionError(
                "Shell integration changes are disabled. Set dashboard.allow_shell_integration=true in bridge.config.json."
            )

    def start_bridge_connection(self, client_address: str) -> dict[str, Any]:
        self.require_process_control(client_address)
        bridge_state = self.process_snapshot("bridge.pid")
        if bridge_state["running"]:
            return {
                "status": "already_running",
                "pid": bridge_state["pid"],
                "message": "Bridge connection is already running.",
            }
        if bridge_state["stale"]:
            try:
                (self.state_dir / "bridge.pid").unlink()
            except FileNotFoundError:
                pass

        stdout_path = self.state_dir / "bridge.stdout.log"
        stderr_path = self.state_dir / "bridge.stderr.log"
        args = [
            sys.executable,
            "-u",
            str(ROOT / "feishu_codex_bridge.py"),
            "--config",
            str(self.config_path.resolve()),
            "--no-dashboard-server",
        ]
        popen_kwargs: dict[str, Any] = {
            "cwd": str(ROOT),
            "env": self.env(),
            "stdin": subprocess.DEVNULL,
        }
        if os.name == "nt":
            creation_flags = 0
            creation_flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            creation_flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
            popen_kwargs["creationflags"] = creation_flags

        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            proc = subprocess.Popen(args, stdout=stdout, stderr=stderr, **popen_kwargs)
        (self.state_dir / "bridge.pid").write_text(str(proc.pid), encoding="ascii")
        self.log("info", "dashboard started bridge connection", pid=proc.pid, stdout=str(stdout_path), stderr=str(stderr_path))
        return {
            "status": "started",
            "pid": proc.pid,
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
        }

    def stop_bridge_connection(self, client_address: str) -> dict[str, Any]:
        self.require_process_control(client_address)
        bridge_state = self.process_snapshot("bridge.pid")
        pid = bridge_state["pid"]
        if not pid:
            return {"status": "not_running", "message": "No bridge connection pid file was found."}
        if pid == os.getpid():
            raise RuntimeError(
                "This dashboard is hosted by the bridge process. "
                "Start the dashboard-only launcher to stop the Feishu connection while keeping the GUI open."
            )
        if bridge_state["running"]:
            self.terminate_process_tree(pid)
        try:
            (self.state_dir / "bridge.pid").unlink()
        except FileNotFoundError:
            pass
        self.log("info", "dashboard stopped bridge connection", pid=pid)
        return {"status": "stopped", "pid": pid}

    def terminate_process_tree(self, pid: int) -> None:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return
        deadline = time.time() + 10
        while time.time() < deadline and self.pid_is_running(pid):
            time.sleep(0.2)
        if self.pid_is_running(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

    def powershell_exe(self) -> str:
        return shutil.which("powershell") or shutil.which("pwsh") or "powershell.exe"

    @staticmethod
    def ps_quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def windows_integration_supported(self) -> bool:
        return os.name == "nt"

    def start_menu_dir(self) -> Path:
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"

    def legacy_start_menu_dir(self) -> Path:
        return self.start_menu_dir() / "Feishu Codex Bridge"

    def start_menu_shortcuts(self) -> dict[str, Path]:
        folder = self.start_menu_dir()
        return {
            "dashboard": folder / "Feishu Codex Bridge Dashboard.lnk",
            "stop": folder / "Feishu Codex Bridge Stop.lnk",
        }

    def legacy_start_menu_shortcuts(self) -> dict[str, Path]:
        folder = self.legacy_start_menu_dir()
        return {
            "dashboard": folder / "Feishu Codex Bridge Dashboard.lnk",
            "stop": folder / "Stop Feishu Codex Bridge.lnk",
        }

    def start_menu_manifest_path(self) -> Path:
        return self.state_dir / "start-menu-shortcuts.json"

    def start_menu_icon_path(self) -> Path | None:
        return START_MENU_ICON if START_MENU_ICON.exists() else None

    def start_menu_status(self) -> dict[str, Any]:
        shortcuts = self.start_menu_shortcuts()
        icon_path = self.start_menu_icon_path()
        items = {key: {"path": str(path), "exists": path.exists()} for key, path in shortcuts.items()}
        existing = [key for key, value in items.items() if value["exists"]]
        missing = [key for key, value in items.items() if not value["exists"]]
        manifest_path = self.start_menu_manifest_path()
        manifest_exists = manifest_path.exists()
        installed = bool(items) and not missing
        needs_repair = bool(manifest_exists and not installed)
        return {
            "installed": installed,
            "partial": bool(existing and missing),
            "needs_repair": needs_repair,
            "manifest_exists": manifest_exists,
            "folder": str(self.start_menu_dir()),
            "shortcuts": {key: str(path) for key, path in shortcuts.items()},
            "icon": str(icon_path) if icon_path else "",
            "icon_exists": bool(icon_path),
            "items": items,
            "missing": missing,
            "existing": existing,
            "status": "installed" if installed else "partial" if existing else "needs_repair" if needs_repair else "missing",
        }

    def write_start_menu_manifest(self, shortcuts: dict[str, Path]) -> None:
        icon_path = self.start_menu_icon_path()
        payload = {
            "installed_at": utcnow(),
            "folder": str(self.start_menu_dir()),
            "shortcuts": {key: str(path) for key, path in shortcuts.items()},
            "icon": str(icon_path) if icon_path else "",
        }
        self.start_menu_manifest_path().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def cleanup_legacy_start_menu(self) -> None:
        legacy_shortcuts = self.legacy_start_menu_shortcuts()
        for path in legacy_shortcuts.values():
            if path.exists():
                path.unlink()
        legacy_folder = self.legacy_start_menu_dir()
        try:
            if legacy_folder.exists() and not any(legacy_folder.iterdir()):
                legacy_folder.rmdir()
        except OSError:
            pass

    def startup_task_command(self, kind: str) -> str:
        powershell = self.powershell_exe()
        if kind == "dashboard":
            parts = [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-WindowStyle",
                "Hidden",
                "-File",
                str(ROOT / "Open-FeishuCodexBridgeDashboard.ps1"),
                "-NoBrowser",
            ]
        elif kind == "connection":
            parts = [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-WindowStyle",
                "Hidden",
                "-File",
                str(ROOT / "Start-FeishuCodexBridge.ps1"),
                "-NoDashboardServer",
            ]
        else:
            raise ValueError(f"Unknown startup task kind: {kind}")
        return subprocess.list2cmdline(parts)

    def run_command(self, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=str(ROOT),
            env=self.env(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )

    def task_installed(self, task_name: str) -> bool:
        if not self.windows_integration_supported():
            return False
        result = self.run_command(["schtasks", "/Query", "/TN", task_name], timeout=10)
        return result.returncode == 0

    def create_startup_task(self, kind: str) -> dict[str, Any]:
        if not self.windows_integration_supported():
            raise RuntimeError("Windows startup integration is only supported on Windows.")
        task_name = STARTUP_TASKS[kind]
        command = self.startup_task_command(kind)
        result = self.run_command(
            ["schtasks", "/Create", "/TN", task_name, "/SC", "ONLOGON", "/TR", command, "/F"],
            timeout=20,
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or f"schtasks exited {result.returncode}").strip())
        self.log("info", "installed startup task", kind=kind, task_name=task_name)
        return {"installed": True, "task_name": task_name, "message": result.stdout.strip()}

    def delete_startup_task(self, kind: str) -> dict[str, Any]:
        if not self.windows_integration_supported():
            raise RuntimeError("Windows startup integration is only supported on Windows.")
        task_name = STARTUP_TASKS[kind]
        if not self.task_installed(task_name):
            return {"installed": False, "task_name": task_name, "message": "Task was not installed."}
        result = self.run_command(["schtasks", "/Delete", "/TN", task_name, "/F"], timeout=20)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or f"schtasks exited {result.returncode}").strip())
        self.log("info", "removed startup task", kind=kind, task_name=task_name)
        return {"installed": False, "task_name": task_name, "message": result.stdout.strip()}

    def create_shortcut(self, shortcut_path: Path, target_path: Path | str, arguments: str, description: str) -> None:
        if not self.windows_integration_supported():
            raise RuntimeError("Start Menu shortcut integration is only supported on Windows.")
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        target = str(target_path)
        icon_path = self.start_menu_icon_path()
        icon = str(icon_path) if icon_path else f"{target},0"
        script = "\n".join(
            [
                "$ErrorActionPreference = 'Stop'",
                f"$shortcutPath = {self.ps_quote(str(shortcut_path))}",
                f"$targetPath = {self.ps_quote(target)}",
                f"$arguments = {self.ps_quote(arguments)}",
                f"$workingDirectory = {self.ps_quote(str(ROOT))}",
                f"$description = {self.ps_quote(description)}",
                f"$iconLocation = {self.ps_quote(icon)}",
                "[System.IO.Directory]::CreateDirectory((Split-Path -Parent $shortcutPath)) | Out-Null",
                "$wsh = New-Object -ComObject WScript.Shell",
                "$link = $wsh.CreateShortcut($shortcutPath)",
                "$link.TargetPath = $targetPath",
                "$link.Arguments = $arguments",
                "$link.WorkingDirectory = $workingDirectory",
                "$link.Description = $description",
                "$link.IconLocation = $iconLocation",
                "$link.WindowStyle = 7",
                "$link.Save()",
            ]
        )
        encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
        powershell = self.powershell_exe()
        result = self.run_command([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded], timeout=20)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or f"PowerShell exited {result.returncode}").strip())

    def install_start_menu(self) -> dict[str, Any]:
        if not self.windows_integration_supported():
            raise RuntimeError("Start Menu integration is only supported on Windows.")
        self.cleanup_legacy_start_menu()
        shortcuts = self.start_menu_shortcuts()
        self.create_shortcut(
            shortcuts["dashboard"],
            ROOT / "Open-FeishuCodexBridgeDashboard.cmd",
            "",
            "Open the local Feishu Codex Bridge dashboard.",
        )
        self.create_shortcut(
            shortcuts["stop"],
            ROOT / "Stop-FeishuCodexBridge.cmd",
            "",
            "Stop Feishu Codex Bridge dashboard, connection, and jobs.",
        )
        deadline = time.time() + 3
        status = self.start_menu_status()
        while time.time() < deadline and not status["installed"]:
            time.sleep(0.2)
            status = self.start_menu_status()
        if not status["installed"]:
            missing = ", ".join(status["missing"])
            raise RuntimeError(f"Start Menu shortcuts were created incompletely. Missing: {missing}")
        self.write_start_menu_manifest(shortcuts)
        self.log("info", "installed Start Menu shortcuts", folder=str(self.start_menu_dir()))
        return {
            "installed": True,
            "folder": str(self.start_menu_dir()),
            "shortcuts": {key: str(path) for key, path in shortcuts.items()},
            "status": status,
        }

    def remove_start_menu(self) -> dict[str, Any]:
        shortcuts = self.start_menu_shortcuts()
        legacy_shortcuts = self.legacy_start_menu_shortcuts()
        removed = []
        for path in list(shortcuts.values()) + list(legacy_shortcuts.values()):
            if path.exists():
                path.unlink()
                removed.append(str(path))
        folder = self.start_menu_dir()
        legacy_folder = self.legacy_start_menu_dir()
        try:
            if legacy_folder.exists() and not any(legacy_folder.iterdir()):
                legacy_folder.rmdir()
        except OSError:
            pass
        manifest_path = self.start_menu_manifest_path()
        if manifest_path.exists():
            manifest_path.unlink()
        self.log("info", "removed Start Menu shortcuts", removed=removed)
        return {"installed": False, "folder": str(folder), "removed": removed}

    def windows_integration_status(self) -> dict[str, Any]:
        supported = self.windows_integration_supported()
        startup = {}
        for kind, task_name in STARTUP_TASKS.items():
            startup[kind] = {
                "task_name": task_name,
                "installed": self.task_installed(task_name) if supported else False,
            }
        return {
            "supported": supported,
            "control_enabled": self.shell_integration_enabled(),
            "start_menu": self.start_menu_status() if supported else {"installed": False, "partial": False, "status": "unsupported"},
            "startup": startup,
        }

    def apply_windows_integration_action(self, action: str, client_address: str) -> dict[str, Any]:
        if action not in WINDOWS_INTEGRATION_ACTIONS:
            raise ValueError(f"Unknown Windows integration action: {action}")
        if action == "status":
            return self.windows_integration_status()
        self.require_shell_integration(client_address)
        if action == "install-start-menu":
            result = self.install_start_menu()
        elif action == "remove-start-menu":
            result = self.remove_start_menu()
        elif action == "enable-dashboard-startup":
            result = self.create_startup_task("dashboard")
        elif action == "disable-dashboard-startup":
            result = self.delete_startup_task("dashboard")
        elif action == "enable-connection-startup":
            result = self.create_startup_task("connection")
        elif action == "disable-connection-startup":
            result = self.delete_startup_task("connection")
        else:
            raise ValueError(f"Unknown Windows integration action: {action}")
        return {"action": action, "result": result, "status": self.windows_integration_status()}

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
        env["CODEX_HOME"] = str(self.codex_home)
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

    @staticmethod
    def parse_lark_message_id(output: str) -> str:
        try:
            parsed = json.loads(output)
            data = parsed.get("data", {}) if isinstance(parsed, dict) else {}
            return str(data.get("message_id") or "")
        except Exception:
            match = re.search(r'"message_id"\s*:\s*"([^"]+)"', output or "")
            return match.group(1) if match else ""

    def reply_text(
        self,
        message_id: str,
        text: str,
        idempotency_key: str | None = None,
        reply_in_thread: bool = False,
    ) -> str:
        body = self.limit_reply(text)
        if self.dry_run:
            self.log("info", "dry-run reply", message_id=message_id, text=body, reply_in_thread=reply_in_thread)
            return ""
        args = ["im", "+messages-reply", "--as", "bot", "--message-id", message_id, "--text", body]
        if reply_in_thread:
            args.append("--reply-in-thread")
        if idempotency_key:
            args += ["--idempotency-key", idempotency_key[:64]]
        try:
            output = self.run_lark(args, timeout=60)
        except Exception as exc:
            if not reply_in_thread:
                raise
            self.log("warn", "thread reply failed; retrying as normal reply", message_id=message_id, error=str(exc))
            fallback_args = [item for item in args if item != "--reply-in-thread"]
            output = self.run_lark(fallback_args, timeout=60)
        return self.parse_lark_message_id(output)

    def send_text(self, chat_id: str, text: str, idempotency_key: str | None = None) -> str:
        body = self.limit_reply(text)
        if self.dry_run:
            self.log("info", "dry-run send", chat_id=chat_id, text=body)
            return ""
        args = ["im", "+messages-send", "--as", "bot", "--chat-id", chat_id, "--text", body]
        if idempotency_key:
            args += ["--idempotency-key", idempotency_key[:64]]
        output = self.run_lark(args, timeout=60)
        return self.parse_lark_message_id(output)

    @staticmethod
    def status_card(title: str, text: str) -> str:
        return json.dumps(
            {
                "config": {"wide_screen_mode": True},
                "header": {"title": {"tag": "plain_text", "content": title[:80] or "消息处理"}},
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "plain_text", "content": (text or "(no output)")[:8000]},
                    }
                ],
            },
            ensure_ascii=False,
        )

    def send_card_response(
        self,
        chat_id: str,
        message_id: str | None,
        title: str,
        text: str,
        prefer_reply: bool,
        idempotency_key: str | None = None,
        reply_in_thread: bool = False,
    ) -> str:
        body = self.limit_reply(text)
        card = self.status_card(title, body)
        if self.dry_run:
            self.log(
                "info",
                "dry-run card response",
                chat_id=chat_id,
                message_id=message_id,
                title=title,
                text=body,
                reply_in_thread=reply_in_thread,
            )
            return ""
        if prefer_reply and message_id:
            args = ["im", "+messages-reply", "--as", "bot", "--message-id", message_id, "--msg-type", "interactive", "--content", card]
            if reply_in_thread:
                args.append("--reply-in-thread")
        else:
            args = ["im", "+messages-send", "--as", "bot", "--chat-id", chat_id, "--msg-type", "interactive", "--content", card]
        if idempotency_key:
            args += ["--idempotency-key", idempotency_key[:64]]
        try:
            output = self.run_lark(args, timeout=60)
        except Exception as exc:
            if not (prefer_reply and message_id and reply_in_thread):
                raise
            self.log("warn", "thread card reply failed; retrying as normal reply", message_id=message_id, error=str(exc))
            fallback_args = [item for item in args if item != "--reply-in-thread"]
            output = self.run_lark(fallback_args, timeout=60)
        return self.parse_lark_message_id(output)

    def update_text_message(self, message_id: str, text: str) -> bool:
        if not message_id:
            return False
        body = self.limit_reply(text)
        if self.dry_run:
            self.log("info", "dry-run update message", message_id=message_id, text=body)
            return True
        data = {"msg_type": "text", "content": json.dumps({"text": body}, ensure_ascii=False)}
        try:
            self.run_lark(
                ["api", "PATCH", f"/open-apis/im/v1/messages/{message_id}", "--as", "bot", "--data", json.dumps(data, ensure_ascii=False)],
                timeout=60,
            )
            return True
        except Exception as exc:
            self.log("warn", "message update failed", message_id=message_id, error=str(exc))
            return False

    def update_card_message(self, message_id: str, title: str, text: str) -> bool:
        if not message_id:
            return False
        body = self.limit_reply(text)
        if self.dry_run:
            self.log("info", "dry-run update card", message_id=message_id, title=title, text=body)
            return True
        data = {"content": self.status_card(title, body)}
        try:
            self.run_lark(
                ["api", "PATCH", f"/open-apis/im/v1/messages/{message_id}", "--as", "bot", "--data", json.dumps(data, ensure_ascii=False)],
                timeout=60,
            )
            return True
        except Exception as exc:
            self.log("warn", "card update failed", message_id=message_id, error=str(exc))
            return False

    def send_file(
        self,
        chat_id: str,
        message_id: str | None,
        path: Path,
        prefer_reply: bool,
        idempotency_key: str,
        reply_in_thread: bool = False,
    ) -> None:
        if self.dry_run:
            self.log("info", "dry-run send file", chat_id=chat_id, message_id=message_id, path=str(path), reply_in_thread=reply_in_thread)
            return
        if prefer_reply and message_id:
            args = ["im", "+messages-reply", "--as", "bot", "--message-id", message_id, "--file", str(path)]
            if reply_in_thread:
                args.append("--reply-in-thread")
        else:
            args = ["im", "+messages-send", "--as", "bot", "--chat-id", chat_id, "--file", str(path)]
        args += ["--idempotency-key", idempotency_key[:64]]
        try:
            self.run_lark(args, timeout=180)
        except Exception as exc:
            if not (prefer_reply and message_id and reply_in_thread):
                raise
            self.log("warn", "thread file reply failed; retrying as normal reply", message_id=message_id, error=str(exc))
            fallback_args = [item for item in args if item != "--reply-in-thread"]
            self.run_lark(fallback_args, timeout=180)

    def send_response(
        self,
        chat_id: str,
        message_id: str | None,
        text: str,
        prefer_reply: bool,
        idempotency_key: str | None = None,
        reply_in_thread: bool = False,
    ) -> str:
        if prefer_reply and message_id:
            return self.reply_text(message_id, text, idempotency_key=idempotency_key, reply_in_thread=reply_in_thread)
        return self.send_text(chat_id, text, idempotency_key=idempotency_key)

    def send_job_start_response(
        self,
        msg: dict[str, Any],
        result: dict[str, Any],
        prefer_reply: bool,
        idempotency_key: str,
    ) -> str:
        message = str(result.get("message") or "")
        reply_in_thread = bool(result.get("reply_in_thread"))
        if result.get("ok") and self.config.get("reply", {}).get("edit_status_message", False):
            title = str(result.get("title") or "已收到消息")
            return self.send_card_response(
                msg["chat_id"],
                msg["message_id"],
                title,
                message,
                prefer_reply,
                idempotency_key=idempotency_key,
                reply_in_thread=reply_in_thread,
            )
        return self.send_response(
            msg["chat_id"],
            msg["message_id"],
            message,
            prefer_reply,
            idempotency_key=idempotency_key,
            reply_in_thread=reply_in_thread,
        )

    def fetch_reply_to(self, message_id: str) -> str:
        if not message_id or self.dry_run:
            return ""
        try:
            output = self.run_lark(["im", "+messages-mget", "--as", "bot", "--message-ids", message_id, "--format", "json"], timeout=30)
            parsed = json.loads(output)
            messages = parsed.get("data", {}).get("messages", []) if isinstance(parsed, dict) else []
            if messages and isinstance(messages[0], dict):
                return str(messages[0].get("reply_to") or "")
        except Exception as exc:
            self.log("debug", "failed to fetch reply_to", message_id=message_id, error=str(exc))
        return ""

    def enrich_reply_to(self, msg: dict[str, Any]) -> dict[str, Any]:
        if msg.get("reply_to") or not self.config.get("sessions", {}).get("reply_guidance_enabled", True):
            return msg
        reply_to = self.fetch_reply_to(str(msg.get("message_id") or ""))
        if reply_to:
            msg["reply_to"] = reply_to
            self.log("debug", "enriched reply_to", message_id=msg.get("message_id"), reply_to=reply_to)
        return msg

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
        sender_obj = raw.get("sender") or raw.get("message", {}).get("sender") or {}
        if not isinstance(sender_obj, dict):
            sender_obj = {}
        sender_id = self.extract_open_id(str(sender))
        sender_name = str(
            sender_obj.get("name")
            or sender_obj.get("display_name")
            or sender_obj.get("en_name")
            or sender_obj.get("localized_name")
            or sender_obj.get("nickname")
            or ""
        )
        parent_id = str(raw.get("parent_id") or raw.get("message", {}).get("parent_id") or "")
        root_id = str(raw.get("root_id") or raw.get("message", {}).get("root_id") or "")
        thread_id = str(raw.get("thread_id") or raw.get("message", {}).get("thread_id") or "")
        reply_to = str(raw.get("reply_to") or raw.get("message", {}).get("reply_to") or parent_id or root_id or thread_id or "")
        return {
            "message_id": message_id,
            "chat_id": chat_id,
            "chat_type": chat_type,
            "sender_id": sender_id or str(sender),
            "sender_open_id": sender_id or str(sender_obj.get("open_id") or ""),
            "sender_user_id": str(sender_obj.get("user_id") or ""),
            "sender_union_id": str(sender_obj.get("union_id") or ""),
            "sender_email": str(sender_obj.get("email") or ""),
            "sender_name": sender_name,
            "sender_mobile": str(sender_obj.get("mobile") or sender_obj.get("phone") or ""),
            "msg_type": msg_type,
            "content": content,
            "reply_to": str(reply_to),
            "parent_id": parent_id,
            "root_id": root_id,
            "thread_id": thread_id,
            "mentions": raw.get("mentions") or raw.get("message", {}).get("mentions") or [],
            "text": self.extract_text(msg_type, content).strip(),
            "raw": raw,
        }

    def normalize_command_text(self, text: str) -> str:
        text = (text or "").strip()
        return re.sub(r"^\s*@\S+\s+", "", text).strip()

    @staticmethod
    def contains(items: Any, value: str) -> bool:
        return any(str(item) == value for item in (items or []))

    @staticmethod
    def extract_open_id(value: str) -> str:
        text = str(value or "")
        match = re.search(r"open_id=([^;\s}]+)", text)
        if match:
            return match.group(1)
        return text

    @staticmethod
    def list_allows(items: Any, value: str) -> bool:
        values = [str(item).strip() for item in (items or []) if str(item).strip()]
        return "*" in values or str(value) in values

    @staticmethod
    def merge_unique(*lists: Any) -> list[str]:
        result: list[str] = []
        for items in lists:
            for item in items or []:
                value = str(item).strip()
                if value and value not in result:
                    result.append(value)
        return result

    def access_config(self) -> dict[str, Any]:
        return self.config.get("access", {}) or {}

    def read_contact_cache(self) -> dict[str, Any]:
        if not self.contact_cache_path.exists():
            return {}
        try:
            data = json.loads(self.contact_cache_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def write_contact_cache(self, data: dict[str, Any]) -> None:
        ensure_dir(self.contact_cache_path.parent)
        tmp = self.contact_cache_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.contact_cache_path)

    def contact_values_for_open_id(self, open_id: str) -> list[str]:
        if not open_id or not self.access_config().get("resolve_contacts_enabled", False):
            return []
        ttl = int(self.access_config().get("contact_cache_ttl_sec", 86400) or 86400)
        cache = self.read_contact_cache()
        cached = cache.get(open_id)
        now = time.time()
        if isinstance(cached, dict) and now - float(cached.get("ts") or 0) < ttl:
            return [str(item) for item in cached.get("values", []) or [] if str(item).strip()]
        values: list[str] = []
        error = ""
        try:
            output = self.run_lark(
                ["contact", "+get-user", "--as", "bot", "--user-id", open_id, "--user-id-type", "open_id", "--format", "json"],
                timeout=30,
            )
            parsed = json.loads(output)
            values = self.extract_contact_values(parsed)
        except Exception as exc:
            error = str(exc)
            self.log("debug", "contact resolve failed", open_id=open_id, error=error)
        cache[open_id] = {"ts": now, "values": values, "error": error}
        self.write_contact_cache(cache)
        return values

    @staticmethod
    def extract_contact_values(data: Any) -> list[str]:
        keys = {
            "open_id",
            "user_id",
            "union_id",
            "email",
            "enterprise_email",
            "mobile",
            "mobile_visible",
            "name",
            "en_name",
            "nickname",
            "display_name",
            "localized_name",
            "employee_no",
        }
        values: list[str] = []

        def walk(value: Any, key: str = "") -> None:
            if isinstance(value, dict):
                for child_key, child_value in value.items():
                    walk(child_value, str(child_key))
            elif isinstance(value, list):
                for item in value:
                    walk(item, key)
            elif key in keys and value not in (None, ""):
                values.append(str(value))

        walk(data)
        return list(dict.fromkeys(item.strip() for item in values if item and item.strip()))

    def access_identities(self) -> dict[str, dict[str, Any]]:
        identities = self.access_config().get("identities", {}) or {}
        if isinstance(identities, dict):
            return {str(key): value for key, value in identities.items() if isinstance(value, dict)}
        if isinstance(identities, list):
            result = {}
            for index, item in enumerate(identities):
                if not isinstance(item, dict):
                    continue
                key = str(item.get("id") or item.get("key") or item.get("label") or f"user-{index + 1}")
                result[key] = item
            return result
        return {}

    def access_groups(self) -> dict[str, dict[str, Any]]:
        groups = self.access_config().get("groups", {}) or {}
        if isinstance(groups, dict):
            return {str(key): value for key, value in groups.items() if isinstance(value, dict)}
        if isinstance(groups, list):
            result = {}
            for index, item in enumerate(groups):
                if not isinstance(item, dict):
                    continue
                key = str(item.get("id") or item.get("key") or item.get("label") or f"group-{index + 1}")
                result[key] = item
            return result
        return {}

    def access_user_groups(self) -> dict[str, dict[str, Any]]:
        groups = self.access_config().get("user_groups", {}) or {}
        if isinstance(groups, dict):
            return {str(key): value for key, value in groups.items() if isinstance(value, dict)}
        if isinstance(groups, list):
            result = {}
            for index, item in enumerate(groups):
                if not isinstance(item, dict):
                    continue
                key = str(item.get("id") or item.get("key") or item.get("label") or f"user-group-{index + 1}")
                result[key] = item
            return result
        return {}

    def identity_values(self, identity: dict[str, Any]) -> list[str]:
        values: list[str] = []
        for key in ("open_id", "user_id", "union_id", "email", "mobile", "name", "user_name", "username"):
            if identity.get(key):
                values.append(str(identity[key]))
        for key in ("open_ids", "user_ids", "union_ids", "emails", "mobiles", "names", "user_names", "usernames", "aliases"):
            values.extend(str(item) for item in identity.get(key, []) or [])
        return [item for item in values if item]

    def sender_values(self, msg_or_sender: dict[str, Any] | str) -> list[str]:
        if isinstance(msg_or_sender, dict):
            values = [
                str(msg_or_sender.get("sender_id") or ""),
                str(msg_or_sender.get("sender_open_id") or ""),
                str(msg_or_sender.get("sender_user_id") or ""),
                str(msg_or_sender.get("sender_union_id") or ""),
                str(msg_or_sender.get("sender_email") or ""),
                str(msg_or_sender.get("sender_name") or ""),
                str(msg_or_sender.get("sender_mobile") or ""),
            ]
            values.extend(self.contact_values_for_open_id(str(msg_or_sender.get("sender_open_id") or msg_or_sender.get("sender_id") or "")))
        else:
            values = [str(msg_or_sender or "")]
        return [item for item in values if item and item != "-"]

    def sender_identity_key(self, msg_or_sender: dict[str, Any] | str) -> str:
        sender_values = set(self.sender_values(msg_or_sender))
        for key, identity in self.access_identities().items():
            if sender_values.intersection(self.identity_values(identity)):
                return key
        return ""

    def sender_identity(self, msg_or_sender: dict[str, Any] | str) -> dict[str, Any]:
        key = self.sender_identity_key(msg_or_sender)
        if key:
            identity = dict(self.access_identities()[key])
            identity["_key"] = key
            return identity
        return {}

    def group_for_chat(self, chat_id: str) -> tuple[str, dict[str, Any]]:
        for key, group in self.access_groups().items():
            if not group.get("enabled", True):
                continue
            if self.contains(group.get("chat_ids") or group.get("chat_id"), chat_id):
                return key, group
            if str(group.get("chat_id") or "") == chat_id:
                return key, group
        return "", {}

    def group_applies_to_sender(self, group: dict[str, Any], identity_key: str, msg_or_sender: dict[str, Any] | str) -> bool:
        members = [str(item) for item in group.get("members", []) or []]
        if not members or "*" in members or bool(group.get("apply_to_all", False)):
            return True
        if identity_key and identity_key in members:
            return True
        sender_values = set(self.sender_values(msg_or_sender))
        return bool(sender_values.intersection(members))

    def matching_user_groups(self, identity_key: str, msg_or_sender: dict[str, Any] | str) -> list[tuple[str, dict[str, Any]]]:
        matches: list[tuple[str, dict[str, Any]]] = []
        for key, group in self.access_user_groups().items():
            if not group.get("enabled", True):
                continue
            if self.group_applies_to_sender(group, identity_key, msg_or_sender):
                matches.append((key, group))
        return matches

    def policy_for(self, msg_or_sender: dict[str, Any] | str, chat_id: str = "") -> dict[str, Any]:
        access = self.access_config()
        default_policy = access.get("default_policy", {}) if isinstance(access.get("default_policy", {}), dict) else {}
        identity_key = self.sender_identity_key(msg_or_sender)
        identity = self.access_identities().get(identity_key, {}) if identity_key else {}
        user_group_matches = self.matching_user_groups(identity_key, msg_or_sender)
        group_key, group = self.group_for_chat(chat_id) if chat_id else ("", {})
        group_applies = bool(group) and self.group_applies_to_sender(group, identity_key, msg_or_sender)

        sources = [default_policy]
        if identity:
            sources.append(identity)
        sources.extend(item for _, item in user_group_matches)
        if group_applies:
            sources.append(group)

        unrestricted = any(bool(source.get("unrestricted")) for source in sources)
        allow_codex = unrestricted or any(bool(source.get("allow_codex")) for source in sources)
        commands = ["*"] if unrestricted else self.merge_unique(*(source.get("commands", []) for source in sources))
        tasks = ["*"] if unrestricted else self.merge_unique(*(source.get("tasks", source.get("task_ids", [])) for source in sources))
        skills = ["*"] if unrestricted else self.merge_unique(*(source.get("skills", []) for source in sources))
        models = ["*"] if unrestricted else self.merge_unique(*(source.get("models", []) for source in sources))
        show_details = bool(self.config.get("reply", {}).get("show_details_by_default", False)) or any(
            bool(source.get("show_details")) for source in sources
        )
        show_progress = bool(self.config.get("reply", {}).get("show_progress_by_default", False)) or any(
            bool(source.get("show_progress")) for source in sources
        )
        return {
            "identity_key": identity_key,
            "identity_label": identity.get("label") or identity.get("name") or identity_key,
            "user_group_keys": [key for key, _ in user_group_matches],
            "user_group_labels": [item.get("label") or item.get("name") or key for key, item in user_group_matches],
            "group_key": group_key if group_applies else "",
            "group_label": group.get("label") or group.get("name") or group_key if group_applies else "",
            "unrestricted": unrestricted,
            "allow_codex": allow_codex,
            "commands": commands,
            "tasks": tasks,
            "skills": skills,
            "models": models,
            "show_details": show_details,
            "show_progress": show_progress,
        }

    def sender_access_level(self, sender: dict[str, Any] | str) -> str:
        policy = self.policy_for(sender)
        if policy.get("unrestricted") or policy.get("allow_codex"):
            return "trusted"
        if policy.get("commands") or policy.get("tasks"):
            return "limited"
        return "none"

    def chat_route_allowed(self, chat_type: str, chat_id: str) -> bool:
        pub = self.config.get("public", {})
        priv = self.config.get("private", {})
        if chat_type == "p2p":
            return bool(priv.get("enabled") and self.contains(priv.get("allowed_chat_ids"), chat_id))
        if pub.get("enabled") and self.contains(pub.get("allowed_chat_ids"), chat_id):
            return True
        return bool(self.group_for_chat(chat_id)[1])

    def command_allowed_for_sender(self, sender: dict[str, Any] | str, name: str, chat_id: str = "") -> bool:
        policy = self.policy_for(sender, chat_id)
        return bool(policy.get("unrestricted")) or self.list_allows(policy.get("commands"), name)

    def preset_tasks(self) -> dict[str, Any]:
        tasks = self.config.get("preset_tasks", {}) or {}
        return tasks if isinstance(tasks, dict) else {}

    def task_allowed_for_sender(self, sender: dict[str, Any] | str, chat_id: str, task_id: str) -> bool:
        task = self.preset_tasks().get(task_id)
        if not isinstance(task, dict) or not task.get("enabled", True):
            return False
        task_chat_ids = task.get("allowed_chat_ids") or []
        if task_chat_ids and not self.contains(task_chat_ids, chat_id):
            return False
        task_sender_ids = task.get("allowed_sender_open_ids") or []
        if task_sender_ids and not any(self.contains(task_sender_ids, value) for value in self.sender_values(sender)):
            return False
        policy = self.policy_for(sender, chat_id)
        if bool(policy.get("unrestricted")) or self.list_allows(policy.get("tasks"), task_id):
            return self.skills_allowed_for_policy(policy, task.get("required_skills", []) or [])
        return False

    def skills_allowed_for_policy(self, policy: dict[str, Any], skills: list[Any]) -> bool:
        required = [str(item) for item in skills or [] if str(item).strip()]
        if not required or bool(policy.get("unrestricted")):
            return True
        allowed = policy.get("skills", [])
        return all(self.list_allows(allowed, skill) for skill in required)

    def model_allowed_for_policy(self, policy: dict[str, Any], model: str) -> bool:
        if not model or bool(policy.get("unrestricted")):
            return True
        return self.list_allows(policy.get("models"), model)

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

    def allowed_for_cmd(self, chat_type: str, chat_id: str, sender: dict[str, Any] | str) -> bool:
        policy = self.policy_for(sender, chat_id)
        return self.chat_route_allowed(chat_type, chat_id) and (
            bool(policy.get("unrestricted")) or bool(policy.get("commands")) or bool(policy.get("tasks"))
        )

    def allowed_for_codex(self, chat_type: str, chat_id: str, sender: dict[str, Any] | str) -> bool:
        policy = self.policy_for(sender, chat_id)
        if not policy.get("allow_codex"):
            return False
        pub = self.config.get("public", {})
        if chat_type == "p2p":
            return self.chat_route_allowed(chat_type, chat_id)
        group = self.group_for_chat(chat_id)[1]
        return bool((pub.get("allow_codex") or group.get("allow_codex")) and self.chat_route_allowed(chat_type, chat_id))

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

    def built_in_command(self, name: str, rest: str = "", msg: dict[str, Any] | None = None) -> str | None:
        key = name.lower()
        show_details = bool(self.policy_for(msg, msg.get("chat_id", "")).get("show_details")) if msg else False
        if key in ("help", "?"):
            return self.help_text()
        if key in ("status", "jobs"):
            return self.format_status(rest.strip() or None, show_details=show_details)
        if key in ("history", "recent"):
            return self.format_history()
        if key in ("capabilities", "caps"):
            if not show_details:
                caps = self.capabilities()
                task_ids = [str(task.get("id")) for task in caps.get("preset_tasks", []) if task.get("id")]
                return "\n".join(
                    [
                        f"可用工作区：{', '.join(caps.get('workspaces', [])) or '-'}",
                        f"可用命令：{', '.join(caps.get('commands', [])) or '-'}",
                        f"预设任务：{', '.join(task_ids) or '-'}",
                        f"活动任务：{caps.get('active_jobs', 0)}/{caps.get('max_concurrent_jobs', 1)}",
                    ]
                )
            return json.dumps(self.capabilities(), ensure_ascii=False, indent=2)
        if key in ("peers", "peer"):
            return self.format_peers()
        return None

    def help_text(self) -> str:
        return "\n".join(
            [
                "可用命令:",
                "/id",
                "/cmd help",
                "/cmd status [job_id]",
                "/cmd history",
                "/cmd capabilities",
                "/cmd peers",
                "/cmd sessions",
                "/cmd new-session",
                "/cmd doctor",
                "/cmd auth",
                "/cmd <preset_task> [input]",
                "/task <preset_task> [input]",
                "/ask [@node] [--new] [workspace=name] [model=id] [reasoning=low|medium|high|xhigh] [mode=fast] [skills=a,b] <prompt>",
                "回复任务卡片会作为该任务的补充；普通新消息会排队继续当前会话。",
                "使用 /cmd new-session 或 /ask --new 可新开会话。",
            ]
        )

    def capabilities(self) -> dict[str, Any]:
        active = [j for j in self.read_jobs() if j.get("status") in ("queued", "running")]
        command_options = self.command_options()
        return {
            "machine_id": self.machine_id,
            "version": self.config.get("protocol_version", "2"),
            "codex_cli": self.codex_cli,
            "codex_home": str(self.codex_home),
            "codex_config": str(self.codex_home / "config.toml"),
            "lark_cli": self.lark_cli,
            "workspaces": sorted((self.config.get("workspaces") or {}).keys()),
            "commands": command_options,
            "skills": self.available_skills(),
            "models": self.available_models(),
            "default_model": self.model_profile("default"),
            "fast_model": self.model_profile("fast"),
            "modalities": self.config.get("capabilities", {}).get("modalities", ["text", "image", "file"]),
            "active_jobs": len(active),
            "max_concurrent_jobs": int(self.config.get("jobs", {}).get("max_concurrent", 1)),
            "routing": self.config.get("routing", {}),
            "sessions": self.config.get("sessions", {}),
            "event_delivery": self.event_delivery_status(),
            "access": {
                "identity_count": len(self.access_identities()),
                "user_group_count": len(self.access_user_groups()),
                "group_count": len(self.access_groups()),
                "default_policy": self.access_config().get("default_policy", {}),
            },
            "preset_tasks": [
                {"id": task_id, "description": task.get("description", ""), "enabled": task.get("enabled", True)}
                for task_id, task in self.preset_tasks().items()
                if isinstance(task, dict)
            ],
        }

    def command_options(self) -> list[str]:
        configured = self.config.get("commands", {}).get("available", []) if isinstance(self.config.get("commands"), dict) else []
        commands = self.merge_unique(
            ["help", "status", "history", "capabilities", "peers", "sessions", "new-session"],
            configured,
            (self.config.get("public", {}).get("commands", {}) or {}).keys(),
            self.preset_tasks().keys(),
        )
        return sorted(commands)

    @staticmethod
    def skill_name_from_file(path: Path) -> str:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            return path.parent.name
        if lines and lines[0].strip() == "---":
            for line in lines[1:80]:
                if line.strip() == "---":
                    break
                match = re.match(r"\s*name\s*:\s*(.+?)\s*$", line)
                if match:
                    return match.group(1).strip().strip("'\"") or path.parent.name
        return path.parent.name

    def discover_skills_dir(self, root: Path, prefix: str = "") -> list[str]:
        if not root.exists():
            return []
        result: list[str] = []
        for path in root.rglob("SKILL.md"):
            name = self.skill_name_from_file(path)
            value = f"{prefix}:{name}" if prefix and not name.startswith(f"{prefix}:") else name
            if value and value not in result:
                result.append(value)
        return result

    def discover_plugin_skills(self) -> list[str]:
        plugins_cache = self.codex_home / "plugins" / "cache"
        if not plugins_cache.exists():
            return []
        result: list[str] = []
        for plugin_json in plugins_cache.rglob(".codex-plugin/plugin.json"):
            try:
                plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
            except Exception:
                continue
            plugin_name = str(plugin.get("name") or "").strip()
            skills_rel = str(plugin.get("skills") or "./skills/")
            skills_dir = (plugin_json.parent.parent / skills_rel).resolve()
            for name in self.discover_skills_dir(skills_dir, plugin_name):
                if name not in result:
                    result.append(name)
        return result

    def discover_codex_skills(self) -> list[str]:
        return self.merge_unique(
            self.discover_skills_dir(self.codex_home / "skills"),
            self.discover_skills_dir(Path.home() / ".agents" / "skills"),
            self.discover_plugin_skills(),
        )

    def available_skills(self) -> list[str]:
        skills_cfg = self.config.get("skills", {})
        configured = skills_cfg.get("available", []) if isinstance(skills_cfg, dict) and isinstance(skills_cfg.get("available"), list) else []
        return self.merge_unique(
            configured,
            self.discover_codex_skills(),
            self.config.get("capabilities", {}).get("skills", []) or [],
        )

    @staticmethod
    def normalize_model_entries(models: Any) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for item in models or []:
            if isinstance(item, dict):
                model_id = str(item.get("id") or item.get("model") or item.get("name") or item.get("slug") or "").strip()
                if model_id:
                    entry = dict(item)
                    entry["id"] = model_id
                    result.append(entry)
            else:
                model_id = str(item).strip()
                if model_id:
                    result.append({"id": model_id, "label": model_id})
        return result

    @staticmethod
    def merge_model_entries(*groups: Any) -> list[dict[str, Any]]:
        order: list[str] = []
        merged: dict[str, dict[str, Any]] = {}
        for group in groups:
            for entry in Bridge.normalize_model_entries(group):
                model_id = str(entry.get("id") or "").strip()
                if not model_id:
                    continue
                if model_id not in merged:
                    merged[model_id] = dict(entry)
                    order.append(model_id)
                    continue
                current = merged[model_id]
                for key, value in entry.items():
                    if value not in (None, "", []) and current.get(key) in (None, "", []):
                        current[key] = value
        return [merged[model_id] for model_id in order]

    def local_codex_config(self) -> dict[str, Any]:
        path = self.codex_home / "config.toml"
        if not path.exists():
            return {}
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def local_codex_model_profile(self) -> dict[str, str]:
        config = self.local_codex_config()
        return {
            "model": str(config.get("model") or ""),
            "reasoning_effort": str(config.get("model_reasoning_effort") or config.get("reasoning_effort") or ""),
            "service_tier": str(config.get("service_tier") or ""),
        }

    def discover_codex_models(self) -> list[dict[str, Any]]:
        result: list[tuple[int, str, dict[str, Any]]] = []
        cache_path = self.codex_home / "models_cache.json"
        if cache_path.exists():
            try:
                parsed = json.loads(cache_path.read_text(encoding="utf-8"))
            except Exception:
                parsed = {}
            for item in (parsed.get("models", []) if isinstance(parsed, dict) else []):
                if not isinstance(item, dict) or item.get("visibility") == "hide":
                    continue
                model_id = str(item.get("slug") or item.get("id") or item.get("model") or item.get("name") or "").strip()
                if not model_id:
                    continue
                efforts = []
                for effort in item.get("supported_reasoning_levels", []) or []:
                    if isinstance(effort, dict):
                        value = str(effort.get("effort") or "").strip()
                    else:
                        value = str(effort).strip()
                    if value:
                        efforts.append(value)
                entry: dict[str, Any] = {
                    "id": model_id,
                    "label": str(item.get("display_name") or model_id),
                }
                if efforts:
                    entry["reasoning_efforts"] = efforts
                if item.get("default_reasoning_level"):
                    entry["default_reasoning_effort"] = str(item.get("default_reasoning_level"))
                if item.get("additional_speed_tiers"):
                    entry["speed_tiers"] = item.get("additional_speed_tiers")
                priority = int(item.get("priority") if isinstance(item.get("priority"), int) else 999)
                result.append((priority, model_id, entry))
        local_profile = self.local_codex_model_profile()
        if local_profile.get("model"):
            result.append((-1000, local_profile["model"], {"id": local_profile["model"], "label": local_profile["model"]}))
        private_model = str(self.config.get("private", {}).get("codex_model") or "").strip()
        if private_model:
            result.append((-999, private_model, {"id": private_model, "label": private_model}))
        return [entry for _, _, entry in sorted(result, key=lambda item: (item[0], item[1]))]

    def available_models(self) -> list[dict[str, Any]]:
        models_cfg = self.config.get("models", {})
        models = models_cfg.get("available", []) if isinstance(models_cfg, dict) else []
        return self.merge_model_entries(self.discover_codex_models(), models)

    def model_profile(self, name: str = "default") -> dict[str, str]:
        models_cfg = self.config.get("models", {}) if isinstance(self.config.get("models", {}), dict) else {}
        profile = models_cfg.get(name, {}) if isinstance(models_cfg.get(name, {}), dict) else {}
        local_profile = self.local_codex_model_profile() if name == "default" else {}
        return {
            "model": str(profile.get("model") or local_profile.get("model") or self.config.get("private", {}).get("codex_model", "")),
            "reasoning_effort": str(profile.get("reasoning_effort") or local_profile.get("reasoning_effort") or ""),
            "service_tier": str(profile.get("service_tier") or local_profile.get("service_tier") or ""),
        }

    def configured_event_types(self) -> list[str]:
        return [str(item) for item in (self.config.get("event_types") or []) if str(item).strip()]

    def event_delivery_status(self) -> dict[str, Any]:
        event_types = self.configured_event_types()
        private_cfg = self.config.get("private", {}) or {}
        has_receive_event = "im.message.receive_v1" in event_types
        polling_fallback = bool(private_cfg.get("polling_fallback_enabled", False))
        return {
            "mode": "event",
            "transport": "lark-cli event +subscribe",
            "identity": "bot",
            "event_types": event_types,
            "private_receive_event_enabled": has_receive_event,
            "private_polling_fallback_enabled": polling_fallback,
            "private_polling_active_by_default": bool(private_cfg.get("enabled")) and polling_fallback,
            "private_poll_interval_sec": int(private_cfg.get("poll_interval_sec", 5)),
            "notes": [
                "im.message.receive_v1 receives private bot messages when the app has the receive-message event and private-message permission enabled and published.",
                "Polling is only a fallback for event delivery failures.",
            ],
        }

    def read_jobs(self) -> list[dict[str, Any]]:
        jobs = []
        for path in self.jobs_dir.glob("job-*.json"):
            try:
                jobs.append(self.reconcile_job_state(json.loads(path.read_text(encoding="utf-8")), path))
            except Exception:
                continue
        jobs.sort(key=lambda j: str(j.get("created_at", "")), reverse=True)
        return jobs

    def reconcile_job_state(self, job: dict[str, Any], path: Path) -> dict[str, Any]:
        if job.get("status") not in ("queued", "running"):
            return job
        if job.get("status") == "queued" and not any(job.get(name) for name in ("worker_pid", "runner_pid", "codex_pid")):
            return job
        pids = [job.get("worker_pid"), job.get("runner_pid"), job.get("codex_pid")]
        has_live_pid = any(self.pid_is_running(self.parse_pid(str(pid))) for pid in pids if pid)
        if has_live_pid:
            return job
        output_file = Path(str(job.get("output_file") or ""))
        stderr_file = Path(str(job.get("stderr_file") or ""))
        stdout_file = Path(str(job.get("stdout_file") or ""))
        worker_stderr_file = Path(str(job.get("worker_stderr_file") or ""))
        if output_file.exists() and output_file.stat().st_size > 0:
            job["status"] = "completed"
            job["finished_at"] = job.get("finished_at") or utcnow()
            job["updated_at"] = utcnow()
            job["result_prefix"] = shorten(self.read_file(str(output_file), 4000), 400)
            job["reconciled"] = True
            job["reconcile_reason"] = "worker exited but output_file exists"
            path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.append_job_event(str(job.get("job_id")), "reconciled_completed")
            return job
        error_text = ""
        for candidate in (worker_stderr_file, stderr_file, stdout_file):
            if candidate.exists() and candidate.stat().st_size > 0:
                error_text = self.read_file(str(candidate), 2000)
                break
        job["status"] = "failed"
        job["finished_at"] = job.get("finished_at") or utcnow()
        job["updated_at"] = utcnow()
        job["error"] = error_text or "Worker process exited before updating job status."
        job["reconciled"] = True
        job["reconcile_reason"] = "worker exited without output"
        path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.append_job_event(str(job.get("job_id")), "reconciled_failed")
        return job

    def format_status(self, job_id: str | None = None, show_details: bool = False) -> str:
        jobs = self.read_jobs()
        if job_id:
            job = next((j for j in jobs if str(j.get("job_id")) == job_id), None)
            if not job:
                return f"未找到任务：{job_id}" if not show_details else f"Job not found: {job_id}"
            if not show_details:
                lines = [
                    f"状态：{job.get('status')}",
                    f"更新时间：{job.get('updated_at')}",
                ]
                if job.get("error"):
                    lines.append(f"错误：{shorten(str(job.get('error')), 180)}")
                return "\n".join(lines)
            lines = [
                f"job_id={job.get('job_id')}",
                f"status={job.get('status')}",
                f"workspace={job.get('workspace')}",
                f"conversation={job.get('conversation_key') or ''}",
                f"queue_kind={job.get('queue_kind') or ''}",
                f"model={(job.get('codex_options') or {}).get('model') or ''}",
                f"created_at={job.get('created_at')}",
                f"updated_at={job.get('updated_at')}",
                f"resume_session_id={job.get('resume_session_id') or ''}",
                f"codex_deeplink={job.get('codex_deeplink') or ''}",
                f"output={job.get('output_file') or ''}",
                f"error={job.get('error') or ''}",
            ]
            return "\n".join(lines)
        active = [j for j in jobs if j.get("status") in ("queued", "running")]
        recent = jobs[:8]
        if not show_details:
            lines = [f"活动任务：{len(active)}"]
            for job in recent:
                lines.append(f"{job.get('status')} updated={job.get('updated_at')} prompt={shorten(str(job.get('prompt','')), 48)}")
            return "\n".join(lines)
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

    def read_conversations(self) -> dict[str, Any]:
        if not self.conversations_path.exists():
            return {}
        try:
            data = json.loads(self.conversations_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def write_conversations(self, data: dict[str, Any]) -> None:
        ensure_dir(self.conversations_path.parent)
        tmp = self.conversations_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.conversations_path)

    def sessions_enabled(self) -> bool:
        return bool(self.config.get("sessions", {}).get("enabled", True))

    def session_mode(self) -> str:
        mode = str((self.config.get("sessions", {}) or {}).get("mode") or "continuous").strip().lower()
        if mode in ("topic", "thread", "topics", "threads", "话题"):
            return "topic"
        return "continuous"

    def topic_mode_enabled(self) -> bool:
        return self.sessions_enabled() and self.session_mode() == "topic"

    def topic_reply_in_thread_enabled(self) -> bool:
        sessions = self.config.get("sessions", {}) or {}
        return bool(sessions.get("topic_reply_in_thread", True))

    def topic_ids_for_msg(self, msg: dict[str, Any]) -> list[str]:
        if not self.topic_mode_enabled():
            return []
        ids = self.merge_unique(
            [msg.get("thread_id")],
            [msg.get("root_id")],
            [msg.get("parent_id")],
            [msg.get("reply_to")],
            [msg.get("message_id")],
        )
        return ids

    def find_conversation_key_by_topic_ids(self, chat_id: str, topic_ids: list[str]) -> str:
        if not chat_id or not topic_ids:
            return ""
        wanted = set(map(str, topic_ids))
        matches: list[tuple[str, dict[str, Any]]] = []
        for key, item in self.read_conversations().items():
            if not isinstance(item, dict):
                continue
            if str(item.get("chat_id") or "") != str(chat_id):
                continue
            known_ids = set(map(str, item.get("topic_ids") or []))
            if wanted.intersection(known_ids):
                matches.append((key, item))
        if not matches:
            return ""
        matches.sort(key=lambda pair: str(pair[1].get("updated_at", "")), reverse=True)
        return str(matches[0][0])

    def topic_conversation_key_for_msg(self, msg: dict[str, Any]) -> str:
        topic_ids = self.topic_ids_for_msg(msg)
        existing = self.find_conversation_key_by_topic_ids(str(msg.get("chat_id") or ""), topic_ids)
        if existing:
            return existing
        topic_id = topic_ids[0] if topic_ids else str(msg.get("message_id") or uuid.uuid4().hex)
        prefix = "p2p" if msg.get("chat_type") == "p2p" else "group"
        return f"{prefix}:{msg.get('chat_id')}:topic:{topic_id}"

    def should_reply_in_thread(self, msg: dict[str, Any], prefer_reply: bool) -> bool:
        return bool(
            prefer_reply
            and msg.get("message_id")
            and self.topic_mode_enabled()
            and self.topic_reply_in_thread_enabled()
        )

    def conversation_key_for_msg(self, msg: dict[str, Any], reply_job: dict[str, Any] | None = None) -> str:
        if reply_job and reply_job.get("conversation_key"):
            return str(reply_job["conversation_key"])
        if self.topic_mode_enabled():
            return self.topic_conversation_key_for_msg(msg)
        sessions = self.config.get("sessions", {}) or {}
        if msg.get("chat_type") == "p2p":
            scope = str(sessions.get("private_scope") or "chat")
            if scope == "sender":
                return f"p2p:{msg.get('sender_id')}"
            return f"p2p:{msg.get('chat_id')}"
        scope = str(sessions.get("group_scope") or "chat")
        if scope == "chat_sender":
            return f"group:{msg.get('chat_id')}:sender:{msg.get('sender_id')}"
        return f"group:{msg.get('chat_id')}"

    def conversation_for_key(self, key: str) -> dict[str, Any]:
        return self.read_conversations().get(key, {}) if key else {}

    def update_conversation(self, key: str, **updates: Any) -> None:
        if not key:
            return
        data = self.read_conversations()
        current = data.get(key, {}) if isinstance(data.get(key), dict) else {}
        topic_ids = updates.pop("topic_ids", None)
        current.update({name: value for name, value in updates.items() if value is not None})
        if topic_ids is not None:
            current["topic_ids"] = self.merge_unique(current.get("topic_ids", []), topic_ids)
        current["updated_at"] = utcnow()
        data[key] = current
        self.write_conversations(data)

    def reset_conversation(self, msg: dict[str, Any], rest: str = "") -> str:
        reply_job = self.find_job_by_message_id(msg.get("reply_to") or "") if self.config.get("sessions", {}).get("reply_guidance_enabled", True) else None
        key = self.conversation_key_for_msg(msg, reply_job=reply_job)
        data = self.read_conversations()
        old = data.pop(key, None)
        self.write_conversations(data)
        detail = f"cleared previous session {old.get('session_id')}" if isinstance(old, dict) and old.get("session_id") else "no previous session"
        return f"New bridge conversation ready for {key}: {detail}."

    def format_sessions(self, msg: dict[str, Any] | None = None) -> str:
        data = self.read_conversations()
        if not data:
            return "No bridge conversations recorded."
        lines = []
        current_key = self.conversation_key_for_msg(msg) if msg else ""
        for key, item in sorted(data.items(), key=lambda pair: str(pair[1].get("updated_at", "")), reverse=True)[:12]:
            marker = "*" if key == current_key else "-"
            topic_ids = ",".join(str(value) for value in (item.get("topic_ids") or [])[:3])
            lines.append(
                f"{marker} {key} session={item.get('session_id') or ''} "
                f"last_job={item.get('last_job_id') or ''} mode={item.get('mode') or 'continuous'} "
                f"topics={topic_ids} updated={item.get('updated_at') or ''}"
            )
        return "\n".join(lines)

    def find_job_by_message_id(self, message_id: str) -> dict[str, Any] | None:
        if not message_id:
            return None
        for job in self.read_jobs():
            source = job.get("source") or {}
            ids = {
                str(source.get("message_id") or ""),
                str(job.get("status_message_id") or ""),
                str(job.get("final_message_id") or ""),
            }
            if message_id in ids:
                return job
        return None

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
            "conversation_key": job.get("conversation_key"),
            "queue_position": job.get("queue_position"),
            "resume_session_id": job.get("resume_session_id"),
            "status_message_id": job.get("status_message_id"),
            "final_message_id": job.get("final_message_id"),
        }

    def dashboard_status(self) -> dict[str, Any]:
        jobs = self.read_jobs()
        counts: dict[str, int] = {}
        for job in jobs:
            status = str(job.get("status") or "unknown")
            counts[status] = counts.get(status, 0) + 1
        active = [j for j in jobs if j.get("status") in ("queued", "running")]
        processes = {
            "bridge": self.process_snapshot("bridge.pid"),
            "dashboard": self.process_snapshot("dashboard.pid"),
            "private_poller": self.process_snapshot("private-poller.pid"),
        }
        pid_files = {
            "bridge.pid": str(processes["bridge"]["pid"] or ""),
            "dashboard.pid": str(processes["dashboard"]["pid"] or ""),
            "private-poller.pid": str(processes["private_poller"]["pid"] or ""),
        }
        mode = self.runtime_mode()
        connection_running = bool(processes["bridge"]["running"])
        can_start = mode == "dashboard-only" and not connection_running and bool(self.config.get("dashboard", {}).get("allow_process_control", True))
        can_stop = mode == "dashboard-only" and connection_running and bool(self.config.get("dashboard", {}).get("allow_process_control", True))
        return {
            "status": "ok",
            "now": utcnow(),
            "config_path": str(self.config_path),
            "codex_home": str(self.codex_home),
            "log_dir": str(self.log_dir),
            "state_dir": str(self.state_dir),
            "pid": os.getpid(),
            "pid_files": pid_files,
            "processes": processes,
            "runtime_mode": mode,
            "feishu_connection": {
                "running": connection_running,
                "pid": processes["bridge"]["pid"],
                "managed_by_dashboard": mode == "dashboard-only",
                "can_start": can_start,
                "can_stop": can_stop,
                "control_enabled": bool(self.config.get("dashboard", {}).get("allow_process_control", True)),
            },
            "capabilities": self.capabilities(),
            "job_counts": counts,
            "active_jobs": [self.summarize_job(j) for j in active],
            "recent_jobs": [self.summarize_job(j) for j in jobs[:10]],
            "dashboard": self.config.get("dashboard", {}),
            "health_server": self.config.get("health_server", {}),
            "windows_integration": self.windows_integration_status(),
            "event_delivery": self.event_delivery_status(),
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
            "runtime": {
                "codex_home": str(self.codex_home),
                "default_codex_home": str(DEFAULT_CODEX_HOME.expanduser()),
            },
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
        def as_bool(candidate: Any) -> bool:
            if isinstance(candidate, str):
                return candidate.strip().lower() in ("1", "true", "yes", "on")
            return bool(candidate)

        if key == "sessions.mode":
            mode = str(value or "continuous").strip().lower()
            if mode not in ("continuous", "topic"):
                raise ValueError("sessions.mode must be continuous or topic")
            return mode
        if key == "sessions.topic_reply_in_thread":
            return as_bool(value)
        if key in ("workspaces", "preset_tasks", "access.default_policy", "access.identities", "access.user_groups", "access.groups", "models.default", "models.fast"):
            if not isinstance(value, dict):
                raise ValueError(f"{key} must be a JSON object")
            return value
        if key in ("peers.nodes", "commands.available", "skills.available", "models.available"):
            if not isinstance(value, list):
                raise ValueError(f"{key} must be a JSON array")
            return value
        if isinstance(old, bool):
            return as_bool(value)
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
        self.codex_home = self.resolve_codex_home()
        self.machine_id = str(self.config.get("machine_id") or self.machine_id)
        self.log("info", "dashboard updated config", changed=changed, backup=str(backup))
        restart_recommended = any(
            key.startswith(("health_server.", "dashboard.", "private.poll_interval_sec", "private.polling_fallback_enabled"))
            or key in ("event_types", "codex.home_dir")
            for key in changed
        )
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

    def parse_codex_rest(self, rest: str) -> dict[str, Any]:
        workspace = str(self.config.get("private", {}).get("default_workspace") or "")
        prompt = rest.strip()
        options: dict[str, Any] = {
            "model": "",
            "reasoning_effort": "",
            "service_tier": "",
            "mode": "default",
            "skills": [],
            "new_session": False,
        }
        while prompt:
            option = re.match(r"^\s*(?P<token>--new|new-session|workspace=[\w.-]+|model=[\w.:/-]+|reasoning=[\w.-]+|effort=[\w.-]+|tier=[\w.-]+|mode=[\w.-]+|skills=[\w.,:-]+)\s*", prompt)
            if not option:
                break
            token = option.group("token")
            prompt = prompt[option.end() :].strip()
            if token in ("--new", "new-session"):
                options["new_session"] = True
            elif token.startswith("workspace="):
                workspace = token.split("=", 1)[1]
            elif token.startswith("model="):
                options["model"] = token.split("=", 1)[1]
            elif token.startswith(("reasoning=", "effort=")):
                options["reasoning_effort"] = token.split("=", 1)[1]
            elif token.startswith("tier="):
                options["service_tier"] = token.split("=", 1)[1]
            elif token.startswith("mode="):
                options["mode"] = token.split("=", 1)[1]
            elif token.startswith("skills="):
                options["skills"] = [item.strip() for item in token.split("=", 1)[1].split(",") if item.strip()]
        workspaces = self.config.get("workspaces") or {}
        if workspace not in workspaces:
            raise ValueError(f"Unknown workspace: {workspace}")
        cwd = str(workspaces[workspace])
        if not Path(cwd).exists():
            raise ValueError(f"Workspace path not found: {cwd}")
        if not prompt:
            raise ValueError("Missing prompt.")
        model_profile = self.model_profile("fast" if str(options.get("mode")).lower() == "fast" else "default")
        for key in ("model", "reasoning_effort", "service_tier"):
            if not options.get(key):
                options[key] = model_profile.get(key, "")
        return {"workspace": workspace, "cwd": cwd, "prompt": prompt, "options": options}

    def can_start_job(self, conversation_key: str | None = None) -> tuple[bool, str]:
        max_jobs = int(self.config.get("jobs", {}).get("max_concurrent", 1))
        active = [j for j in self.read_jobs() if j.get("status") == "running" or (j.get("status") == "queued" and j.get("worker_pid"))]
        if len(active) >= max_jobs:
            return False, f"Bridge is busy: {len(active)}/{max_jobs} active jobs. Use /cmd status."
        if self.sessions_enabled() and conversation_key and any(str(j.get("conversation_key") or "") == conversation_key for j in active):
            return False, "This conversation already has a running job. The follow-up will stay queued."
        return True, ""

    def save_job(self, job: dict[str, Any]) -> Path:
        job["updated_at"] = utcnow()
        path = self.jobs_dir / f"{job['job_id']}.json"
        if path.exists():
            try:
                previous = json.loads(path.read_text(encoding="utf-8"))
                for key in ("status_message_id", "final_message_id", "queue_position"):
                    if previous.get(key) and not job.get(key):
                        job[key] = previous[key]
            except Exception:
                pass
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        if self.config.get("jobs", {}).get("auto_cleanup_enabled", False):
            self.cleanup_jobs_history()
        return path

    def job_path(self, job_id: str) -> Path:
        return self.jobs_dir / f"{job_id}.json"

    def cleanup_jobs_history(self, limit: int | None = None) -> dict[str, Any]:
        jobs_cfg = self.config.get("jobs", {}) or {}
        keep = int(limit if limit is not None else jobs_cfg.get("history_limit", 200) or 200)
        keep = max(0, keep)
        delete_artifacts = bool(jobs_cfg.get("cleanup_delete_artifacts", True))
        terminal = {"completed", "failed", "timed_out", "stopped"}
        jobs = [j for j in self.read_jobs() if str(j.get("status") or "") in terminal]
        jobs.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
        to_delete = jobs[keep:] if keep else jobs
        deleted: list[str] = []
        errors: list[dict[str, str]] = []
        for job in to_delete:
            job_id = str(job.get("job_id") or "")
            if not job_id:
                continue
            try:
                json_path = self.job_path(job_id)
                if json_path.exists():
                    json_path.unlink()
                if delete_artifacts:
                    for directory in (self.jobs_dir / job_id, self.artifacts_dir / job_id):
                        if directory.exists() and directory.is_dir():
                            shutil.rmtree(directory)
                deleted.append(job_id)
            except Exception as exc:
                errors.append({"job_id": job_id, "error": str(exc)})
        if deleted or errors:
            self.log("info", "cleaned job history", keep=keep, deleted=deleted, errors=errors)
        return {"kept": keep, "deleted": deleted, "deleted_count": len(deleted), "errors": errors}

    def queued_jobs(self) -> list[dict[str, Any]]:
        return [j for j in self.read_jobs() if j.get("status") == "queued" and not j.get("worker_pid")]

    def start_worker_for_job(self, job: dict[str, Any]) -> bool:
        job_path = self.save_job(job)
        if self.dry_run:
            self.append_job_event(job["job_id"], "dry_run_worker_skipped")
            return False
        cmd = [
            sys.executable,
            "-u",
            str(Path(__file__).resolve()),
            "--config",
            str(self.config_path),
            "--run-job",
            str(job_path),
        ]
        worker_stdout = open(job["worker_stdout_file"], "a", encoding="utf-8", errors="replace")
        worker_stderr = open(job["worker_stderr_file"], "a", encoding="utf-8", errors="replace")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=worker_stdout,
                stderr=worker_stderr,
                stdin=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                env=self.env(),
            )
        finally:
            worker_stdout.close()
            worker_stderr.close()
        job["worker_pid"] = proc.pid
        self.save_job(job)
        self.append_job_event(job["job_id"], "worker_started", pid=proc.pid)
        return True

    def schedule_queued_jobs(self) -> int:
        if self.dry_run:
            return 0
        started = 0
        while True:
            ok, _ = self.can_start_job()
            if not ok:
                return started
            queued = sorted(self.queued_jobs(), key=lambda item: str(item.get("created_at", "")))
            if not queued:
                return started
            job = None
            for candidate in queued:
                can_start, _ = self.can_start_job(conversation_key=str(candidate.get("conversation_key") or ""))
                if can_start:
                    job = candidate
                    break
            if job is None:
                return started
            conversation = self.conversation_for_key(str(job.get("conversation_key") or ""))
            if self.sessions_enabled() and not job.get("new_session") and conversation.get("session_id"):
                job["resume_session_id"] = str(conversation.get("session_id") or "")
                job["resume_session_path"] = str(conversation.get("session_path") or "")
            job["queue_position"] = 0
            self.start_worker_for_job(job)
            started += 1

    def queue_position_for_job(self, job_id: str) -> int:
        queued = sorted(self.queued_jobs(), key=lambda item: str(item.get("created_at", "")))
        for index, job in enumerate(queued, start=1):
            if job.get("job_id") == job_id:
                return index
        return 0

    def attach_status_message(self, job_id: str, message_id: str) -> None:
        path = self.job_path(job_id)
        if not path.exists():
            return
        try:
            job = json.loads(path.read_text(encoding="utf-8"))
            job["status_message_id"] = message_id
            if job.get("conversation_mode") == "topic":
                job["topic_ids"] = self.merge_unique(job.get("topic_ids", []), [message_id])
            self.save_job(job)
            self.append_job_event(job_id, "status_message_attached", message_id=message_id)
            if job.get("conversation_mode") == "topic":
                self.update_conversation(str(job.get("conversation_key") or ""), topic_ids=[message_id])
            if job.get("status") in ("queued", "running"):
                self.update_job_status_message(job, str(job.get("status") or "queued"))
        except Exception as exc:
            self.log("warn", "failed to attach status message", job_id=job_id, message_id=message_id, error=str(exc))

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

    def start_preset_task_job(self, msg: dict[str, Any], task_id: str, task: dict[str, Any], user_input: str, prefer_reply: bool) -> dict[str, Any]:
        if not self.task_allowed_for_sender(msg, msg["chat_id"], task_id):
            return {"ok": False, "message": self.access_config().get("deny_message", "This sender is not allowed to run that task.")}
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
            selected_skills=[str(item) for item in task.get("required_skills", []) or []],
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
        selected_skills: list[str] | None = None,
        reply_job: dict[str, Any] | None = None,
        status_message_id_override: str | None = None,
    ) -> dict[str, Any]:
        policy = self.policy_for(msg, msg["chat_id"])
        if prompt_override is not None:
            workspace = workspace_override or str(self.config.get("private", {}).get("default_workspace") or "")
            prompt = prompt_override.strip()
            cwd = self.workspace_to_cwd(workspace)
            options = self.model_profile("default")
            options.update({"mode": "default", "skills": selected_skills or [], "new_session": False})
            if not prompt:
                raise ValueError("Missing prompt.")
        else:
            parsed = self.parse_codex_rest(rest)
            workspace = parsed["workspace"]
            cwd = parsed["cwd"]
            prompt = parsed["prompt"]
            options = parsed["options"]
            selected_skills = [str(item) for item in options.get("skills", []) or []]
        model = str(options.get("model") or "")
        if not self.model_allowed_for_policy(policy, model):
            return {"ok": False, "message": f"Model is not allowed for this sender: {model}"}
        if not self.skills_allowed_for_policy(policy, selected_skills or []):
            return {"ok": False, "message": "One or more requested skills are not allowed for this sender."}
        new_session = bool(options.get("new_session"))
        conversation_key = self.conversation_key_for_msg(msg, reply_job=reply_job)
        conversation = self.conversation_for_key(conversation_key)
        conversation_mode = self.session_mode()
        topic_ids = self.topic_ids_for_msg(msg)
        reply_in_thread = self.should_reply_in_thread(msg, prefer_reply)
        queue_kind = "new"
        if reply_job:
            queue_kind = "guidance" if reply_job.get("status") in ("queued", "running") else "followup"
        elif conversation.get("last_job_id"):
            queue_kind = "followup"
        if new_session:
            self.update_conversation(conversation_key, session_id="", session_path="", last_job_id="")
            conversation = {}
        elif conversation.get("last_status") == "completed" and not self.config.get("sessions", {}).get("continue_after_completion", True):
            conversation = {}
        job_id = "job-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        attachments = self.download_resources(msg["message_id"], msg["msg_type"], msg["content"], job_id=job_id)
        job_dir = self.jobs_dir / job_id
        ensure_dir(job_dir)
        resume_session_id = ""
        if self.sessions_enabled() and not new_session and conversation.get("session_id"):
            resume_session_id = str(conversation.get("session_id") or "")
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
            "codex_options": options,
            "selected_skills": selected_skills or [],
            "conversation_key": conversation_key,
            "conversation_mode": conversation_mode,
            "topic_ids": topic_ids,
            "queue_kind": queue_kind,
            "parent_job_id": reply_job.get("job_id") if reply_job else "",
            "new_session": new_session,
            "resume_session_id": resume_session_id,
            "show_details": bool(policy.get("show_details")),
            "show_progress": bool(policy.get("show_progress")),
            "status_message_id": status_message_id_override or "",
            "source": {
                "chat_id": msg["chat_id"],
                "chat_type": msg["chat_type"],
                "sender_id": msg["sender_id"],
                "message_id": msg["message_id"],
                "reply_to": msg.get("reply_to", ""),
                "parent_id": msg.get("parent_id", ""),
                "root_id": msg.get("root_id", ""),
                "thread_id": msg.get("thread_id", ""),
                "msg_type": msg["msg_type"],
                "prefer_reply": prefer_reply,
                "reply_in_thread": reply_in_thread,
            },
            "attachments": attachments,
            "output_file": str(job_dir / "last-message.txt"),
            "prompt_file": str(job_dir / "prompt.txt"),
            "stdout_file": str(job_dir / "codex-stdout.log"),
            "stderr_file": str(job_dir / "codex-stderr.log"),
            "worker_stdout_file": str(job_dir / "worker-stdout.log"),
            "worker_stderr_file": str(job_dir / "worker-stderr.log"),
        }
        self.save_job(job)
        self.update_conversation(
            conversation_key,
            chat_id=msg["chat_id"],
            chat_type=msg["chat_type"],
            sender_id=msg["sender_id"],
            workspace=workspace,
            last_job_id=job_id,
            mode=conversation_mode,
            topic_ids=topic_ids,
        )
        self.append_job_event(
            job_id,
            "queued",
            workspace=workspace,
            message_id=msg["message_id"],
            conversation_key=conversation_key,
            queue_kind=queue_kind,
        )
        if self.dry_run:
            message = self.format_job_start_message(job, queue_position=1, dry_run=True)
            return {
                "ok": True,
                "job_id": job_id,
                "title": "已收到消息",
                "message": message,
                "conversation_key": conversation_key,
                "reply_in_thread": reply_in_thread,
            }
        if not self.config.get("sessions", {}).get("queue_while_running", True):
            ok, why = self.can_start_job(conversation_key=conversation_key)
            if not ok:
                return {"ok": False, "message": why}
        self.schedule_queued_jobs()
        queue_position = self.queue_position_for_job(job_id)
        job["queue_position"] = queue_position
        self.save_job(job)
        message = self.format_job_start_message(job, queue_position=queue_position)
        return {
            "ok": True,
            "job_id": job_id,
            "title": "已收到消息",
            "message": message,
            "conversation_key": conversation_key,
            "reply_in_thread": reply_in_thread,
        }

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
            f"- conversation_key: {job.get('conversation_key') or ''}",
            f"- conversation_mode: {job.get('conversation_mode') or self.session_mode()}",
            f"- queue_kind: {job.get('queue_kind') or 'new'}",
        ]
        if job.get("topic_ids"):
            lines.append(f"- topic_ids: {', '.join(str(item) for item in job.get('topic_ids') or [])}")
        if job.get("resume_session_id"):
            lines.append(f"- resumed_codex_session_id: {job.get('resume_session_id')}")
        selected_skills = [str(item) for item in job.get("selected_skills", []) or []]
        if selected_skills:
            lines.extend(["", "Requested bridge skills:"])
            lines.extend(f"- {item}" for item in selected_skills)
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
        options = job.get("codex_options") or {}
        resume_session_id = str(job.get("resume_session_id") or "").strip()
        args = ["exec", "resume"] if resume_session_id else ["exec"]
        model = str(options.get("model") or cfg.get("codex_model") or "").strip()
        if model:
            args += ["-m", model]
        reasoning = str(options.get("reasoning_effort") or "").strip()
        if reasoning:
            args += ["-c", f'model_reasoning_effort="{reasoning}"']
        service_tier = str(options.get("service_tier") or "").strip()
        if service_tier:
            args += ["-c", f'service_tier="{service_tier}"']
        sandbox = str(cfg.get("codex_sandbox") or "workspace-write").strip()
        if sandbox == "danger-full-access":
            args += ["--dangerously-bypass-approvals-and-sandbox"]
        elif not resume_session_id:
            args += ["--sandbox", sandbox]
        if resume_session_id:
            args += ["--output-last-message", str(job["output_file"])]
        else:
            args += ["-C", str(job["cwd"]), "--output-last-message", str(job["output_file"])]
        for image in image_paths:
            args += ["--image", image]
        if resume_session_id:
            args += [resume_session_id]
        args += ["-"]
        return args

    def job_details_allowed(self, job: dict[str, Any]) -> bool:
        return bool(job.get("show_details"))

    def job_progress_allowed(self, job: dict[str, Any]) -> bool:
        return bool(job.get("show_progress"))

    def format_job_start_message(self, job: dict[str, Any], queue_position: int = 0, dry_run: bool = False) -> str:
        queue_kind = str(job.get("queue_kind") or "new")
        if queue_position and queue_kind == "guidance":
            lines = [f"已收到补充，会在当前任务结束后继续处理。队列位置：{queue_position}。"]
        elif queue_position:
            lines = [f"已收到消息，当前有任务在处理，已排队。队列位置：{queue_position}。"]
        elif queue_kind == "guidance":
            lines = ["已收到补充，正在继续处理。"]
        elif job.get("resume_session_id"):
            lines = ["已收到消息，正在沿用当前会话处理。"]
        else:
            lines = ["已收到消息，正在开始处理。"]
        lines.append("处理完成后会在这条消息里更新最终结论。")
        if str(job.get("conversation_mode") or self.session_mode()) == "topic":
            lines.append("在这个话题里继续发送消息会沿用本会话；在话题外触发任务会新开任务。")
        else:
            lines.append("继续发送消息会沿用本会话；发送 /cmd new-session 可新开会话。")
        if dry_run:
            lines.append("当前是 dry-run，不会实际执行。")
        if self.job_details_allowed(job):
            options = job.get("codex_options") or {}
            lines.extend(
                [
                    "",
                    "调试信息:",
                    f"job_id={job.get('job_id')}",
                    f"workspace={job.get('workspace')}",
                    f"conversation={job.get('conversation_key') or ''}",
                    f"mode={options.get('mode') or 'default'} model={options.get('model') or '(config default)'} reasoning={options.get('reasoning_effort') or '(config default)'}",
                    f"attachments={len(job.get('attachments') or [])}",
                    f"/cmd status {job.get('job_id')}",
                ]
            )
        return "\n".join(lines).strip()

    def mark_guidance_received(self, parent_job: dict[str, Any], guidance_job: dict[str, Any]) -> None:
        if not parent_job.get("job_id"):
            return
        path = self.job_path(str(parent_job["job_id"]))
        try:
            latest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else parent_job
        except Exception:
            latest = parent_job
        guidance = latest.get("guidance_queue", []) if isinstance(latest.get("guidance_queue"), list) else []
        guidance.append(
            {
                "job_id": guidance_job.get("job_id"),
                "message_id": (guidance_job.get("source") or {}).get("message_id"),
                "prompt": guidance_job.get("prompt"),
                "created_at": guidance_job.get("created_at"),
            }
        )
        latest["guidance_queue"] = guidance[-10:]
        latest["pending_guidance_count"] = len(latest["guidance_queue"])
        self.save_job(latest)
        self.append_job_event(str(latest["job_id"]), "guidance_received", guidance_job_id=guidance_job.get("job_id"))
        self.update_job_status_message(latest, str(latest.get("status") or "running"))

    def format_job_status_message(self, job: dict[str, Any], phase: str, result: str = "") -> str:
        phase_text = {
            "queued": "已收到消息，正在排队。",
            "running": "正在处理你的消息。",
            "completed": "处理完成。",
            "failed": "处理失败。",
            "timed_out": "处理超时。",
        }.get(str(phase), f"当前状态：{phase}")
        elapsed = ""
        if job.get("started_at"):
            seconds = max(0, int(time.time() - parse_ts(str(job.get("started_at")))))
            elapsed = f"已用时 {seconds} 秒。"
        model = (job.get("codex_options") or {}).get("model") or "(config default)"
        lines = [phase_text]
        if job.get("queue_position"):
            lines.append(f"队列位置：{job.get('queue_position')}")
        if job.get("pending_guidance_count"):
            lines.append(f"已收到 {job.get('pending_guidance_count')} 条补充，会继续在这张卡片里处理。")
        if elapsed:
            lines.append(elapsed)
        if result:
            lines.extend(["", "最终结论:", result.strip()])
            if str(job.get("conversation_mode") or self.session_mode()) == "topic":
                lines.extend(["", "在这个话题里继续发送消息会沿用本会话；在话题外触发任务会新开任务。"])
            else:
                lines.extend(["", "继续发送消息会沿用本会话；发送 /cmd new-session 可新开会话。"])
        elif phase in ("running", "queued"):
            lines.extend(["", "处理完成后会在这里更新最终结论。"])
            progress = self.progress_summary_for_job(job)
            if progress:
                lines.extend(["", "执行进度:", *progress])
        if self.job_details_allowed(job):
            lines.extend(
                [
                    "",
                    "调试信息:",
                    f"job_id={job.get('job_id')}",
                    f"workspace={job.get('workspace')}",
                    f"conversation={job.get('conversation_key') or ''}",
                    f"model={model}",
                ]
            )
        return "\n".join(lines).strip()

    def progress_summary_for_job(self, job: dict[str, Any]) -> list[str]:
        if not self.job_progress_allowed(job):
            return []
        max_lines = max(1, int(self.config.get("reply", {}).get("progress_max_lines", 8) or 8))
        raw = self.read_file(str(job.get("stderr_file") or ""), 12000)
        if not raw:
            raw = self.read_file(str(job.get("worker_stderr_file") or ""), 6000)
        lines: list[str] = []
        for line in raw.splitlines():
            cleaned = strip_ansi(line).strip()
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in ("exec", "codex", "tokens used"):
                continue
            if "tokens used" in lowered or "failed to read mcp server stderr" in lowered:
                continue
            if " succeeded in " in cleaned:
                lines.append("命令完成：" + shorten(cleaned.split(" in ", 1)[0], 120))
            elif " exited " in cleaned:
                lines.append("命令返回：" + shorten(cleaned.split(" in ", 1)[0], 120))
            elif cleaned.startswith('"') or cleaned.startswith("'"):
                lines.append("执行：" + shorten(cleaned, 140))
            elif cleaned.startswith("- ") or cleaned.startswith("|") or re.match(r"^[A-Za-z0-9_.-]+\s+[A-Za-z0-9_.-]+", cleaned):
                lines.append("输出：" + shorten(cleaned, 140))
            elif len(cleaned) <= 160:
                lines.append("输出：" + cleaned)
        deduped: list[str] = []
        for line in lines:
            if line not in deduped:
                deduped.append(line)
        return deduped[-max_lines:]

    def update_job_status_message(self, job: dict[str, Any], phase: str, result: str = "") -> bool:
        reply_cfg = self.config.get("reply", {}) or {}
        if not bool(reply_cfg.get("edit_status_message", False)):
            return False
        message_id = str(job.get("status_message_id") or "")
        if not message_id:
            return False
        title = {
            "queued": "已收到消息",
            "running": "正在处理",
            "completed": "处理完成",
            "failed": "处理失败",
            "timed_out": "处理超时",
        }.get(str(phase), "状态更新")
        return self.update_card_message(message_id, title, self.format_job_status_message(job, phase, result=result))

    def start_status_updater(self, job: dict[str, Any], done: threading.Event) -> threading.Thread | None:
        reply_cfg = self.config.get("reply", {}) or {}
        if not bool(reply_cfg.get("edit_status_message", False)) or not job.get("status_message_id"):
            return None
        interval = max(3, int(reply_cfg.get("status_update_interval_sec", 10) or 10))

        def worker() -> None:
            while not done.wait(interval):
                try:
                    path = self.job_path(str(job["job_id"]))
                    latest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else job
                    if latest.get("status") == "running":
                        self.update_job_status_message(latest, "running")
                except Exception as exc:
                    self.log("debug", "status updater skipped", job_id=job.get("job_id"), error=str(exc))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread

    def wait_for_status_message(self, job: dict[str, Any], timeout_sec: float = 8.0) -> dict[str, Any]:
        deadline = time.time() + timeout_sec
        latest = job
        while time.time() < deadline:
            if latest.get("status_message_id"):
                return latest
            time.sleep(0.25)
            try:
                path = self.job_path(str(job["job_id"]))
                latest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else latest
            except Exception:
                pass
        return latest

    def final_output_idle_ready(self, job: dict[str, Any], grace_sec: int) -> bool:
        if grace_sec <= 0:
            return False
        output_file = Path(str(job.get("output_file") or ""))
        if not output_file.exists() or output_file.stat().st_size <= 0:
            return False
        candidates = [
            Path(str(job.get("output_file") or "")),
            Path(str(job.get("stdout_file") or "")),
            Path(str(job.get("stderr_file") or "")),
        ]
        mtimes = [path.stat().st_mtime for path in candidates if path.exists()]
        if not mtimes:
            return False
        return time.time() - max(mtimes) >= grace_sec

    def wait_for_codex_process(self, proc: subprocess.Popen[str], job: dict[str, Any], prompt: str, timeout: int) -> str:
        if proc.stdin:
            try:
                proc.stdin.write(prompt)
                proc.stdin.flush()
            except Exception as exc:
                self.log("warn", "failed to write codex prompt", job_id=job.get("job_id"), error=str(exc))
            finally:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
        deadline = time.time() + timeout
        grace_sec = int(self.config.get("private", {}).get("final_output_idle_grace_sec") or 45)
        while True:
            if proc.poll() is not None:
                return "exited"
            if self.final_output_idle_ready(job, grace_sec):
                self.append_job_event(job["job_id"], "final_output_idle", grace_sec=grace_sec)
                self.terminate_process_tree(proc.pid)
                try:
                    proc.wait(timeout=10)
                except Exception:
                    pass
                return "final_output_idle"
            remaining = deadline - time.time()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(proc.args, timeout)
            time.sleep(min(1.0, remaining))

    def run_codex_job(self, job_path: Path) -> int:
        job = json.loads(job_path.read_text(encoding="utf-8"))
        job["status"] = "running"
        job["started_at"] = utcnow()
        job["runner_pid"] = os.getpid()
        self.save_job(job)
        self.append_job_event(job["job_id"], "running")
        job = self.wait_for_status_message(job)
        self.update_job_status_message(job, "running")
        updater_done = threading.Event()
        updater_thread = self.start_status_updater(job, updater_done)
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
                    wait_reason = self.wait_for_codex_process(proc, job, prompt, timeout)
                except subprocess.TimeoutExpired:
                    self.terminate_process_tree(proc.pid)
                    try:
                        proc.wait(timeout=5)
                    except Exception:
                        pass
                    result = self.read_job_result(job)
                    if result.strip():
                        job["status"] = "completed"
                        job["finished_at"] = utcnow()
                        job["error"] = f"Codex process timed out after {timeout} seconds after writing a final message."
                        job["result_prefix"] = shorten(result, 400)
                        self.save_job(job)
                        self.append_job_event(job["job_id"], "completed_after_timeout")
                        self.notify_job_done(job, result)
                        updater_done.set()
                        self.schedule_queued_jobs()
                        return 0
                    job["status"] = "timed_out"
                    job["finished_at"] = utcnow()
                    job["error"] = f"Timed out after {timeout} seconds"
                    self.save_job(job)
                    self.append_job_event(job["job_id"], "timed_out")
                    self.notify_job_done(job, "Timed out")
                    updater_done.set()
                    self.schedule_queued_jobs()
                    return 124
            job["exit_code"] = proc.returncode
            session_path, deeplink = self.find_codex_session_for_job(job, start_time)
            job["codex_session_path"] = session_path
            job["codex_deeplink"] = deeplink
            result = self.read_job_result(job)
            if wait_reason == "final_output_idle" and result.strip():
                job["status"] = "completed"
                job["finished_at"] = utcnow()
                job["finalize_reason"] = "final output idle"
                job["result_prefix"] = shorten(result, 400)
                self.save_job(job)
                self.append_job_event(job["job_id"], "completed_after_output_idle", codex_deeplink=deeplink)
                self.notify_job_done(job, result)
                updater_done.set()
                self.schedule_queued_jobs()
                return 0
            if proc.returncode == 0:
                job["status"] = "completed"
                job["result_prefix"] = shorten(result, 400)
                self.save_job(job)
                self.append_job_event(job["job_id"], "completed", codex_deeplink=deeplink)
                self.notify_job_done(job, result)
                updater_done.set()
                self.schedule_queued_jobs()
                return 0
            if result.strip():
                job["status"] = "completed"
                job["finished_at"] = utcnow()
                job["finalize_reason"] = f"nonzero exit {proc.returncode} after final output"
                job["result_prefix"] = shorten(result, 400)
                self.save_job(job)
                self.append_job_event(job["job_id"], "completed_after_nonzero_with_output", exit_code=proc.returncode, codex_deeplink=deeplink)
                self.notify_job_done(job, result)
                updater_done.set()
                self.schedule_queued_jobs()
                return 0
            job["status"] = "failed"
            job["error"] = self.read_file(job["stderr_file"], 2000) or self.read_file(job["stdout_file"], 2000)
            self.save_job(job)
            self.append_job_event(job["job_id"], "failed", exit_code=proc.returncode)
            self.notify_job_done(job, f"任务处理失败。\n{job.get('error')}")
            updater_done.set()
            self.schedule_queued_jobs()
            return int(proc.returncode or 1)
        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)
            self.save_job(job)
            self.append_job_event(job["job_id"], "failed", error=str(exc))
            self.notify_job_done(job, f"任务处理失败。\n{exc}")
            updater_done.set()
            self.schedule_queued_jobs()
            return 1

    @staticmethod
    def read_file(path: str, limit: int | None = None) -> str:
        if not path:
            return ""
        p = Path(path)
        if not p.exists() or p.is_dir():
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
        reply_in_thread = bool(source.get("reply_in_thread"))
        status = job.get("status")
        status_text = {"completed": "处理完成。", "failed": "处理失败。", "timed_out": "处理超时。"}.get(str(status), f"状态：{status}")
        if self.job_details_allowed(job):
            header = f"任务 {job['job_id']} {status}"
            if job.get("codex_deeplink"):
                header += f"\n{job['codex_deeplink']}"
            body = header + "\n\n最终结论:\n" + (result or "")
        else:
            body = status_text + "\n\n最终结论:\n" + (result or "")
        key = f"{job['job_id']}-{status}"
        edited = self.update_job_status_message(job, str(status), result=result)
        sent_id = ""
        if not edited:
            sent_id = self.send_response(
                chat_id,
                message_id,
                body,
                prefer_reply=prefer_reply,
                idempotency_key=key,
                reply_in_thread=reply_in_thread,
            )
        final_message_id = sent_id or str(job.get("status_message_id") or "")
        if final_message_id:
            job["final_message_id"] = final_message_id
            if job.get("conversation_mode") == "topic":
                job["topic_ids"] = self.merge_unique(job.get("topic_ids", []), [final_message_id])
            self.save_job(job)
        if status == "completed":
            session_id = ""
            if job.get("codex_deeplink"):
                session_id = str(job.get("codex_deeplink")).rsplit("/", 1)[-1]
            if not session_id:
                for key_name in ("stderr_file", "stdout_file", "worker_stderr_file"):
                    session_id = self.extract_session_id_from_text(self.read_file(str(job.get(key_name) or ""), 20000))
                    if session_id:
                        break
            self.update_conversation(
                str(job.get("conversation_key") or ""),
                session_id=session_id,
                session_path=job.get("codex_session_path") or self.session_path_for_id(session_id),
                last_job_id=job.get("job_id"),
                last_status=status,
                last_message_id=final_message_id or message_id,
                topic_ids=job.get("topic_ids", []),
            )
        reply_cfg = self.config.get("reply", {})
        output_file = Path(str(job.get("output_file") or ""))
        if (
            reply_cfg.get("upload_full_output_file", True)
            and output_file.exists()
            and len((result or "")) > int(reply_cfg.get("max_chars", 3500))
        ):
            try:
                self.send_file(
                    chat_id,
                    message_id,
                    output_file,
                    prefer_reply,
                    idempotency_key=key + "-file",
                    reply_in_thread=reply_in_thread,
                )
            except Exception as exc:
                self.log("error", "failed to upload full output file", job_id=job["job_id"], error=str(exc))

    @staticmethod
    def extract_session_id_from_text(text: str) -> str:
        match = re.search(r"\bsession id:\s*([0-9a-fA-F-]{36})", text or "", re.IGNORECASE)
        return match.group(1) if match else ""

    def session_path_for_id(self, session_id: str) -> str:
        if not session_id:
            return ""
        sessions = self.codex_home / "sessions"
        if not sessions.exists():
            return ""
        pattern = str(sessions / "**" / f"*{session_id}*.jsonl")
        matches = [Path(path) for path in glob.glob(pattern, recursive=True)]
        if matches:
            return str(max(matches, key=lambda p: p.stat().st_mtime))
        return ""

    def find_codex_session_for_job(self, job: dict[str, Any], start_time: float) -> tuple[str, str]:
        for key in ("stderr_file", "stdout_file", "worker_stderr_file"):
            text = self.read_file(str(job.get(key) or ""), 20000)
            session_id = self.extract_session_id_from_text(text)
            if session_id:
                return self.session_path_for_id(session_id), f"codex://threads/{session_id}"
        return self.find_codex_session(start_time)

    def find_codex_session(self, start_time: float) -> tuple[str, str]:
        sessions = self.codex_home / "sessions"
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
        msg = self.enrich_reply_to(msg)
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
        if re.match(r"^\s*/(?:id|whoami|assistant-id)\s*$", text):
            identity_key = self.sender_identity_key(msg) or "-"
            identity_label = self.sender_identity(msg).get("label") or identity_key
            body = "\n".join(
                [
                    f"node={self.machine_id}",
                    f"user={identity_label}",
                    f"user_key={identity_key}",
                    f"open_id={msg['sender_id']}",
                    f"chat_id={msg['chat_id']}",
                    f"chat_type={msg['chat_type']}",
                ]
            )
            self.send_response(msg["chat_id"], msg["message_id"], body, prefer_reply, idempotency_key=msg["message_id"] + "-id")
            return
        if re.match(r"^\s*/(?:codex-id|codex)\b", text):
            self.send_response(
                msg["chat_id"],
                msg["message_id"],
                "这个命令不可用。请使用 /id 查看识别信息，或使用 /ask 提交明确任务。",
                prefer_reply,
                idempotency_key=msg["message_id"] + "-legacy-deny",
            )
            return
        match = re.match(r"^\s*/cmd\s+(?P<name>[\w.-]+)(?:\s+(?P<rest>[\s\S]*))?$", text)
        if match:
            if not self.allowed_for_cmd(msg["chat_type"], msg["chat_id"], msg):
                return
            name = match.group("name")
            rest = match.group("rest") or ""
            task = self.preset_tasks().get(name)
            if isinstance(task, dict):
                result = self.start_preset_task_job(msg, name, task, rest, prefer_reply=prefer_reply)
                answer = str(result.get("message") or "")
            elif self.command_allowed_for_sender(msg, name, msg["chat_id"]):
                if name.lower() in ("new-session", "new", "reset-session"):
                    answer = self.reset_conversation(msg, rest)
                elif name.lower() in ("sessions", "session"):
                    answer = self.format_sessions(msg)
                else:
                    answer = self.built_in_command(name, rest, msg=msg)
                    if answer is None:
                        answer = self.invoke_fixed_command(name)
            else:
                answer = self.access_config().get("deny_message", "This sender is not allowed to run that command.")
            if isinstance(task, dict):
                sent_id = self.send_job_start_response(msg, result, prefer_reply, idempotency_key=msg["message_id"] + "-cmd")
            else:
                sent_id = self.send_response(msg["chat_id"], msg["message_id"], answer, prefer_reply, idempotency_key=msg["message_id"] + "-cmd")
            if isinstance(task, dict) and result.get("job_id") and sent_id:
                self.attach_status_message(str(result["job_id"]), sent_id)
            return
        task_id, task, task_input = self.match_preset_task(text)
        if task_id and isinstance(task, dict):
            if not self.chat_route_allowed(msg["chat_type"], msg["chat_id"]):
                return
            result = self.start_preset_task_job(msg, task_id, task, task_input, prefer_reply=prefer_reply)
            answer = str(result.get("message") or "")
            sent_id = self.send_job_start_response(msg, result, prefer_reply, idempotency_key=msg["message_id"] + "-task")
            if result.get("job_id") and sent_id:
                self.attach_status_message(str(result["job_id"]), sent_id)
            return
        match = re.match(r"^\s*/(?:ask|assistant)\s+(?:@(?P<target>[\w.-]+)\s+)?(?P<rest>[\s\S]*)$", text)
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
        if not self.allowed_for_codex(msg["chat_type"], msg["chat_id"], msg):
            if self.chat_route_allowed(msg["chat_type"], msg["chat_id"]) and self.sender_access_level(msg) == "limited":
                self.send_response(
                    msg["chat_id"],
                    msg["message_id"],
                    self.access_config().get("deny_message", "This sender can only run approved preset tasks."),
                    prefer_reply,
                    idempotency_key=msg["message_id"] + "-deny",
                )
            return
        reply_job = self.find_job_by_message_id(msg.get("reply_to") or "") if self.config.get("sessions", {}).get("reply_guidance_enabled", True) else None
        try:
            status_message_override = ""
            if reply_job and reply_job.get("status") in ("queued", "running"):
                status_message_override = str(reply_job.get("status_message_id") or "")
            result = self.start_codex_job(
                msg,
                codex_rest,
                prefer_reply=prefer_reply,
                reply_job=reply_job,
                status_message_id_override=status_message_override or None,
            )
            answer = str(result.get("message") or "")
        except Exception as exc:
            answer = f"暂时无法开始处理：{exc}"
            result = {}
            self.log("error", "could not start codex job", error=str(exc), message_id=msg["message_id"])
        if reply_job and reply_job.get("status") in ("queued", "running") and result.get("job_id"):
            guidance_job = json.loads(self.job_path(str(result["job_id"])).read_text(encoding="utf-8"))
            self.mark_guidance_received(reply_job, guidance_job)
            return
        sent_id = self.send_job_start_response(msg, result, prefer_reply, idempotency_key=msg["message_id"] + "-job") if result.get("job_id") else self.send_response(msg["chat_id"], msg["message_id"], answer, prefer_reply, idempotency_key=msg["message_id"] + "-job")
        if result.get("job_id") and sent_id:
            self.attach_status_message(str(result["job_id"]), sent_id)

    def handle_event(self, event: dict[str, Any]) -> None:
        event_type = str(event.get("type") or "")
        if event_type and event_type != "im.message.receive_v1":
            self.log("info", "received non-message event", event_type=event_type, keys=list(event.keys()))
            if event_type == "im.chat.access_event.bot_p2p_chat_entered_v1":
                self.save_onboarding_contact(event)
            return
        msg = self.enrich_reply_to(self.normalize_message(event))
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
                self.send_text(chat_id, f"识别信息 node={self.machine_id}; open_id={data['sender_id']}; chat_id={chat_id}; chat_type=p2p")

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
        args = ["event", "+subscribe", "--as", "bot", "--event-types", event_types, "--compact", "--quiet"]
        if self.dry_run:
            print(f"Dry run OK. Config loaded for machine_id={self.machine_id}.")
            return
        restart_count = 0
        backoff_sec = 2
        while not self.stop_event.is_set():
            self.log("info", "event subscriber starting", event_types=event_types, restart_count=restart_count)
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
                        self.log("error", "event subscriber exited", returncode=proc.returncode, restart_in_sec=backoff_sec)
                        break
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
            if self.stop_event.is_set():
                break
            restart_count += 1
            self.stop_event.wait(backoff_sec)
            backoff_sec = min(backoff_sec * 2, 60)

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
                    elif path == "/api/windows-integration":
                        self.send_json(200, bridge.windows_integration_status())
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
                    if path == "/api/connection/start":
                        self.send_json(200, bridge.start_bridge_connection(self.client_address[0]))
                        return
                    if path == "/api/connection/stop":
                        self.send_json(200, bridge.stop_bridge_connection(self.client_address[0]))
                        return
                    if path == "/api/jobs/cleanup":
                        if not bridge.is_loopback(self.client_address[0]):
                            raise PermissionError("Job cleanup is only accepted from loopback clients.")
                        limit_value = payload.get("history_limit") if isinstance(payload, dict) else None
                        limit = int(limit_value) if limit_value is not None else None
                        self.send_json(200, bridge.cleanup_jobs_history(limit=limit))
                        return
                    if path.startswith("/api/windows-integration/"):
                        action = path.rsplit("/", 1)[-1]
                        self.send_json(200, bridge.apply_windows_integration_action(action, self.client_address[0]))
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

    def run(self, private_only: bool = False, no_private_poller: bool = False, no_dashboard_server: bool = False) -> None:
        self.log("info", "bridge starting", dry_run=self.dry_run)
        if self.dry_run:
            print(f"Dry run OK. Config loaded for machine_id={self.machine_id}.")
            return
        if not no_dashboard_server:
            self.start_health_server()
        private_cfg = self.config.get("private", {}) or {}
        if private_cfg.get("enabled") and private_cfg.get("polling_fallback_enabled", False) and not no_private_poller:
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
    parser.add_argument("--no-dashboard-server", action="store_true")
    parser.add_argument("--windows-integration", choices=sorted(WINDOWS_INTEGRATION_ACTIONS))
    args = parser.parse_args()
    pid_name = None
    if not args.dry_run and not args.run_job and not args.windows_integration:
        pid_name = "dashboard.pid" if args.dashboard_only else "bridge.pid"
    bridge = Bridge(Path(args.config), dry_run=args.dry_run, pid_name=pid_name)
    install_signal_handlers(bridge)
    if args.windows_integration:
        result = bridge.apply_windows_integration_action(args.windows_integration, "127.0.0.1")
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        return 0
    if args.run_job:
        return bridge.run_codex_job(Path(args.run_job))
    if args.dashboard_only:
        server = bridge.start_health_server(force=True, host_override=args.dashboard_host, port_override=args.dashboard_port)
        host, port = server or ("127.0.0.1", 8765)
        print(f"Feishu Codex Bridge dashboard: http://{host}:{port}/", flush=True)
        while not bridge.stop_event.is_set():
            time.sleep(1)
        return 0
    bridge.run(
        private_only=args.private_poller_only,
        no_private_poller=args.no_private_poller,
        no_dashboard_server=args.no_dashboard_server,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
