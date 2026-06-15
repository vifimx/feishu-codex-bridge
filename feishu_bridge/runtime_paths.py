from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RuntimePaths:
    log_dir: Path
    state_dir: Path
    jobs_dir: Path
    artifacts_dir: Path
    conversations_path: Path
    contact_cache_path: Path
    processed_path: Path

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RuntimePaths":
        state_dir = Path(config["state_dir"]).expanduser()
        return cls(
            log_dir=Path(config["log_dir"]).expanduser(),
            state_dir=state_dir,
            jobs_dir=state_dir / "jobs",
            artifacts_dir=state_dir / "artifacts",
            conversations_path=state_dir / "conversations.json",
            contact_cache_path=state_dir / "contact-cache.json",
            processed_path=state_dir / "processed-message-ids.txt",
        )

    def ensure_base_dirs(self) -> None:
        for path in (self.log_dir, self.state_dir, self.jobs_dir, self.artifacts_dir):
            path.mkdir(parents=True, exist_ok=True)
