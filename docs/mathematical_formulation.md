# Mathematical Formulation

**Product:** LastMile Lab: ViennaCart CVRP Dispatch Planner  
**Problem class:** Capacitated Vehicle Routing Problem (CVRP)  
**Document role:** Source of truth for the mixed-integer model the author must be able to explain.

This document records the three-index mixed-integer linear program (MILP) for the MVP. Google OR-Tools `RoutingModel` is the solver used in the application. It does **not** solve this MILP with a MIP solver. Section 8 maps each MILP symbol to the quantity the MVP actually obtains from returned routes.

---

## 1. Business interpretation

ViennaCart plans one static morning dispatch wave. One depot, a homogeneous van fleet, and a set of mandatory customer orders are known in advance.

Each order has an integer demand in standardized delivery totes. Each van has a tote capacity. Every customer order must be delivered in full by exactly one van. Split deliveries are forbidden. A van may remain unused. Every used van leaves the depot once, serves its assigned customers as a single trip, and returns to the same depot.

The objective is to minimise total travel distance. Distance is the MVP cost proxy. Driver time, wages, energy, emissions, and service-level penalties are out of scope.

---

## 2. Sets

```text
N     set of customers
N0    set of all nodes, including depot 0
      N0 = N ∪ {0}
K     set of available vehicles
```

The fleet size is `|K|`. There is no separate parameter `M` for the number of vehicles.

Index conventions used throughout this document:

- `i`, `j` index nodes in `N0` unless a constraint explicitly restricts them to customers in `N`
- `k` indexes vehicles in `K`
- node `0` is the unique depot
- the row location of a route variable is the origin; the column location is the destination

---

## 3. Parameters

```text
q_i       tote demand of customer i ∈ N
          positive integer; depot demand is not defined
Q_k       tote capacity of vehicle k ∈ K
          positive integer
d_ij      distance from node i to node j, i, j ∈ N0
          non-negative integer metres
          d_ii = 0
```

Homogeneous MVP fleet:

```text
Q_k = Q    for every vehicle k ∈ K
```

The distance matrix is symmetric in the MVP:

```text
d_ij = d_ji    for all i, j ∈ N0
```

Self-loops are forbidden in the route variables, so `d_ii` is stored as zero for matrix integrity and is never selected.

---

## 4. Decision variables

### 4.1 Route variable

```text
x_ijk = 1  if vehicle k travels directly from node i to node j
x_ijk = 0  otherwise
```

Domain:

```text
x_ijk ∈ {0, 1}     ∀ i, j ∈ N0, i ≠ j, k ∈ K
```

`x_ijk` is defined only for `i ≠ j`. Self-loops are forbidden.

### 4.2 Customer assignment variable

```text
y_ik = 1  if customer i is assigned to vehicle k
y_ik = 0  otherwise
```

Domain:

```text
y_ik ∈ {0, 1}      ∀ i ∈ N, k ∈ K
```

There is no assignment variable for the depot.

### 4.3 Vehicle-use variable

```text
u_k = 1  if vehicle k serves at least one customer
u_k = 0  if vehicle k remains unused
```

Domain:

```text
u_k ∈ {0, 1}       ∀ k ∈ K
```

### 4.4 Load-order potential for subtour elimination

```text
w_ik = load-order potential of customer i on vehicle k
```

Domain:

```text
w_ik ≥ 0           ∀ i ∈ N, k ∈ K
```

`w_ik` is a Miller–Tucker–Zemlin (MTZ) potential. It is **not** required to equal the operational cumulative load displayed in the application.

When `y_ik = 0`, the bounds in Section 6.7 force `w_ik = 0`. When `y_ik = 1` and `x_ijk = 1`, the potential on `j` is at least the potential on `i` plus `q_j`. Slack can remain when the van is not filled, so two feasible potentials can differ while representing the same route.

The exact load shown on route cards, KPIs, and the Model Inspector is reconstructed by summing tote demand along the returned stop sequence. Do not read `w_ik` from OR-Tools. OR-Tools enforces capacity with a dimension, not with these variables.

---

## 5. Objective function

Minimise total travel distance:

