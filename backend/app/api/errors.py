"""HTTP error bodies using the locked API contract."""

from __future__ import annotations

from fastapi.responses import JSONResponse

from app.core.domain import RunStatus
from app.core.validation import CheckResult, PrecheckResult
from app.models.responses import ErrorBody

DOMAIN_HTTP = {
    RunStatus.feasible: 200,
    RunStatus.infeasible: 200,
    RunStatus.heuristic_incomplete: 200,
    RunStatus.no_solution_found: 200,
    RunStatus.invalid: 400,
    RunStatus.error: 500,
}


def checks_payload(checks: list[CheckResult]) -> list[dict[str, object]]:
    return [check.model_dump() for check in checks]


def error_response(
    *,
    http_status: int,
    status: str,
    code: str,
    message: str,
    checks: list[CheckResult] | None = None,
) -> JSONResponse:
    body = ErrorBody(
        status=status,
        code=code,
        message=message,
        checks=checks_payload(checks or []),
    )
    return JSONResponse(status_code=http_status, content=body.model_dump())


def unknown_scenario(scenario_id: str) -> JSONResponse:
    return error_response(
        http_status=404,
        status="invalid",
        code="UNKNOWN_SCENARIO",
        message=f"Scenario '{scenario_id}' was not found.",
    )


def unknown_run(run_id: str) -> JSONResponse:
    return error_response(
        http_status=404,
        status="invalid",
        code="UNKNOWN_RUN",
        message=f"Run '{run_id}' was not found.",
    )


def invalid_request(message: str, checks: list[CheckResult] | None = None) -> JSONResponse:
    return error_response(
        http_status=400,
        status="invalid",
        code="INVALID_REQUEST",
        message=message,
        checks=checks,
    )


def invalid_precheck(precheck: PrecheckResult) -> JSONResponse:
    return error_response(
        http_status=400,
        status="invalid",
        code="INVALID_SCENARIO",
        message="Data integrity failed (Check 4).",
        checks=precheck.checks,
    )
