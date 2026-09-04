# LastMile Lab: ViennaCart CVRP Dispatch Planner

## Project Specification for Cursor AI

**Document purpose:** Source of truth for the clean rebuild of the LastMile Lab portfolio project.

**Product name:** LastMile Lab  
**Fictional operator:** ViennaCart  
**Displayed title:** LastMile Lab: ViennaCart CVRP Dispatch Planner

**Document version:** 1.2  
**Revision date:** 3 September 2026  
**Companion review notes:** `ViennaCart_CVRP_Specification_Review_Notes.md`

**Project type:** Supply-chain and logistics decision-support application.

**Primary optimisation problem:** Capacitated Vehicle Routing Problem (CVRP).

**Development approach:** Build and test one phase at a time. Do not generate the entire application in one step.

---

## 1. Executive Summary

ViennaCart is a fictional same-day e-commerce delivery operation serving synthetic customers around Vienna, Austria.

The MVP plans a **static morning dispatch wave**. It is not live same-day control. At the beginning of the planning period, ViennaCart knows:

- the delivery depot
- the customer orders that must be served
- the location of every customer
- the demand of every customer order, measured in standardized delivery totes
- the number of delivery vans available
- the carrying capacity of each van
- the distance between every pair of locations

The planner must decide:

1. Which van should serve each customer?
2. In what order should each van visit its assigned customers?
3. Can every customer order be served with the available fleet capacity?
4. What is the shortest feasible set of routes?
5. How much better is the optimised solution than a simple operational baseline?

Distance is the MVP cost proxy. Vans are homogeneous and driver time, wages, and energy costs are out of scope, so the model minimises total distance rather than a blended financial objective.

The application will provide a professional frontend where a user can inspect the demand, distance matrix, vehicle assignments, route sequence, capacity utilisation, and baseline-versus-optimised results.

The project must demonstrate understanding of the optimisation model. It must not be only a visual wrapper around OR-Tools.

The documented mixed-integer formulation in Sections 7 to 9 is the model the author must be able to explain. Google OR-Tools `RoutingModel` is the MVP solver. It does not solve that three-index MILP directly. The Model Inspector reconstructs the MILP symbols from returned routes.

---

## 2. Portfolio Objective

This project is intended to be linked on a resume for roles involving:

- supply-chain analytics
- logistics and transport planning
- e-commerce operations
- operations research
- business and data analysis
- process optimisation
- location and routing analysis
- decision-support applications

The finished project should demonstrate:

- correct CVRP formulation
- demand and vehicle-capacity modelling
- route and assignment decisions
- distance-matrix construction
- baseline design
- optimisation with Google OR-Tools
- Python engineering
- FastAPI development
- Streamlit frontend development
- data validation
- automated testing
- explainable operational KPIs
- Git and GitHub workflow
- Docker and deployment fundamentals

---

## 3. Business Story

ViennaCart operates one fictional urban delivery depot.

Customer orders have been prepared in standardized delivery totes. A tote is a simple operational capacity unit representing one reusable order container. It is used instead of arbitrary litres so that demand and capacity remain intuitive and auditable.

Example:

```text
Customer C001 requires 7 totes.
Customer C002 requires 6 totes.
Van V01 can carry at most 30 totes.
```

Each van is loaded once at the depot, completes one route, and returns to the same depot.

Every customer order must be delivered in full by one van. Two vans may not split the same customer order in the MVP.

The operating story is same-day delivery. The MVP still plans one frozen wave: orders in, vans out, no midday re-optimisation.

---

## 4. Fixed MVP Modelling Decisions

| Decision | MVP rule |
|---|---|
| Depot | One depot |
| Customers | Multiple synthetic customer orders |
| Fleet | Multiple identical vans |
| Demand unit | Integer delivery totes |
| Customer service | Every customer must be served |
| Split deliveries | Not allowed |
| Vehicle trips | One route per vehicle |
| Vehicle use | A van may remain unused |
| Route start | Depot |
| Route end | Same depot |
| Capacity | Total demand assigned to a van cannot exceed its tote capacity |
| Distance | Symmetric distance matrix for MVP |
| Coordinate reference | WGS84 latitude and longitude |
| Internal distance unit | Integer metres |
| Displayed distance unit | Kilometres, three decimal places |
| Primary objective | Minimise total route distance |
| Planning type | Static, deterministic, one planning period |
| Solver | Google OR-Tools RoutingModel |

### Mandatory interpretation

- One van may serve several customers.
- One customer may be assigned to only one van.
- The selected van must carry the customer's entire tote demand.
- All customers must appear in the final solution exactly once.
- If Check 1 or Check 2 fails, the scenario status is `infeasible` and the solver is not run.
- If those checks pass but no complete plan is found, the status is `no_solution_found`. That is not a proof of infeasibility.
- The optimiser must never silently drop a customer.

---

## 5. Explicit Non-Goals for the MVP

Do not implement the following in the first release:

- delivery time windows
- service-time scheduling
- live traffic
- dynamic or real-time rerouting
- split deliveries
- repeated depot trips by the same vehicle
- multiple depots
- heterogeneous vehicles
- electric-vehicle charging
- vehicle range constraints
- customer priorities
- optional or dropped deliveries
- penalty costs for unserved customers
- emissions optimisation
- driver breaks
- driver preferences
- authentication
- user accounts
- machine learning
- LLM route explanations
- Snowflake
- Power BI
- React
- microservices
- Kubernetes

These exclusions are deliberate. The CVRP foundation must be correct, transparent, tested, and understandable before extensions are considered.

---

## 6. Core Business Question

The application must answer:

> How should ViennaCart assign mandatory customer orders to its available vans and sequence the deliveries so that every order is served without exceeding van capacity, while minimising total distance travelled?

---

## 7. Model Components

### 7.1 Sets

```text
N     set of customers
N0    set of all nodes, including depot 0
K     set of available vehicles
```

The fleet size is `|K|`. Do not introduce a separate parameter `M` for the number of vehicles.

### 7.2 Parameters

```text
q_i       tote demand of customer i
Q_k       tote capacity of vehicle k
d_ij      distance from node i to node j, in integer metres
```

For the homogeneous MVP:

```text
Q_k = Q for every vehicle k
```

### 7.3 Decision Variables

#### Route variable

```text
x_ijk = 1 if vehicle k travels directly from node i to node j
x_ijk = 0 otherwise
```

The row location is the origin. The column location is the destination.

`x_ijk` is defined only for `i ≠ j`. Self-loops are forbidden.

#### Customer assignment variable

```text
y_ik = 1 if customer i is assigned to vehicle k
y_ik = 0 otherwise
```

#### Vehicle-use variable

```text
u_k = 1 if vehicle k serves at least one customer
u_k = 0 if vehicle k remains unused
```

#### Load-order potential for subtour elimination

```text
w_ik = load-order potential of customer i on vehicle k
```

`w_ik` is a Miller–Tucker–Zemlin potential. It is not required to equal the operational cumulative load displayed in the application.

When `y_ik = 0`, the bounds in Section 9.7 force `w_ik = 0`. When `y_ik = 1` and `x_ijk = 1`, the potential on `j` is at least the potential on `i` plus `q_j`. Slack can remain when the van is not filled, so two feasible potentials can differ while representing the same route.

The exact load shown on route cards, KPIs, and the Model Inspector is reconstructed by summing tote demand along the returned stop sequence. Do not read `w_ik` from OR-Tools. OR-Tools enforces capacity with a dimension, not with these variables.

### 7.4 Variable Domains

```text
x_ijk ∈ {0, 1}     ∀ i, j ∈ N0, i ≠ j, k ∈ K
y_ik  ∈ {0, 1}     ∀ i ∈ N, k ∈ K
u_k   ∈ {0, 1}     ∀ k ∈ K
w_ik  ≥ 0          ∀ i ∈ N, k ∈ K
```

Section 9.7 then forces `w_ik ≤ Q_k y_ik`, so `w_ik = 0` whenever customer `i` is not assigned to vehicle `k`.

---

## 8. Objective Function

The MVP objective is to minimise total travel distance:

```text
minimise sum over k, i, j of d_ij * x_ijk
```

Conceptually:

\[
\min \sum_{k \in K}\sum_{i \in N_0}\sum_{j \in N_0, j \ne i}d_{ij}x_{ijk}
\]

Do not combine distance, emissions, workload, service level, and cost into an arbitrary weighted score.

Every customer is mandatory, so service level is a hard requirement rather than an objective.

---

## 9. Required Constraints

### 9.1 Demand Satisfaction and Unique Assignment

Every customer must be assigned to exactly one vehicle:

\[
\sum_{k \in K} y_{ik}=1 \qquad \forall i \in N
\]

This is the main demand-satisfaction or customer-service constraint.

