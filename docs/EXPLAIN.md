# Insique - Project Handover & Engineering Overview

## Project Overview

Insique is a full-stack personal market intelligence platform designed to help users:

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
Insique/

backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       └── routes/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
│
├── alembic/
├── tests/
│
frontend/
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
* Stock Search & Autocomplete
* Market Data (quotes, history)
* Analytics (SMA, EMA, RSI, MACD)
* Signals & Watchlist Signals
* Visual Charts (Recharts)
* Settings & Profile
* Dashboard
* Landing Page
* Branding Migration (Insique)
* Connectivity Layer (BFF proxy, auth forwarding)
* Smart Search (company name, exchange-aware)
* Alert Engine (CRUD, evaluation, scheduling)
* In-App Notifications

## Partially Complete

* Trades (scaffolded only)

## Not Started

* Portfolio Tracking
* Paper Trading
* Backtesting
* ML Forecasting
* Live Market Updates
* Deployment

---

*Older Sprint roadmaps (Sprints 2–6) have been superseded by completed sprint records below.*

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

Sprint 4B Status: COMPLETE

Implemented:
- RSI endpoint
- MACD endpoint
- RSI calculations
- MACD calculations
- Analytics schemas
- Analytics integration tests

Test Status:
103 passed
0 failed
1 known Starlette warning

Sprint 5A Status: COMPLETE

Implemented:
- SignalService
- Signal endpoint
- Signal schemas
- RSI signals
- MACD crossover signals
- SMA trend signals
- EMA trend signals
- Score aggregation
- Confidence calculation
- Signal integration tests

Test Status:
127 passed
0 failed
1 known Starlette warning

Sprint 5B Status: COMPLETE

Implemented:
- Watchlist signal aggregation
- GET /api/v1/watchlists/{watchlist_id}/signals
- WatchlistSignalItemRead schema
- WatchlistSignalsResponse schema
- WatchlistService.get_watchlist_signals()
- Ownership enforcement
- Partial per-ticker failure handling
- Deterministic ticker ordering
- Watchlist signal integration tests

Test Status:
141 passed
0 failed
1 known Starlette warning

Sprint 7A Status: COMPLETE

Implemented:
- Next.js frontend foundation
- TypeScript configuration
- TailwindCSS setup
- shadcn/ui component library
- Theme system (dark/light mode)
- Theme persistence
- TanStack Query provider
- App provider architecture
- API client foundation
- Auth session management
- Auth context and hooks
- Login page
- Register page
- Protected dashboard shell
- Responsive sidebar navigation
- Mobile navigation
- Next.js BFF auth route handlers
- Middleware route protection
- Frontend feature module structure

Frontend Status:
- 52 files created
- 0 lint errors
- 0 type errors

Backend Status:
- 141 passed
- 0 failed
- 1 known Starlette warning

Notes:
- Sprint 7A intentionally excludes watchlists UI, analytics UI, signals UI, charts, and dashboard data integration.
- Frontend foundation is complete and ready for Sprint 7B.

Sprint 7B Status: COMPLETE

Implemented:
- Watchlist BFF route handlers
- Authenticated FastAPI forwarding helper
- Watchlist API layer
- Watchlist TanStack Query hooks
- Dashboard data integration
- Watchlists page
- Create watchlist flow
- Delete watchlist flow
- Add ticker flow
- Remove ticker flow
- Watchlist detail panel
- Watchlist quote table
- Loading states
- Error states
- Empty states
- Mobile-responsive watchlist UI

Frontend Status:
- 24 files created
- 5 files modified
- 0 lint errors
- 0 type errors
- Production build successful

Backend Status:
- 141 passed
- 0 failed
- 1 known Starlette warning

Notes:
- Sprint 7B intentionally excludes signals UI, analytics UI, charts, and portfolio features.
- Frontend is now connected to live backend watchlist APIs.
Sprint 8A Status: COMPLETE

Implemented:
- Analytics feature module
- Analytics endpoint integration
- Analytics query hooks
- Analytics BFF routes
- Analytics page
- Ticker search form
- RSI analytics display
- SMA analytics display
- EMA analytics display
- MACD analytics display
- Loading states
- Error states
- Empty states
- Mobile responsive analytics UI

