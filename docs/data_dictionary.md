# Data Dictionary

**Product:** LastMile Lab: ViennaCart CVRP Dispatch Planner  
**Internal units:** integer metres for distance; integer totes for demand and capacity  
**Displayed distance:** kilometres to three decimal places (`metres / 1000`)  
**Displayed utilisation:** stored as a fraction, shown as a percentage to one decimal place

This dictionary defines fields, units, allowed values, and validation rules for the MVP. It does not change the mathematical model in `docs/mathematical_formulation.md`.

---

## 1. Identifier conventions

| Identifier | Pattern | Notes |
|---|---|---|
| `scenario_id` | string | Fixed: `LEARNING_6`, `VIENNA_STANDARD_24`, `INFEASIBLE_SINGLE_OVERSIZE`, `INFEASIBLE_FLEET_OVERFLOW`, `INFEASIBLE_BIN_PACKING`. Generated: `GEN_{seed}_{customer_count}_{vehicle_count}` |
| `depot_id` | string | LEARNING_6: `DEPOT_L6`. Vienna and generated geographic scenarios: `DEPOT_01`. Bin-packing fixture: `DEPOT_BP` |
| `customer_id` | string | LEARNING_6 and infeasible fixtures: `C1`, `C2`, … Vienna and generated: `C001`, `C002`, … zero-padded to three digits |
| `vehicle_id` | string | `V01`, `V02`, … zero-padded to two digits |
| `run_id` | string | Assigned when a baseline or optimisation run is stored |
| `zone_id` | string or null | Geographic: `Z1`, `Z2`, `Z3`, `Z4`. LEARNING_6: null |
| `node_id` | string | Depot or customer identifier used in matrices and stop sequences |

### LEARNING_6 depot label convention

Fixture files store the depot node as `DEPOT_L6`, matching `depot_id`. The specification teaching table labels that node `Depot`. The Learning Lab and other UI copy may display `Depot`; stored identifiers remain `DEPOT_L6`.

---

## 2. Domain run statuses

Every validation, baseline, and optimisation response uses exactly one of these domain statuses.

| Status | Meaning | Solver run? | Comparison eligible? |
|---|---|---|---|
| `pending` | Run created, not finished | maybe | no |
| `invalid` | Data integrity failed (Check 4) | no | no |
| `infeasible` | Check 1 or Check 2 failed | no | no |
| `feasible` | Every customer served, capacity respected, routes depot-connected | yes, or complete baseline | yes |
| `heuristic_incomplete` | Baseline constructed some routes but left customers unserved | baseline only | no |
| `no_solution_found` | Checks 1, 2, and 4 passed; the search returned no complete plan | yes | no |
| `error` | Unexpected runtime failure | maybe | no |

Rules:

- `infeasible` is **only** for hard pre-checks (Check 1 or Check 2). A missing OR-Tools solution is not infeasibility.
- Invalid input and infeasible demand are different statuses. A broken CSV is `invalid`, not `infeasible`.
- The optimiser must never silently drop a customer in order to return a partial plan.
- Page 3 baseline-versus-optimised comparison is shown only when **both** runs have `comparison_eligible = true`.

HTTP mapping (locked; implemented in Phase 6):

| Domain status | HTTP |
|---|---|
| `feasible` | 200 |
| `infeasible` | 200 |
| `heuristic_incomplete` | 200 |
| `no_solution_found` | 200 |
| `invalid` | 400 |
| unknown `scenario_id` | 404 |
| `error` | 500 |

---

## 3. Solver termination

Recorded separately from domain status.

| Value | Meaning |
|---|---|
| `success` | A complete feasible plan was returned |
| `timeout` | Search stopped at the time limit without a complete mandatory plan |
| `no_first_solution` | First-solution strategy produced no complete plan |
| `search_exhausted` | Search ended without a complete plan for a reason other than timeout |
| `not_run` | Solver was not started (invalid or infeasible pre-check, or baseline-only path) |
| `error` | Unexpected solver or runtime failure |
| `null` | Not applicable (for example a baseline run that does not invoke OR-Tools) |

Preferred user-facing message when `solver_termination = timeout`:

> No complete plan was found within the configured search limit. This does not prove the scenario is infeasible.

Supported time limits: `1`, `5`, `10` seconds.

---

## 4. Validation checks

| Check | Class | Fail status | Rule |
|---|---|---|---|
| Check 1 | hard fail | `infeasible` | `max customer demand <= vehicle capacity` |
| Check 2 | hard fail | `infeasible` | `total customer demand <= vehicle count * vehicle capacity` |
| Check 3 | informational | does not fail | `ceil(total demand / vehicle capacity)`; display only |
| Check 4 | hard fail | `invalid` | data integrity (see below) |

Check 4 rules:

- customer IDs are unique
- vehicle IDs are unique
- demand is a positive integer
- capacity is a positive integer
- coordinates are valid WGS84 numbers where the scenario uses geography
- LEARNING_6 may omit coordinates and supply a fixed matrix instead
- depot exists
- distance matrix is square
- matrix dimensions match the node count
- diagonal distances equal zero
- distances are non-negative integers in metres
- the MVP distance matrix is symmetric

