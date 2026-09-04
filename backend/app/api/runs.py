"""Run retrieval, constraint checks, and export."""

from __future__ import annotations

import csv
import io
import zipfile

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.errors import invalid_request, unknown_run
from app.api.serializers import plan_summary
from app.storage.repository import AppRepository

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


def _repo(request: Request) -> AppRepository:
    return request.app.state.repo


@router.get("/{run_id}")
def get_run(run_id: str, request: Request):
    stored = _repo(request).get_run(run_id)
    if stored is None:
        return unknown_run(run_id)
    summary = plan_summary(stored)
    return {
        **summary.model_dump(),
        "kpis": stored.scenario_kpis.model_dump(mode="json"),
        "vehicle_kpis": [item.model_dump(mode="json") for item in stored.vehicle_kpis],
        "assignments": [item.model_dump(mode="json") for item in stored.assignments],
    }


@router.get("/{run_id}/routes")
def get_routes(run_id: str, request: Request):
    stored = _repo(request).get_run(run_id)
    if stored is None:
        return unknown_run(run_id)
    return {
        "run_id": stored.plan.run.run_id,
        "scenario_id": stored.plan.run.scenario_id,
        "status": stored.plan.run.status.value,
        "routes": [route.model_dump(mode="json") for route in stored.plan.routes],
        "stops": [stop.model_dump(mode="json") for stop in stored.plan.stops],
        "vehicle_kpis": [item.model_dump(mode="json") for item in stored.vehicle_kpis],
    }


@router.get("/{run_id}/checks")
def get_checks(run_id: str, request: Request):
    stored = _repo(request).get_run(run_id)
    if stored is None:
        return unknown_run(run_id)
    return {
        "run_id": stored.plan.run.run_id,
        "scenario_id": stored.plan.run.scenario_id,
        "status": stored.plan.run.status.value,
        "checks": [check.model_dump(mode="json") for check in stored.checks],
        "assignments": [item.model_dump(mode="json") for item in stored.assignments],
    }


def _csv_bytes(headers: list[str], rows: list[list[object]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


@router.get("/{run_id}/export")
def export_run(
    run_id: str,
    request: Request,
    format: str = Query(default="json"),
):
    stored = _repo(request).get_run(run_id)
    if stored is None:
        return unknown_run(run_id)
    scenario_id = stored.plan.run.scenario_id
    if format == "json":
        payload = {
            "scenario_id": scenario_id,
            "run_id": run_id,
            "summary": plan_summary(stored).model_dump(),
            "kpis": stored.scenario_kpis.model_dump(mode="json"),
            "vehicle_kpis": [item.model_dump(mode="json") for item in stored.vehicle_kpis],
            "assignments": [item.model_dump(mode="json") for item in stored.assignments],
            "routes": [route.model_dump(mode="json") for route in stored.plan.routes],
            "stops": [stop.model_dump(mode="json") for stop in stored.plan.stops],
            "checks": [check.model_dump(mode="json") for check in stored.checks],
        }
        return JSONResponse(payload)
    if format != "csv":
        return invalid_request("export format must be json or csv")

    assignment_rows = [
        [
            scenario_id,
            run_id,
            item.customer_id,
            item.demand_totes,
            item.assigned_vehicle or "",
            item.service_count,
        ]
        for item in stored.assignments
    ]
    stop_rows = [
        [
            scenario_id,
            run_id,
            stop.vehicle_id,
            stop.sequence_number,
            stop.node_id,
            stop.node_type.value,
            stop.demand_totes,
            stop.load_after_service_totes,
            stop.leg_distance_metres,
            stop.cumulative_distance_metres,
        ]
        for stop in stored.plan.stops
    ]
    vehicle_rows = [
        [
            scenario_id,
            run_id,
            item.vehicle_id,
            item.customer_count,
            item.assigned_demand_totes,
            item.capacity_totes,
            item.remaining_capacity_totes,
            item.route_distance_metres,
            item.is_used,
        ]
        for item in stored.vehicle_kpis
    ]
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(
            "assignments.csv",
            _csv_bytes(
                [
                    "scenario_id",
                    "run_id",
                    "customer_id",
                    "demand_totes",
                    "assigned_vehicle",
                    "service_count",
                ],
                assignment_rows,
            ),
        )
        zip_file.writestr(
            "stops.csv",
            _csv_bytes(
                [
                    "scenario_id",
                    "run_id",
                    "vehicle_id",
                    "sequence_number",
                    "node_id",
                    "node_type",
                    "demand_totes",
                    "load_after_service_totes",
                    "leg_distance_metres",
                    "cumulative_distance_metres",
                ],
                stop_rows,
            ),
        )
        zip_file.writestr(
            "vehicles.csv",
            _csv_bytes(
                [
                    "scenario_id",
                    "run_id",
                    "vehicle_id",
                    "customer_count",
                    "assigned_demand_totes",
                    "capacity_totes",
                    "remaining_capacity_totes",
                    "route_distance_metres",
                    "is_used",
                ],
                vehicle_rows,
            ),
        )
    archive.seek(0)
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{run_id}.zip"'},
    )
