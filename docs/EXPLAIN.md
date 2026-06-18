# SignalForge - Project Handover & Engineering Overview

## Project Overview

SignalForge is a full-stack personal market intelligence platform designed to help users:

* Analyze stocks
* Maintain watchlists
* Track trades
* Visualize market charts
* Receive structured technical insights

The goal is NOT to create an AI stock predictor.

The goal is to build a production-style analytics platform that demonstrates:

* Backend Engineering
* API Design
* Authentication & Security
* Database Design
* Data Engineering
* Financial Data Processing

---

# Current Project Status

Current Phase:

```text
Sprint 0 ✅ Complete
Sprint 1 ✅ Complete
Sprint 2 ✅ Complete
```

Current Backend Capabilities:

* User Registration
* User Authentication
* JWT Access Tokens
* Refresh Tokens
* Protected Routes
* PostgreSQL Persistence
* Alembic Migrations
* Integration Tests
* Authentication Rate Limiting
* Watchlist CRUD
* Watchlist Repository
* Watchlist Service
* Watchlist Schemas

---

# Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Alembic

## Database

* PostgreSQL
* psycopg

## Security

* JWT
* Passlib
* bcrypt

## Testing

* pytest
* FastAPI TestClient

## Future Frontend

Phase 1:

* Streamlit
* Plotly

Phase 2:

* React
* Tailwind CSS

---

# High Level Architecture

```text
Frontend
    |
    v
FastAPI API
    |
    +----------------+
    |                |
    v                v
Auth Layer      Business Logic
    |                |
    +--------+-------+
             |
             v
      SQLAlchemy ORM
             |
             v
        PostgreSQL
```

---

# Repository Structure

```text
SignalForge/

backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── dependencies/
│
├── alembic/
├── tests/
│
frontend_streamlit/
docs/
```

---

# Database Models

## User

Purpose:

Stores registered users.

Important Fields:

* id
* username
* email
* hashed_password
* is_active
* created_at
* last_login_at

Relationships:

* One User → Many Watchlists
* One User → Many Trades
* One User → Many Refresh Tokens

---

## Watchlist

Purpose:

Stores named watchlists created by users.

Example:

```text
Tech Stocks
Long Term Investments
Swing Trades
```

Relationships:

* Belongs to User
* Contains WatchlistItems

---

## WatchlistItem

Purpose:

Stores tickers inside watchlists.

Example:

```text
AAPL
MSFT
RELIANCE
TCS
```

---

## Trade

Purpose:

Stores user trade journal entries.

Planned Usage:

* Buy records
* Sell records
* Trade analytics
* Win rate calculations

---

## MarketData

Purpose:

Stores historical market data.

Planned Usage:

* Chart generation
* Indicators
* Technical analysis

---

## RefreshToken

Purpose:

Stores refresh token metadata.

Added during Sprint 1 hardening.

Used for:

* Token rotation
* Session management
* Future token revocation

---

# Authentication System

## Registration Flow

```text
Register Request
      |
      v
Validate Input
      |
      v
Hash Password
      |
      v
Store User
      |
      v
Return User Response
```

Endpoint:

```http
POST /api/v1/auth/register
```

---

## Login Flow

```text
Identifier + Password
          |
          v
Verify User
          |
          v
Verify Password
          |
          v
Generate Access Token
          |
          v
Generate Refresh Token
          |
          v
Return Tokens
```

Endpoint:

```http
POST /api/v1/auth/login
```

---

## Protected Routes

Protected routes use:

```python
Depends(get_current_user)
```

Example:

```http
GET /api/v1/auth/me
```

---

## Refresh Tokens

Current Status:

Implemented.

Purpose:

* Renew access tokens
* Maintain user sessions

Future Improvements:

* Revocation
* Logout Everywhere
* Session Dashboard

---

## Rate Limiting

Sprint 1 hardening introduced login protection.

Purpose:

```text
Prevent brute-force attacks
Limit repeated login attempts
Protect authentication endpoints
```

---

# API Endpoints

## Health

```http
GET /api/v1/health
```

---

## Authentication

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

---

## Watchlists

Current:

```http
GET    /api/v1/watchlists
POST   /api/v1/watchlists
GET    /api/v1/watchlists/{watchlist_id}
PATCH  /api/v1/watchlists/{watchlist_id}
DELETE /api/v1/watchlists/{watchlist_id}
POST   /api/v1/watchlists/{watchlist_id}/items
DELETE /api/v1/watchlists/{watchlist_id}/items/{ticker}
```

Implemented authenticated Watchlist CRUD with ticker management, ticker normalization, ownership validation, deterministic ordering, and integration tests.

---

## Trades

Current:

```http
GET /api/v1/trades/status
```

