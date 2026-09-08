# Deployment

LastMile Lab is a Streamlit UI plus a FastAPI planning service. The browser talks only to Streamlit. Streamlit calls FastAPI with server-side HTTP (`BACKEND_URL`). There are no Mapbox tokens or other secrets. Distances remain synthetic.

This document distinguishes two topologies. **Free recruiter/demo deployment** is Streamlit Community Cloud plus a Render FastAPI service. **Docker Compose** remains available for local or self-hosted use; it is not required for the free demo.

## A. Free recruiter/demo deployment

```text
Browser  →  Streamlit Community Cloud (https://<subdomain>.streamlit.app)
                →  HTTPS (server-side httpx)
                →  Render Free FastAPI (https://<service>.onrender.com)
                →  ephemeral local DuckDB
```

### Streamlit Community Cloud

| Setting | Value |
|---|---|
| Main file | `frontend/Home.py` |
| Working directory | repository root |
| Python | 3.12 |
| Dependencies | `frontend/requirements.txt` (next to the entrypoint) |
| System packages | none (`packages.txt` not required) |

In **App settings → Secrets**, set a root-level secret (this becomes an environment variable; do not commit it):

```toml
BACKEND_URL = "https://<render-service>.onrender.com"
```

Replace `<render-service>` with the Render hostname after the backend exists. Do not put a real production URL in Git.

### Render Free Web Service (native Python)

Use Render’s native Python runtime, not `Dockerfile.backend`. Render supplies `$PORT`; the Docker CMD still listens on `8000` for Compose only.

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Python version | 3.12 |
| Root directory | repository root |
| Build | `pip install -r backend/requirements.txt` |
| Start | `PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check | `GET /health` |
| Auto-deploy | connect the GitHub `main` branch |

Optional env: `LOG_LEVEL=INFO`. `DUCKDB_PATH` may stay unset; the service then uses `data/runs/lastmile.duckdb` on the instance disk.

CORS does not gate the Streamlit UI (server-side httpx). Do not set `CORS_ORIGINS=*`.

### Free-tier storage (technical)

Render local DuckDB storage is **ephemeral**. After a backend restart, spin-down, or redeploy:

- preset fixtures are re-seeded and remain usable
- generated/custom scenarios and stored run records may disappear

The UI recovers without promising history: a sleeping service is treated as starting; a missing stored `run_id` is an expired result, not a solver failure. Do not put this limitation in recruiter-facing copy.

## B. Optional local / self-hosted deployment (Docker Compose)

```text
Public HTTPS  →  Streamlit (published)  →  FastAPI (internal Compose network)  →  DuckDB (named volume)
```

This path keeps FastAPI internal and retains run history on volume `duckdb_data`. It is optional; the free demo does not depend on Compose.

### Local Compose

From the project root, with Docker Engine 24+ and Compose V2:

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
copy .env.example .env
docker compose up --build
```

Open the UI at `http://localhost:8501` (or `http://localhost:$FRONTEND_PORT`). Follow **Overview → Scenarios → Vienna Standard → Run comparison → Plan**.

FastAPI stays on the Compose network. It is not at `localhost:8000`. Check health from inside the backend container:

```powershell
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
```

Expected body includes `"status":"ok"`.

To inspect OpenAPI locally without making the API public, use the optional overlay (not for a public host):

```powershell
docker compose -f docker-compose.yml -f docker-compose.publish-api.yml up --build
```

Stop a foreground stack with `Ctrl+C`. For a detached stack: `docker compose stop` or `docker compose down`. Do **not** add `-v` unless you intend to delete run history.

Two-process PowerShell (no Docker) is documented in [`local_setup.md`](local_setup.md).

### Compose environment

`.env.example` is the Compose template. Copy it to `.env` beside `docker-compose.yml`. Do not copy it for Community Cloud or two-process PowerShell.

| Variable | Compose role |
|---|---|
| `BACKEND_URL` | Documented as `http://backend:8000`. The frontend service sets this explicitly. |
| `LOG_LEVEL` | Backend log level (`INFO` default). |
| `DUCKDB_PATH` | Container path `/app/data/runs/lastmile.duckdb`. |
| `FRONTEND_PORT` | Host port mapped to Streamlit container port 8501 (`8501` default). |

### Persistent DuckDB (Compose only)

| Item | Value |
|---|---|
| Container path | `/app/data/runs/lastmile.duckdb` |
| Volume name | `duckdb_data` |
| Mount | `duckdb_data:/app/data/runs` |

Generated scenarios and run history survive `docker compose down`, `up -d`, and image rebuilds. They are lost only if the named volume is removed.

### Health checks (Compose)

| Service | Probe |
|---|---|
| FastAPI | `GET /health` → `{"status":"ok","service":"viennacart-cvrp"}` |
| Streamlit 1.44.1 | `GET /_stcore/health` → `ok` |

## Future updates

On the free path, a push to the connected GitHub `main` branch can rebuild Streamlit Community Cloud and Render without changing the public Streamlit URL or the Render hostname. Recruiter links stay those two URLs (share the Streamlit URL).

On Compose, `git pull`, `docker compose build`, and `docker compose up -d` keep the published Streamlit URL.
