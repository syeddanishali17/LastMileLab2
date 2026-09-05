# Local setup (Windows PowerShell)

Use Python 3.12 and the project virtual environment at `.venv`. Do not install packages globally.

## Create the virtual environment

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r backend\requirements-dev.txt -r frontend\requirements.txt
```

Activation is optional if you call the venv interpreter directly:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, keep using `.\.venv\Scripts\python.exe` instead of activating.

Copy environment defaults. There are no secrets.

```powershell
copy .env.example .env
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend tests frontend
```

## Run FastAPI and Streamlit (two terminals)

Terminal 1 — API at `http://127.0.0.1:8000`:

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — UI at `http://localhost:8501`:

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
.\.venv\Scripts\python.exe -m streamlit run frontend\Home.py
```

Open:

- Planner: http://localhost:8501
- Health: http://127.0.0.1:8000/health
- OpenAPI: http://127.0.0.1:8000/docs

In the UI, follow **Overview → Scenarios → Vienna Standard 24 → Run comparison**. The default five-second search opens **Plan** automatically with both route maps and visible JSON/CSV ZIP exports. The Overview proof card is the published snapshot; the Plan page shows the current API run.

For a custom delivery wave, choose **Custom scenario**, edit tote demand, then **Generate scenario**. Generation is disabled if an order exceeds a van's capacity or total demand exceeds fleet capacity. A passed input check is not a guarantee that unsplit orders can be packed. Generated locations use the existing Vienna zones. **Methodology** and **Model validation** are optional sidebar links.

Do not host the UI on Streamlit Community Cloud. That host cannot run the FastAPI sidecar.

Compose deployment is documented in [`deployment.md`](deployment.md).
