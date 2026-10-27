"""Feasible-solution invariants for reconstructed OR-Tools routes."""

from __future__ import annotations

from ortools.constraint_solver import pywrapcp

from app.core.domain import RunStatus, SolverTermination
from app.core.invariants import feasible_invariant_errors
from app.core.loader import load_and_precheck
from app.core.optimizer import map_ortools_status, plan_optimise


def test_vienna_optimiser_satisfies_invariants() -> None:
    _, dataset = load_and_precheck("VIENNA_STANDARD_24")
    assert dataset is not None
    plan = plan_optimise("VIENNA_STANDARD_24", time_limit_seconds=5)
    assert plan.run.status is RunStatus.feasible
    assert plan.customers_served == 24
    assert plan.demand_served_totes == 108
    assert feasible_invariant_errors(dataset, plan) == []
    assert plan.run.objective_distance_metres is not None
    assert plan.run.objective_distance_metres > 0


def test_search_trace_records_strict_improvements_ending_at_objective() -> None:
    plan = plan_optimise("VIENNA_STANDARD_24", time_limit_seconds=1)
    trace = plan.run.search_trace
    assert trace, "the optimiser must log at least its first solution"
    objectives = [point.objective_distance_metres for point in trace]
    elapsed = [point.elapsed_seconds for point in trace]
    assert objectives == sorted(objectives, reverse=True)
    assert len(set(objectives)) == len(objectives)
    assert elapsed == sorted(elapsed)
    assert objectives[-1] == plan.run.objective_distance_metres


def test_timeout_is_not_mapped_to_infeasible() -> None:
    status, termination = map_ortools_status(
        pywrapcp.RoutingModel.ROUTING_FAIL_TIMEOUT,
        complete=False,
    )
    assert status is RunStatus.no_solution_found
    assert termination is SolverTermination.timeout
    assert status is not RunStatus.infeasible


def test_ortools_infeasible_status_is_no_solution_found() -> None:
    status, termination = map_ortools_status(
        pywrapcp.RoutingModel.ROUTING_INFEASIBLE,
        complete=False,
    )
    assert status is RunStatus.no_solution_found
    assert termination is SolverTermination.no_first_solution
    assert status is not RunStatus.infeasible