It also establishes the unsplit-delivery rule.

### 9.2 Vehicle Capacity

The total tote demand assigned to a vehicle cannot exceed its capacity:

\[
\sum_{i \in N}q_i y_{ik}\le Q_k \qquad \forall k \in K
\]

The MTZ potential constraints in Section 9.7 also prevent capacity-infeasible routed tours when `x_ijk = 1`. Keep this aggregate inequality because it is the form a planner can audit without reading the subtour inequalities.

### 9.3 Assignment and Route Linking

If customer `i` is assigned to vehicle `k`, that vehicle must enter and leave the customer exactly once:

\[
\sum_{j \in N_0, j\ne i}x_{ijk}=y_{ik} \qquad \forall i \in N, k \in K
\]

\[
\sum_{j \in N_0, j\ne i}x_{jik}=y_{ik} \qquad \forall i \in N, k \in K
\]

### 9.4 Flow Conservation at Customers

Section 9.3 already forces incoming selected arcs to equal outgoing selected arcs at every customer. Do not implement 9.4 as a separate coded constraint. Keep the statement only as a reading aid for the route matrix:

- the row sum represents movements leaving a node
- the column sum represents movements entering a node

Depot flow is handled in Section 9.5, not by copying 9.3.

### 9.5 Depot Departure and Return

Every used vehicle must leave the depot once and return once:

\[
\sum_{j \in N}x_{0jk}=u_k \qquad \forall k \in K
\]

\[
\sum_{i \in N}x_{i0k}=u_k \qquad \forall k \in K
\]

Unused vehicles have `u_k = 0` and therefore no depot arcs.

### 9.6 Vehicle-Use Linking

A vehicle is used if and only if it serves at least one customer:

\[
u_k \ge y_{ik} \qquad \forall i \in N, k \in K
\]

\[
u_k \le \sum_{i \in N} y_{ik} \qquad \forall k \in K
\]

Without these inequalities, a formulation can assign customers while leaving `u_k = 0`, which yields customer cycles that never touch the depot.

### 9.7 Route Connectivity and MTZ Subtour Elimination

Disconnected customer cycles are not allowed. Flow balance alone is not sufficient to eliminate subtours in a manually written MILP.

Use Miller–Tucker–Zemlin load-order potentials with assignment-linked bounds:

\[
q_i y_{ik} \le w_{ik} \le Q_k y_{ik} \qquad \forall i \in N, k \in K
\]

\[
w_{ik} - w_{jk} + Q_k x_{ijk} \le Q_k - q_j y_{jk} \qquad \forall i \in N, j \in N, i \ne j, k \in K
\]

The right-hand side **must** include `y_{jk}`. The weaker right-hand side `Q_k - q_j` is incorrect in this three-index model.

Counter-example with the documented 31 km optimum. Vehicle V01 serves Depot → C1 → C5 → C6 → Depot, so a feasible potential can take `w_{C6,V01} = 10`. Customer C4 is on V02, so `y_{C4,V01} = 0`, `w_{C4,V01} = 0`, and `x_{C6,C4,V01} = 0`, with `q_{C4} = 5` and `Q = 10`.

Wrong inequality:

\[
10 - 0 + 0 \le 10 - 5 \quad \Rightarrow \quad 10 \le 5
\]

That rejects a valid solution. Correct inequality:

\[
10 - 0 + 0 \le 10 - 5\cdot 0 \quad \Rightarrow \quad 10 \le 10
\]

When `x_{ijk} = 1`, linking forces `y_{jk} = 1`, and the inequality reduces to `w_{jk} \ge w_{ik} + q_j`. Summing around a customer-only cycle then yields `0 \le -\sum q < 0`, which eliminates subtours.

Do not treat `w_{ik}` as the operational load after serving `i`. Reconstruct that load from the route.

OR-Tools `RoutingModel` enforces continuous depot-connected vehicle routes through its own routing representation. The inspector reconstructs `x_ijk` from consecutive stops; it does not read OR-Tools decision variables named `x_ijk`.

### 9.8 Documented MILP Versus OR-Tools

| MILP symbol | Meaning in the documented model | How the MVP obtains it |
|---|---|---|
| `y_ik` | Customer `i` assigned to vehicle `k` | Customer appears on vehicle `k`'s returned route |
| `x_ijk` | Vehicle `k` travels `i → j` | Consecutive stops on vehicle `k`'s returned route, including depot legs |
| `u_k` | Vehicle `k` is used | Returned route contains at least one customer |
| `w_ik` | Load-order potential for customer `i` on vehicle `k` | Not taken from the solver. Displayed load is the cumulative tote sum along the returned route |
| Capacity | Assigned demand ≤ `Q` | Unary demand callback plus OR-Tools capacity dimension |
| Subtours | Forbidden by MTZ potentials | Forbidden by `RoutingModel` route continuity from the depot |

Do not claim that OR-Tools solved this three-index MILP with a MIP solver.

---

## 10. Feasibility Checks Before Optimisation

Classify every pre-check as a **hard fail** or **informational**.

Hard-fail checks block the solver and return status `invalid` or `infeasible` as specified below. Informational checks are displayed only.

### Check 1: Individual demand — hard fail, `infeasible`

```text
maximum customer demand <= vehicle capacity
```

If one customer requires 35 totes and every van holds 30, the unsplit scenario is infeasible.

### Check 2: Aggregate fleet capacity — hard fail, `infeasible`

```text
total customer demand <= vehicle count * vehicle capacity
```

### Check 3: Theoretical lower bound on vehicles — informational

```text
minimum vehicles by aggregate demand = ceiling(total demand / vehicle capacity)
```

This is a lower bound, not a guarantee of feasibility, because indivisible customer orders may require additional vehicles.

`INFEASIBLE_BIN_PACKING` is the teaching example: Check 1 and Check 2 both pass, yet no feasible unsplit assignment exists.

Do not fail validation because Check 3 is tight. Display it on Dispatch Setup. Do not add an exact bin-packing pre-check in the MVP. Exact packing is NP-hard; failing first-fit decreasing is not a proof of infeasibility.

### Check 4: Data integrity — hard fail, `invalid`

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

Invalid input and infeasible demand are different statuses. Do not call a broken CSV `infeasible`.

### 10.5 Run status catalogue

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

`infeasible` is **only** for hard pre-checks. A missing OR-Tools solution is **not** infeasibility.

`no_solution_found` covers time limits, a failed first-solution strategy, and search that stopped without a complete mandatory plan. Record the cause separately:

```text
solver_termination:
  success
  timeout
  no_first_solution
  search_exhausted
  not_run
  error
```

Preferred user-facing message when `solver_termination = timeout`:

> No complete plan was found within the configured search limit. This does not prove the scenario is infeasible.

Preferred user-facing message when pre-checks passed and the instance is the bin-packing fixture:

> Pre-checks passed. No complete unsplit assignment was found. Aggregate fleet capacity is necessary but not sufficient when orders cannot be split.

Do not implement optional drops in order to return a partial optimiser plan. Mandatory customers stay mandatory.

---

## 11. Canonical Learning Scenario

This small scenario must be implemented first and retained permanently as a test fixture.

### 11.1 Configuration

```yaml
scenario_id: LEARNING_6
depot_id: DEPOT_L6
depot_count: 1
customer_count: 6
vehicle_ids: [V01, V02]
vehicle_count: 2
vehicle_capacity_totes: 10
total_customer_demand_totes: 20
split_deliveries: false
all_customers_mandatory: true
has_geographic_coordinates: false
distance_source: fixed_matrix
internal_distance_unit: metres
```

LEARNING_6 has no WGS84 coordinates. The published matrix is a teaching matrix. It is not required to be embeddable in the plane.

### 11.2 Customer Data

```csv
customer_id,demand_totes
C1,4
C2,2
C3,3
C4,5
C5,2
C6,4
```

### 11.3 Distance Matrix

Displayed distances are kilometres. Store every cell as integer metres by multiplying the published kilometre value by 1000.

| From / To | Depot | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Depot | 0 | 3 | 5 | 8 | 7 | 5 | 3 |
| C1 | 3 | 0 | 2 | 5 | 5 | 4 | 4 |
| C2 | 5 | 2 | 0 | 3 | 4 | 5 | 6 |
| C3 | 8 | 5 | 3 | 0 | 3 | 6 | 7 |
| C4 | 7 | 5 | 4 | 3 | 0 | 4 | 6 |
| C5 | 5 | 4 | 5 | 6 | 4 | 0 | 3 |
| C6 | 3 | 4 | 6 | 7 | 6 | 3 | 0 |

Example: displayed `3` km is stored as `3000` metres.

### 11.4 Sequential Nearest-Neighbour Outcome

Apply the product baseline in Section 15, including the tie-breaks.