```text
minimise   sum_{k ∈ K} sum_{i ∈ N0} sum_{j ∈ N0, j ≠ i}  d_ij * x_ijk
```

Every customer is mandatory, so service level is a hard requirement rather than an objective term. Distance, emissions, workload, and cost are not combined into a weighted score.

---

## 6. Constraints

### 6.1 Demand satisfaction and unique assignment

Every customer must be assigned to exactly one vehicle:

```text
sum_{k ∈ K} y_ik = 1     ∀ i ∈ N
```

This is the main demand-satisfaction constraint. It also establishes the unsplit-delivery rule: one customer cannot be split across two vans, and no customer may be left unassigned.

### 6.2 Vehicle capacity

The total tote demand assigned to a vehicle cannot exceed its capacity:

```text
sum_{i ∈ N} q_i y_ik  ≤  Q_k     ∀ k ∈ K
```

The MTZ potential constraints in Section 6.7 also prevent capacity-infeasible routed tours when `x_ijk = 1`. This aggregate inequality is retained because a planner can audit it without reading the subtour inequalities.

### 6.3 Assignment and route linking

If customer `i` is assigned to vehicle `k`, that vehicle must enter and leave the customer exactly once:

```text
sum_{j ∈ N0, j ≠ i} x_ijk = y_ik     ∀ i ∈ N, k ∈ K
```

```text
sum_{j ∈ N0, j ≠ i} x_jik = y_ik     ∀ i ∈ N, k ∈ K
```

The first equality is the outgoing-arc identity. The second is the incoming-arc identity.

### 6.4 Flow conservation at customers (reading aid only)

Section 6.3 already forces incoming selected arcs to equal outgoing selected arcs at every customer. This section is **not** a separate coded constraint.

Reading aid for the reconstructed route matrix of one vehicle:

- the row sum represents movements leaving a node
- the column sum represents movements entering a node

Depot flow is handled in Section 6.5, not by copying Section 6.3.

### 6.5 Depot departure and return

Every used vehicle must leave the depot once and return once:

```text
sum_{j ∈ N} x_0jk = u_k     ∀ k ∈ K
```

```text
sum_{i ∈ N} x_i0k = u_k     ∀ k ∈ K
```

Unused vehicles have `u_k = 0` and therefore no depot arcs.

### 6.6 Vehicle-use linking

A vehicle is used if and only if it serves at least one customer:

```text
u_k ≥ y_ik                    ∀ i ∈ N, k ∈ K
```

```text
u_k ≤ sum_{i ∈ N} y_ik        ∀ k ∈ K
```

Without these inequalities, a formulation can assign customers while leaving `u_k = 0`, which yields customer cycles that never touch the depot.

### 6.7 Route connectivity and MTZ subtour elimination

Disconnected customer cycles are not allowed. Flow balance alone is not sufficient to eliminate subtours in a manually written MILP.

Use Miller–Tucker–Zemlin load-order potentials with assignment-linked bounds:

```text
q_i y_ik  ≤  w_ik  ≤  Q_k y_ik     ∀ i ∈ N, k ∈ K
```

```text
w_ik - w_jk + Q_k x_ijk  ≤  Q_k - q_j y_jk
        ∀ i ∈ N, j ∈ N, i ≠ j, k ∈ K
```

The right-hand side **must** include `y_jk`. The weaker right-hand side `Q_k - q_j` is incorrect in this three-index model.

#### Why the weaker right-hand side is wrong

Counter-example using the documented 31 km LEARNING_6 optimum. Vehicle V01 serves Depot → C1 → C5 → C6 → Depot, so a feasible potential can take `w_{C6,V01} = 10`. Customer C4 is on V02, so `y_{C4,V01} = 0`, `w_{C4,V01} = 0`, and `x_{C6,C4,V01} = 0`, with `q_{C4} = 5` and `Q = 10`.

Wrong inequality:

```text
10 - 0 + 0  ≤  10 - 5     ⇒     10 ≤ 5
```

That rejects a valid solution.

Correct inequality:

```text
10 - 0 + 0  ≤  10 - 5 · 0     ⇒     10 ≤ 10
```