Generator request domains (reject outside these with `invalid`; do not normalise weights):

| Field | Type | Domain | Default |
|---|---|---|---|
| `random_seed` | integer | 0 to 2147483647 inclusive | 42 |
| `customer_count` | integer | 1 to 50 inclusive | required |
| `vehicle_count` | integer | 1 to 10 inclusive | required |
| `vehicle_capacity_totes` | integer | 1 to 100 inclusive | required |
| `detour_factor` | decimal | 1.00 to 2.00 inclusive, two decimal places | 1.25 |
| `geographic_zone_weights` | four numbers | each ≥ 0; sum = 1 ± 1e-9 | 0.25 each |

---

## 5. Entities

### 5.1 Scenario

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `scenario_id` | string | see identifiers | unique |
| `scenario_name` | string | display name | required |
| `random_seed` | integer or null | 0 to 2147483647, or null for fixed fixtures that are not generated | LEARNING_6: null. Vienna Standard 24: 42 |
| `depot_id` | string | see identifiers | required; depot must exist |
| `customer_count` | integer | 1 to 50 for generated scenarios | must equal number of customer rows |
| `vehicle_count` | integer | 1 to 10 for generated scenarios | must equal number of vehicle rows |
| `vehicle_capacity_totes` | integer | 1 to 100 for generated scenarios; positive integer | homogeneous fleet in MVP |
| `detour_factor` | decimal | 1.00 to 2.00 inclusive, two decimal places | unused for LEARNING_6 fixed matrix |
| `distance_unit` | string | internal: `metres` | displayed unit is kilometres |
| `has_geographic_coordinates` | boolean | true or false | LEARNING_6: false. Vienna: true |
| `created_at` | timestamp | ISO-8601 when stored | application-assigned later |
| `is_synthetic` | boolean | true for all MVP data | required; all data are synthetic |
| `distance_source` | string | `fixed_matrix` or `haversine_detour` | LEARNING_6: `fixed_matrix` |
| `split_deliveries` | boolean | always false in MVP | must be false |
| `all_customers_mandatory` | boolean | always true in MVP | must be true |

### 5.2 Depot

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `depot_id` | string | see identifiers | unique within scenario |
| `scenario_id` | string | parent scenario | required |
| `name` | string | display name | required |
| `latitude` | decimal or null | WGS84 degrees | required for geographic scenarios; null for LEARNING_6 |
| `longitude` | decimal or null | WGS84 degrees | required for geographic scenarios; null for LEARNING_6 |

Geographic coordinate display may use six decimal places. Coordinates are never described as live GPS traces of real customers.

### 5.3 Customer

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `customer_id` | string | see identifiers | unique within scenario |
| `scenario_id` | string | parent scenario | required |
| `zone_id` | string or null | `Z1`–`Z4` or null | null when `has_geographic_coordinates` is false |
| `latitude` | decimal or null | WGS84 degrees | required for geographic scenarios; null for LEARNING_6 |
| `longitude` | decimal or null | WGS84 degrees | required for geographic scenarios; null for LEARNING_6 |
| `demand_totes` | integer | totes | positive integer; zero, negative, and non-integer values are `invalid` |

### 5.4 Vehicle

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `vehicle_id` | string | see identifiers | unique within scenario |
| `scenario_id` | string | parent scenario | required |
| `capacity_totes` | integer | totes | positive integer; zero is `invalid` |

MVP vehicles are homogeneous: every vehicle in a scenario has the same `capacity_totes`.

### 5.5 Distance matrix cell

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| origin `node_id` | string | depot or customer | must exist |
| destination `node_id` | string | depot or customer | must exist |
| `distance_metres` | integer | metres | ≥ 0; diagonal must be 0; MVP matrix symmetric |

Display:

```text
distance_km_display = format(distance_metres / 1000, three decimal places)
```

Example: stored `3000` metres displays as `3.000 km`.

Geographic construction (later phases): Earth radius `6371000` m, Haversine as specified, detour factor, `integer_metres = floor(raw_metres + 0.5)`, compute `i < j` once and mirror. Do not use Python `round()`.

### 5.6 Planning run

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `run_id` | string | unique run identifier | required once stored |
| `scenario_id` | string | parent scenario | required |
| `run_type` | string | `baseline` or `optimised` | required |
| `status` | string | Section 2 catalogue | required; exactly one value |
| `comparison_eligible` | boolean | true only for complete feasible plans | false when incomplete, invalid, infeasible, or no solution |
| `unserved_customer_ids` | list of strings | sorted customer IDs | empty list when every customer is served |
| `partial_distance_metres` | integer or null | metres | set for `heuristic_incomplete`; null when complete; must not be used as a comparison baseline |
| `solver_termination` | string or null | Section 3 catalogue | null or `not_run` for baseline |
| `solver_time_limit_seconds` | integer or null | 1, 5, or 10 | null for baseline |
| `solver_runtime_seconds` | decimal or null | seconds | null if solver not run |
| `objective_distance_metres` | integer or null | metres | null when the plan is not complete |
| `vehicles_used` | integer or null | count | null if no complete or partial routes are produced |
| `created_at` | timestamp | ISO-8601 when stored | application-assigned later |

