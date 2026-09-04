# LEARNING_6 Independent Enumeration

**Scenario:** `LEARNING_6`  
**Purpose:** Verify the 31.000 km optimum by exhaustive enumeration. Do not take 31 km on trust from OR-Tools.

This document is a Phase 0 verification record. It is not application code. A dedicated automated test (`tests/test_learning_6_enumeration.py`) will repeat this enumeration in Phase 4.

---

## 1. Demand and capacity audit

Customers:

| Customer | Demand (totes) |
|---|---:|
| C1 | 4 |
| C2 | 2 |
| C3 | 3 |
| C4 | 5 |
| C5 | 2 |
| C6 | 4 |
| **Total** | **20** |

Fleet:

| Vehicle | Capacity (totes) |
|---|---:|
| V01 | 10 |
| V02 | 10 |
| **Total** | **20** |

Pre-checks:

- Check 1: max demand `5 <= 10` — pass
- Check 2: total demand `20 <= 20` — pass
- Check 3 (informational): `ceil(20 / 10) = 2` vehicles

Total demand equals total fleet capacity, so both vehicles must be used and each must load **exactly 10 totes**.

Unsplit rule: a customer cannot be shared. Therefore a feasible assignment is a partition of `{C1, C2, C3, C4, C5, C6}` into two packs, each summing to 10.

---

## 2. Why only two feasible partitions exist

No two-customer subset sums to 10:

```text
C1+C4 = 9
C1+C6 = 8
C2+C3 = 5
C3+C4 = 8
C4+C6 = 9
```

Every feasible pack therefore has three customers. The three-customer subsets that sum to 10 are:

```text
{C1, C2, C6} = 4 + 2 + 4 = 10     complement {C3, C4, C5} = 3 + 5 + 2 = 10
{C1, C5, C6} = 4 + 2 + 4 = 10     complement {C2, C3, C4} = 2 + 3 + 5 = 10
```

No other 3-and-3 split sums to 10 on both sides. Example rejects:

```text
{C1, C2, C3} = 9
{C1, C2, C4} = 11
{C1, C2, C5} = 8
{C1, C3, C4} = 12
{C1, C3, C5} = 9
{C1, C3, C6} = 11
{C1, C4, C5} = 11
{C1, C4, C6} = 13
{C2, C3, C6} = 9
{C2, C4, C5} = 9
{C2, C5, C6} = 8
{C3, C5, C6} = 9
{C4, C5, C6} = 11
```

---

## 3. Distance unit

The published teaching matrix is in kilometres. Stored fixture values are integer metres (`km * 1000`). The tables below use kilometres for readability. The verified optimum is `31.000 km` = `31000` metres.

Depot node in fixture files: `DEPOT_L6`. Display label: `Depot`.

---

## 4. All depot-start sequences

For each pack of three customers there are `3! = 6` sequences that start and end at the depot. Across two partitions that is `2 * 6 * 6 = 72` directed route pairs.

### Partition A

Pack `{C1, C2, C6}`:

| Sequence | Legs (km) | Distance (km) |
|---|---|---:|
| Depot → C1 → C2 → C6 → Depot | 3 + 2 + 6 + 3 | 14.000 |
| Depot → C1 → C6 → C2 → Depot | 3 + 4 + 6 + 5 | 18.000 |
| Depot → C2 → C1 → C6 → Depot | 5 + 2 + 4 + 3 | 14.000 |
| Depot → C2 → C6 → C1 → Depot | 5 + 6 + 4 + 3 | 18.000 |
| Depot → C6 → C1 → C2 → Depot | 3 + 4 + 2 + 5 | 14.000 |
| Depot → C6 → C2 → C1 → Depot | 3 + 6 + 2 + 3 | 14.000 |

Pack minimum: **14.000 km**.

Pack `{C3, C4, C5}`:

| Sequence | Legs (km) | Distance (km) |
|---|---|---:|
| Depot → C3 → C4 → C5 → Depot | 8 + 3 + 4 + 5 | 20.000 |
| Depot → C3 → C5 → C4 → Depot | 8 + 6 + 4 + 7 | 25.000 |
| Depot → C4 → C3 → C5 → Depot | 7 + 3 + 6 + 5 | 21.000 |
| Depot → C4 → C5 → C3 → Depot | 7 + 4 + 6 + 8 | 25.000 |
| Depot → C5 → C3 → C4 → Depot | 5 + 6 + 3 + 7 | 21.000 |
| Depot → C5 → C4 → C3 → Depot | 5 + 4 + 3 + 8 | 20.000 |

Pack minimum: **20.000 km**.

Partition A minimum total: `14.000 + 20.000 = 34.000 km`.

That 34.000 km pairing is the **teaching comparison packing**, not sequential nearest neighbour:

```text
V01: Depot → C1 → C2 → C6 → Depot     load 10     14.000 km
V02: Depot → C5 → C4 → C3 → Depot     load 10     20.000 km
Total: 34.000 km
```

### Partition B

Pack `{C1, C5, C6}`:

| Sequence | Legs (km) | Distance (km) |
|---|---|---:|
| Depot → C1 → C5 → C6 → Depot | 3 + 4 + 3 + 3 | 13.000 |
| Depot → C1 → C6 → C5 → Depot | 3 + 4 + 3 + 5 | 15.000 |
| Depot → C5 → C1 → C6 → Depot | 5 + 4 + 4 + 3 | 16.000 |
| Depot → C5 → C6 → C1 → Depot | 5 + 3 + 4 + 3 | 15.000 |
| Depot → C6 → C1 → C5 → Depot | 3 + 4 + 4 + 5 | 16.000 |
| Depot → C6 → C5 → C1 → Depot | 3 + 3 + 4 + 3 | 13.000 |

Pack minimum: **13.000 km**.

Pack `{C2, C3, C4}`:

| Sequence | Legs (km) | Distance (km) |
|---|---|---:|
| Depot → C2 → C3 → C4 → Depot | 5 + 3 + 3 + 7 | 18.000 |
| Depot → C2 → C4 → C3 → Depot | 5 + 4 + 3 + 8 | 20.000 |
| Depot → C3 → C2 → C4 → Depot | 8 + 3 + 4 + 7 | 22.000 |
| Depot → C3 → C4 → C2 → Depot | 8 + 3 + 4 + 5 | 20.000 |
| Depot → C4 → C2 → C3 → Depot | 7 + 4 + 3 + 8 | 22.000 |
| Depot → C4 → C3 → C2 → Depot | 7 + 3 + 3 + 5 | 18.000 |

Pack minimum: **18.000 km**.

Partition B minimum total: `13.000 + 18.000 = 31.000 km`.

---

## 5. Verified optimum

The minimum over both partitions is **31.000 km (31000 m)**.

One attaining plan:

```text
V01: Depot → C1 → C5 → C6 → Depot     load 4+2+4 = 10     13.000 km
V02: Depot → C2 → C3 → C4 → Depot     load 2+3+5 = 10     18.000 km
Total: 31.000 km
```

Equal-length reversals also attain 31.000 km:

```text
V01: Depot → C6 → C5 → C1 → Depot     13.000 km
V02: Depot → C4 → C3 → C2 → Depot     18.000 km
```

Properties of every optimal plan:

- every customer appears exactly once
- each vehicle load equals 10 totes
- both routes start and end at the depot
- displayed optimum is `31.000 km`, not an ambiguous `31 km`

This enumeration is independent of OR-Tools. Later solver tests may assert 31000 m for LEARNING_6 because this proof exists. They must not freeze an objective for `VIENNA_STANDARD_24`.
