"""DuckDB persistence behind the same repository interface."""

from __future__ import annotations

from app.core.baseline import plan_baseline
from app.core.generator import generate_scenario
from app.core.pipeline import build_stored_run
from app.storage.duckdb_repo import DuckDBRepository


def test_duckdb_round_trips_a_run(tmp_path) -> None:
    path = str(tmp_path / "history.duckdb")
    first = DuckDBRepository(path)
    dataset = first.get_dataset("LEARNING_6")
    assert dataset is not None
    plan = plan_baseline("LEARNING_6")
    stored = build_stored_run(dataset, plan)
    first.put_run(stored)
    run_id = stored.plan.run.run_id
    first.close()

    second = DuckDBRepository(path)
    restored = second.get_run(run_id)
    assert restored is not None
    assert restored.plan.run.status.value == "heuristic_incomplete"
    assert restored.plan.run.unserved_customer_ids == ["C4"]
    assert restored.plan.run.partial_distance_metres == 27000
    customers = second._conn.execute(
        "SELECT COUNT(*) FROM customers WHERE scenario_id = 'LEARNING_6'"
    ).fetchone()
    assert customers[0] == 6
    routes = second._conn.execute(
        "SELECT COUNT(*) FROM routes WHERE run_id = ?",
        [run_id],
    ).fetchone()
    assert routes[0] == 2


def test_generated_scenario_survives_reconnect(tmp_path) -> None:
    path = str(tmp_path / "generated.duckdb")
    repo = DuckDBRepository(path)
    error, dataset = generate_scenario(
        random_seed=7,
        customer_count=8,
        vehicle_count=2,
        vehicle_capacity_totes=30,
    )
    assert error is None
    assert dataset is not None
    repo.put_dataset(dataset)
    scenario_id = dataset.scenario.scenario_id
    repo.close()

    reopened = DuckDBRepository(path)
    loaded = reopened.get_dataset(scenario_id)
    assert loaded is not None
    assert loaded.scenario.customer_count == 8
    assert scenario_id in reopened.list_scenario_ids()
