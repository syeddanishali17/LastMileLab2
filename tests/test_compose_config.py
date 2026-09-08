"""Compose production topology stays internal-API and volume-backed."""

from pathlib import Path


def test_default_compose_keeps_fastapi_internal_and_duckdb_on_named_volume() -> None:
    text = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "8000:8000" not in text
    assert "BACKEND_URL: http://backend:8000" in text
    assert "DUCKDB_PATH: /app/data/runs/lastmile.duckdb" in text
    assert "duckdb_data:/app/data/runs" in text
    assert '"${FRONTEND_PORT:-8501}:8501"' in text
    assert "http://127.0.0.1:8000/health" in text
    assert "http://127.0.0.1:8501/_stcore/health" in text
    assert "restart: unless-stopped" in text


def test_deployment_doc_distinguishes_free_demo_from_compose() -> None:
    text = Path("docs/deployment.md").read_text(encoding="utf-8")
    assert "Streamlit Community Cloud" in text
    assert "Render Free FastAPI" in text or "Render Free Web Service" in text
    assert "pip install -r backend/requirements.txt" in text
    assert "PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port $PORT" in text
    assert "frontend/Home.py" in text
    assert "ephemeral" in text
    assert "docker compose up --build" in text
    assert "Do not deploy the UI to Streamlit Community Cloud" not in text
    overlay = Path("docker-compose.publish-api.yml").read_text(encoding="utf-8")
    default = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "8000:8000" in overlay
    assert "8000:8000" not in default
