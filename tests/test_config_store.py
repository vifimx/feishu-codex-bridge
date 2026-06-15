import json
import tempfile
import unittest
from pathlib import Path

from feishu_bridge.config_store import CONFIG_WRITE_ALLOWLIST, ConfigStore, config_change_requires_restart
from feishu_bridge.runtime_paths import RuntimePaths


class ConfigStoreTest(unittest.TestCase):
    def base_config(self, root: Path) -> dict:
        return {
            "machine_id": "local",
            "log_dir": str(root / "logs"),
            "state_dir": str(root / "state"),
            "dashboard": {"allow_config_write": True},
            "sessions": {"enabled": True},
            "jobs": {"history_limit": 50},
        }

    def test_allowlist_includes_dashboard_session_mode(self) -> None:
        self.assertIn("sessions.mode", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("sessions.topic_reply_in_thread", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("assistant", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("assistant.display_name", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("assistant.hide_internal_identity", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("private.codex_active_output_grace_sec", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("private.codex_timeout_extension_sec", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("private.coalesce_forward_comment_enabled", CONFIG_WRITE_ALLOWLIST)
        self.assertIn("private.coalesce_forward_comment_window_sec", CONFIG_WRITE_ALLOWLIST)

    def test_updates_session_mode_when_missing_from_existing_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "bridge.config.json"
            config = self.base_config(root)
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            store = ConfigStore(config_path)
            loaded = store.load()
            result = store.update(loaded, {"sessions.mode": "topic", "sessions.topic_reply_in_thread": True})

            self.assertEqual(["sessions.mode", "sessions.topic_reply_in_thread"], result.changed)
            self.assertEqual("topic", result.config["sessions"]["mode"])
            self.assertTrue(result.config["sessions"]["topic_reply_in_thread"])
            self.assertTrue(result.restart_recommended)
            self.assertTrue(result.backup and result.backup.exists())
            self.assertEqual("topic", json.loads(config_path.read_text(encoding="utf-8"))["sessions"]["mode"])

    def test_bridge_runtime_config_changes_recommend_restart(self) -> None:
        self.assertTrue(config_change_requires_restart("sessions.mode"))
        self.assertTrue(config_change_requires_restart("models.default.model"))
        self.assertTrue(config_change_requires_restart("access.resolve_contacts_enabled"))
        self.assertTrue(config_change_requires_restart("assistant"))
        self.assertTrue(config_change_requires_restart("assistant.identity_prompt"))

    def test_coerces_new_assistant_boolean_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "bridge.config.json"
            config = self.base_config(root)
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            store = ConfigStore(config_path)
            result = store.update(config, {"assistant.hide_internal_identity": True})

            self.assertIs(result.config["assistant"]["hide_internal_identity"], True)

    def test_coerces_numeric_keys_even_when_existing_value_is_string(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "bridge.config.json"
            config = self.base_config(root)
            config["private"] = {"final_output_ready_sec": "0"}
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            store = ConfigStore(config_path)
            result = store.update(config, {"private.final_output_ready_sec": 3})

            self.assertEqual(3, result.config["private"]["final_output_ready_sec"])
            self.assertIsInstance(result.config["private"]["final_output_ready_sec"], int)

    def test_coerces_forward_coalesce_settings_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "bridge.config.json"
            config = self.base_config(root)
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            store = ConfigStore(config_path)
            result = store.update(
                config,
                {
                    "private.coalesce_forward_comment_enabled": "false",
                    "private.coalesce_forward_comment_window_sec": "2.5",
                },
            )

            self.assertIs(result.config["private"]["coalesce_forward_comment_enabled"], False)
            self.assertEqual(2.5, result.config["private"]["coalesce_forward_comment_window_sec"])
            self.assertIsInstance(result.config["private"]["coalesce_forward_comment_window_sec"], float)

    def test_rejects_unknown_dashboard_key_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "bridge.config.json"
            config = self.base_config(root)
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            store = ConfigStore(config_path)
            with self.assertRaisesRegex(ValueError, "not editable"):
                store.update(config, {"sessions.unknown": True})

            self.assertFalse(list(root.glob("bridge.config.json.*.bak")))

    def test_runtime_paths_derive_state_files(self) -> None:
        paths = RuntimePaths.from_config({"log_dir": "logs", "state_dir": "state"})

        self.assertEqual(Path("state") / "jobs", paths.jobs_dir)
        self.assertEqual(Path("state") / "artifacts", paths.artifacts_dir)
        self.assertEqual(Path("state") / "conversations.json", paths.conversations_path)


if __name__ == "__main__":
    unittest.main()
