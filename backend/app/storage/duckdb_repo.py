"""DuckDB run history behind the AppRepository interface."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from app.core.domain import (
    ConstraintCheck,
    CustomerResult,
    PlanResult,
    RunType,
    ScenarioDataset,
    ScenarioKpis,
    VehicleKpis,
)
from app.core.loader import known_fixture_ids, load_and_precheck
from app.core.pipeline import StoredRun

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS scenarios (
        scenario_id VARCHAR PRIMARY KEY,
        scenario_name VARCHAR,
        customer_count INTEGER,
        vehicle_count INTEGER,
        vehicle_capacity_totes INTEGER,
        has_geographic_coordinates BOOLEAN,
        is_synthetic BOOLEAN,
        dataset_json VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS customers (
        scenario_id VARCHAR,
        customer_id VARCHAR,
        zone_id VARCHAR,
        latitude DOUBLE,
        longitude DOUBLE,
        demand_totes INTEGER,
        PRIMARY KEY (scenario_id, customer_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vehicles (
        scenario_id VARCHAR,
        vehicle_id VARCHAR,
        capacity_totes INTEGER,
        PRIMARY KEY (scenario_id, vehicle_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS planning_runs (
        run_id VARCHAR PRIMARY KEY,
        scenario_id VARCHAR NOT NULL,
        run_type VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        comparison_eligible BOOLEAN,
        created_at VARCHAR,
        stored_json VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS routes (
        run_id VARCHAR,
        vehicle_id VARCHAR,
        is_used BOOLEAN,
        assigned_demand_totes INTEGER,
        capacity_totes INTEGER,
        distance_metres INTEGER,
        customer_count INTEGER,
        PRIMARY KEY (run_id, vehicle_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS route_stops (
        run_id VARCHAR,
        vehicle_id VARCHAR,
        sequence_number INTEGER,
        node_id VARCHAR,
        node_type VARCHAR,
        demand_totes INTEGER,
        load_after_service_totes INTEGER,
        leg_distance_metres INTEGER,
        cumulative_distance_metres INTEGER,
        PRIMARY KEY (run_id, vehicle_id, sequence_number)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS constraint_checks (
        run_id VARCHAR,
        code VARCHAR,
        name VARCHAR,
        passed BOOLEAN,
        message VARCHAR,
        PRIMARY KEY (run_id, code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS scenario_kpis (
        run_id VARCHAR PRIMARY KEY,
        kpis_json VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vehicle_kpis (
        run_id VARCHAR,
        vehicle_id VARCHAR,
        sequence_json VARCHAR,
        customer_count INTEGER,
        assigned_demand_totes INTEGER,
        capacity_totes INTEGER,
        remaining_capacity_totes INTEGER,
        capacity_utilisation DOUBLE,
        route_distance_metres INTEGER,
        is_used BOOLEAN,
        PRIMARY KEY (run_id, vehicle_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS assignments (
        run_id VARCHAR,
        customer_id VARCHAR,
        demand_totes INTEGER,
        assigned_vehicle VARCHAR,
        service_count INTEGER,
        demand_check VARCHAR,
        PRIMARY KEY (run_id, customer_id)
    )
    """,
]


def _dumps(model: object) -> str:
    if hasattr(model, "model_dump"):
        return json.dumps(model.model_dump(mode="json"))
    return json.dumps(model)


def stored_run_from_json(raw: str) -> StoredRun:
    payload = json.loads(raw)
    return StoredRun(
        dataset=ScenarioDataset.model_validate(payload["dataset"]),
        plan=PlanResult.model_validate(payload["plan"]),
        scenario_kpis=ScenarioKpis.model_validate(payload["scenario_kpis"]),
        vehicle_kpis=[VehicleKpis.model_validate(item) for item in payload["vehicle_kpis"]],
        assignments=[CustomerResult.model_validate(item) for item in payload["assignments"]],
        checks=[ConstraintCheck.model_validate(item) for item in payload["checks"]],
    )


def stored_run_to_json(stored: StoredRun) -> str:
    return json.dumps(
        {
            "dataset": stored.dataset.model_dump(mode="json"),
            "plan": stored.plan.model_dump(mode="json"),
            "scenario_kpis": stored.scenario_kpis.model_dump(mode="json"),
            "vehicle_kpis": [item.model_dump(mode="json") for item in stored.vehicle_kpis],
            "assignments": [item.model_dump(mode="json") for item in stored.assignments],
            "checks": [item.model_dump(mode="json") for item in stored.checks],
        }
    )