Placeholder endpoint.

---

## Market Data

Current:

```http
GET /api/v1/market-data/status
```

Placeholder endpoint.

---

# Alembic Migration History

Sprint 0:

Initial schema creation.

Created:

* Users
* Watchlists
* WatchlistItems
* Trades
* MarketData

Sprint 1 Hardening:

Added:

* RefreshToken table

---

# Testing

Current:

```text
test_auth_integration.py
test_watchlist_integration.py
```

Coverage:

* Registration
* Login
* Refresh Tokens
* Protected Routes
* Watchlist CRUD
* Watchlist Ownership Validation
* Watchlist Ticker Management

Run Tests:

```bash
pytest
```

---

# Major Bugs Encountered

## Sprint 0

### Alembic Metadata Import

Issue:

```text
ImportError: Base not found
```

Cause:

Wrong Base import path.

Resolution:

Use models.base as metadata source.

---

### PostgreSQL Authentication Failure

Issue:

```text
password authentication failed for user postgres
```

Cause:

Credential mismatch.

Resolution:

Align DATABASE_URL with actual PostgreSQL credentials.

---

## Sprint 1

### bcrypt Compatibility Issue

Issue:

```text
password cannot be longer than 72 bytes
```

Observed with:

```text
passlib 1.7.4
bcrypt 5.0.0
```

Resolution:

```text
bcrypt==4.0.1
```

---

### Login 422 Error

Cause:

Login schema expects:

```json
{
  "identifier": "...",
  "password": "..."
}
```

not:

```json
{
  "email": "..."
}
```

Resolution:

Use identifier field.

---

# Current State Assessment

## Completed

* Authentication System
* JWT Access Tokens
* Refresh Tokens
* Protected Routes
* PostgreSQL Integration
* SQLAlchemy ORM
* Alembic Migrations
* Integration Tests
* Watchlist CRUD
* Watchlist Repository
* Watchlist Service
* Watchlist Schemas

## Partially Complete

* Trades
* Market Data

Trades and Market Data are currently scaffolded only.

## Not Started

* Stock Search
* Data Ingestion
* Charting
* Technical Analysis Engine
* Trade Analytics Dashboard
* Deployment

---

# Sprint 2 Roadmap

## Watchlists

Status:

```text
Completed
```

Implemented:

* Watchlist CRUD
* Watchlist Repository
* Watchlist Service
* Watchlist Schemas
* Integration Tests

Goals:

* Create Watchlist
* Rename Watchlist
* Delete Watchlist
* Add Ticker
* Remove Ticker
* User Ownership Validation

Success Criteria:

User can maintain multiple watchlists through authenticated endpoints.

---

# Sprint 3 Roadmap

## Market Data

Goals:

* Stock Search
* Historical Data Fetching
* yfinance Integration
* Data Persistence

---

# Sprint 4 Roadmap

## Trade Journal

Goals:

* Create Trades
* Edit Trades
* Delete Trades
* Trade History

---

# Sprint 5 Roadmap

## Analytics Engine

Goals:

* Support/Resistance
* Trend Detection
* Volume Analysis
* Momentum Analysis

---

# Sprint 6 Roadmap

## Deployment

Goals:

* Docker
* CI/CD
* Render/Railway
* PostgreSQL Hosting
* Production Environment Variables

---

# AI Agent Instructions

Before modifying code:

1. Read this file.
2. Inspect current models.
3. Inspect current migrations.
4. Inspect authentication implementation.
5. Do not duplicate existing functionality.
6. Prefer incremental changes.
7. Preserve Alembic migration history.
8. Preserve JWT authentication architecture.

---

# Recommended Next Task

Sprint 2:

Implement Watchlist CRUD.

Priority Order:

1. Create Watchlist
2. List User Watchlists
3. Add Ticker
4. Remove Ticker
5. Delete Watchlist

This is the highest-value next feature and the natural continuation of the current architecture.

Sprint 3A Status: COMPLETE

Implemented:
- MarketDataService
- Quote endpoint
- History endpoint
- Historical data persistence
- yfinance integration
- Mocked integration tests

Test Status:
42 passed
1 warning (known Starlette deprecation warning)

Sprint 3B Status: COMPLETE

Implemented:
- GET /api/v1/watchlists/{watchlist_id}/quotes
- Live quote aggregation
- Ownership enforcement
- Partial provider failure handling
- Watchlist quote schemas
- Integration tests

Test Status:
50 passed
0 failed

Sprint 4A Status: COMPLETE

Implemented:
- AnalyticsService
- SMA endpoint
- EMA endpoint
- Analytics schemas
- Analytics integration tests

Test Status:
73 passed
0 failed
1 known warning