```text
Vehicle V01: Depot -> C1 -> C2 -> C3 -> Depot
Load: 4 + 2 + 3 = 9 totes
Distance: 16.000 km (16000 m)
Status: open, then closed when remaining capacity is 1 tote

Vehicle V02: Depot -> C6 -> C5 -> Depot
Load: 4 + 2 = 6 totes
Distance: 11.000 km (11000 m)

Unserved: C4 (demand 5 totes; remaining capacity on V02 is 4)
Baseline status: heuristic_incomplete
comparison_eligible: false
unserved_customer_ids: [C4]
partial_distance_metres: 27000
objective_distance_metres: null
distance improvement percentage: null
```

`partial_distance_metres` is the sum of constructed route distances, including depot return legs. It must not be used as a baseline comparison distance.

Reason: from the depot, C1 and C6 are both 3 km; the customer-id tie-break selects C1. After C1 then C2, remaining capacity is 4 totes. C3 (3 totes, 3 km) is feasible and nearer than C6 (6 km), so V01 takes C3 and cannot later take C4.

This is the required automated baseline result for LEARNING_6. Do not expect a complete 34 km sequential-NN plan.

### 11.5 Reference Feasible Packing

The following 34 km plan is a **teaching comparison**, not the sequential NN output.

It is obtained by fixing the capacity-feasible packs `{C1, C2, C6}` and `{C5, C4, C3}`, then sequencing each pack by nearest neighbour from the depot with the same customer-id tie-break.

```text
Vehicle V01: Depot -> C1 -> C2 -> C6 -> Depot
Pack: {C1, C2, C6}
Load: 4 + 2 + 4 = 10
Distance: 14.000 km (14000 m)

Vehicle V02: Depot -> C5 -> C4 -> C3 -> Depot
Pack: {C5, C4, C3}
Load: 2 + 5 + 3 = 10
Distance: 20.000 km (20000 m)

Total distance: 34.000 km (34000 m)
```

Use this packing only in the Learning Lab, to show that a feasible assignment exists even when sequential construction fails.

### 11.6 Known Best Solution for the Fixture

```text
Vehicle V01: Depot -> C1 -> C5 -> C6 -> Depot
Load: 4 + 2 + 4 = 10
Distance: 13.000 km (13000 m)

Vehicle V02: Depot -> C2 -> C3 -> C4 -> Depot
Load: 2 + 3 + 5 = 10
Distance: 18.000 km (18000 m)

Total distance: 31.000 km (31000 m)
```

### 11.7 Independent Enumeration of the Optimum

Total demand equals total fleet capacity, so both vehicles must be used and each must load exactly 10 totes. No two-customer subset sums to 10, so every feasible assignment is a 3-and-3 partition.

The only capacity-feasible partitions are:

```text
{C1, C2, C6} | {C3, C4, C5}
{C1, C5, C6} | {C2, C3, C4}
```

For each pack of three customers, evaluate all `3! = 6` depot-start sequences. Across two partitions that is 72 directed route pairs. The minimum total is 31.000 km, attained by the routes in Section 11.6 (and by their equal-length reversals).

Phase 0 and a dedicated test must repeat this enumeration. Do not take 31 km on trust from OR-Tools.

This fixture teaches:

- feasibility, controlled by assignment and capacity
- quality, controlled by route distance
- why a greedy construction can fail on a tight, feasible instance

### 11.8 Learning Scenario Display Rules

- Convert stored metres to kilometres by dividing by 1000. Display three decimal places: `31.000 km`, not `31 km` as an ambiguous mixed unit.
- Do not draw LEARNING_6 on an OpenStreetMap canvas. There are no coordinates, and forcing a 2D layout would disagree with the matrix.
- The Learning Lab may use a schematic node diagram only if it is labelled as a diagram, not a map.

### 11.9 Companion Infeasible Fixtures

Keep these tiny datasets next to LEARNING_6 so validation tests are named fixtures, not ad hoc literals.

```yaml
scenario_id: INFEASIBLE_SINGLE_OVERSIZE
vehicle_count: 2
vehicle_capacity_totes: 10
customers:
  - {customer_id: C1, demand_totes: 11}
expected_status: infeasible
reason: individual demand exceeds vehicle capacity
```

```yaml
scenario_id: INFEASIBLE_FLEET_OVERFLOW
vehicle_count: 2
vehicle_capacity_totes: 10
total_fleet_capacity_totes: 20
customers:
  - {customer_id: C1, demand_totes: 8}
  - {customer_id: C2, demand_totes: 8}
  - {customer_id: C3, demand_totes: 8}
expected_status: infeasible
reason: aggregate demand 24 exceeds fleet capacity 20
```

```yaml
scenario_id: INFEASIBLE_BIN_PACKING
depot_id: DEPOT_BP
vehicle_count: 2
vehicle_capacity_totes: 10
total_fleet_capacity_totes: 20
has_geographic_coordinates: false
customers:
  - {customer_id: C1, demand_totes: 6}
  - {customer_id: C2, demand_totes: 6}
  - {customer_id: C3, demand_totes: 6}
distance_matrix: all off-diagonal cells 1000 metres; diagonal 0
expected_precheck_status: passed
expected_check_1: pass   # 6 <= 10
expected_check_2: pass   # 18 <= 20
expected_solver_status: no_solution_found
independent_packing_result: infeasible
reason: two six-tote orders cannot share a ten-tote van, and three such orders exceed two vans
```

`INFEASIBLE_BIN_PACKING` is the unsplit-demand teaching fixture. Checks 1 and 2 pass. No two orders can share a van, so at most two of three customers can be served. An independent enumeration of assignments must prove that no feasible packing exists. The optimiser still reports `no_solution_found`, not `infeasible`, because the MVP does not include an exact bin-packing pre-check.

---

## 12. Portfolio Demo Scenario

The public application should open with this deterministic scenario already available.

### 12.1 Configuration

```yaml
scenario_id: VIENNA_STANDARD_24
scenario_name: Vienna Standard Dispatch
random_seed: 42
depot_id: DEPOT_01
depot_count: 1
customer_count: 24
vehicle_ids: [V01, V02, V03, V04]
vehicle_count: 4
vehicle_capacity_totes: 30
total_fleet_capacity_totes: 120
total_customer_demand_totes: 108
aggregate_capacity_utilisation: 90_percent
split_deliveries: false
all_customers_mandatory: true
has_geographic_coordinates: true
```

The total demand is deliberately close to fleet capacity so capacity affects route design.

Do not freeze the 24-customer objective distance in automated tests. Assert invariants, not a claimed kilometre total. OR-Tools local search is not bit-deterministic across package versions.

### 12.2 Depot

The depot is fictional and located at a synthetic coordinate in the Vienna area. Coordinates are WGS84.

```csv
depot_id,latitude,longitude,name
DEPOT_01,48.1700,16.4400,ViennaCart Dispatch Depot
```

### 12.3 Customer Dataset

All coordinates and demands are synthetic.

```csv
customer_id,zone_id,latitude,longitude,demand_totes
C001,Z1,48.208,16.374,7
C002,Z1,48.214,16.360,6
C003,Z1,48.202,16.385,5
C004,Z1,48.220,16.380,7
C005,Z1,48.198,16.368,4
C006,Z1,48.211,16.392,6
C007,Z2,48.242,16.435,5
C008,Z2,48.255,16.420,5
C009,Z2,48.235,16.455,4
C010,Z2,48.265,16.445,6
C011,Z2,48.250,16.470,5
C012,Z2,48.230,16.425,4
C013,Z3,48.150,16.360,4
C014,Z3,48.142,16.375,3
C015,Z3,48.160,16.345,5
C016,Z3,48.135,16.350,4
C017,Z3,48.155,16.390,4
C018,Z3,48.145,16.330,4
C019,Z4,48.182,16.455,4
C020,Z4,48.168,16.470,3
C021,Z4,48.190,16.485,4
C022,Z4,48.160,16.450,3
C023,Z4,48.175,16.500,3
C024,Z4,48.195,16.465,3
```

Demand by zone:

```text
Z1 total demand: 35 totes
Z2 total demand: 29 totes
Z3 total demand: 24 totes
Z4 total demand: 20 totes
```

Z1 exceeds one van's capacity of 30 totes. The optimiser therefore cannot simply assign one vehicle to each geographic zone. It must move at least one Z1 customer into another vehicle route while balancing capacity and distance. This creates the intended CVRP challenge.

### 12.4 Sequential nearest-neighbour outcome

With the Section 13.2 distance procedure, the Section 15 baseline serves every customer.

