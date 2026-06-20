# Architecture

Insique uses a backend-first architecture with explicit separation between API, service, repository, and persistence layers.

## Principles

- Store market history in PostgreSQL and cache external data server-side.
- Keep chart intelligence deterministic and educational.
- Avoid client-side direct calls to market APIs.
- Preserve a clean path from Streamlit MVP to React production UI.

## Modules

- Authentication and authorization
- User profiles and watchlists
- Market data ingestion and caching
- Technical indicator computation
- Signal generation and scoring
- Alert engine with scheduled evaluation
- In-app notifications
- Chart intelligence and visualization
- Trade journaling and analytics
- Smart search with autocomplete
