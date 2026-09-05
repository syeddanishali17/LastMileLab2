"""Scenario list, retrieve, generate, and validate endpoints."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Request

from app.api.errors import invalid_precheck, invalid_request, unknown_scenario
from app.core.generator import generate_scenario
from app.core.kpis import metres_to_km
from app.core.loader import load_and_precheck
from app.core.validation import precheck_dataset
from app.models.requests import GenerateRequest, ScenarioIdRequest
from app.storage.repository import AppRepository

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])


def _repo(request: Request) -> AppRepository:
    return request.app.state.repo


@router.get("")
def list_scenarios(request: Request) -> dict[str, object]:
    repo = _repo(request)
    items = []
    for scenario_id in repo.list_scenario_ids():
        dataset = repo.get_dataset(scenario_id)
        if dataset is None:
            continue
        items.append(
            {
                "scenario_id": dataset.scenario.scenario_id,
                "scenario_name": dataset.scenario.scenario_name,
                "customer_count": dataset.scenario.customer_count,
                "vehicle_count": dataset.scenario.vehicle_count,
                "vehicle_capacity_totes": dataset.scenario.vehicle_capacity_totes,
                "has_geographic_coordinates": dataset.scenario.has_geographic_coordinates,
                "is_synthetic": dataset.scenario.is_synthetic,
            }
        )
    return {"scenarios": items}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str, request: Request):
    dataset = _repo(request).get_dataset(scenario_id)
    if dataset is None:
        return unknown_scenario(scenario_id)
    precheck = precheck_dataset(dataset)
    return {
        "scenario": dataset.scenario.model_dump(mode="json"),
        "depot": dataset.depot.model_dump(mode="json"),
        "customers": [customer.model_dump(mode="json") for customer in dataset.customers],
        "vehicles": [vehicle.model_dump(mode="json") for vehicle in dataset.vehicles],
        "distance_matrix": dataset.distance_matrix.model_dump(mode="json"),
        "precheck": precheck.model_dump(mode="json"),
        "synthetic_distance_label": (
            "Estimated synthetic distance. This is not a live road or traffic measurement."
        ),
    }


@router.post("/generate")
def generate(payload: GenerateRequest, request: Request):
    weights = None
    if payload.geographic_zone_weights is not None:
        weights = payload.geographic_zone_weights.model_dump()
    error, dataset = generate_scenario(
        random_seed=payload.random_seed,
        customer_count=payload.customer_count,
        vehicle_count=payload.vehicle_count,
        vehicle_capacity_totes=payload.vehicle_capacity_totes,
        detour_factor=Decimal(str(payload.detour_factor)),
        geographic_zone_weights=weights,
        customer_demands=payload.customer_demands,
    )
    if error or dataset is None:
        return invalid_request(error or "Scenario generation request is invalid.")
    _repo(request).put_dataset(dataset)
    precheck = precheck_dataset(dataset)
    return {
        "scenario_id": dataset.scenario.scenario_id,
        "status": precheck.status.value,
        "scenario": dataset.scenario.model_dump(mode="json"),
        "precheck": precheck.model_dump(mode="json"),
        "total_demand_totes": sum(customer.demand_totes for customer in dataset.customers),
        "total_distance_cell_km": metres_to_km(
            dataset.distance_matrix.distances_metres[0][1]
        )
        if len(dataset.distance_matrix.node_ids) > 1
        else 0,
    }


@router.post("/validate")
def validate(payload: ScenarioIdRequest, request: Request):
    repo = _repo(request)
    dataset = repo.get_dataset(payload.scenario_id)
    if dataset is None:
        if payload.scenario_id in {
            "LEARNING_6",
            "VIENNA_STANDARD_24",
            "INFEASIBLE_SINGLE_OVERSIZE",
            "INFEASIBLE_FLEET_OVERFLOW",
            "INFEASIBLE_BIN_PACKING",
        }:
            precheck, loaded = load_and_precheck(payload.scenario_id)
            if loaded is not None:
                repo.put_dataset(loaded)
                dataset = loaded
            elif precheck.status.value == "invalid":
                return invalid_precheck(precheck)
            else:
                return unknown_scenario(payload.scenario_id)
        else:
            return unknown_scenario(payload.scenario_id)
    precheck = precheck_dataset(dataset)
    if precheck.status.value == "invalid":
        return invalid_precheck(precheck)
    return {
        "scenario_id": payload.scenario_id,
        "status": precheck.status.value,
        "checks": [check.model_dump() for check in precheck.checks],
        "minimum_vehicles_by_demand": precheck.minimum_vehicles_by_demand,
    }