```text
V01 load 29 totes
Route: DEPOT_01 -> C022 -> C020 -> C019 -> C024 -> C021 -> C023 -> C009 -> C007 -> DEPOT_01

V02 load 28 totes
Route: DEPOT_01 -> C017 -> C014 -> C013 -> C015 -> C018 -> C016 -> C005 -> DEPOT_01

V03 load 29 totes
Route: DEPOT_01 -> C003 -> C001 -> C002 -> C004 -> C012 -> DEPOT_01

V04 load 22 totes
Route: DEPOT_01 -> C006 -> C008 -> C010 -> C011 -> DEPOT_01

Customers served: 24 / 24
Demand served: 108 / 108
Status: feasible
comparison_eligible: true
unserved_customer_ids: []
```

A regression test must assert complete service and these four loads. Also assert that each route's distance equals the sum of Section 13.2 matrix legs. Do not freeze the OR-Tools objective for this scenario.

---

## 13. Distance Model

### 13.1 Learning Scenario

Use the explicit fixed distance matrix in Section 11. Convert published kilometres to integer metres by multiplying by 1000. Do not apply Haversine or a detour factor.

### 13.2 Geographic scenarios

Use this procedure for `VIENNA_STANDARD_24` and every generated geographic scenario. No other Earth radius, formula, or rounding rule is permitted in the MVP.

**Constants**

```text
EARTH_RADIUS_M = 6371000
default_detour_factor = 1.25
detour_factor domain = [1.00, 2.00] inclusive, stored with two decimal places
```

**Node order**

1. Depot first.
2. Then every customer sorted by `customer_id` ascending (lexicographic).
3. Index `0` is the depot. Customer `C001` precedes `C002`.

**Haversine great-circle distance in metres**, with latitudes and longitudes in decimal degrees:

```text
φ1 = radians(lat_i)
φ2 = radians(lat_j)
Δφ = radians(lat_j - lat_i)
Δλ = radians(lon_j - lon_i)
a  = sin²(Δφ / 2) + cos(φ1) * cos(φ2) * sin²(Δλ / 2)
a  = min(1, max(0, a))
c  = 2 * atan2(sqrt(a), sqrt(1 - a))
haversine_metres = EARTH_RADIUS_M * c
```

Use Python 3.12 `math.radians`, `math.sin`, `math.cos`, `math.atan2`, and `math.sqrt`. Do not use `math.asin` or a Vincenty formula.

**Detour and rounding**

```text
raw_metres = haversine_metres * detour_factor
integer_metres = floor(raw_metres + 0.5)
```

Distances are non-negative, so `floor(x + 0.5)` is round-half-up. Do not use Python 3's `round()`, which uses banker's rounding and can break symmetry.

**Build one triangle and mirror**

1. Set `d_ii = 0` for every node.
2. For each pair with `i < j`, compute `integer_metres` once.
3. Set `d_ij = d_ji = integer_metres`.
4. Never compute the reverse pair independently.

Required properties after construction:

- diagonal values are zero
- matrix is symmetric by construction
- internal unit is integer metres
- displayed unit is kilometres with three decimal places: `value_m / 1000`, format to three decimals
- the same coordinates, detour factor, and node order always produce the same matrix

Required user-facing label:

> Estimated synthetic distance. This is not a live road or traffic measurement.

On geographic maps, route polylines are **schematic straight connections** between stops, drawn from this synthetic matrix. They are not road geometry and must not be labelled as driving directions.

Do not call an external routing service at runtime in the MVP.

A cached road-network matrix may be considered only after the CVRP MVP is complete.

---

## 14. Scenario Generation

The fixed portfolio dataset must always be available.

The application may also generate synthetic scenarios after the fixed scenario works.

### 14.1 Generator request

```json
{
  "random_seed": 42,
  "customer_count": 24,
  "vehicle_count": 4,
  "vehicle_capacity_totes": 30,
  "detour_factor": 1.25,
  "geographic_zone_weights": {
    "Z1": 0.25,
    "Z2": 0.25,
    "Z3": 0.25,
    "Z4": 0.25
  }
}
```

| Field | Type | Domain | Default |
|---|---|---|---|
| `random_seed` | integer | 0 to 2147483647 inclusive | 42 |
| `customer_count` | integer | 1 to 50 inclusive | required |
| `vehicle_count` | integer | 1 to 10 inclusive | required |
| `vehicle_capacity_totes` | integer | 1 to 100 inclusive | required |
| `detour_factor` | decimal | 1.00 to 2.00 inclusive, two decimal places | 1.25 |
| `geographic_zone_weights` | four numbers | each ≥ 0; sum = 1 ± 1e-9 | 0.25 each |

Reject any request outside those domains with status `invalid`. Do not normalise weights that do not already sum to one. Do not let a visitor generate a 500-customer solve.

Generated identifiers:

```text
scenario_id    GEN_{seed}_{customer_count}_{vehicle_count}
depot_id       DEPOT_01
depot coords   48.1700, 16.4400   (same synthetic depot as Vienna Standard)
customer_id    C001, C002, ... zero-padded to three digits, in creation order
vehicle_id     V01, V02, ... zero-padded to two digits, in creation order
```

### 14.2 Random-number generator

Use Python 3.12 `random.Random(random_seed)` only. Do not use NumPy, `random.seed` on the global module, or `SystemRandom`.

For each customer `t = 1 .. customer_count`, in that order, draw **exactly four** numbers in this order:

1. `u_zone = rng.random()` in `[0.0, 1.0)`
2. `u_lat  = rng.uniform(-0.015, 0.015)`
3. `u_lon  = rng.uniform(-0.015, 0.015)`
4. `u_demand = rng.random()` in `[0.0, 1.0)`

Do not draw extra unused random numbers.

### 14.3 Zone selection

Zones and default centres (WGS84):

```text
Z1 central urban cluster                 48.209, 16.377
Z2 north-east residential cluster        48.246, 16.442
Z3 southern mixed-use cluster            48.148, 16.358
Z4 eastern residential and commercial    48.178, 16.471
```

Let `w_Z1, w_Z2, w_Z3, w_Z4` be the requested weights in that order. Cumulative edges:

```text
c1 = w_Z1
c2 = w_Z1 + w_Z2
c3 = w_Z1 + w_Z2 + w_Z3
c4 = 1
```

Select the zone from `u_zone`:

```text
Z1 if u_zone < c1
Z2 if c1 <= u_zone < c2
Z3 if c2 <= u_zone < c3
Z4 otherwise
```

If a prefix weight is 0, that zone is never selected.

### 14.4 Coordinate offset

```text
latitude  = clip(zone_centre_lat + u_lat,  48.10, 48.32)
longitude = clip(zone_centre_lon + u_lon,  16.25, 16.55)
```

`clip(x, lo, hi)` is `min(hi, max(lo, x))`. Offsets are independent Uniform(-0.015, 0.015) draws from `rng.uniform`. Store coordinates as floats; do not round them before Haversine. Display maps may show six decimal places.

Coordinates must always be described as synthetic.

### 14.5 Demand sampling

Use integer tote demand from 1 to 8 with this exact discrete distribution:

| Totes | Probability | Cumulative upper bound (exclusive) |
|---:|---:|---:|
| 1 | 0.05 | 0.05 |
| 2 | 0.10 | 0.15 |
| 3 | 0.15 | 0.30 |
| 4 | 0.20 | 0.50 |
| 5 | 0.20 | 0.70 |
| 6 | 0.15 | 0.85 |
| 7 | 0.10 | 0.95 |
| 8 | 0.05 | 1.00 |

```text
1 if u_demand < 0.05
2 if 0.05 <= u_demand < 0.15
3 if 0.15 <= u_demand < 0.30
4 if 0.30 <= u_demand < 0.50
5 if 0.50 <= u_demand < 0.70
6 if 0.70 <= u_demand < 0.85
7 if 0.85 <= u_demand < 0.95
8 otherwise
```

Do not silently resample until a scenario becomes feasible.

Generate the requested scenario once, build the Section 13.2 matrix, run the feasibility checks, and report the domain status. A generated scenario may be `infeasible` (Check 1 or 2) and still stored for inspection.

---

## 15. Baseline Heuristic

Implement a capacity-aware nearest-neighbour baseline.

### Procedure

1. Open the next unused vehicle in `vehicle_id` ascending order, starting at the depot.
2. Among unserved customers whose demand fits the remaining capacity, select the nearest customer to the current node.
3. If several customers share that minimum distance, pick the lowest `customer_id`.
4. Add that customer to the route.
5. Update remaining vehicle capacity and the current node.
6. Continue until no unserved customer fits.
7. Return the vehicle to the depot.
8. If unserved customers remain and an unused vehicle exists, go to step 1.
9. If unserved customers remain and the fleet is exhausted, stop with `heuristic_incomplete`.

### Incomplete baseline payload

When status is `heuristic_incomplete`, the run **must** include:

```text
status: heuristic_incomplete
comparison_eligible: false
unserved_customer_ids: sorted list of unserved customer IDs
partial_distance_metres: sum of constructed route distances, including depot returns
objective_distance_metres: null
baseline_distance: null
distance_improvement_percentage: null
customers_served: count of customers on constructed routes
demand_served_totes: sum of those demands
```

Constructed routes, loads, and `partial_distance_metres` are still stored and displayed, labelled as a partial plan. Page 3 must not compute an improvement percentage from `partial_distance_metres`.

When the baseline is complete:

```text
status: feasible
comparison_eligible: true
unserved_customer_ids: []
partial_distance_metres: null
objective_distance_metres: total complete distance
```

### Important interpretation

The greedy baseline may fail even when the OR-Tools model finds a feasible solution. LEARNING_6 is the canonical example. In that case, display:

```text
Baseline status: heuristic_incomplete
Optimiser status: feasible
```

Do not incorrectly declare the whole scenario infeasible because the baseline failed.

Show the Page 3 baseline-versus-optimised comparison only when **both** runs have `comparison_eligible: true`.

The baseline and optimiser must use the same:

- depot
- customers
- demands
- vehicle capacity
- fleet size
- distance matrix

---

## 16. OR-Tools Implementation

Use:

- `RoutingIndexManager`
- `RoutingModel`
- an integer distance callback
- a unary demand callback
- the OR-Tools capacity dimension

All customers are mandatory. Do not add disjunction penalties in the MVP.

Pin versions in Phase 1:

```text
Python 3.12
ortools==9.11.4210
```

If that exact OR-Tools wheel is unavailable, pin the latest published 9.11.x or 9.12.x wheel and record the chosen version in `requirements.txt` and this specification. Do not float to a new major version.

Suggested initial solver settings:

```text
first_solution_strategy: PATH_CHEAPEST_ARC
local_search_metaheuristic: GUIDED_LOCAL_SEARCH
time_limit_seconds: 5
```

`PATH_CHEAPEST_ARC` is a cheapest-arc construction, related in spirit to nearest neighbour. Guided local search is what should improve on that first solution. The custom Section 15 baseline remains the operational benchmark because it is fully specified and testable without OR-Tools.

Supported time-limit choices:

```text
1 second
5 seconds
10 seconds
```

The response should distinguish:

- `feasible` — a complete feasible solution was found
- `infeasible` — Check 1 or Check 2 failed; the solver was not run
- `invalid` — broken input
- `error` — unexpected runtime failure
- `heuristic_incomplete` — baseline only; some customers unserved
- `no_solution_found` — pre-checks passed; search returned no complete plan

Also return `solver_termination` from Section 10.5.

Never map a timeout or a missing first solution to `infeasible`.

Do not claim global optimality for normal portfolio scenarios.

Preferred wording:

> Best feasible solution found within the configured search limit.

The `LEARNING_6` fixture is the exception because its optimum can be verified independently through exhaustive enumeration.

OR-Tools guided local search is not guaranteed bit-deterministic across CPU, seed, or package version. Preserve determinism in data, matrices, and the baseline. Do not write tests that freeze the Vienna 24 objective kilometres.

---

## 17. Required KPIs

### Formulae

```text
customers served              = count of customers appearing on a used route
demand served                 = sum of those customers' tote demand
vehicles used                 = count of vehicles with at least one customer
total route distance          = sum of all route distances, including depot return legs
average distance per delivery = total route distance / customers served
used-fleet utilisation        = demand served / (vehicles used * Q)
available-fleet utilisation   = demand served / (vehicles available * Q)
longest route distance        = max distance among used vehicles
shortest non-empty route      = min distance among used vehicles
route-distance imbalance      = longest route distance - shortest non-empty route
```

If `customers served = 0`, average distance per delivery is null.

If the plan is not `comparison_eligible`, `baseline_distance` and `distance improvement percentage` are null.

If fewer than two vehicles are used, route-distance imbalance is null and the comparison row is hidden.

Utilisation rates are stored as fractions and displayed as percentages to one decimal place.

Average distance per delivery **includes** the outbound and return depot legs. The denominator is customers served, not stops and not including the depot as a delivery.

### Scenario-Level KPIs

- customer orders
- customer orders served
- total demand in totes
- demand served in totes
- available vehicles
- vehicles used
- total fleet capacity
- total route distance in kilometres
- average distance per delivery
- aggregate capacity utilisation across used vehicles
- aggregate capacity utilisation across all available vehicles
- longest route distance
- shortest non-empty route distance
- route-distance imbalance
- baseline distance
- optimised distance
- distance improvement percentage

### Vehicle-Level KPIs

- vehicle ID
- route sequence
- customer count
- assigned demand
- vehicle capacity
- remaining capacity
- capacity utilisation
- route distance

### Customer-Level Results

- customer ID
- demand
- assigned vehicle
- route sequence position
- previous node
- next node
- inbound leg distance
- cumulative route distance
- service count

For every valid complete solution:

```text
customers served = total customers
demand served = total demand
service count per customer = 1
```

---

## 18. Baseline Versus Optimised Comparison

Show this comparison only when the baseline constructs a complete feasible solution.

| KPI | Baseline | Optimised | Change |
|---|---:|---:|---:|
| Customers served | Dynamic | Dynamic | Dynamic |
| Demand served | Dynamic | Dynamic | Dynamic |
| Vehicles used | Dynamic | Dynamic | Dynamic |
| Total distance | Dynamic | Dynamic | Dynamic |
| Distance per delivery | Dynamic | Dynamic | Dynamic |
| Average used-vehicle utilisation | Dynamic | Dynamic | Dynamic |
| Route-distance imbalance | Dynamic | Dynamic | Dynamic |

If route-distance imbalance is null on either side, omit that row.

Distance improvement:

\[
Improvement\% = \frac{BaselineDistance-OptimisedDistance}{BaselineDistance}\times100
\]

Never hard-code a percentage-improvement claim.

LEARNING_6 does not get this table for sequential NN, because that baseline is incomplete. Vienna Standard 24 is the public complete comparison.

---

## 19. Frontend Product Design

The frontend should look like a professional logistics planning tool, not a school exercise.

The visible product title is `LastMile Lab: ViennaCart CVRP Dispatch Planner`. LastMile Lab is the portfolio project. ViennaCart is the fictional operator.

Use Streamlit and Plotly unless a later decision explicitly changes the frontend technology.

Geographic maps must use Plotly with the `open-street-map` style, or an equivalent tile source that needs no Mapbox token. Do not add a Mapbox secret.

Route lines on the map are straight schematic connections between consecutive stops. Caption every map:

> Schematic connections based on synthetic estimated distances. These lines are not road geometry or live driving directions.

Hold `scenario_id`, `baseline_run_id`, and `optimised_run_id` in `st.session_state`. Call the FastAPI endpoints. Do not recalculate optimisation, baseline construction, or KPI formulae inside Streamlit widgets.

### General Design Principles

- restrained professional visual identity
- clear logistics terminology
- consistent vehicle colours
- compact controls
- readable data tables
- no unnecessary animations
- no decorative AI branding
- no oversized headings
- no fake operational claims

### Page 1: Dispatch Setup

Purpose: Understand and validate the problem before solving it.

Show:

- scenario selector
- fixed Learning scenario
- fixed Vienna Standard scenario
- optional generated scenario
- customer count
- total demand
- fleet size
- capacity per van
- total fleet capacity
- theoretical minimum vehicle count
- aggregate demand-to-capacity ratio
- feasibility pre-check, with Check 3 labelled informational
- customer demand table
- customer map for geographic scenarios
- matrix-first distance view for LEARNING_6; no fake geo map
- advanced expandable distance matrix

Actions:

```text
Load Scenario
Validate Scenario
Run Baseline
Run Optimisation
```

### Page 2: Route Plan

Show:

- colour-coded route map for geographic scenarios
- schematic or table-only routes for LEARNING_6
- depot marker
- customer markers sized or labelled by tote demand
- route sequence
- one colour per vehicle
- route cards
- capacity bars
- unused vehicles

Example vehicle card:

```text
Van V01
Route: Depot -> C004 -> C011 -> C003 -> Depot
Orders: 3
Load: 29 / 30 totes
Capacity utilisation: 96.7%
Distance: dynamic km
```

### Page 3: Baseline vs Optimised

Show:

- side-by-side KPI table
- total-distance comparison chart
- vehicle-load comparison chart
- route-distance comparison chart
- concise dynamically generated operational summary

The summary must be based on calculated values. Do not use an LLM.

If the baseline is `heuristic_incomplete`, explain that fact and still show the optimiser result. Do not invent a baseline distance.

### Page 4: Model Inspector

This page is important for demonstrating that the author understands the model.

Show:

