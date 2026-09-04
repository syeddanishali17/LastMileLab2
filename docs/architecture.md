# Architecture

LastMile Lab is a static morning CVRP dispatch planner. The Streamlit UI never solves routes or recomputes KPIs. FastAPI never contains the solver body. Planning lives in `backend/app/core`, and both the API and the pytest suite call that package directly.

## Request flow

```text
Browser
   |
   v
Streamlit UI  (port 8501)
   |  HTTP JSON only
   v
FastAPI /api/v1  (port 8000)
   |
   +-- scenarios: load, validate, generate
   +-- plans: baseline, OR-Tools
   +-- runs: retrieve, constraint checks, JSON/CSV export
   |
   +--> core.validation / core.distance_matrix
   +--> core.baseline  (sequential nearest neighbour)
   +--> core.optimizer (OR-Tools RoutingModel)
   +--> core.kpis / core.invariants
   |
   v
DuckDBRepository  (data/runs/lastmile.duckdb)
```

```mermaid
flowchart TD
  user[Recruiter or planner]
  ui[Streamlit pages<br/>Home, Dispatch Setup,<br/>Route Plan, Baseline vs Optimised,<br/>Model Inspector, Learning Lab]
  api[FastAPI<br/>GET /health<br/>/api/v1/scenarios<br/>/api/v1/plans<br/>/api/v1/runs]
  core[Core planning package]
  val[Validation and pre-checks]
  dist[Haversine triangle-and-mirror matrix]
  nn[Capacity-aware sequential NN]
  ort[OR-Tools RoutingModel]
  kpi[KPI and reconciliation]
  db[(DuckDB run history)]
  tests[Pytest calling core directly]

  user --> ui
  ui -->|JSON, no solver| api
  api --> core
  core --> val
  core --> dist
  core --> nn
  core --> ort
  core --> kpi
  api --> db
  tests --> core
```

The same core functions are imported by tests without starting Uvicorn or Streamlit.

## Layers

| Layer | Responsibility | Must not do |
|---|---|---|
| `frontend/` Streamlit | Scenario selection, maps, tables, captions | Recalculate distances, utilisation, or improvement % |
| `backend/app/api/` | HTTP mapping, CORS, error bodies, serializers | Own a second solver or a second KPI formula |
| `backend/app/core/` | Validation, matrix, NN, OR-Tools, KPIs, invariants | Depend on FastAPI or Streamlit |
| `backend/app/storage/` | `AppRepository` protocol; DuckDB implementation | Change API contracts when the store changes |

Phase 6 used an in-memory repository. Phase 8 swapped in DuckDB behind the same protocol. Run IDs, exports, and HTTP status mapping stayed the same.

## Frontend pages

| Page | Role |
|---|---|
| Home | Product story, API health, synthetic-data notice |
| Dispatch Setup | Load scenario, demand/capacity, pre-checks, run baseline and optimiser |
| Route Plan | Vehicle sequences, reconstructed loads, OSM schematic map |
| Baseline vs Optimised | Comparison KPIs only when both runs are `comparison_eligible` |
| Model Inspector | Reconstruct `x_ijk`, `y_ik`, `u_k` and cumulative tote loads from stops |
| Learning Lab | LEARNING_6 incomplete NN, 34.000 km named packing, 31.000 km verified optimum |

Session state keeps `scenario_id`, `baseline_run_id`, and `optimised_run_id`. Changing scenario drops stale run IDs so a LEARNING_6 baseline cannot be compared with a Vienna optimiser run.

OpenStreetMap tiles are schematic. Route lines are synthetic connections, not road geometry. LEARNING_6 has no geographic map.

## Documented MILP versus OR-Tools

The three-index formulation in [`mathematical_formulation.md`](mathematical_formulation.md) is the model the author must be able to explain. Google OR-Tools `RoutingModel` is the MVP solver. It does **not** solve that MILP with a MIP engine.

| Symbol | Documented meaning | How the application obtains it |
|---|---|---|
| `y_ik` | Customer `i` assigned to van `k` | Customer appears on vehicle `k`'s returned route |
| `x_ijk` | Van `k` travels `i → j` | Consecutive stops, including depot legs |
| `u_k` | Van `k` is used | Returned route contains at least one customer |
| `w_ik` | MTZ load-order potential | Not taken from the solver. Displayed load is the cumulative tote sum along the route |

OR-Tools settings used by the optimiser:

- first solution: `PATH_CHEAPEST_ARC`
- local search: `GUIDED_LOCAL_SEARCH`
- time limit: 1, 5, or 10 seconds

Ordinary portfolio output is the best feasible plan found within that search limit. It is not labelled globally optimal. LEARNING_6 is the documented exception because its 31.000 km optimum is independently enumerated.

## Data and fixtures

Fixed CSV scenarios live under `data/fixtures/`. Generated scenarios exist only in the repository for the process lifetime (or until DuckDB is cleared). Distances are integer metres. Displayed kilometres use three decimal places. There are no Mapbox tokens or other secrets.

## Runtime topology

Local PowerShell (two processes on one machine):

```text
127.0.0.1:8000   FastAPI / Uvicorn
127.0.0.1:8501   Streamlit  (BACKEND_URL=http://localhost:8000)
```

Docker Compose:

```text
frontend:8501  -->  backend:8000  on the Compose network
browser        -->  localhost:8501 and localhost:8000
```

CORS allows the Streamlit origin. The frontend container still calls `http://backend:8000`. Deployment notes are in [`deployment.md`](deployment.md).
