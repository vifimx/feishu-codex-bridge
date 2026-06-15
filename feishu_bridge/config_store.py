from __future__ import annotations

import copy
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_WRITE_ALLOWLIST = {
    "assistant",
    "assistant.display_name",
    "assistant.hide_internal_identity",
    "assistant.identity_prompt",
    "codex.home_dir",
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
    "private.codex_active_output_grace_sec",
    "private.codex_timeout_extension_sec",
    "private.codex_model",
    "private.final_output_ready_sec",
    "private.final_output_idle_grace_sec",
    "private.polling_fallback_enabled",
    "private.poll_interval_sec",
    "private.treat_all_text_as_codex",
    "private.coalesce_forward_comment_enabled",
    "private.coalesce_forward_comment_window_sec",
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
    "routing.only_respond_to_bot_mention",
    "routing.private_only_respond_to_bot_mention",
    "routing.dispatch_to_peers",
    "routing.prefer_local_when_capable",
    "task_scheduler",
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
    "access.default_template",
    "access.enable_preset_intent_matching",
    "access.resolve_contacts_enabled",
    "access.contact_cache_ttl_sec",
    "preset_tasks",
    "workspaces",
    "event_types",
}

JSON_OBJECT_KEYS = {
    "workspaces",
    "preset_tasks",
    "assistant",
    "access.default_policy",
    "access.identities",
    "access.user_groups",
    "access.groups",
    "models.default",
    "models.fast",
    "task_scheduler",
}

JSON_ARRAY_KEYS = {
    "peers.nodes",
    "skills.available",
    "models.available",
}

BOOLEAN_KEYS = {
    "private.coalesce_forward_comment_enabled",
}

NUMBER_KEYS = {
    "access.contact_cache_ttl_sec",
    "jobs.history_limit",
    "jobs.max_concurrent",
    "multimodal.download_timeout_sec",
    "private.codex_active_output_grace_sec",
    "private.codex_timeout_sec",
    "private.codex_timeout_extension_sec",
    "private.final_output_idle_grace_sec",
    "private.final_output_ready_sec",
    "private.poll_interval_sec",
    "reply.max_chars",
    "reply.progress_max_lines",
    "reply.status_update_interval_sec",
    "health_server.port",
}

FLOAT_KEYS = {
    "private.coalesce_forward_comment_window_sec",
}


@dataclass(frozen=True)
class ConfigUpdateResult:
    config: dict[str, Any]
    changed: list[str]
    backup: Path | None
    restart_recommended: bool

    def api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "changed": self.changed,
            "restart_recommended": self.restart_recommended,
        }
        if self.backup:
            payload["backup"] = str(self.backup)
        return payload


def get_dotted(data: dict[str, Any], key: str) -> Any:
    current: Any = data
    for part in key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


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


def as_bool(candidate: Any) -> bool:
    if isinstance(candidate, str):
        return candidate.strip().lower() in ("1", "true", "yes", "on")
    return bool(candidate)


def config_change_requires_restart(key: str) -> bool:
    return key.startswith(
        (
            "access.",
            "assistant.",
            "commands.",
            "dashboard.",
            "health_server.",
            "jobs.",
            "models.",
            "multimodal.",
            "peers.",
            "private.",
            "public.",
            "reply.",
            "routing.",
            "task_scheduler",
            "sessions.",
            "skills.",
        )
    ) or key in {
        "assistant",
        "event_types",
        "codex.home_dir",
        "preset_tasks",
        "workspaces",
    }


class ConfigStore:
    def __init__(self, path: Path, allowlist: set[str] | None = None):
        self.path = path
        self.allowlist = set(allowlist or CONFIG_WRITE_ALLOWLIST)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.validate(data)
        return data

    @staticmethod
    def validate(config: dict[str, Any]) -> None:
        for key in ("machine_id", "log_dir", "state_dir"):
            if not config.get(key):
                raise ValueError(f"Config missing {key}")

    def editable_keys(self) -> list[str]:
        return sorted(self.allowlist)

    def update(self, current_config: dict[str, Any], updates: dict[str, Any]) -> ConfigUpdateResult:
        if not updates:
            return ConfigUpdateResult(config=current_config, changed=[], backup=None, restart_recommended=False)

        new_config = copy.deepcopy(current_config)
        changed: list[str] = []
        for key, value in updates.items():
            if key not in self.allowlist:
                raise ValueError(f"Config key is not editable from dashboard: {key}")
            coerced = self.coerce_value(current_config, key, value)
            if get_dotted(new_config, key) != coerced:
                set_dotted(new_config, key, coerced)
                changed.append(key)

        if not changed:
            return ConfigUpdateResult(config=current_config, changed=[], backup=None, restart_recommended=False)

        backup = self.backup_path()
        backup.write_text(json.dumps(current_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.path.write_text(json.dumps(new_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return ConfigUpdateResult(
            config=new_config,
            changed=changed,
            backup=backup,
            restart_recommended=any(config_change_requires_restart(key) for key in changed),
        )

    def backup_path(self) -> Path:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        return self.path.with_suffix(self.path.suffix + f".{stamp}.bak")

    @staticmethod
    def coerce_value(current_config: dict[str, Any], key: str, value: Any) -> Any:
        old = get_dotted(current_config, key)

        if key == "sessions.mode":
            mode = str(value or "continuous").strip().lower()
            if mode not in ("continuous", "topic"):
                raise ValueError("sessions.mode must be continuous or topic")
            return mode
        if key == "sessions.topic_reply_in_thread":
            return as_bool(value)
        if key == "assistant.hide_internal_identity":
            return as_bool(value)
        if key in JSON_OBJECT_KEYS:
            if not isinstance(value, dict):
                raise ValueError(f"{key} must be a JSON object")
            return value
        if key in JSON_ARRAY_KEYS:
            if not isinstance(value, list):
                raise ValueError(f"{key} must be a JSON array")
            return value
        if key in BOOLEAN_KEYS:
            return as_bool(value)
        if key in NUMBER_KEYS:
            return int(value)
        if key in FLOAT_KEYS:
            return float(value)
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