- demand-satisfaction table
- one row per customer
- assigned vehicle
- demand served
- service count
- pass or fail constraint status
- vehicle-capacity reconciliation using reconstructed cumulative loads, not MILP potentials `w_ik`
- incoming and outgoing selected arcs reconstructed from routes
- selected route matrix for each vehicle, reconstructed from consecutive stops
- a note that these matrices are reconstructed, not OR-Tools native variables
- distance matrix
- solver configuration

For Vienna Standard 24, default the per-vehicle route matrix to a compact selected-arc list. Offer the full 25 × 25 matrix behind an expander. LEARNING_6 can show the full matrix by default.

Example demand check:

| Customer | Required | Delivered | Vehicle | Visit Count | Check |
|---|---:|---:|---|---:|---|
| C001 | 7 | 7 | V02 | 1 | Pass |

### Page 5: Learning Lab

Use the six-customer fixture to explain:

- how to read a distance matrix
- how to read reconstructed `x_ijk`
- why row sums are outgoing movements
- why column sums are incoming movements
- how demand assignment affects vehicle capacity
- why sequential nearest neighbour is `heuristic_incomplete` on this tight instance
- how the 34.000 km reference packing differs from sequential construction
- why the 31.000 km plan is shorter than that packing
- why the nearest feasible route may not be the shortest total solution
- why `INFEASIBLE_BIN_PACKING` passes Checks 1 and 2 and is still unschedulable without split deliveries

This page should reuse actual backend calculations rather than contain a disconnected hard-coded demonstration. The 34.000 km packing may be stored as a named reference plan computed by the same distance engine.

---

## 20. Backend Architecture

Keep optimisation logic independent from the frontend.

Recommended flow:

```text
Streamlit frontend
        |
        v
FastAPI REST API
        |
        +-- Scenario validation
        +-- Distance matrix
        +-- Baseline heuristic
        +-- OR-Tools optimiser
        +-- KPI and reconciliation engine
        +-- Run storage and export
```

Through Phase 7, run storage is an in-memory repository. Generated scenarios live in that store for the process lifetime. Phase 8 replaces the repository implementation with DuckDB without changing API contracts.

The core optimisation package must also be callable directly from tests without starting FastAPI or Streamlit.

---

## 21. Recommended Repository Structure

```text
viennacart-cvrp/
|
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- api/
|   |   |   |-- scenarios.py
|   |   |   |-- planning.py
|   |   |   `-- runs.py
|   |   |-- models/
|   |   |   |-- requests.py
|   |   |   `-- responses.py
|   |   |-- core/
|   |   |   |-- domain.py
|   |   |   |-- validation.py
|   |   |   |-- distance_matrix.py
|   |   |   |-- baseline.py
|   |   |   |-- optimizer.py
|   |   |   |-- kpis.py
|   |   |   `-- reconciliation.py
|   |   `-- storage/
|   |       |-- repository.py
|   |       `-- memory.py
|   `-- requirements.txt
|
|-- frontend/
|   |-- Home.py
|   `-- pages/
|       |-- 1_Dispatch_Setup.py
|       |-- 2_Route_Plan.py
|       |-- 3_Baseline_vs_Optimised.py
|       |-- 4_Model_Inspector.py
|       `-- 5_Learning_Lab.py
|
|-- data/
|   |-- fixtures/
|   |   |-- learning_6_customers.csv
|   |   |-- learning_6_distance_matrix.csv
|   |   |-- learning_6_vehicles.csv
|   |   |-- vienna_standard_24_customers.csv
|   |   |-- vienna_standard_24_depot.csv
|   |   |-- vienna_standard_24_vehicles.csv
|   |   |-- infeasible_single_oversize.yaml
|   |   |-- infeasible_fleet_overflow.yaml
|   |   `-- infeasible_bin_packing.yaml
|   `-- generated/
|
|-- tests/
|   |-- test_validation.py
|   |-- test_distance_matrix.py
|   |-- test_baseline.py
|   |-- test_optimizer_learning_6.py
|   |-- test_learning_6_enumeration.py
|   |-- test_vienna_baseline.py
|   |-- test_bin_packing.py
|   |-- test_optimizer_invariants.py
|   |-- test_kpi_reconciliation.py
|   `-- test_api.py
|
|-- docs/
|   |-- mathematical_formulation.md
|   |-- data_dictionary.md
|   |-- architecture.md
|   |-- methodology.md
|   `-- screenshots/
|
|-- .github/workflows/ci.yml
|-- Dockerfile.backend
|-- Dockerfile.frontend
|-- docker-compose.yml
|-- README.md
|-- LICENSE
|-- .gitignore
`-- .env.example
```

Do not create a giant Streamlit file. Business logic must not be implemented inside UI widgets.

Intended public licence: MIT, unless Phase 10 explicitly chooses another OSI licence.

---

## 22. Core Data Schemas

### Scenario

```text
scenario_id: string
scenario_name: string
random_seed: integer or null
depot_id: string
customer_count: integer
vehicle_count: integer
vehicle_capacity_totes: integer
detour_factor: decimal
distance_unit: string
has_geographic_coordinates: boolean
created_at: timestamp
is_synthetic: boolean
```

### Depot

```text
depot_id: string
scenario_id: string
name: string
latitude: decimal or null
longitude: decimal or null
```

LEARNING_6 stores `DEPOT_L6` with null coordinates.

### Customer

```text
customer_id: string
scenario_id: string
zone_id: string or null
latitude: decimal or null
longitude: decimal or null
demand_totes: integer
```

### Vehicle

```text
vehicle_id: string
scenario_id: string
capacity_totes: integer
```

### Planning Run

```text
run_id: string
scenario_id: string
run_type: baseline or optimised
status: pending, feasible, infeasible, invalid, error, heuristic_incomplete, no_solution_found
comparison_eligible: boolean
unserved_customer_ids: list of strings
partial_distance_metres: integer or null
solver_termination: success, timeout, no_first_solution, search_exhausted, not_run, error, or null
solver_time_limit_seconds: integer or null
solver_runtime_seconds: decimal or null
objective_distance_metres: integer or null
vehicles_used: integer or null
created_at: timestamp
```

### Route

```text
run_id: string
vehicle_id: string
is_used: boolean
assigned_demand_totes: integer
capacity_totes: integer
distance_metres: integer
customer_count: integer
```

### Route Stop

```text
run_id: string
vehicle_id: string
sequence_number: integer
node_id: string
node_type: depot or customer
demand_totes: integer
load_after_service_totes: integer   # reconstructed operational cumulative load, not w_ik
leg_distance_metres: integer
cumulative_distance_metres: integer
```

---

## 23. API Design

Base prefix for resource endpoints:

```text
/api/v1
```

`GET /health` stays outside that prefix. It is a liveness probe, not a business resource.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/api/v1/scenarios` | List available scenarios |
| GET | `/api/v1/scenarios/{scenario_id}` | Retrieve a scenario |
| POST | `/api/v1/scenarios/generate` | Generate a deterministic synthetic scenario |
| POST | `/api/v1/scenarios/validate` | Run data and feasibility pre-checks |
| POST | `/api/v1/plans/baseline` | Run nearest-neighbour baseline |
| POST | `/api/v1/plans/optimise` | Run OR-Tools CVRP optimisation |
| GET | `/api/v1/runs/{run_id}` | Retrieve run metadata and summary |
| GET | `/api/v1/runs/{run_id}/routes` | Retrieve vehicle routes and stops |
| GET | `/api/v1/runs/{run_id}/checks` | Retrieve constraint reconciliation |
| GET | `/api/v1/runs/{run_id}/export` | Export results |

### Validate Request

```json
{
  "scenario_id": "VIENNA_STANDARD_24"
}
```

Validation runs against a stored scenario, including in-memory generated scenarios.

### Export

```text
GET /api/v1/runs/{run_id}/export?format=json
GET /api/v1/runs/{run_id}/export?format=csv
```

- `format=json` returns `application/json` for the complete run
- `format=csv` returns `application/zip` containing the assignment, stop, and vehicle CSVs, or a documented multi-file equivalent
- default `format` is `json`

Every export must include `scenario_id` and `run_id`.

### Error Body

```json
{
  "status": "invalid",
  "code": "UNKNOWN_SCENARIO",
  "message": "Scenario 'MISSING' was not found.",
  "checks": []
}
```

`checks` lists named pre-check results when validation or planning stops on domain status. HTTP mapping is locked:

| Domain status | HTTP |
|---|---|
| `feasible` | 200 |
| `infeasible` | 200 |
| `heuristic_incomplete` | 200 |
| `no_solution_found` | 200 |
| `invalid` | 400 |
| unknown `scenario_id` | 404 |
| `error` | 500 |

A successfully evaluated business scenario always returns HTTP 200 plus a domain `status`. Check 1 / Check 2 failures are `200` with `status: "infeasible"`. Do not use HTTP 409.

