# LEARNING_6 Sequential Nearest Neighbour

**Scenario:** `LEARNING_6`  
**Procedure:** capacity-aware sequential nearest neighbour (specification Section 15)

This is the required baseline result. It is **not** a complete 34.000 km plan. Sequential construction fails on this tight feasible instance.

---

## Tie-break rules used

1. Open the next unused vehicle in `vehicle_id` ascending order, starting at the depot.
2. Among unserved customers whose demand fits remaining capacity, choose the nearest to the current node.
3. If several customers share that minimum distance, pick the lowest `customer_id`.
4. Continue until no unserved customer fits, then return to the depot.
5. If unserved customers remain and an unused vehicle exists, open the next vehicle.
6. If the fleet is exhausted with customers still unserved, stop with `heuristic_incomplete`.

---

## Construction

### Vehicle V01

Open V01 at `DEPOT_L6`. Remaining capacity: 10 totes.

From the depot, C1 and C6 are both 3.000 km. The customer-id tie-break selects **C1** (demand 4).

```text
Depot → C1
Load: 4
Remaining capacity: 6
```

From C1, feasible unserved customers and distances:

| Customer | Demand | Fits remaining 6? | Distance from C1 (km) |
|---|---:|---|---:|
| C2 | 2 | yes | 2.000 |
| C3 | 3 | yes | 5.000 |
| C4 | 5 | yes | 5.000 |
| C5 | 2 | yes | 4.000 |
| C6 | 4 | yes | 4.000 |

Nearest is **C2**.

```text
Depot → C1 → C2
Load: 6
Remaining capacity: 4
```

From C2, feasible unserved customers:

| Customer | Demand | Fits remaining 4? | Distance from C2 (km) |
|---|---:|---|---:|
| C3 | 3 | yes | 3.000 |
| C4 | 5 | no | — |
| C5 | 2 | yes | 5.000 |
| C6 | 4 | yes | 6.000 |

Nearest feasible is **C3** (3.000 km), nearer than C6 (6.000 km). V01 takes C3 and cannot later take C4.

```text
Depot → C1 → C2 → C3
Load: 9
Remaining capacity: 1
```

No remaining unserved customer has demand `<= 1`. Close V01.

```text
V01: Depot → C1 → C2 → C3 → Depot
Load: 4 + 2 + 3 = 9 totes
Distance: 3 + 2 + 3 + 8 = 16.000 km (16000 m)
Status: closed
```

### Vehicle V02

Open V02 at `DEPOT_L6`. Remaining capacity: 10 totes. Unserved: C4 (5), C5 (2), C6 (4).

From the depot:

| Customer | Demand | Distance from depot (km) |
|---|---:|---:|
| C4 | 5 | 7.000 |
| C5 | 2 | 5.000 |
| C6 | 4 | 3.000 |

Nearest is **C6**.

```text
Depot → C6
Load: 4
Remaining capacity: 6
```

From C6:

| Customer | Demand | Fits remaining 6? | Distance from C6 (km) |
|---|---:|---|---:|
| C4 | 5 | yes | 6.000 |
| C5 | 2 | yes | 3.000 |

Nearest is **C5**.

```text
Depot → C6 → C5
Load: 6
Remaining capacity: 4
```

C4 demand is 5, which does not fit remaining capacity 4. Close V02.

```text
V02: Depot → C6 → C5 → Depot
Load: 4 + 2 = 6 totes
Distance: 3 + 3 + 5 = 11.000 km (11000 m)
```

### Unserved

C4 remains (demand 5 totes; remaining capacity on V02 was 4). The fleet is exhausted.

---

## Required baseline payload

```text
status: heuristic_incomplete
comparison_eligible: false
unserved_customer_ids: [C4]
partial_distance_metres: 27000
objective_distance_metres: null
baseline_distance: null
distance_improvement_percentage: null
customers_served: 5
demand_served_totes: 15
```

`partial_distance_metres` is `16000 + 11000 = 27000`. It must not be used as a baseline comparison distance.

Page 3 must not compute an improvement percentage from this incomplete baseline.

The scenario is still feasible. The 31.000 km plan in `docs/learning_6_enumeration.md` serves every customer. Sequential nearest neighbour failed because greedy packing trapped 1 leftover tote on V01 and 4 leftover totes on V02, neither of which can take C4's 5 totes.
