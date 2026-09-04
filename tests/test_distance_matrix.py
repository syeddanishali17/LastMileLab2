"""Distance-matrix construction tests."""

from __future__ import annotations

from decimal import Decimal

from app.core.distance_matrix import (
    EARTH_RADIUS_M,
    build_geographic_matrix,
    matrix_lookup,
    metres_to_display_km,
    round_half_up,
)
from app.core.loader import load_and_precheck


def test_earth_radius_is_6371000() -> None:
    assert EARTH_RADIUS_M == 6371000


def test_round_half_up_is_not_python_round() -> None:
    assert round(2.5) == 2
    assert round_half_up(2.5) == 3
    assert round_half_up(3.5) == 4


def test_learning_6_depot_to_c1_is_3000_metres() -> None:
    result, dataset = load_and_precheck("LEARNING_6")
    assert result.status.value == "passed"
    assert dataset is not None
    metres = matrix_lookup(dataset.distance_matrix, "DEPOT_L6", "C1")
    assert metres == 3000
    assert metres_to_display_km(metres) == "3.000"


def test_learning_6_matrix_properties() -> None:
    _, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    matrix = dataset.distance_matrix
    size = len(matrix.node_ids)
    assert size == 7
    assert matrix.node_ids[0] == "DEPOT_L6"
    assert all(len(row) == size for row in matrix.distances_metres)
    for i in range(size):
        assert matrix.distances_metres[i][i] == 0
        for j in range(size):
            value = matrix.distances_metres[i][j]
            assert isinstance(value, int)
            assert value >= 0
            assert value == matrix.distances_metres[j][i]


def test_kilometre_display_reconciles_with_metres() -> None:
    assert metres_to_display_km(0) == "0.000"
    assert metres_to_display_km(31000) == "31.000"
    assert metres_to_display_km(16000) == "16.000"


def test_vienna_matrix_is_symmetric_by_construction() -> None:
    result, dataset = load_and_precheck("VIENNA_STANDARD_24")
    assert result.status.value == "passed"
    assert dataset is not None
    matrix = dataset.distance_matrix
    assert len(matrix.node_ids) == 25
    assert matrix.node_ids[0] == "DEPOT_01"
    assert matrix.node_ids[1] == "C001"
    for i, origin in enumerate(matrix.node_ids):
        assert matrix.distances_metres[i][i] == 0
        for j, destination in enumerate(matrix.node_ids):
            assert matrix.distances_metres[i][j] == matrix.distances_metres[j][i]
            assert matrix.distances_metres[i][j] >= 0
            assert matrix_lookup(matrix, origin, destination) == matrix.distances_metres[i][j]


def test_geographic_matrix_is_deterministic() -> None:
    _, first = load_and_precheck("VIENNA_STANDARD_24")
    _, second = load_and_precheck("VIENNA_STANDARD_24")
    assert first is not None and second is not None
    rebuilt = build_geographic_matrix(
        first.depot,
        first.customers,
        first.scenario.detour_factor,
    )
    assert first.distance_matrix == second.distance_matrix
    assert first.distance_matrix == rebuilt
    assert first.scenario.detour_factor == Decimal("1.25")
