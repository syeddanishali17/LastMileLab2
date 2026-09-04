"""Vienna Standard 24 sequential nearest-neighbour regression."""

from __future__ import annotations

from app.core.baseline import plan_baseline
from app.core.domain import RunStatus
from app.core.routes import node_sequence_for_vehicle


def test_vienna_standard_24_sequential_nn_serves_all_customers() -> None:
    plan = plan_baseline("VIENNA_STANDARD_24")
    assert plan.run.status is RunStatus.feasible
    assert plan.run.comparison_eligible is True
    assert plan.run.unserved_customer_ids == []
    assert plan.customers_served == 24
    assert plan.demand_served_totes == 108
    assert plan.run.partial_distance_metres is None
    assert plan.run.objective_distance_metres == sum(
        route.distance_metres for route in plan.routes if route.is_used
    )

    expected = {
        "V01": (
            29,
            [
                "DEPOT_01",
                "C022",
                "C020",
                "C019",
                "C024",
                "C021",
                "C023",
                "C009",
                "C007",
                "DEPOT_01",
            ],
        ),
        "V02": (
            28,
            [
                "DEPOT_01",
                "C017",
                "C014",
                "C013",
                "C015",
                "C018",
                "C016",
                "C005",
                "DEPOT_01",
            ],
        ),
        "V03": (
            29,
            [
                "DEPOT_01",
                "C003",
                "C001",
                "C002",
                "C004",
                "C012",
                "DEPOT_01",
            ],
        ),
        "V04": (
            22,
            ["DEPOT_01", "C006", "C008", "C010", "C011", "DEPOT_01"],
        ),
    }
    for vehicle_id, (load, sequence) in expected.items():
        route = next(item for item in plan.routes if item.vehicle_id == vehicle_id)
        assert route.assigned_demand_totes == load
        assert node_sequence_for_vehicle(plan.stops, vehicle_id) == sequence
        assert route.distance_metres == sum(
            stop.leg_distance_metres
            for stop in plan.stops
            if stop.vehicle_id == vehicle_id
        )