Test Status:
Frontend lint passed
Frontend typecheck passed
Frontend production build passed

Known Limitations:
- Four requests per ticker (SMA, EMA, RSI, MACD)
- No indicator parameter controls
- No charts
- No autocomplete search
- Uses backend default indicator settings

Sprint 8B Status: COMPLETE

Implemented:
- Signals feature module
- Signal API layer
- Signal query hooks
- Signal BFF route handlers
- Signals page
- Single ticker signal lookup
- Watchlist signals view
- Signal hero card
- Signal indicator breakdown cards
- Watchlist signal row cards
- Loading states
- Error states
- Empty states
- Mobile responsive signals UI

Files Created:
- Signal API fetchers
- Signal query hooks
- Single ticker signal BFF route
- Watchlist signals BFF route
- Signals page
- Signals page content
- Single ticker view
- Watchlist signals view
- Signals search form
- Signals empty state
- Signals loading skeleton
- Signals error state
- Signal hero card
- Signal indicator breakdown card
- Signal ticker row card

Files Modified:
- Signal types
- Desktop navigation (Signals enabled)
- Mobile navigation (Signals enabled)

Frontend Status:
- Signals page connected to backend
- Single ticker signals integrated
- Watchlist signals integrated
- BUY / SELL / NEUTRAL ratings displayed
- Confidence display implemented
- Signal reasoning display implemented
- Protected dashboard route
- Mobile responsive

Build Status:
- ESLint: 0 warnings, 0 errors
- TypeScript: 0 errors
- Production build: successful

Known Limitations:
- Signal generation can be slow on first request
- Watchlist signals scale linearly with watchlist size
- No parameter controls
- No autocomplete search
- Uses backend default signal settings

Project Status:
- Sprint 7A Complete
- Sprint 7B Complete
- Sprint 8A Complete
- Sprint 8B Complete
- Frontend Signals Layer Complete

Sprint 9A Status: COMPLETE

Implemented:
- Market Data page
- Market Data BFF route
- Market Data API layer
- Market Data query hooks
- Single ticker quote lookup
- Quote refresh functionality
- Settings page
- Profile section
- Theme section
- Logout section
- Dashboard enhancements
- Quick actions
- Improved dashboard empty states
- Analytics interpretation badges
- RSI interpretation
- SMA trend interpretation
- EMA trend interpretation
- MACD interpretation
- Signal hero summary improvements
- Signal confidence progress bar
- Improved signal explanations
- UX consistency improvements

Files Created:
- Market Data BFF route
- Market Data API fetcher
- Market Data query hook
- Market Data page
- Settings page
- Market Data components
- Settings content component
- Profile section
- Theme section
- Danger section

Files Modified:
- Desktop navigation
- Mobile navigation
- Dashboard content
- Analytics indicator card
- Analytics MACD card
- Analytics page content
- Signal hero card
- Signal indicator breakdown card

Frontend Status:
- Market Data page connected to backend
- Settings page functional
- Dashboard enhanced
- Analytics interpretation layer added
- Signals interpretation layer added
- All navigation items functional
- Mobile responsive
- Dark/light mode supported

Build Status:
- ESLint: 0 warnings, 0 errors
- TypeScript: 0 errors
- Production build: successful

Known Limitations:
- Market data depends on yfinance response times
- No charts
- No alerts
- No notifications
- No autocomplete search
- No portfolio tracking

Project Status:
- Sprint 7A Complete
- Sprint 7B Complete
- Sprint 8A Complete
- Sprint 8B Complete
- Sprint 9A Complete
- Insique V1 Complete

Sprint 9B Status: COMPLETE

Implemented:
- Recharts integration
- Analytics visualizations
- RSI trend chart
- SMA price overlay chart
- EMA price overlay chart
- MACD visualization chart
- Signal confidence gauge
- Indicator confidence visualization
- Watchlist signal distribution chart
- Mini confidence bars
- Theme-aware chart system
- Responsive chart layouts

Files Created:
- Chart container
- RSI chart
- SMA chart
- EMA chart
- MACD chart
- Confidence gauge
- Indicator confidence chart
- Signal distribution chart

Files Modified:
- Analytics indicator card
- Analytics MACD card
- Signal hero card
- Single ticker signals view
- Watchlist signals view
- Signal ticker row card