### Optimisation Request

```json
{
  "scenario_id": "LEARNING_6",
  "solver_time_limit_seconds": 5
}
```

### Optimisation Response

Verified LEARNING_6 shape. Every numeric field is calculated, not a decorative example.

```json
{
  "run_id": "RUN_L6_OPT",
  "scenario_id": "LEARNING_6",
  "status": "feasible",
  "comparison_eligible": true,
  "solver_termination": "success",
  "solver_runtime_seconds": 0.12,
  "customers_total": 6,
  "customers_served": 6,
  "unserved_customer_ids": [],
  "demand_total_totes": 20,
  "demand_served_totes": 20,
  "vehicles_available": 2,
  "vehicles_used": 2,
  "total_distance_km": 31.0,
  "objective_distance_metres": 31000,
  "message": "Independently verified optimum for LEARNING_6."
}
```

For `VIENNA_STANDARD_24`, use the same field names. Put `objective_distance_metres / 1000` in `total_distance_km`. The UI always displays three decimal places. Never hard-code a Vienna distance in this specification or in source.

Incomplete baseline example:

```json
{
  "run_id": "RUN_L6_NN",
  "scenario_id": "LEARNING_6",
  "status": "heuristic_incomplete",
  "comparison_eligible": false,
  "unserved_customer_ids": ["C4"],
  "partial_distance_metres": 27000,
  "objective_distance_metres": null,
  "customers_served": 5,
  "demand_served_totes": 15,
  "message": "Baseline constructed a partial plan. Improvement percentage is not defined."
}
```

CORS: allow the Streamlit origin from configuration, not `*`. See `.env.example`.

---

## 24. Required Automated Tests

### 24.1 Data Validation Tests

- duplicate customer ID rejected
- zero demand rejected
- negative demand rejected
- non-integer tote demand rejected
- zero vehicle capacity rejected
- missing depot rejected
- invalid coordinates rejected
- `INFEASIBLE_SINGLE_OVERSIZE` marked infeasible
- `INFEASIBLE_FLEET_OVERFLOW` marked infeasible
- `INFEASIBLE_BIN_PACKING` passes Checks 1 and 2
- independent enumeration proves `INFEASIBLE_BIN_PACKING` has no feasible unsplit assignment
- optimiser on `INFEASIBLE_BIN_PACKING` returns `no_solution_found`, not `infeasible`
- generator rejects `customer_count > 50` and `vehicle_count > 10`
- generator rejects `detour_factor` outside `[1.00, 2.00]`

### 24.2 Distance Matrix Tests

- correct dimensions
- zero diagonal
- no negative distances
- symmetry for MVP
- deterministic values
- kilometre display reconciles with integer metres
- LEARNING_6 cell `Depot → C1` stores `3000` metres and displays `3.000 km`
- geographic matrix is symmetric by triangle-and-mirror construction
- `floor(raw + 0.5)` is used, not Python `round()`
- `EARTH_RADIUS_M` is `6371000`

### 24.3 Learning Fixture Tests

- total demand equals 20
- total fleet capacity equals 20
- sequential nearest-neighbour status is `heuristic_incomplete`
- `comparison_eligible` is false
- `unserved_customer_ids` equals `["C4"]`
- `partial_distance_metres` equals 27000
- `objective_distance_metres` is null
- V01 route is Depot → C1 → C2 → C3 → Depot with load 9 and distance 16000 m
- V02 route is Depot → C6 → C5 → Depot with load 6 and distance 11000 m
- independently verified optimum equals 31000 m
- displayed optimum is `31.000 km`
- every customer is served once in the optimal plan
- each vehicle load equals 10 in the optimal plan
- both optimal routes start and end at depot
- brute-force enumeration in `test_learning_6_enumeration.py` agrees with 31000 m
- baseline `heuristic_incomplete` does not mark the optimiser infeasible

Do not assert that sequential NN equals 34 km.

### 24.4 Optimisation Invariant Tests

For every feasible solution:

- every customer appears exactly once
- no customer appears on two vehicle routes
- demand served equals total demand
- each route starts at depot
- each route ends at depot
- every selected arc belongs to one vehicle
- route demand does not exceed capacity
- route distance equals the sum of its legs
- scenario distance equals the sum of route distances
- unused vehicles contain no customer stops
- no disconnected customer cycle exists

Do not assert a fixed objective for `VIENNA_STANDARD_24`.

### 24.5 Baseline Tests

- nearest feasible customer is selected
- equal distances break ties by lowest `customer_id`
- vehicles open in `vehicle_id` order
- remaining capacity updates correctly
- new vehicle begins when no remaining customer fits
- all served customers are unique
- baseline failure does not mark optimiser infeasible
- `VIENNA_STANDARD_24` sequential NN serves all 24 customers
- Vienna NN loads are V01 29, V02 28, V03 29, V04 22
- Vienna NN routes match Section 12.4
- Vienna NN `comparison_eligible` is true

### 24.6 API Tests

- health endpoint returns HTTP 200
- known scenario loads successfully
- invalid scenario returns a clear validation error
- baseline endpoint returns structured output
- optimisation endpoint returns structured output
- unknown scenario returns HTTP 404
- Check 1 / Check 2 failure returns HTTP 200 with `status: "infeasible"`
- solver timeout without a plan returns HTTP 200 with `status: "no_solution_found"` and `solver_termination: "timeout"`
- incomplete baseline returns HTTP 200 with `comparison_eligible: false` and null improvement
- run result endpoints reconcile with the optimisation response
- export `format=json` includes `scenario_id` and `run_id`

---

## 25. Persistence and Export

Persistence on disk is not required until the optimisation and KPI phases work correctly.

Through Phase 7, use the in-memory repository.

From Phase 8, use DuckDB for lightweight run history, keeping the same repository interface.

Store:

- scenarios
- customers
- vehicles
- planning runs
- routes
- route stops
- constraint checks
- scenario KPIs
- vehicle KPIs

Exports:

- customer assignments as CSV
- route stops as CSV
- vehicle summary as CSV
- complete run result as JSON

Every export must include `scenario_id` and `run_id`.

---

## 26. Documentation Requirements

### README

The public README must contain:

1. title `LastMile Lab: ViennaCart CVRP Dispatch Planner` and one-sentence value proposition
2. live application URL
3. hero screenshot or short GIF
4. business problem
5. exact MVP assumptions
6. demand and capacity explanation
7. baseline versus optimised result from the fixed **Vienna Standard 24** demo, computed at publish time, with OR-Tools version and time limit stated
8. application screenshots
9. architecture
10. mathematical formulation
11. data methodology and synthetic-data disclosure
12. technology stack
13. local setup for Windows PowerShell
14. test instructions
15. API documentation link
16. limitations
17. roadmap
18. licence

Do not present LEARNING_6 sequential NN as a complete 34 km baseline in the README.

### Mathematical Formulation

`docs/mathematical_formulation.md` must use consistent indices.

It must clearly distinguish:

- `x_ijk`, the selected arc for vehicle `k`, defined only for `i ≠ j`
- `y_ik`, the customer assignment to vehicle `k`
- `u_k`, vehicle use
- `w_ik`, MTZ load-order potential for customer `i` on vehicle `k`, not the displayed operational load
- `q_i`, the fixed customer demand
- `Q_k`, the vehicle capacity

It must include the corrected MTZ inequality with right-hand side `Q_k - q_j y_{jk}`, the assignment-linked bounds, the V01/C4 counter-example for the incorrect form, the `u_k` linking constraints, and the table in Section 9.8.

It must not repeat the indexing ambiguities present in the earlier warehouse thesis formulation.

It must not claim that OR-Tools solves this MILP as written.

### Data Dictionary

`docs/data_dictionary.md` must define every field, unit, allowed value, and validation rule.

### Methodology

`docs/methodology.md` must explain:

- why totes were selected as the demand unit
- why split delivery is excluded
- why the MVP minimises distance rather than a financial cost
- how the distance matrix is generated, including Earth radius, Haversine, rounding, and triangle mirroring
- how the baseline works, including tie-breaks, LEARNING_6 incompleteness, and `comparison_eligible`
- how OR-Tools implements capacity
- why a solver timeout is `no_solution_found`, not `infeasible`
- how solution invariants are verified
- why normal solver output is described as feasible rather than globally optimal
- why LEARNING_6 is the exception
- why aggregate capacity checks are not a complete unsplit-feasibility test

### Environment Example

`.env.example` must document at least:

```text
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:8501
LOG_LEVEL=INFO
```

No secrets. No Mapbox token.

---

## 27. Synthetic Data Disclosure

Display this notice in the application and README:

> LastMile Lab is a fictional portfolio case study. ViennaCart is a fictional operator. All depots, customers, order demands, routes, distances, and operating assumptions are synthetic. The application does not use proprietary customer data or live Vienna traffic information.

---

## 28. Implementation Phases for Cursor

Cursor must work phase by phase. At the start of every task, state the active phase. At the end, report files changed, tests run, results, and remaining issues. Do not begin the next phase without user instruction.

### Phase 0: Model Confirmation

Before writing application code:

- create the mathematical formulation document, including the corrected MTZ inequality, domains, and the OR-Tools mapping table
- create the data dictionary, including every domain status in Section 10.5
- create the two fixed scenario CSV datasets plus vehicle files and the three infeasible fixtures
- verify all demand totals manually
- verify the `LEARNING_6` optimum independently by enumerating the two feasible partitions and all depot-start sequences
- record that sequential NN on LEARNING_6 is `heuristic_incomplete` with C4 unserved
- record that sequential NN on `VIENNA_STANDARD_24` serves all 24 customers with loads 29, 28, 29, 22
- record that `INFEASIBLE_BIN_PACKING` passes Checks 1 and 2 and has no feasible packing

Stop and review.

### Phase 1: Foundation

Create:

- repository structure
- Python 3.12 virtual environment instructions
- dependencies, including pinned `ortools==9.11.4210` or the recorded fallback 9.x wheel
- Pydantic domain models
- FastAPI application
- `/health`
- pytest configuration
- ruff configuration

Stop and test.

### Phase 2: Validation and Distance Matrix

Implement:

- scenario loading
- customer and fleet validation
- feasibility pre-checks, with Check 3 informational
- Haversine calculation with `EARTH_RADIUS_M = 6371000`
- detour factor in `[1.00, 2.00]`
- triangle-and-mirror integer distance matrix
- round-half-up via `floor(x + 0.5)`
- LEARNING_6 km-to-metre conversion
- matrix validation

Stop and test.

### Phase 3: Baseline

Implement:

- capacity-aware nearest-neighbour baseline with documented tie-breaks
- route extraction
- `heuristic_incomplete` status and incomplete payload
- baseline KPI calculation on complete plans only
- Vienna Standard 24 complete-service regression

Stop and test. Confirm LEARNING_6 matches Section 11.4 and Vienna matches Section 12.4.

### Phase 4: OR-Tools CVRP

Implement:

- routing manager
- routing model
- distance callback
- demand callback
- capacity dimension
- mandatory customer visits
- route extraction
- solver status handling, including `no_solution_found` and `solver_termination`
- learning-fixture regression test for 31000 m
- enumeration test
- bin-packing fixture test
- solution-invariant tests

This is the most important learning phase. Explain the relationship between the mathematical variables and OR-Tools implementation before coding.

Stop and test.

### Phase 5: KPI and Reconciliation Engine

Implement:

- scenario KPIs using Section 17 formulae
- vehicle KPIs
- customer assignment output
- constraint checks
- independent distance reconciliation
- independent demand reconciliation
- baseline comparison when the baseline is complete

Stop and test.

### Phase 6: API Completion

Implement all MVP endpoints, the locked HTTP mapping, the error body, export formats, CORS, and API tests.

Stop and test.

### Phase 7: Streamlit Frontend

Implement pages in this order:

1. Dispatch Setup
2. Route Plan
3. Baseline vs Optimised
4. Model Inspector
5. Learning Lab

Use backend API responses. Do not recalculate optimisation logic in Streamlit.

Use `open-street-map` tiles. Label route lines as schematic synthetic connections. Skip the geo map on LEARNING_6.

Stop and test locally.

### Phase 8: Persistence and Export

Implement:

- DuckDB run history behind the same repository interface
- CSV exports
- JSON export

Stop and test.

### Phase 9: Engineering and Deployment

Implement:

- structured logging
- graceful frontend error handling
- GitHub Actions on Python 3.12
- Dockerfiles
- Docker Compose running API and Streamlit together
- `.env.example` with `BACKEND_URL` and `CORS_ORIGINS`
- deployment configuration for a host that can run Compose, or a single VM running both processes

Do not target Streamlit Community Cloud as the public demo host. It cannot run the FastAPI sidecar.

Run from a clean environment before publishing.

### Phase 10: Portfolio Polish

Complete:

- public README
- screenshots
- demonstration results for Vienna Standard 24, with solver version and time limit
- architecture diagram
- methodology
- limitations
- live frontend URL
- working API documentation URL, if publicly exposed
- public GitHub repository
- MIT licence file, unless another OSI licence was chosen

Verify that all links work without being signed into the owner's account.

---

## 29. Cursor Working Rules

1. Read this entire specification before changing architecture or model logic.
2. Treat this as a clean CVRP rebuild.
3. Inspect existing files before adding or replacing code.
4. Work on only one implementation phase at a time.
5. Explain the intended model change before implementing it.
6. Keep functions small and typed.
7. Use Pydantic at API boundaries.
8. Keep optimisation logic independent from FastAPI and Streamlit.
9. Keep KPI calculations independent from UI rendering.
10. Use integer metres and integer tote demand internally.
11. Preserve deterministic behaviour in data, matrices, and the baseline. Do not assume OR-Tools search is bit-deterministic.
12. Add or update tests whenever business logic changes.
13. Never silently change the unsplit-demand rule.
14. Never silently allow dropped customers.
15. Never hard-code optimisation improvements.
16. Never describe synthetic distances as live road distances.
17. Never label an ordinary OR-Tools solution globally optimal.
18. Do not add time windows or V2 features before the MVP definition of done is satisfied.
19. Do not place secrets in the repository. Do not add a Mapbox token.
20. Provide Windows PowerShell commands where local commands are needed.
21. Sequential nearest neighbour on LEARNING_6 is `heuristic_incomplete`. Do not treat 34.000 km as the NN result.
22. Reconstruct inspector matrices from routes. Do not claim OR-Tools solved the documented three-index MILP.
23. Never map an OR-Tools timeout or missing solution to `infeasible`.
24. Never use Python `round()` on distances. Use `floor(x + 0.5)` after building one triangle of the matrix.
25. Displayed loads are reconstructed from routes. Do not present `w_ik` as the operational tote load.

---

## 30. Definition of Done

The CVRP MVP is complete when a new visitor can:

1. Open the public application without signing in.
2. Understand the business problem within one minute.
3. Load the six-customer learning scenario.
4. Inspect customer demand and the distance matrix, without a misleading geo map.
5. See why each customer must be assigned once.
6. Run the baseline and see `heuristic_incomplete` with C4 unserved.
7. Run the OR-Tools optimiser.
8. Verify the 31.000 km optimal learning result, and inspect the 34.000 km reference packing in the Learning Lab.
9. Load the 24-customer Vienna scenario.
10. Inspect the demand-to-capacity challenge.
11. View colour-coded schematic routes on an OpenStreetMap canvas, labelled as synthetic connections not road geometry.
12. Inspect the assigned demand and remaining capacity of every van.
13. Confirm that every customer was served once.
14. Compare baseline and optimised distance on Vienna Standard 24.
15. Export the result.

Engineering completion requires:

- all automated tests pass
- all solution invariants pass
- KPI values reconcile with route legs and assignments
- LEARNING_6 enumeration test passes
- Vienna Standard 24 baseline serves all 24 customers
- GitHub Actions pass
- Docker Compose build succeeds
- local setup works from a fresh environment on Windows PowerShell
- README and documentation are complete
- public application and repository URLs work
- no real customer data are included
- no secrets are committed

---

## 31. Future Roadmap After MVP

Extensions should be added one at a time and compared against the CVRP baseline.

### V1.1

- user CSV upload
- saved scenario comparison
- capacity and fleet-size what-if analysis
- cached road-network distance matrix

### V1.2

- heterogeneous vehicle capacities
- fixed vehicle dispatch cost
- route workload balance reporting

### V2

- delivery time windows
- customer service duration
- maximum driver shift duration

### V3

- optional customers and business penalties
- split-delivery experiment
- multi-trip routing experiment

Do not implement these extensions until the CVRP MVP is complete, tested, and publicly demonstrable.

---

## 32. Final Project Principle

The project is not successful merely because OR-Tools returns coloured routes.

It is successful when the application proves, through inspectable data and tests, that:

```text
every customer was assigned exactly once
every customer's full demand was served
no vehicle exceeded capacity
every used route started and ended at the depot
all route distances reconciled with the distance matrix
the selected plan improved on a transparent baseline
```

On LEARNING_6, the last line is demonstrated by contrasting the incomplete greedy construction, the 34.000 km reference packing, and the 31.000 km verified optimum. On Vienna Standard 24, it is demonstrated by a complete baseline-versus-optimised KPI table.

The solver is one component. The real portfolio value is the complete decision-support workflow and the author's ability to explain it.
