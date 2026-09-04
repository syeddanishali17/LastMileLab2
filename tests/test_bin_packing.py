"""Independent unsplit-packing proof for INFEASIBLE_BIN_PACKING.

This is not a pre-check. Validation must still report `passed` for Checks 1 and 2.
The optimiser mapping to `no_solution_found` belongs to Phase 4.
"""

from __future__ import annotations

from app.core.domain import PrecheckStatus, RunStatus
from app.core.loader import load_and_precheck
from app.core.optimizer import plan_optimise
from app.core.validation import check_by_code


def exists_feasible_unsplit_assignment(
    demands: list[int],
    vehicle_count: int,
    capacity: int,
) -> bool:
    loads = [0] * vehicle_count

    def assign(index: int) -> bool:
        if index == len(demands):
            return True
        for vehicle in range(vehicle_count):
            if loads[vehicle] + demands[index] <= capacity:
                loads[vehicle] += demands[index]
                if assign(index + 1):
                    return True
                loads[vehicle] -= demands[index]
        return False

    return assign(0)


def test_bin_packing_fixture_has_no_feasible_unsplit_assignment() -> None:
    result, dataset = load_and_precheck("INFEASIBLE_BIN_PACKING")
    assert result.status is PrecheckStatus.passed
    assert check_by_code(result, "CHECK_1").passed is True
    assert check_by_code(result, "CHECK_2").passed is True
    assert dataset is not None
    demands = [customer.demand_totes for customer in dataset.customers]
    assert exists_feasible_unsplit_assignment(demands, vehicle_count=2, capacity=10) is False


def test_learning_6_does_have_a_feasible_unsplit_assignment() -> None:
    _, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    demands = [customer.demand_totes for customer in dataset.customers]
    assert exists_feasible_unsplit_assignment(demands, vehicle_count=2, capacity=10) is True


def test_bin_packing_optimiser_returns_no_solution_found() -> None:
    plan = plan_optimise("INFEASIBLE_BIN_PACKING", time_limit_seconds=1)
    assert plan.run.status is RunStatus.no_solution_found
    assert plan.run.status is not RunStatus.infeasible
    assert plan.run.comparison_eligible is False
