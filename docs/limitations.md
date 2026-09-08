# Limitations and roadmap

## Current limitations

- **Synthetic geography.** Distances are Haversine metres with a detour factor, rounded to integer metres. OpenStreetMap polylines are schematic connections, not driving directions or live traffic.
- **One frozen morning wave.** The planner does not re-optimise during the day, accept late orders, or model service times.
- **Homogeneous fleet.** Every van has the same tote capacity. There is no dispatch fixed cost, workload-balance objective, or vehicle-specific constraint.
- **Unsplit mandatory service.** Customers cannot be split, dropped, or made optional. Time windows are out of scope.
- **OR-Tools is a search engine.** Ordinary portfolio results are the best feasible plan found within 1, 5, or 10 seconds. They are not globally optimal. Guided local search is not bit-deterministic; Vienna optimiser kilometres may move slightly between machines.
- **No exact packing pre-check.** Checks 1 and 2 can pass while no unsplit assignment exists. A missing complete plan is `no_solution_found`, not a MILP infeasibility proof.
- **Displayed loads are reconstructed.** The inspector shows cumulative tote counts from stop sequences. It does not display MTZ potentials `w_ik`, and OR-Tools did not solve the documented three-index MILP.
- **LEARNING_6 baseline is incomplete.** Sequential nearest neighbour leaves C4 unserved. Do not treat 27.000 km or 34.000 km as that baseline's complete objective.
- **No public auth.** The demo is unauthenticated. Do not put real customer data in the fixtures.
- **Hosting.** The free demo runs Streamlit Community Cloud against a separate FastAPI service (Render). Streamlit cannot run the solver itself. Optional Docker Compose keeps both processes on one host with a persistent volume; see [`deployment.md`](deployment.md).
- **Persistence.** On Compose, DuckDB run history lives on a named volume and is lost if that volume is cleared. On Render Free, local DuckDB is ephemeral: presets re-seed after restart, while generated scenarios and stored runs may disappear. Generated scenarios are not a substitute for the fixed fixtures.

## Explicit MVP non-goals

Time windows, live traffic, split deliveries, multi-trips, multiple depots, heterogeneous vehicles, EV range, optional customers, emissions, driver breaks, user accounts, Mapbox, Snowflake, Power BI, React, and Kubernetes are out of scope until the CVRP MVP is publicly demonstrable.

## Roadmap

Extensions should be added one at a time and compared against this CVRP baseline.

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