Frontend Status:
- Analytics charts integrated
- Signal confidence visualization integrated
- Watchlist signal distribution visualization integrated
- Mobile responsive charts
- Dark/light theme compatible
- No additional backend dependencies

Build Status:
- ESLint: 0 warnings, 0 errors
- TypeScript: 0 errors
- Production build: successful

Known Limitations:
- Charts depend on existing analytics history depth
- No advanced chart interactions
- No chart export functionality
- No multi-ticker chart comparison

Project Status:
- Sprint 7A Complete
- Sprint 7B Complete
- Sprint 8A Complete
- Sprint 8B Complete
- Sprint 9A Complete
- Sprint 9B Complete
- Insique V1.1 Complete

# Sprint 10B — Smart Search

## Objective

Upgrade Insique search from a basic ticker input into an intelligent stock discovery system.

---

## Problem Statement

After Sprint 10A, users could navigate efficiently but still needed prior knowledge of ticker symbols.

Examples:

User knows:

HDFCBANK.NS

Search succeeds.

User knows only:

HDFC Bank

Search fails.

This created a discovery problem for new users.

---

## Features Implemented

### Intelligent Autocomplete

Added real-time ticker suggestions while typing.

Examples:

Input:

hd

Suggestions:

* HDFCBANK.NS
* HDFCLIFE.NS
* HDFCAMC.NS

---

### Company Name Search

Users can now search using company names instead of exact ticker symbols.

Examples:

Input:

HDFC Bank

Result:

HDFCBANK.NS

Input:

Reliance

Result:

RELIANCE.NS

Benefits:

* Lower learning curve
* Faster stock discovery

---

### Exchange Awareness

Search results now display exchange information.

Examples:

* NSE (NS)
* BSE (BO)

Benefits:

* Better ticker identification
* Reduced ambiguity

---

### Search Suggestion Dropdown

Implemented an interactive search results panel.

Features:

* Dynamic suggestions
* Click-to-select
* Keyboard navigation support
* Loading states
* Error states

---

### Search Provider Integration

Integrated Yahoo Finance search infrastructure through backend proxy services.

Benefits:

* Large ticker coverage
* Company name matching
* Relevance ranking
* No manual ticker catalog maintenance

---

## Architecture Changes

### Backend

Added:

* Search Service Layer
* Search API Endpoint
* Search Response Schemas

Responsibilities:

* Query external provider
* Normalize responses
* Cache results
* Handle failures gracefully

---

### Frontend

Added:

* Search API hooks
* Search result types
* Suggestion dropdown component
* Search query utilities

Responsibilities:

* Debounced search requests
* Suggestion rendering
* Selection handling
* Keyboard interactions

---

## Search Flow

User Types:

mtar

↓

Frontend Debounce

↓

Search Endpoint

↓

Yahoo Finance Search

↓

Results Returned

↓

Suggestions Displayed

Example Result:

* MTARTECH.NS
* MTARTECH.BO

---

## User Experience Improvements

Before:

User must know exact ticker.

Example:

HDFCBANK.NS

After:

User can search naturally.

Examples:

* hdfc
* reliance
* tata
* infosys

Result:

* Easier stock discovery
* Better onboarding experience
* Reduced user friction

---

## Technical Improvements

### Debounced Requests

Search requests are delayed briefly while typing.

Benefits:

* Reduced API calls
* Better performance
* Improved responsiveness

---

### Cached Results

Frequently requested searches are cached.

Benefits:

* Faster repeat searches
* Reduced provider load

---

### Error Handling

Implemented graceful failure states.

Examples:

* Provider unavailable
* Network failure
* Empty search results

Benefits:

* Better resilience
* Improved user feedback

---

## Outcome

Sprint 10B successfully transformed search into an intelligent discovery system.

Users no longer need exact ticker knowledge to find stocks.

This sprint significantly improves usability and onboarding while creating the foundation for future recommendation systems.

Future Expansion:

* Popular Stocks
* High Confidence Suggestions
* Recommendation Ranking
* Signal-Aware Search

Status: COMPLETE
# Sprint 11A — Alert Engine

## Objective

Transform Insique from a passive analysis platform into a proactive market monitoring system by introducing automated alert evaluation, trigger detection, and alert history tracking.

---

## Problem Statement