class DuckDBRepository:
    def __init__(self, path: str) -> None:
        self.path = path
        if path not in {":memory:", ""} and not path.startswith("md:"):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(path)
        for statement in SCHEMA_STATEMENTS:
            self._conn.execute(statement)
        self._seed_fixtures()

    def _seed_fixtures(self) -> None:
        for scenario_id in known_fixture_ids():
            _precheck, dataset = load_and_precheck(scenario_id)
            if dataset is not None:
                self.put_dataset(dataset)

    def list_scenario_ids(self) -> list[str]:
        fixture_ids = known_fixture_ids()
        rows = self._conn.execute("SELECT scenario_id FROM scenarios").fetchall()
        stored = [row[0] for row in rows]
        generated = [scenario_id for scenario_id in stored if scenario_id not in fixture_ids]
        return [*fixture_ids, *sorted(generated)]

    def get_dataset(self, scenario_id: str) -> ScenarioDataset | None:
        row = self._conn.execute(
            "SELECT dataset_json FROM scenarios WHERE scenario_id = ?",
            [scenario_id],
        ).fetchone()
        if row is None:
            return None
        return ScenarioDataset.model_validate(json.loads(row[0]))

    def put_dataset(self, dataset: ScenarioDataset) -> None:
        scenario = dataset.scenario
        self._conn.execute(
            """
            INSERT OR REPLACE INTO scenarios (
                scenario_id, scenario_name, customer_count, vehicle_count,
                vehicle_capacity_totes, has_geographic_coordinates, is_synthetic, dataset_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                scenario.scenario_id,
                scenario.scenario_name,
                scenario.customer_count,
                scenario.vehicle_count,
                scenario.vehicle_capacity_totes,
                scenario.has_geographic_coordinates,
                scenario.is_synthetic,
                _dumps(dataset),
            ],
        )
        self._conn.execute("DELETE FROM customers WHERE scenario_id = ?", [scenario.scenario_id])
        self._conn.execute("DELETE FROM vehicles WHERE scenario_id = ?", [scenario.scenario_id])
        for customer in dataset.customers:
            self._conn.execute(
                """
                INSERT INTO customers (
                    scenario_id, customer_id, zone_id, latitude, longitude, demand_totes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    customer.scenario_id,
                    customer.customer_id,
                    customer.zone_id,
                    customer.latitude,
                    customer.longitude,
                    customer.demand_totes,
                ],
            )
        for vehicle in dataset.vehicles:
            self._conn.execute(
                """
                INSERT INTO vehicles (scenario_id, vehicle_id, capacity_totes)
                VALUES (?, ?, ?)
                """,
                [vehicle.scenario_id, vehicle.vehicle_id, vehicle.capacity_totes],
            )

    def get_run(self, run_id: str) -> StoredRun | None:
        row = self._conn.execute(
            "SELECT stored_json FROM planning_runs WHERE run_id = ?",
            [run_id],
        ).fetchone()
        if row is None:
            return None
        return stored_run_from_json(row[0])

    def put_run(self, stored: StoredRun) -> None:
        run = stored.plan.run
        self._conn.execute(
            """
            INSERT OR REPLACE INTO planning_runs (
                run_id, scenario_id, run_type, status, comparison_eligible, created_at, stored_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                run.run_id,
                run.scenario_id,
                run.run_type.value,
                run.status.value,
                run.comparison_eligible,
                run.created_at.isoformat(),
                stored_run_to_json(stored),
            ],
        )
        self._conn.execute("DELETE FROM routes WHERE run_id = ?", [run.run_id])
        self._conn.execute("DELETE FROM route_stops WHERE run_id = ?", [run.run_id])
        self._conn.execute("DELETE FROM constraint_checks WHERE run_id = ?", [run.run_id])
        self._conn.execute("DELETE FROM scenario_kpis WHERE run_id = ?", [run.run_id])
        self._conn.execute("DELETE FROM vehicle_kpis WHERE run_id = ?", [run.run_id])
        self._conn.execute("DELETE FROM assignments WHERE run_id = ?", [run.run_id])
        for route in stored.plan.routes:
            self._conn.execute(
                """
                INSERT INTO routes (
                    run_id, vehicle_id, is_used, assigned_demand_totes,
                    capacity_totes, distance_metres, customer_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    route.run_id,
                    route.vehicle_id,
                    route.is_used,
                    route.assigned_demand_totes,
                    route.capacity_totes,
                    route.distance_metres,
                    route.customer_count,
                ],
            )
        for stop in stored.plan.stops:
            self._conn.execute(
                """
                INSERT INTO route_stops (
                    run_id, vehicle_id, sequence_number, node_id, node_type,
                    demand_totes, load_after_service_totes, leg_distance_metres,
                    cumulative_distance_metres
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    stop.run_id,
                    stop.vehicle_id,
                    stop.sequence_number,
                    stop.node_id,
                    stop.node_type.value,
                    stop.demand_totes,
                    stop.load_after_service_totes,
                    stop.leg_distance_metres,
                    stop.cumulative_distance_metres,
                ],
            )
        for check in stored.checks:
            self._conn.execute(
                """
                INSERT INTO constraint_checks (run_id, code, name, passed, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                [run.run_id, check.code, check.name, check.passed, check.message],
            )
        self._conn.execute(
            "INSERT INTO scenario_kpis (run_id, kpis_json) VALUES (?, ?)",
            [run.run_id, _dumps(stored.scenario_kpis)],
        )
        for item in stored.vehicle_kpis:
            self._conn.execute(
                """
                INSERT INTO vehicle_kpis (
                    run_id, vehicle_id, sequence_json, customer_count, assigned_demand_totes,
                    capacity_totes, remaining_capacity_totes, capacity_utilisation,
                    route_distance_metres, is_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    run.run_id,
                    item.vehicle_id,
                    json.dumps(item.sequence),
                    item.customer_count,
                    item.assigned_demand_totes,
                    item.capacity_totes,
                    item.remaining_capacity_totes,
                    item.capacity_utilisation,
                    item.route_distance_metres,
                    item.is_used,
                ],
            )
        for item in stored.assignments:
            self._conn.execute(
                """
                INSERT INTO assignments (
                    run_id, customer_id, demand_totes, assigned_vehicle, service_count, demand_check
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    run.run_id,
                    item.customer_id,
                    item.demand_totes,
                    item.assigned_vehicle,
                    item.service_count,
                    item.demand_check,
                ],
            )

    def latest_complete_baseline(self, scenario_id: str) -> StoredRun | None:
        row = self._conn.execute(
            """
            SELECT stored_json FROM planning_runs
            WHERE scenario_id = ? AND run_type = ? AND comparison_eligible
            ORDER BY created_at DESC
            LIMIT 1
            """,
            [scenario_id, RunType.baseline.value],
        ).fetchone()
        if row is None:
            return None
        return stored_run_from_json(row[0])

    def close(self) -> None:
        self._conn.close()
