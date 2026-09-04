"""Load Phase 0 fixture files into domain objects."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from app.core.distance_matrix import build_geographic_matrix
from app.core.domain import (
    Customer,
    Depot,
    DistanceMatrix,
    DistanceSource,
    DistanceUnit,
    PrecheckStatus,
    Scenario,
    ScenarioDataset,
    Vehicle,
)
from app.core.validation import PrecheckResult, RawScenarioInput, evaluate_prechecks

FIXTURE_CREATED_AT = datetime(2026, 9, 3, tzinfo=UTC)
DEFAULT_DETOUR = Decimal("1.25")

CSV_SCENARIOS = {
    "LEARNING_6": {
        "scenario_name": "Learning Lab 6",
        "random_seed": None,
        "distance_source": DistanceSource.fixed_matrix,
        "has_geographic_coordinates": False,
        "detour_factor": DEFAULT_DETOUR,
        "customers_file": "learning_6_customers.csv",
        "vehicles_file": "learning_6_vehicles.csv",
        "depot_file": "learning_6_depot.csv",
        "matrix_file": "learning_6_distance_matrix.csv",
    },
    "VIENNA_STANDARD_24": {
        "scenario_name": "Vienna Standard Dispatch",
        "random_seed": 42,
        "distance_source": DistanceSource.haversine_detour,
        "has_geographic_coordinates": True,
        "detour_factor": DEFAULT_DETOUR,
        "customers_file": "vienna_standard_24_customers.csv",
        "vehicles_file": "vienna_standard_24_vehicles.csv",
        "depot_file": "vienna_standard_24_depot.csv",
        "matrix_file": None,
    },
}

YAML_SCENARIOS = {
    "INFEASIBLE_SINGLE_OVERSIZE": "infeasible_single_oversize.yaml",
    "INFEASIBLE_FLEET_OVERFLOW": "infeasible_fleet_overflow.yaml",
    "INFEASIBLE_BIN_PACKING": "infeasible_bin_packing.yaml",
}


def fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "fixtures"


def _optional_float(value: str | None) -> float | None:
    if value is None:
        return None
    stripped = str(value).strip()
    if stripped == "":
        return None
    return float(stripped)


def _optional_str(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_csv_matrix(path: Path) -> DistanceMatrix:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        node_ids = header[1:]
        distances: list[list[int]] = []
        row_ids: list[str] = []
        for row in reader:
            row_ids.append(row[0])
            distances.append([int(cell) for cell in row[1:]])
    if row_ids != node_ids:
        raise ValueError(f"distance matrix row labels do not match columns in {path.name}")
    return DistanceMatrix(node_ids=node_ids, distances_metres=distances)


def _yaml_matrix(payload: dict[str, Any]) -> DistanceMatrix:
    block = payload["distance_matrix_metres"]
    return DistanceMatrix(node_ids=list(block["nodes"]), distances_metres=list(block["rows"]))


def _csv_raw(scenario_id: str) -> RawScenarioInput:
    spec = CSV_SCENARIOS[scenario_id]
    directory = fixtures_dir()
    depot_row = _read_csv_rows(directory / spec["depot_file"])[0]
    customer_rows = _read_csv_rows(directory / spec["customers_file"])
    vehicle_rows = _read_csv_rows(directory / spec["vehicles_file"])
    matrix = _load_csv_matrix(directory / spec["matrix_file"]) if spec["matrix_file"] else None
    customers = [
        {
            "customer_id": row["customer_id"],
            "demand_totes": row["demand_totes"],
            "zone_id": _optional_str(row.get("zone_id")),
            "latitude": _optional_float(row.get("latitude")),
            "longitude": _optional_float(row.get("longitude")),
        }
        for row in customer_rows
    ]
    vehicles = [
        {"vehicle_id": row["vehicle_id"], "capacity_totes": row["capacity_totes"]}
        for row in vehicle_rows
    ]
    depot = {
        "depot_id": depot_row["depot_id"],
        "name": depot_row.get("name") or depot_row["depot_id"],
        "latitude": _optional_float(depot_row.get("latitude")),
        "longitude": _optional_float(depot_row.get("longitude")),
    }
    return RawScenarioInput(
        scenario_id=scenario_id,
        has_geographic_coordinates=bool(spec["has_geographic_coordinates"]),
        depot=depot,
        customers=customers,
        vehicles=vehicles,
        distance_matrix=matrix,
    )


def _yaml_raw(scenario_id: str) -> RawScenarioInput:
    path = fixtures_dir() / YAML_SCENARIOS[scenario_id]
    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return RawScenarioInput(
        scenario_id=payload["scenario_id"],
        has_geographic_coordinates=bool(payload["has_geographic_coordinates"]),
        depot={
            "depot_id": payload["depot_id"],
            "name": payload.get("depot_name") or payload["depot_id"],
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
        },
        customers=list(payload["customers"]),
        vehicles=list(payload["vehicles"]),
        distance_matrix=_yaml_matrix(payload),
    )


def load_raw_scenario(scenario_id: str) -> RawScenarioInput:
    if scenario_id in CSV_SCENARIOS:
        return _csv_raw(scenario_id)
    if scenario_id in YAML_SCENARIOS:
        return _yaml_raw(scenario_id)
    raise KeyError(f"unknown scenario_id: {scenario_id}")


def _to_dataset(raw: RawScenarioInput) -> ScenarioDataset:
    if raw.scenario_id is None or raw.depot is None:
        raise ValueError("cannot build a dataset from invalid raw input")
    meta = CSV_SCENARIOS.get(raw.scenario_id)
    if meta is None:
        distance_source = DistanceSource.fixed_matrix
        scenario_name = raw.scenario_id
        random_seed = None
        detour_factor = DEFAULT_DETOUR
    else:
        distance_source = meta["distance_source"]
        scenario_name = str(meta["scenario_name"])
        random_seed = meta["random_seed"]
        detour_factor = Decimal(str(meta["detour_factor"]))

    depot = Depot(
        depot_id=str(raw.depot["depot_id"]),
        scenario_id=raw.scenario_id,
        name=str(raw.depot["name"]),
        latitude=raw.depot.get("latitude"),
        longitude=raw.depot.get("longitude"),
    )
    customers = [
        Customer(
            customer_id=str(row["customer_id"]),
            scenario_id=raw.scenario_id,
            zone_id=row.get("zone_id"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            demand_totes=int(row["demand_totes"]),
        )
        for row in raw.customers
    ]
    vehicles = [
        Vehicle(
            vehicle_id=str(row["vehicle_id"]),
            scenario_id=raw.scenario_id,
            capacity_totes=int(row["capacity_totes"]),
        )
        for row in raw.vehicles
    ]
    if distance_source is DistanceSource.haversine_detour:
        matrix = build_geographic_matrix(depot, customers, detour_factor)
    elif raw.distance_matrix is None:
        raise ValueError(f"{raw.scenario_id} is missing a fixed distance matrix")
    else:
        matrix = raw.distance_matrix

    scenario = Scenario(
        scenario_id=raw.scenario_id,
        scenario_name=scenario_name,
        random_seed=random_seed,
        depot_id=depot.depot_id,
        customer_count=len(customers),
        vehicle_count=len(vehicles),
        vehicle_capacity_totes=vehicles[0].capacity_totes,
        detour_factor=detour_factor,
        distance_unit=DistanceUnit.metres,
        distance_source=distance_source,
        has_geographic_coordinates=raw.has_geographic_coordinates,
        created_at=FIXTURE_CREATED_AT,
        is_synthetic=True,
    )
    return ScenarioDataset(
        scenario=scenario,
        depot=depot,
        customers=customers,
        vehicles=vehicles,
        distance_matrix=matrix,
    )


def _attach_geographic_matrix(raw: RawScenarioInput) -> None:
    if raw.scenario_id not in CSV_SCENARIOS:
        return
    spec = CSV_SCENARIOS[raw.scenario_id]
    if spec["distance_source"] is not DistanceSource.haversine_detour or raw.depot is None:
        return
    depot = Depot(
        depot_id=str(raw.depot["depot_id"]),
        scenario_id=raw.scenario_id,
        name=str(raw.depot["name"]),
        latitude=raw.depot.get("latitude"),
        longitude=raw.depot.get("longitude"),
    )
    customers = [
        Customer(
            customer_id=str(row["customer_id"]),
            scenario_id=raw.scenario_id,
            zone_id=row.get("zone_id"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            demand_totes=int(row["demand_totes"]),
        )
        for row in raw.customers
    ]
    raw.distance_matrix = build_geographic_matrix(
        depot,
        customers,
        Decimal(str(spec["detour_factor"])),
    )


def load_and_precheck(scenario_id: str) -> tuple[PrecheckResult, ScenarioDataset | None]:
    raw = load_raw_scenario(scenario_id)
    _attach_geographic_matrix(raw)
    result = evaluate_prechecks(raw)
    if result.status is PrecheckStatus.invalid:
        return result, None
    return result, _to_dataset(raw)


def known_fixture_ids() -> list[str]:
    return [*CSV_SCENARIOS.keys(), *YAML_SCENARIOS.keys()]