Prior to Sprint 11A, users were required to manually revisit the platform to discover new opportunities.

Typical workflow:

Open Dashboard

↓

Check Watchlists

↓

Check Signals

↓

Check Analytics

↓

Repeat

This approach required constant manual monitoring and increased the likelihood of missing important market events.

---

## Features Implemented

### Alert Creation

Users can create custom market alerts tied to individual tickers.

Supported Alert Types:

* Price Alerts
* Signal Alerts
* Confidence Alerts
* RSI Alerts

Examples:

RELIANCE.NS
Price > 3500

HDFCBANK.NS
Price < 1800

INFY.NS
Signal = BUY

ICICIBANK.NS
Confidence > 80%

RELIANCE.NS
RSI < 30

---

### Alert Management

Implemented full alert lifecycle management.

Features:

* Create alerts
* View alerts
* Update alerts
* Delete alerts
* Enable/Disable alerts

Benefits:

* Flexible monitoring
* User-controlled alert behavior
* Improved alert organization

---

### Background Alert Evaluation

Introduced automated alert processing using APScheduler.

Evaluation Interval:

Every 5 minutes

Responsibilities:

* Load active alerts
* Evaluate conditions
* Detect trigger events
* Record trigger history

Benefits:

* No manual monitoring required
* Consistent evaluation cycle
* Foundation for future notifications

---

### Trigger Detection Engine

Implemented a dedicated alert evaluation service.

Supported Evaluations:

* Price thresholds
* Signal changes
* Confidence thresholds
* RSI thresholds

Benefits:

* Centralized evaluation logic
* Easier maintenance
* Future extensibility

---

### Trigger History

Implemented persistent trigger tracking.

Each trigger stores:

* Alert reference
* Trigger timestamp
* Evaluation snapshot
* Trigger context

Benefits:

* Historical visibility
* Audit trail
* Future notification support

---

## Architecture Changes

### Database Layer

Added:

alerts

Stores:

* Alert definition
* Condition type
* Threshold values
* Status
* Ownership

triggered_alerts

Stores:

* Trigger records
* Evaluation snapshots
* Trigger timestamps

Benefits:

* Separation of configuration and history
* Improved scalability
* Better reporting capabilities

---

### Backend Services

Added:

Alert Repository

Alert Service

Alert Evaluation Service

Scheduler Service

Responsibilities:

* CRUD operations
* Alert ownership validation
* Condition evaluation
* Scheduled execution

---

### API Layer

Implemented alert endpoints for:

* Create Alert
* List Alerts
* Get Alert
* Update Alert
* Delete Alert
* View Trigger History

Benefits:

* Complete alert lifecycle support
* Frontend integration
* Future automation support

---

## User Experience Improvements

Before:

User manually checks markets.

↓

Opportunity may be missed.

After:

User creates alert.

↓

Background scheduler monitors conditions.

↓

Trigger recorded automatically.

↓

History available for review.

Benefits:

* Reduced manual effort
* Continuous monitoring
* Improved awareness

---

## Technical Improvements

### Ownership Enforcement

All alerts are tied to authenticated users.

Benefits:

* Data isolation
* Security
* Multi-user support

---

### Indexed Queries

Added database indexes for:

* Active alerts
* User alerts
* Trigger history

Benefits:

* Faster evaluations
* Better scalability

---

### Automated Scheduling

Introduced application-managed scheduler lifecycle.

Startup:

Scheduler starts automatically.

Shutdown:

Scheduler stops gracefully.

Benefits:

* Reliable execution
* Cleaner deployment behavior

---

## Testing & Validation

Implemented:

* Alert CRUD tests
* Evaluation engine tests
* Trigger generation tests
* Ownership validation tests

Results:

176 tests passing

0 failures

Production build successful

Database migration successful

---

## Outcome

Sprint 11A successfully introduced the Alert Engine.

Insique can now:

* Monitor market conditions automatically
* Evaluate user-defined rules
* Record trigger events
* Maintain trigger history

This sprint establishes the foundation for Sprint 11B Notification Delivery.

Future Expansion:

* In-App Notifications
* Email Alerts
* Telegram Alerts
* Discord Alerts
* Push Notifications

Status: COMPLETE
# Sprint 11B — Notification Center

## Objective

