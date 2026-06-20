# Insique

Insique is a production-oriented market intelligence platform focused on decision support, analytics, and portfolio journaling. It is explicitly not a prediction engine and must not provide automatic buy/sell recommendations.

## Current Scope

- FastAPI backend foundation
- PostgreSQL-first data model
- SQLAlchemy + Alembic wiring
- Streamlit MVP shell
- Future React frontend slot

## Repository Layout

- `backend/` FastAPI application, domain models, services, and API routes
- `frontend_streamlit/` early MVP user interface
- `frontend_react/` reserved for the later production UI
- `infra/` deployment and environment assets
- `docs/` architecture notes and API conventions

## Local Setup

1. Copy `.env.example` to `.env` and adjust values.
2. Start PostgreSQL locally or with Docker.
3. Install dependencies from `pyproject.toml`.
4. Run the backend with Uvicorn.

## Run Commands

Backend:

```bash
uvicorn backend.app.main:app --reload
```

Streamlit:

```bash
streamlit run frontend_streamlit/app.py
```

## Architecture Notes

The backend is organized around a service layer and explicit persistence boundaries so the same API can support Streamlit now and React later. Market data is designed to be cached in PostgreSQL rather than fetched from external APIs on every request.
