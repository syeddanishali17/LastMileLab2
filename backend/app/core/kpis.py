"""KPI formulae from specification Section 17."""

from __future__ import annotations

from app.core.domain import (
    CustomerResult,
    NodeType,
    PlanResult,
    RouteStop,
    RunStatus,
    RunType,
    ScenarioDataset,
    ScenarioKpis,
    VehicleKpis,
)
from app.core.routes import node_sequence_for_vehicle


def metres_to_km(metres: int | None) -> float | None:
    if metres is None:
        return None
    return metres / 1000


def format_utilisation_pct(fraction: float | None) -> str | None:
    if fraction is None:
        return None
    return f"{fraction * 100:.1f}%"


def _used_routes(plan: PlanResult):
    return [route for route in plan.routes if route.is_used]


def _operational_distance(plan: PlanResult) -> int | None:
    used = _used_routes(plan)
    if not used:
        return None
    return sum(route.distance_metres for route in used)


def compute_scenario_kpis(
    dataset: ScenarioDataset,
    plan: PlanResult,
    *,
    baseline_plan: PlanResult | None = None,
) -> ScenarioKpis:
    capacity = dataset.scenario.vehicle_capacity_totes
    total_demand = sum(customer.demand_totes for customer in dataset.customers)
    vehicles_available = len(dataset.vehicles)
    used = _used_routes(plan)
    vehicles_used = len(used)
    served = plan.customers_served
    demand_served = plan.demand_served_totes
    total_distance = _operational_distance(plan)

    average: float | None = None
    if served > 0 and total_distance is not None:
        average = total_distance / served

    used_util: float | None = None
    if vehicles_used > 0:
        used_util = demand_served / (vehicles_used * capacity)
    available_util: float | None = None
    if vehicles_available > 0:
        available_util = demand_served / (vehicles_available * capacity)

    longest = max((route.distance_metres for route in used), default=None)
    shortest = min((route.distance_metres for route in used), default=None)
    imbalance = None
    if vehicles_used >= 2 and longest is not None and shortest is not None:
        imbalance = longest - shortest

    baseline_distance = None
    optimised_distance = None
    improvement = None
    if plan.run.run_type is RunType.baseline and plan.run.comparison_eligible:
        baseline_distance = plan.run.objective_distance_metres
    if plan.run.run_type is RunType.optimised and plan.run.comparison_eligible:
        optimised_distance = plan.run.objective_distance_metres
        if (
            baseline_plan is not None
            and baseline_plan.run.comparison_eligible
            and baseline_plan.run.objective_distance_metres
        ):
            baseline_distance = baseline_plan.run.objective_distance_metres
            improvement = (
                (baseline_distance - optimised_distance) / baseline_distance * 100
                if optimised_distance is not None
                else None
            )
    if plan.run.status is not RunStatus.feasible:
        if not plan.run.comparison_eligible:
            improvement = None
            if plan.run.run_type is RunType.baseline:
                baseline_distance = None

    return ScenarioKpis(
        customer_orders=len(dataset.customers),
        customer_orders_served=served,
        total_demand_totes=total_demand,
        demand_served_totes=demand_served,
        vehicles_available=vehicles_available,
        vehicles_used=vehicles_used,
        total_fleet_capacity_totes=vehicles_available * capacity,
        total_route_distance_metres=total_distance,
        average_distance_per_delivery_metres=average,
        used_fleet_utilisation=used_util,
        available_fleet_utilisation=available_util,
        longest_route_distance_metres=longest,
        shortest_non_empty_route_distance_metres=shortest,
        route_distance_imbalance_metres=imbalance,
        baseline_distance_metres=baseline_distance,
        optimised_distance_metres=optimised_distance,
        distance_improvement_percentage=improvement,
    )


def compute_vehicle_kpis(dataset: ScenarioDataset, plan: PlanResult) -> list[VehicleKpis]:
    results: list[VehicleKpis] = []
    for route in sorted(plan.routes, key=lambda item: item.vehicle_id):
        sequence = node_sequence_for_vehicle(plan.stops, route.vehicle_id)
        utilisation = None
        if route.capacity_totes > 0:
            utilisation = route.assigned_demand_totes / route.capacity_totes
        results.append(
            VehicleKpis(
                vehicle_id=route.vehicle_id,
                sequence=sequence,
                customer_count=route.customer_count,
                assigned_demand_totes=route.assigned_demand_totes,
                capacity_totes=route.capacity_totes,
                remaining_capacity_totes=route.capacity_totes - route.assigned_demand_totes,
                capacity_utilisation=utilisation,
                route_distance_metres=route.distance_metres,
                is_used=route.is_used,
            )
        )
    if not plan.routes:
        for vehicle in sorted(dataset.vehicles, key=lambda item: item.vehicle_id):
            results.append(
                VehicleKpis(
                    vehicle_id=vehicle.vehicle_id,
                    sequence=[],
                    customer_count=0,
                    assigned_demand_totes=0,
                    capacity_totes=vehicle.capacity_totes,
                    remaining_capacity_totes=vehicle.capacity_totes,
                    capacity_utilisation=0.0,
                    route_distance_metres=0,
                    is_used=False,
                )
            )
    return results


def _stop_context(stops: list[RouteStop], index: int) -> tuple[str | None, str | None]:
    previous_node = stops[index - 1].node_id if index > 0 else None
    next_node = stops[index + 1].node_id if index + 1 < len(stops) else None
    return previous_node, next_node


def compute_customer_results(dataset: ScenarioDataset, plan: PlanResult) -> list[CustomerResult]:
    by_vehicle: dict[str, list[RouteStop]] = {}
    for stop in plan.stops:
        by_vehicle.setdefault(stop.vehicle_id, []).append(stop)
    for vehicle_id, stops in by_vehicle.items():
        by_vehicle[vehicle_id] = sorted(stops, key=lambda item: item.sequence_number)

    assigned: dict[str, CustomerResult] = {}
    for vehicle_id, stops in by_vehicle.items():
        customer_order = 0
        for index, stop in enumerate(stops):
            if stop.node_type is not NodeType.customer:
                continue
            customer_order += 1
            previous_node, next_node = _stop_context(stops, index)
            assigned[stop.node_id] = CustomerResult(
                customer_id=stop.node_id,
                demand_totes=stop.demand_totes,
                assigned_vehicle=vehicle_id,
                route_sequence_position=customer_order,
                previous_node=previous_node,
                next_node=next_node,
                inbound_leg_distance_metres=stop.leg_distance_metres,
                cumulative_route_distance_metres=stop.cumulative_distance_metres,
                service_count=1,
                demand_check="Pass",
            )

    results: list[CustomerResult] = []
    for customer in dataset.customers:
        if customer.customer_id in assigned:
            results.append(assigned[customer.customer_id])
            continue
        results.append(
            CustomerResult(
                customer_id=customer.customer_id,
                demand_totes=customer.demand_totes,
                assigned_vehicle=None,
                route_sequence_position=None,
                previous_node=None,
                next_node=None,
                inbound_leg_distance_metres=None,
                cumulative_route_distance_metres=None,
                service_count=0,
                demand_check="Fail",
            )
        )
    return results
