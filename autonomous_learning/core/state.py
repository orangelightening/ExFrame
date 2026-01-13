"""
State persistence for Autonomous Learning System.

Provides:
- File-based state persistence (JSON)
- Thread-safe state access
- Automatic state backup
- State recovery on restart
"""

import fcntl
import json
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import get_logger


@dataclass
class WorkerState:
    """State of an autonomous worker."""
    worker_id: str
    status: str  # "idle", "running", "paused", "error"
    task: Optional[str] = None
    last_heartbeat: Optional[str] = None
    last_action: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


@dataclass
class SurveyState:
    """State of a survey."""
    survey_id: str
    name: str
    level: str  # "domain", "neighbourhood", "universe"
    universe: str
    neighbourhood: Optional[str]
    domain: Optional[str]
    status: str = "idle"  # "idle", "running", "paused", "completed", "failed"
    progress: float = 0.0
    patterns_created: int = 0
    patterns_certified: int = 0
    patterns_flagged: int = 0
    patterns_rejected: int = 0
    patterns_pending: int = 0
    domains_created: int = 0
    neighbourhoods_created: int = 0
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class SystemState:
    """Global system state."""
    surveys: Dict[str, SurveyState] = None
    workers: Dict[str, WorkerState] = None
    last_updated: Optional[str] = None

    def __post_init__(self):
        if self.surveys is None:
            self.surveys = {}
        if self.workers is None:
            self.workers = {}
        if self.last_updated is None:
            self.last_updated = datetime.utcnow().isoformat()


class StateManager:
    """
    Thread-safe state persistence manager.

    Uses file locking for concurrent access safety.
    """

    def __init__(self, state_file: Path, backup_dir: Optional[Path] = None):
        """
        Initialize state manager.

        Args:
            state_file: Path to state file (JSON)
            backup_dir: Optional directory for state backups
        """
        self.state_file = state_file
        self.backup_dir = backup_dir
        self._lock = threading.RLock()
        self._logger = get_logger("state")

        # Ensure state directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if backup_dir:
            backup_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize state
        self._state = self._load_state()

    def _load_state(self) -> SystemState:
        """Load state from file or create new state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)

                # Reconstruct state objects
                state = SystemState()
                state.surveys = {
                    sid: SurveyState(**sdata)
                    for sid, sdata in data.get("surveys", {}).items()
                }
                state.workers = {
                    wid: WorkerState(**wdata)
                    for wid, wdata in data.get("workers", {}).items()
                }
                state.last_updated = data.get("last_updated")

                self._logger.info(f"Loaded state from {self.state_file}")
                return state

            except Exception as e:
                self._logger.error(f"Failed to load state: {e}")
                # Create backup of corrupted state
                if self.backup_dir:
                    backup_path = self.backup_dir / f"state_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    self.state_file.rename(backup_path)
                    self._logger.info(f"Corrupted state backed up to {backup_path}")

        # Return new state
        return SystemState()

    def _save_state(self):
        """Save state to file with locking."""
        # Create backup if enabled
        if self.backup_dir and self.state_file.exists():
            backup_path = self.backup_dir / f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import shutil
            shutil.copy2(self.state_file, backup_path)
            self._logger.debug(f"State backed up to {backup_path}")

        # Update timestamp
        self._state.last_updated = datetime.utcnow().isoformat()

        # Write to temporary file first
        temp_file = self.state_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump({
                "surveys": {
                    sid: asdict(survey)
                    for sid, survey in self._state.surveys.items()
                },
                "workers": {
                    wid: asdict(worker)
                    for wid, worker in self._state.workers.items()
                },
                "last_updated": self._state.last_updated,
            }, f, indent=2, default=str)

        # Atomic rename
        temp_file.replace(self.state_file)
        self._logger.debug(f"State saved to {self.state_file}")

    def get_state(self) -> SystemState:
        """Get current system state."""
        with self._lock:
            # Return a copy to prevent external modification
            return SystemState(
                surveys={k: SurveyState(**asdict(v)) for k, v in self._state.surveys.items()},
                workers={k: WorkerState(**asdict(v)) for k, v in self._state.workers.items()},
                last_updated=self._state.last_updated,
            )

    def update_survey(self, survey_id: str, **updates) -> None:
        """
        Update survey state.

        Args:
            survey_id: Survey identifier
            **updates: Fields to update
        """
        with self._lock:
            if survey_id not in self._state.surveys:
                # Create new survey state
                self._state.surveys[survey_id] = SurveyState(
                    survey_id=survey_id,
                    name=updates.get("name", ""),
                    level=updates.get("level", "domain"),
                    universe=updates.get("universe", "default"),
                    neighbourhood=updates.get("neighbourhood"),
                    domain=updates.get("domain"),
                )

            # Update fields
            survey = self._state.surveys[survey_id]
            for key, value in updates.items():
                if hasattr(survey, key):
                    setattr(survey, key, value)

            self._save_state()
            self._logger.debug(f"Survey {survey_id} updated: {updates}")

    def update_worker(self, worker_id: str, **updates) -> None:
        """
        Update worker state.

        Args:
            worker_id: Worker identifier
            **updates: Fields to update
        """
        with self._lock:
            if worker_id not in self._state.workers:
                # Create new worker state
                self._state.workers[worker_id] = WorkerState(
                    worker_id=worker_id,
                    status=updates.get("status", "idle"),
                )

            # Update fields
            worker = self._state.workers[worker_id]
            for key, value in updates.items():
                if hasattr(worker, key):
                    setattr(worker, key, value)

            self._save_state()
            self._logger.debug(f"Worker {worker_id} updated: {updates}")

    def remove_survey(self, survey_id: str) -> None:
        """Remove survey from state."""
        with self._lock:
            if survey_id in self._state.surveys:
                del self._state.surveys[survey_id]
                self._save_state()
                self._logger.info(f"Survey {survey_id} removed from state")

    def remove_worker(self, worker_id: str) -> None:
        """Remove worker from state."""
        with self._lock:
            if worker_id in self._state.workers:
                del self._state.workers[worker_id]
                self._save_state()
                self._logger.info(f"Worker {worker_id} removed from state")

    def get_survey(self, survey_id: str) -> Optional[SurveyState]:
        """Get survey state."""
        with self._lock:
            if survey_id in self._state.surveys:
                return SurveyState(**asdict(self._state.surveys[survey_id]))
            return None

    def get_worker(self, worker_id: str) -> Optional[WorkerState]:
        """Get worker state."""
        with self._lock:
            if worker_id in self._state.workers:
                return WorkerState(**asdict(self._state.workers[worker_id]))
            return None

    def list_surveys(self) -> list[str]:
        """List all survey IDs."""
        with self._lock:
            return list(self._state.surveys.keys())

    def list_workers(self) -> list[str]:
        """List all worker IDs."""
        with self._lock:
            return list(self._state.workers.keys())


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager(state_file: Optional[Path] = None) -> StateManager:
    """
    Get or create global state manager.

    Args:
        state_file: Optional path to state file

    Returns:
        StateManager instance
    """
    global _state_manager

    if _state_manager is None:
        if state_file is None:
            state_file = Path("data/state/autonomous_learning.json")

        _state_manager = StateManager(
            state_file=state_file,
            backup_dir=Path("data/state/backups")
        )

    return _state_manager
