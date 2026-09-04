# Deployment

LastMile Lab needs FastAPI and Streamlit on the same host. Do not deploy the UI to Streamlit Community Cloud; that host cannot run the API sidecar.

There are no Mapbox tokens or other secrets. Distances remain synthetic.

## Docker Compose on a VM

From the project root, with Docker Engine 24+ and Compose V2:

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
copy .env.example .env
docker compose up --build
```

Open:

- UI: `http://localhost:8501`
- API health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

Stop with `Ctrl+C`, then `docker compose down`. DuckDB history lives in the `duckdb_data` volume.

If the public URL is not localhost, set `CORS_ORIGINS` to the Streamlit origin the browser uses, for example `http://YOUR_HOST:8501`. The frontend container still calls the API as `http://backend:8000` on the Compose network.

## Single VM without Compose

Run both processes on the same machine. Keep `BACKEND_URL` pointing at the API the Streamlit process can reach.

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

```powershell
cd c:\Users\danis\Desktop\LastMileLab2
.\.venv\Scripts\python.exe -m streamlit run frontend\Home.py
```