When `x_ijk = 1`, linking forces `y_jk = 1`, and the inequality reduces to `w_jk ≥ w_ik + q_j`. Summing around a customer-only cycle then yields `0 ≤ -sum q < 0`, which eliminates subtours.

Do not treat `w_ik` as the operational load after serving `i`. Reconstruct that load from the route.

OR-Tools `RoutingModel` enforces continuous depot-connected vehicle routes through its own routing representation. The inspector reconstructs `x_ijk` from consecutive stops; it does not read OR-Tools decision variables named `x_ijk`.

---

## 7. Pre-checks that are not part of the MILP

The application classifies some demand-capacity facts before any solver is called. These checks are operating rules, not additional MILP rows.

**Check 1 (hard fail, status `infeasible`):**

```text
max_{i ∈ N} q_i  ≤  Q
```

If one unsplit order exceeds van capacity, no feasible assignment exists.

**Check 2 (hard fail, status `infeasible`):**

```text
sum_{i ∈ N} q_i  ≤  |K| · Q
```

If aggregate demand exceeds fleet capacity, no feasible assignment exists.

**Check 3 (informational only):**

```text
minimum vehicles by aggregate demand = ceil(sum q_i / Q)
```

This is a lower bound. Indivisible orders may require additional vehicles. It must not fail validation.

Checks 1 and 2 are necessary but not sufficient. The fixture `INFEASIBLE_BIN_PACKING` passes both checks and still has no feasible unsplit assignment. The MVP does not add an exact bin-packing pre-check. If the solver then finds no complete plan, the domain status is `no_solution_found`, not `infeasible`.

---

## 8. Documented MILP versus OR-Tools

Do not claim that OR-Tools solved this three-index MILP with a MIP solver.

| MILP symbol | Meaning in the documented model | How the MVP obtains it |
|---|---|---|
| `y_ik` | Customer `i` assigned to vehicle `k` | Customer appears on vehicle `k`'s returned route |
| `x_ijk` | Vehicle `k` travels `i → j` | Consecutive stops on vehicle `k`'s returned route, including depot legs |
| `u_k` | Vehicle `k` is used | Returned route contains at least one customer |
| `w_ik` | Load-order potential for customer `i` on vehicle `k` | Not taken from the solver. Displayed load is the cumulative tote sum along the returned route |
| Capacity | Assigned demand ≤ `Q` | Unary demand callback plus OR-Tools capacity dimension |
| Subtours | Forbidden by MTZ potentials | Forbidden by `RoutingModel` route continuity from the depot |

OR-Tools settings used later in the application (not part of this MILP):

- first solution strategy: `PATH_CHEAPEST_ARC`
- local search: `GUIDED_LOCAL_SEARCH`
- time limit: 1, 5, or 10 seconds

Ordinary portfolio solutions are described as the best feasible plan found within the search limit. They are not labelled globally optimal.

The LEARNING_6 fixture is the documented exception: its 31.000 km optimum can be verified independently by enumerating the two capacity-feasible 3-and-3 partitions and all depot-start sequences. That enumeration is recorded in `docs/learning_6_enumeration.md`.

---

## 9. Operational load reconstruction

For a used vehicle `k` with stop sequence

```text
0 = n0 → n1 → n2 → … → n_r → n_{r+1} = 0
```

where `n1, …, n_r` are customers, the displayed load after serving customer `n_t` is:

```text
load_after(n_t) = sum_{s = 1}^{t} q_{n_s}
```

This quantity must satisfy `load_after(n_t) ≤ Q_k` for every `t`. It is not `w_{n_t k}`.

The reconstructed route distance is the sum of matrix legs:

```text
distance_k = sum_{t = 0}^{r} d_{n_t, n_{t+1}}
```

The scenario objective is the sum of `distance_k` over used vehicles.

---

## 10. What this formulation does not include

The following are explicit MVP non-goals and must not be added silently:

- delivery time windows
- service times
- split deliveries
- dropped or optional customers
- penalty costs for unserved customers
- multiple depots
- heterogeneous capacities
- multiple trips per vehicle
- a financial or emissions objective
