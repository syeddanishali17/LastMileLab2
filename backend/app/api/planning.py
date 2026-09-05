"""Baseline and optimisation planning endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api.errors import DOMAIN_HTTP, error_response, invalid_request, unknown_scenario
from app.api.serializers import plan_summary
from app.core.baseline import plan_baseline
from app.core.optimizer import SUPPORTED_TIME_LIMITS, plan_optimise
from app.core.pipeline import build_stored_run
from app.logging_config import get_logger
from app.models.requests import OptimiseRequest, ScenarioIdRequest
from app.storage.repository import AppRepository

router = APIRouter(prefix="/api/v1/plans", tags=["plans"])
logger = get_logger(__name__)


def _repo(request: Request) -> AppRepository:
    return request.app.state.repo


@router.post("/baseline")
def run_baseline(payload: ScenarioIdRequest, request: Request):
    repo = _repo(request)
    dataset = repo.get_dataset(payload.scenario_id)
    if dataset is None:
        return unknown_scenario(payload.scenario_id)
    plan = plan_baseline(payload.scenario_id, dataset=dataset)
    if plan.run.status.value == "invalid":
        return error_response(
            http_status=400,
            status="invalid",
            code="INVALID_SCENARIO",
            message=plan.message or "Baseline was not run.",
        )
    stored = build_stored_run(dataset, plan)
    repo.put_run(stored)
    logger.info(
        "planning_complete",
        extra={
            "scenario_id": payload.scenario_id,
            "run_type": "baseline",
            "run_status": plan.run.status.value,
            "run_id": plan.run.run_id,
        },
    )
    http_status = DOMAIN_HTTP.get(plan.run.status, 200)
    summary = plan_summary(stored)
    if http_status != 200:
        return error_response(
            http_status=http_status,
            status=plan.run.status.value,
            code=plan.run.status.value.upper(),
            message=plan.message or "Planning failed.",
        )
    return summary


@router.post("/optimise")
def run_optimise(payload: OptimiseRequest, request: Request):
    if payload.solver_time_limit_seconds not in SUPPORTED_TIME_LIMITS:
        return invalid_request("solver_time_limit_seconds must be 1, 5, or 10.")
    repo = _repo(request)
    dataset = repo.get_dataset(payload.scenario_id)
    if dataset is None:
        return unknown_scenario(payload.scenario_id)
    plan = plan_optimise(
        payload.scenario_id,
        time_limit_seconds=payload.solver_time_limit_seconds,
        dataset=dataset,
    )
    if plan.run.status.value == "invalid":
        return error_response(
            http_status=400,
            status="invalid",
            code="INVALID_SCENARIO",
            message=plan.message or "Solver was not run.",
        )
    if plan.run.status.value == "error":
        return error_response(
            http_status=500,
            status="error",
            code="SOLVER_ERROR",
            message=plan.message or "Unexpected runtime failure.",
        )
    baseline = repo.latest_complete_baseline(payload.scenario_id)
    stored = build_stored_run(
        dataset,
        plan,
        baseline_plan=None if baseline is None else baseline.plan,
    )
    repo.put_run(stored)
    logger.info(
        "planning_complete",
        extra={
            "scenario_id": payload.scenario_id,
            "run_type": "optimised",
            "run_status": plan.run.status.value,
            "run_id": plan.run.run_id,
            "solver_time_limit_seconds": payload.solver_time_limit_seconds,
        },
    )
    return plan_summary(stored)
