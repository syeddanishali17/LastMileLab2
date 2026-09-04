"""Repository interface. In-memory through Phase 7; DuckDB in Phase 8."""

from __future__ import annotations

from typing import Protocol

from app.core.domain import ScenarioDataset
from app.core.pipeline import StoredRun


class AppRepository(Protocol):
    def list_scenario_ids(self) -> list[str]: ...

    def get_dataset(self, scenario_id: str) -> ScenarioDataset | None: ...

    def put_dataset(self, dataset: ScenarioDataset) -> None: ...

    def get_run(self, run_id: str) -> StoredRun | None: ...

    def put_run(self, stored: StoredRun) -> None: ...

    def latest_complete_baseline(self, scenario_id: str) -> StoredRun | None: ...
