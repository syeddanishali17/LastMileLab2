"""Validation tests for Checks 1–4. Generator tests wait until scenario generation exists."""

from __future__ import annotations

import copy

from app.core.domain import PrecheckStatus
from app.core.loader import load_and_precheck, load_raw_scenario
from app.core.validation import check_by_code, evaluate_prechecks


def _learning_raw():
    return load_raw_scenario("LEARNING_6")


def test_duplicate_customer_id_rejected() -> None:
    raw = _learning_raw()
    raw.customers.append(copy.deepcopy(raw.customers[0]))
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid
    assert check_by_code(result, "CHECK_4").passed is False


def test_zero_demand_rejected() -> None:
    raw = _learning_raw()
    raw.customers[0]["demand_totes"] = 0
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid


def test_negative_demand_rejected() -> None:
    raw = _learning_raw()
    raw.customers[0]["demand_totes"] = -1
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid


def test_non_integer_tote_demand_rejected() -> None:
    raw = _learning_raw()
    raw.customers[0]["demand_totes"] = "3.5"
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid


def test_zero_vehicle_capacity_rejected() -> None:
    raw = _learning_raw()
    raw.vehicles[0]["capacity_totes"] = 0
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid


def test_missing_depot_rejected() -> None:
    raw = _learning_raw()
    raw.depot = None
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid
    assert "depot" in check_by_code(result, "CHECK_4").message


def test_invalid_coordinates_rejected() -> None:
    raw = load_raw_scenario("VIENNA_STANDARD_24")
    raw.customers[0]["latitude"] = 91.0
    result = evaluate_prechecks(raw)
    assert result.status is PrecheckStatus.invalid
    assert "WGS84" in check_by_code(result, "CHECK_4").message


def test_infeasible_single_oversize_is_infeasible() -> None:
    result, dataset = load_and_precheck("INFEASIBLE_SINGLE_OVERSIZE")
    assert result.status is PrecheckStatus.infeasible
    assert check_by_code(result, "CHECK_1").passed is False
    assert check_by_code(result, "CHECK_2").passed is True
    assert dataset is not None


def test_infeasible_fleet_overflow_is_infeasible() -> None:
    result, dataset = load_and_precheck("INFEASIBLE_FLEET_OVERFLOW")
    assert result.status is PrecheckStatus.infeasible
    assert check_by_code(result, "CHECK_1").passed is True
    assert check_by_code(result, "CHECK_2").passed is False
    assert dataset is not None


def test_infeasible_bin_packing_passes_checks_1_and_2() -> None:
    result, dataset = load_and_precheck("INFEASIBLE_BIN_PACKING")
    assert result.status is PrecheckStatus.passed
    assert check_by_code(result, "CHECK_1").passed is True
    assert check_by_code(result, "CHECK_2").passed is True
    assert check_by_code(result, "CHECK_3").hard_fail is False
    assert result.minimum_vehicles_by_demand == 2
    assert dataset is not None
    assert sum(customer.demand_totes for customer in dataset.customers) == 18


def test_learning_6_prechecks_pass_and_demand_is_20() -> None:
    result, dataset = load_and_precheck("LEARNING_6")
    assert result.status is PrecheckStatus.passed
    assert dataset is not None
    assert sum(customer.demand_totes for customer in dataset.customers) == 20
    assert sum(vehicle.capacity_totes for vehicle in dataset.vehicles) == 20
    assert result.minimum_vehicles_by_demand == 2
    assert check_by_code(result, "CHECK_3").passed is True


def test_generator_rejects_customer_count_above_50() -> None:
    from decimal import Decimal

    from app.core.generator import validate_generator_request

    error = validate_generator_request(
        random_seed=1,
        customer_count=51,
        vehicle_count=4,
        vehicle_capacity_totes=30,
        detour_factor=Decimal("1.25"),
        geographic_zone_weights={"Z1": 0.25, "Z2": 0.25, "Z3": 0.25, "Z4": 0.25},
    )
    assert error is not None


def test_generator_rejects_vehicle_count_above_10() -> None:
    from decimal import Decimal

    from app.core.generator import validate_generator_request

    error = validate_generator_request(
        random_seed=1,
        customer_count=10,
        vehicle_count=11,
        vehicle_capacity_totes=30,
        detour_factor=Decimal("1.25"),
        geographic_zone_weights={"Z1": 0.25, "Z2": 0.25, "Z3": 0.25, "Z4": 0.25},
    )
    assert error is not None


def test_generator_rejects_detour_factor_outside_range() -> None:
    from decimal import Decimal

    from app.core.generator import validate_generator_request

    weights = {"Z1": 0.25, "Z2": 0.25, "Z3": 0.25, "Z4": 0.25}
    assert (
        validate_generator_request(
            random_seed=1,
            customer_count=10,
            vehicle_count=2,
            vehicle_capacity_totes=30,
            detour_factor=Decimal("0.99"),
            geographic_zone_weights=weights,
        )
        is not None
    )
    assert (
        validate_generator_request(
            random_seed=1,
            customer_count=10,
            vehicle_count=2,
            vehicle_capacity_totes=30,
            detour_factor=Decimal("2.01"),
            geographic_zone_weights=weights,
        )
        is not None
    )


def test_vienna_standard_24_prechecks_pass() -> None:
    result, dataset = load_and_precheck("VIENNA_STANDARD_24")
    assert result.status is PrecheckStatus.passed
    assert dataset is not None
    assert len(dataset.customers) == 24
    assert sum(customer.demand_totes for customer in dataset.customers) == 108
    zones = {"Z1": 0, "Z2": 0, "Z3": 0, "Z4": 0}
    for customer in dataset.customers:
        assert customer.zone_id in zones
        zones[customer.zone_id] += customer.demand_totes
    assert zones == {"Z1": 35, "Z2": 29, "Z3": 24, "Z4": 20}
    assert result.minimum_vehicles_by_demand == 4
