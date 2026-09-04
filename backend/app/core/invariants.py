"""Independent checks on reconstructed routes. These do not read OR-Tools internals."""

from __future__ import annotations

from app.core.distance_matrix import matrix_lookup
from app.core.domain import NodeType, PlanResult, RouteStop, ScenarioDataset, Vehicle


def _stops_by_vehicle(plan: PlanResult) -> dict[str, list[RouteStop]]:
    grouped: dict[str, list[RouteStop]] = {}
    for stop in plan.stops:
        grouped.setdefault(stop.vehicle_id, []).append(stop)
    for vehicle_id, stops in grouped.items():
        grouped[vehicle_id] = sorted(stops, key=lambda item: item.sequence_number)
    return grouped


def feasible_invariant_errors(dataset: ScenarioDataset, plan: PlanResult) -> list[str]:
    errors: list[str] = []
    depot_id = dataset.depot.depot_id
    expected_customers = {customer.customer_id for customer in dataset.customers}
    demand = {customer.customer_id: customer.demand_totes for customer in dataset.customers}
    vehicles = {vehicle.vehicle_id: vehicle for vehicle in dataset.vehicles}
    grouped = _stops_by_vehicle(plan)
    served: list[str] = []

    for route in plan.routes:
        vehicle: Vehicle = vehicles[route.vehicle_id]
        stops = grouped.get(route.vehicle_id, [])
        if not stops:
            errors.append(f"{route.vehicle_id} has no stops")
            continue
        if stops[0].node_id != depot_id or stops[-1].node_id != depot_id:
            errors.append(f"{route.vehicle_id} does not start and end at the depot")
        customers = [stop.node_id for stop in stops if stop.node_type is NodeType.customer]
        if route.is_used:
            served.extend(customers)
            if any(stop.node_type is NodeType.depot for stop in stops[1:-1]):
                errors.append(f"{route.vehicle_id} has a disconnected depot visit")
        elif customers:
            errors.append(f"unused vehicle {route.vehicle_id} contains customer stops")
        if route.assigned_demand_totes > vehicle.capacity_totes:
            errors.append(f"{route.vehicle_id} exceeds capacity")
        leg_sum = sum(stop.leg_distance_metres for stop in stops)
        if route.distance_metres != leg_sum:
            errors.append(f"{route.vehicle_id} distance does not equal the sum of its legs")
        for previous, current in zip(stops, stops[1:], strict=False):
            expected_leg = matrix_lookup(
                dataset.distance_matrix,
                previous.node_id,
                current.node_id,
            )
            if current.leg_distance_metres != expected_leg:
                errors.append(
                    f"{route.vehicle_id} leg {previous.node_id}->{current.node_id} "
                    "does not match the distance matrix"
                )
        reconstructed_load = sum(demand[customer_id] for customer_id in customers)
        if reconstructed_load != route.assigned_demand_totes:
            errors.append(f"{route.vehicle_id} assigned demand does not match served customers")

    if len(served) != len(set(served)):
        errors.append("a customer appears on more than one vehicle route")
    if set(served) != expected_customers:
        errors.append("every customer must appear exactly once")
    if sum(demand[customer_id] for customer_id in served) != sum(demand.values()):
        errors.append("demand served does not equal total demand")
    used = [route for route in plan.routes if route.is_used]
    if plan.run.objective_distance_metres != sum(route.distance_metres for route in used):
        errors.append("scenario distance does not equal the sum of route distances")
    return errors