Transform Insique's Alert Engine into a proactive user notification system by delivering triggered alerts directly inside the platform.

---

## Problem Statement

Sprint 11A introduced automated alert evaluation and trigger detection.

However, users still needed to manually review alert history to discover whether an alert had fired.

Workflow before Sprint 11B:

Alert triggers

↓

Trigger stored in database

↓

User manually opens Alerts page

↓

User checks trigger history

This reduced the practical value of alerts because important events could still be overlooked.

---

## Features Implemented

### In-App Notifications

Introduced a centralized notification system for triggered alerts.

When an alert condition is met:

Alert Trigger

↓

Notification Generated

↓

Displayed to User

Benefits:

* Immediate visibility
* Reduced manual monitoring
* Improved user awareness

---

### Notification Center

Added a dedicated notification center accessible from the global navigation bar.

Features:

* Notification history
* Unread indicators
* Read indicators
* Trigger timestamps

Benefits:

* Centralized alert visibility
* Consistent user experience
* Historical tracking

---

### Notification Bell

Added a notification bell to the application top bar.

Features:

* Real-time unread count
* Visual notification indicator
* One-click access to notifications

Benefits:

* Increased discoverability
* Familiar dashboard pattern
* Faster access to important events

---

### Unread Tracking

Implemented notification state management.

States:

* Unread
* Read

Benefits:

* Prevents duplicate review
* Improves organization
* Enables future notification workflows

---

### Mark as Read

Users can manually acknowledge notifications.

Features:

* Mark individual notifications as read
* Update unread count automatically

Benefits:

* Better notification management
* Cleaner notification experience

---

### Mark All as Read

Added bulk notification management.

Benefits:

* Faster cleanup
* Improved usability
* Better handling of large notification volumes

---

## Architecture Changes

### Database Layer

Added:

notifications

Stores:

* User reference
* Alert reference
* Trigger reference
* Notification title
* Notification content
* Read status
* Creation timestamp

Benefits:

* Separation from trigger history
* Future notification channel support
* Improved scalability

---

### Notification Pipeline

Introduced a dedicated notification flow.

Workflow:

Alert Evaluation

↓

Trigger Created

↓

Notification Service

↓

Notification Record

↓

Notification Center

Benefits:

* Decoupled architecture
* Future extensibility
* Easier maintenance

---

### Backend Services

Added:

Notification Repository

Notification Service

Responsibilities:

* Notification creation
* Notification retrieval
* Read state management
* Unread count calculation

---

## API Layer

Implemented endpoints for:

* List Notifications
* Get Notification Count
* Mark Notification Read
* Mark All Read
* Notification Preferences

Benefits:

* Frontend integration
* Consistent notification management
* Future external channel support

---

## User Experience Improvements

Before:

Alert triggers

↓

Stored silently

↓

User must investigate manually

After:

Alert triggers

↓

Notification generated

↓

Bell count updates

↓

User opens notification center

↓

Notification reviewed

Benefits:

* Faster awareness
* Reduced friction
* Improved engagement

---

## Technical Improvements

### Trigger-to-Notification Conversion

Created a dedicated layer responsible for converting alert triggers into user-facing notifications.

Benefits:

* Cleaner architecture
* Better separation of concerns
* Multi-channel readiness

---

### Notification State Management

Implemented efficient unread tracking.

Benefits:

* Accurate badge counts
* Faster queries
* Better user experience

---

### Indexed Notification Queries

Added indexes for:

* User notifications
* Unread notifications
* Notification timestamps

Benefits:

* Faster retrieval
* Improved dashboard performance
* Better scalability

---

## Testing & Validation

Implemented:

* Notification creation tests
* Read/unread state tests
* Notification retrieval tests
* Notification count tests
* Trigger integration tests

Results:

All tests passing

No linting errors

Production build successful

Notification pipeline verified

---

## Outcome

Sprint 11B successfully introduced the Notification Center.

Insique can now:

* Detect market conditions
* Generate alerts automatically
* Notify users inside the platform
* Track read/unread notification status
* Maintain notification history

This sprint completes the first proactive monitoring workflow within Insique.

Future Expansion:

* Email Notifications
* Telegram Notifications
* Discord Notifications
* Browser Push Notifications
* Notification Preferences

Status: COMPLETE
