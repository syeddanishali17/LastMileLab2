# Methodology

This note explains the modelling choices behind LastMile Lab. Formulae live in [`mathematical_formulation.md`](mathematical_formulation.md). Field definitions live in [`data_dictionary.md`](data_dictionary.md). LEARNING_6 construction and enumeration are recorded in [`learning_6_sequential_nn.md`](learning_6_sequential_nn.md) and [`learning_6_enumeration.md`](learning_6_enumeration.md).

LastMile Lab is a fictional portfolio case study. ViennaCart is a fictional operator. All depots, customers, order demands, routes, distances, and operating assumptions are synthetic. The application does not use proprietary customer data or live Vienna traffic information.

## Why totes are the demand unit

ViennaCart orders are packed in reusable delivery totes. A tote is one integer capacity unit: customer C001 needs 7 totes; van V01 holds 30.

Totes were chosen instead of kilograms, litres, or mixed SKU volumes because:

- demand and capacity stay in the same integer unit
- every capacity check is auditable without unit conversion
- unsplit service is obvious: 7 totes either fit on the van or they do not
- the Model Inspector can reconstruct operational load as a running tote sum

The MVP does not model cube, weight, or multi-commodity packing inside a tote.

## Why split delivery is excluded

Each customer order is one unsplit job. Two vans may not share a customer. That is an operating rule, not a solver convenience.

Split delivery would change the problem: a 5-tote leftover on V02 could take part of C4, and LEARNING_6 would no longer teach packing failure. The documented MILP assignment constraint `sum_k y_ik = 1` would no longer hold.

Unsplit demand is also why Checks 1 and 2 are not a complete feasibility test. Aggregate fleet capacity can be enough in totes while no packing of whole orders exists. `INFEASIBLE_BIN_PACKING` is the teaching fixture for that gap.

## Why the MVP minimises distance rather than a financial cost

Vans are homogeneous. Driver wages, energy, tolls, and time windows are out of scope. With identical vehicles and one frozen morning wave, total route distance is a transparent cost proxy.

A blended money objective would require cost coefficients that this synthetic case study does not have. Distance stays reconcilable: every displayed kilometre is the sum of integer-metre matrix legs, including the return to the depot.

Displayed kilometres use three decimal places (`metres / 1000`). Internal arithmetic stays in integer metres.

## Distance matrix

Geographic scenarios (Vienna Standard 24 and generated instances) use WGS84 coordinates. LEARNING_6 uses a published teaching matrix in kilometres, stored as metres (`km * 1000`).

For every geographic pair:

1. Compute great-circle metres with Haversine and Earth radius `6371000`.
2. Multiply by the detour factor (default `1.25`, allowed range `[1.00, 2.00]`).
3. Round to integer metres with `floor(x + 0.5)`. Never use Python `round()`.
4. Fill one triangle of the matrix, then mirror it so the matrix is symmetric.
5. Set the diagonal to 0.

The detour factor is a synthetic urban allowance. It is not live traffic and not a road-network path. Route lines on OpenStreetMap are schematic connections based on this matrix.

Node order is depot first, then customer IDs sorted lexicographically. Matrix lookup is the only distance source for baseline construction, OR-Tools callbacks, KPI reconciliation, and the inspector.

## Baseline: capacity-aware sequential nearest neighbour

The operational benchmark is fully specified and testable without OR-Tools.

1. Open the next unused vehicle in `vehicle_id` ascending order, starting at the depot.
2. Among unserved customers whose demand fits remaining capacity, choose the nearest to the current node.
3. If several customers share that minimum distance, pick the lowest `customer_id`.
4. Continue until no unserved customer fits, then return to the depot.
5. If unserved customers remain and an unused vehicle exists, open the next vehicle.
6. If the fleet is exhausted with customers still unserved, stop.

Vienna Standard 24 completes: all 24 customers served, loads 29 / 28 / 29 / 22 totes. That complete plan is `comparison_eligible`.

LEARNING_6 does not complete. Sequential construction yields:

```text
V01: Depot → C1 → C2 → C3 → Depot     9 totes     16.000 km
V02: Depot → C6 → C5 → Depot          6 totes     11.000 km
Unserved: C4
status: heuristic_incomplete
comparison_eligible: false
partial_distance_metres: 27000
objective_distance_metres: null
```

From the depot, C1 and C6 are both 3.000 km; the customer-id tie-break selects C1. After C1 then C2, remaining capacity is 4 totes. C3 (3 totes, 3.000 km) is feasible and nearer than C6, so V01 takes C3 and cannot later take C4. V02 then takes C6 and C5, leaving 4 totes of residual capacity against C4's 5-tote order.

