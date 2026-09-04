"""LEARNING_6 independent enumeration of the 31.000 km optimum."""

from __future__ import annotations

from itertools import permutations

from app.core.distance_matrix import matrix_lookup, metres_to_display_km
from app.core.loader import load_and_precheck


def _route_distance(dataset, sequence: tuple[str, ...]) -> int:
    depot = dataset.depot.depot_id
    nodes = [depot, *sequence, depot]
    return sum(
        matrix_lookup(dataset.distance_matrix, nodes[index], nodes[index + 1])
        for index in range(len(nodes) - 1)
    )


def test_learning_6_enumeration_minimum_is_31000_metres() -> None:
    _, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    demand = {customer.customer_id: customer.demand_totes for customer in dataset.customers}
    customers = list(demand)
    totals: list[int] = []
    partitions: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    for pack in permutations(customers, 3):
        if sum(demand[customer_id] for customer_id in pack) != 10:
            continue
        complement = tuple(sorted(set(customers) - set(pack)))
        if sum(demand[customer_id] for customer_id in complement) != 10:
            continue
        left = tuple(sorted(pack))
        right = complement
        key = tuple(sorted((left, right)))
        partitions.add(key)

    assert partitions == {
        (("C1", "C2", "C6"), ("C3", "C4", "C5")),
        (("C1", "C5", "C6"), ("C2", "C3", "C4")),
    }

    for left, right in partitions:
        for seq_left in permutations(left):
            for seq_right in permutations(right):
                totals.append(
                    _route_distance(dataset, seq_left) + _route_distance(dataset, seq_right)
                )

    assert len(totals) == 72
    assert min(totals) == 31000
    assert metres_to_display_km(min(totals)) == "31.000"
    assert 34000 in totals