Incomplete baseline payload (status `heuristic_incomplete`):

- `comparison_eligible`: false
- `objective_distance_metres`: null
- `baseline_distance`: null
- `distance_improvement_percentage`: null
- `partial_distance_metres`: sum of constructed route distances, including depot return legs
- `customers_served`: count of customers on constructed routes
- `demand_served_totes`: sum of those demands

Complete baseline or optimiser (status `feasible`):

- `comparison_eligible`: true
- `unserved_customer_ids`: `[]`
- `partial_distance_metres`: null
- `objective_distance_metres`: total complete distance

### 5.7 Route

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `run_id` | string | parent run | required |
| `vehicle_id` | string | vehicle on this run | required |
| `is_used` | boolean | true if the route contains at least one customer | unused vehicles have no customer stops |
| `assigned_demand_totes` | integer | totes | `<= capacity_totes` |
| `capacity_totes` | integer | totes | copy of vehicle capacity |
| `distance_metres` | integer | metres | sum of stop legs, including depot return |
| `customer_count` | integer | count | 0 if unused |

### 5.8 Route stop

| Field | Type | Unit / domain | Validation |
|---|---|---|---|
| `run_id` | string | parent run | required |
| `vehicle_id` | string | parent route | required |
| `sequence_number` | integer | 0-based or 1-based later; order is strict | first and last used-route stops are the depot |
| `node_id` | string | depot or customer | required |
| `node_type` | string | `depot` or `customer` | required |
| `demand_totes` | integer | totes | 0 at depot; customer demand otherwise |
| `load_after_service_totes` | integer | totes | reconstructed operational cumulative load, **not** MILP `w_ik` |
| `leg_distance_metres` | integer | metres | inbound leg into this stop; 0 at the opening depot |
| `cumulative_distance_metres` | integer | metres | sum of legs up to this stop |

---

## 6. KPI fields

Formulae use integer metres internally. Display converts to kilometres with three decimal places.

| KPI | Formula | Null when |
|---|---|---|
| customers served | count of customers on used routes | — |
| demand served | sum of those customers' tote demand | — |
| vehicles used | count of vehicles with at least one customer | — |
| total route distance | sum of all route distances, including depot returns | — |
| average distance per delivery | total route distance / customers served | `customers served = 0` |
| used-fleet utilisation | demand served / (vehicles used * Q) | no used vehicles |
| available-fleet utilisation | demand served / (vehicles available * Q) | — |
| longest route distance | max distance among used vehicles | no used vehicles |
| shortest non-empty route | min distance among used vehicles | no used vehicles |
| route-distance imbalance | longest − shortest non-empty | fewer than two vehicles used |
| baseline distance | complete baseline `objective_distance_metres` | plan not `comparison_eligible` |
| distance improvement percentage | `(baseline − optimised) / baseline * 100` | either run not `comparison_eligible` |

Average distance per delivery includes outbound and return depot legs. The denominator is customers served, not stops, and does not count the depot as a delivery.

For every valid complete solution:

```text
customers served = total customers
demand served = total demand
service count per customer = 1
```

---

## 7. Fixture inventory

| Fixture | Role | Demand | Fleet | Expected Phase 0 record |
|---|---|---|---|---|
| `LEARNING_6` | teaching CVRP | 20 totes | 2 × 10 | NN `heuristic_incomplete` with C4 unserved; verified optimum 31000 m |
| `VIENNA_STANDARD_24` | public demo | 108 totes | 4 × 30 | NN complete, loads 29, 28, 29, 22 |
| `INFEASIBLE_SINGLE_OVERSIZE` | Check 1 | 11 | 2 × 10 | `infeasible` |
| `INFEASIBLE_FLEET_OVERFLOW` | Check 2 | 24 | 2 × 10 | `infeasible` |
| `INFEASIBLE_BIN_PACKING` | unsplit packing | 18 | 2 × 10 | Checks 1 and 2 pass; independent packing infeasible; solver later `no_solution_found` |

Files under `data/fixtures/`:

- `learning_6_customers.csv`, `learning_6_vehicles.csv`, `learning_6_distance_matrix.csv`, `learning_6_depot.csv`, `learning_6_expected_results.yaml`
- `vienna_standard_24_customers.csv`, `vienna_standard_24_depot.csv`, `vienna_standard_24_vehicles.csv`, `vienna_standard_24_expected_baseline.yaml`
- `infeasible_single_oversize.yaml`, `infeasible_fleet_overflow.yaml`, `infeasible_bin_packing.yaml`

`learning_6_depot.csv` is an additive fixture so the teaching scenario has an explicit depot row with null coordinates, matching Check 4 (“depot exists”) and the Vienna depot file. Stored node id is `DEPOT_L6`.

---

## 8. Synthetic data disclosure

> LastMile Lab is a fictional portfolio case study. ViennaCart is a fictional operator. All depots, customers, order demands, routes, distances, and operating assumptions are synthetic. The application does not use proprietary customer data or live Vienna traffic information.