That 27.000 km figure is a partial constructed distance. It is not a complete plan and must not be used as a comparison baseline. It is not the 34.000 km named teaching packing.

`comparison_eligible` is true only for complete feasible plans. Improvement percentage is defined only when both the baseline and the optimiser are comparison-eligible:

```text
100 * (baseline_metres - optimised_metres) / baseline_metres
```

The UI formats that value to one decimal place. LEARNING_6 shows no improvement percentage.

## How OR-Tools implements capacity

OR-Tools is used as a vehicle-routing engine, not as a MIP solver of the documented three-index model.

- `RoutingIndexManager` indexes depot and customers; vehicle 0 starts at the depot node.
- A transit callback returns integer matrix metres.
- A unary demand callback returns tote demand at each customer (0 at the depot).
- `AddDimensionWithVehicleCapacity` enforces assigned demand ≤ `Q` per vehicle.
- Every customer is mandatory. There are no disjunctions and no drop penalties.

First solution strategy is `PATH_CHEAPEST_ARC`. Local search is `GUIDED_LOCAL_SEARCH`. Allowed time limits are 1, 5, and 10 seconds.

Routes are extracted from `NextVar` chains. The application then reconstructs assignments, arcs, vehicle use, and cumulative tote loads. Displayed load after serving a customer is the running sum of `q_i` along that route. It is not the MTZ potential `w_ik`.

## Why a solver timeout is `no_solution_found`, not `infeasible`

`infeasible` is reserved for Checks 1 and 2, which are decided before any search:

- Check 1: `max q_i > Q` — one unsplit order cannot fit on any van.
- Check 2: `sum q_i > |K| · Q` — aggregate demand exceeds fleet capacity.

If those checks pass, a feasible packing might still exist. A time limit, a missing first solution, or search exhaustion means the engine did not return a complete mandatory plan. That is `no_solution_found`, with `solver_termination` recording `timeout`, `no_first_solution`, or `search_exhausted`.

Calling a timeout `infeasible` would claim a proof the search did not produce. `INFEASIBLE_BIN_PACKING` is the other direction of the same rule: Checks 1 and 2 pass, no complete unsplit assignment exists, and the optimiser still reports `no_solution_found` because the MVP has no exact bin-packing pre-check.

## How solution invariants are verified

After a complete plan is assembled, independent checks (not OR-Tools internals) require:

- every used route starts and ends at the depot
- every customer appears on exactly one used route
- assigned demand equals the sum of those customers' tote demands
- assigned demand ≤ vehicle capacity
- each leg equals the distance-matrix entry
- route distance equals the sum of its legs
- scenario objective equals the sum of used-route distances

KPI values are computed from those reconstructed routes. Streamlit only formats the API payload.

## Why normal solver output is feasible rather than globally optimal

Guided local search with a wall-clock limit returns the best complete plan found in that window. It is not a branch-and-cut proof of optimality. OR-Tools search is not guaranteed bit-deterministic across CPU, seed, or package version.

Preferred wording for Vienna Standard 24 and generated scenarios:

> Best feasible solution found within the configured search limit.

Do not freeze ordinary OR-Tools kilometres in tests. The Vienna baseline kilometres and sequences are deterministic and are frozen.

## Why LEARNING_6 is the exception

LEARNING_6 has six customers, two vans of 10 totes, and total demand 20. Both vans must load exactly 10 totes. Only two capacity-feasible 3-and-3 partitions exist. Enumerating all depot-start sequences on those partitions proves that the minimum complete distance is 31.000 km.

OR-Tools on LEARNING_6 is therefore checked against 31000 metres. The 34.000 km named packing `{C1,C2,C6}` / `{C5,C4,C3}` is a teaching comparison, not sequential nearest neighbour and not the optimum. Sequential NN remains `heuristic_incomplete` with C4 unserved and partial distance 27.000 km.

The stored depot id is `DEPOT_L6`. The UI label is `Depot`.

## Why aggregate capacity checks are not a complete unsplit-feasibility test

Check 3 reports `ceil(sum q_i / Q)` as an informational lower bound on vehicles. It never fails validation. Indivisible orders can require more vans than that bound.

Checks 1 and 2 are necessary and not sufficient. Three 6-tote orders and two 10-tote vans pass both checks (`18 ≤ 20`) and still have no feasible unsplit packing. The MVP does not add an exact packing pre-check. Exact bin packing is NP-hard; failing a heuristic such as first-fit decreasing is not a proof of infeasibility.

The planner therefore separates:

- proven infeasibility from simple capacity rules (`infeasible`)
- search that returned no complete mandatory plan (`no_solution_found`)
- a complete feasible plan (`feasible`), which is still not a global-optimality claim except on LEARNING_6
