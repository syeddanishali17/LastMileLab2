"""Display-side estimates: continuum approximation, shift timeline, search convergence."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import components
import continuum
import insights
from app.main import create_app
from app.storage.duckdb_repo import DuckDBRepository


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(repo=DuckDBRepository(":memory:")))


@pytest.fixture(scope="module")
def vienna(client: TestClient) -> dict:
    return client.get("/api/v1/scenarios/VIENNA_STANDARD_24").json()


def test_continuum_estimate_reconstructs_vienna_inputs(vienna: dict) -> None:
    estimate = continuum.estimate(vienna)
    assert estimate is not None
    assert estimate.customers == 24
    assert estimate.routes == 4  # ceil(108 totes / 30)
    # The synthetic matrix is haversine x 1.25, so the measured circuity recovers it.
    assert estimate.circuity == pytest.approx(1.25, abs=0.01)
    assert estimate.k == continuum.DAGANZO_K
    assert estimate.total_km == pytest.approx(estimate.linehaul_km + estimate.local_km)
    # Same order of magnitude as the published plans (97.2 km OR-Tools, 122.4 km baseline).
    assert 80 < estimate.total_km < 125


def test_continuum_estimate_scales_with_service_area(client: TestClient, vienna: dict) -> None:
    wide = client.get("/api/v1/scenarios/VIENNA_WIDE_24").json()
    assert continuum.estimate(wide).area_km2 > continuum.estimate(vienna).area_km2
    assert continuum.estimate(wide).total_km > continuum.estimate(vienna).total_km


def test_continuum_estimate_needs_coordinates() -> None:
    assert continuum.estimate(None) is None
    assert continuum.estimate({"scenario": {"has_geographic_coordinates": False}}) is None
    assert continuum.convex_hull_area_km2([(48.2, 16.3), (48.2, 16.3)]) == 0.0


def test_gap_is_signed_against_estimate() -> None:
    assert continuum.gap_pct(110, 100) == pytest.approx(10)
    assert continuum.gap_pct(90, 100) == pytest.approx(-10)


def _routes() -> dict:
    def stop(seq: int, node: str, kind: str, leg: int, demand: int = 0) -> dict:
        return {
            "vehicle_id": "V01",
            "sequence_number": seq,
            "node_id": node,
            "node_type": kind,
            "leg_distance_metres": leg,
            "demand_totes": demand,
        }

    return {
        "stops": [
            stop(0, "DEPOT_01", "depot", 0),
            stop(1, "C001", "customer", 12500, 5),
            stop(2, "DEPOT_01", "depot", 12500),
            {**stop(0, "DEPOT_01", "depot", 0), "vehicle_id": "V02"},
            {**stop(1, "DEPOT_01", "depot", 0), "vehicle_id": "V02"},
        ]
    }


def test_shift_summary_lays_routes_on_the_clock() -> None:
    summary = insights.shift_summary(_routes())
    kinds = [segment.kind for segment in summary.segments]
    assert kinds == ["drive", "service", "drive"]
    assert {segment.vehicle_id for segment in summary.segments} == {"V01"}  # unused van skipped
    drive = insights.drive_minutes(12500)
    assert drive == pytest.approx(30.0)  # 12.5 km at 25 km/h
    expected_return = insights.DEPARTURE_MINUTE + 2 * drive + insights.SERVICE_MINUTES_PER_STOP
    assert summary.return_minute == pytest.approx(expected_return)
    assert insights.clock(summary.return_minute) == "09:05"
    assert summary.co2e_kg == pytest.approx(25 * insights.CO2E_KG_PER_KM)
    assert insights.timeline_figure(summary) is not None
    assert insights.hours_label(1.0) == "1 h 00 m"
    assert insights.hours_label(5.89) == "5 h 53 m"


def test_convergence_figure_traces_best_so_far() -> None:
    assert insights.convergence_figure([], baseline_m=1000, time_limit_s=5) is None
    trace = [
        {"elapsed_seconds": 0.0, "objective_distance_metres": 122394},
        {"elapsed_seconds": 0.04, "objective_distance_metres": 97193},
    ]
    figure = insights.convergence_figure(trace, baseline_m=122394, time_limit_s=5)
    line = figure.data[0]
    assert line.line.shape == "hv"
    assert line.x[0] == pytest.approx(0.1)  # t=0 is clamped for the log axis
    assert line.x[-1] == pytest.approx(5000)  # flat to the end of the search budget
    assert line.y[-1] == pytest.approx(97.193)
    assert figure.layout.xaxis.type == "log"


def test_dispatch_console_marks_stage_progress() -> None:
    running = components.dispatch_console_html(2, seconds=5, scenario_name="Vienna Standard")
    assert "is-running" in running
    assert running.count('class="is-done"') == 2
    assert running.count('class="is-active"') == 1
    assert "--lm-budget:5s" in running  # countdown only while OR-Tools searches
    done = components.dispatch_console_html(
        len(components.CONSOLE_STAGES), seconds=5, scenario_name="Vienna Standard"
    )
    assert "is-running" not in done and "lm-console-budget" not in done
    failed = components.dispatch_console_html(
        1, seconds=5, scenario_name="Vienna Standard", error=True
    )
    assert 'class="is-error"' in failed and "is-running" not in failed


def test_workflow_stepper_marks_current_step() -> None:
    markup = components.workflow_stepper_html(2)
    assert markup.count('class="is-done"') == 1
    assert 'aria-current="step"' in markup


def test_continuum_check_places_estimate_marker() -> None:
    markup = components.continuum_check_html(
        100.0, [("Baseline", 125.0, "is-baseline"), ("Optimized", 98.0, "is-optimised")]
    )
    assert "+25.0%" in markup
    assert "−2.0%" in markup
    assert markup.count("<i style=") == 2
