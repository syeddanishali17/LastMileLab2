"""In-memory scenario and run store. Lives for the process lifetime."""

from __future__ import annotations

from app.core.domain import RunType, ScenarioDataset
from app.core.loader import known_fixture_ids, load_and_precheck
from app.core.pipeline import StoredRun


class InMemoryRepository:
    def __init__(self) -> None:
        self._datasets: dict[str, ScenarioDataset] = {}
        self._runs: dict[str, StoredRun] = {}
        self._load_fixtures()

    def _load_fixtures(self) -> None:
        for scenario_id in known_fixture_ids():
            _precheck, dataset = load_and_precheck(scenario_id)
            if dataset is not None:
                self._datasets[scenario_id] = dataset

    def list_scenario_ids(self) -> list[str]:
        fixture_ids = known_fixture_ids()
        generated = [
            scenario_id
            for scenario_id in self._datasets
            if scenario_id not in fixture_ids
        ]
        return [*fixture_ids, *sorted(generated)]

    def get_dataset(self, scenario_id: str) -> ScenarioDataset | None:
        return self._datasets.get(scenario_id)

    def put_dataset(self, dataset: ScenarioDataset) -> None:
        self._datasets[dataset.scenario.scenario_id] = dataset

    def get_run(self, run_id: str) -> StoredRun | None:
        return self._runs.get(run_id)

    def put_run(self, stored: StoredRun) -> None:
        self._runs[stored.plan.run.run_id] = stored

    def latest_complete_baseline(self, scenario_id: str) -> StoredRun | None:
        matches = [
            stored
            for stored in self._runs.values()
            if stored.plan.run.scenario_id == scenario_id
            and stored.plan.run.run_type is RunType.baseline
            and stored.plan.run.comparison_eligible
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item.plan.run.created_at)
