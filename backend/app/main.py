"""FastAPI entrypoint for LastMile Lab."""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.errors import error_response, invalid_request
from app.api.planning import router as planning_router
from app.api.runs import router as runs_router
from app.api.scenarios import router as scenarios_router
from app.logging_config import configure_logging, get_logger
from app.models.responses import HealthResponse
from app.settings import get_settings
from app.storage.duckdb_repo import DuckDBRepository
from app.storage.repository import AppRepository

logger = get_logger("app")


def create_app(repo: AppRepository | None = None) -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    application = FastAPI(
        title="LastMile Lab: ViennaCart CVRP Dispatch Planner",
        version="0.1.0",
        description=(
            "Static morning CVRP dispatch planner for the fictional ViennaCart operator. "
            "LastMile Lab is a fictional portfolio case study. All depots, customers, "
            "order demands, routes, distances, and operating assumptions are synthetic. "
            "The application does not use proprietary customer data or live Vienna "
            "traffic information."
        ),
    )
    application.state.repo = repo or DuckDBRepository(settings.duckdb_path)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    application.include_router(scenarios_router)
    application.include_router(planning_router)
    application.include_router(runs_router)

    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        logger.info(
            "http_request",
            extra={
                "request_id": request_id,
                "http_method": request.method,
                "http_path": request.url.path,
                "http_status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        response.headers["x-request-id"] = request_id
        return response

    @application.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return invalid_request(str(exc.errors()))

    @application.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_error",
            extra={"http_path": request.url.path, "error_type": type(exc).__name__},
        )
        return error_response(
            http_status=500,
            status="error",
            code="INTERNAL_ERROR",
            message="Unexpected runtime failure.",
        )

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="viennacart-cvrp")

    logger.info("app_started", extra={"log_level": settings.log_level})
    return application


app = create_app()
