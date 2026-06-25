# 🐞 Insique Beta Bug Tracker & Product Roadmap

**Project:** Insique
**Version:** Beta v0.1
**Status:** Active Beta Testing

---

# 🔴 P0 — Critical (Must Fix Before Public Release)

## 1. Password Visibility Toggle

**Status:** ❌ Open

### User Feedback

> "I can't see what I'm typing while entering my password."

### Issue

Both Sign Up and Login password fields do not have a Show/Hide password (eye icon).

### Expected

* Eye icon beside password field
* Toggle between hidden and visible password
* Works for both Password & Confirm Password

### Priority

⭐⭐⭐⭐⭐

---

## 2. Forgot Password Flow

**Status:** ❌ Open

### User Feedback

> "What if I forget my password?"

### Issue

There is currently no password recovery mechanism.

### Solution

* Add **Forgot Password**
* Email reset link
* Secure password reset token
* Expiration (15–30 min)

### Priority

⭐⭐⭐⭐⭐

---

## 3. Delete Account

**Status:** ❌ Open

### User Feedback

> "How do I permanently delete my account?"

### Issue

Users cannot remove their account or data.

### Solution

Settings → Account

```
Delete Account
```

Requirements

* Confirmation dialog
* Password verification
* Permanent database deletion
* Logout all sessions

### Priority

⭐⭐⭐⭐⭐

---

# 🟠 P1 — High Priority

## 4. Dashboard Feels Static

**Status:** ❌ Open

### User Feedback

> "Dashboard looks too simple."

### Current State

Dashboard mainly displays static cards.

### Improvements

* Portfolio Summary
* Market Status
* Today's Movers
* Latest Signals
* Watchlist Snapshot
* Top Gainers / Losers
* News Highlights
* Animated charts

### Goal

Dashboard should answer:

> "What happened in the market today?"

### Priority

⭐⭐⭐⭐

---

## 5. Watchlist Search Suggestions Missing

**Status:** ❌ Open

### User Feedback

> "Typing inside the watchlist search doesn't show stock suggestions."

### Screenshot

Observed during beta testing.

### Current Behaviour

Searching:

```
AAPL
HDFC
RELIANCE
```

does not consistently display recommendations.

### Expected

Autocomplete should appear while typing.

Example:

```
HDFCBANK.NS
HDFC
HDFCLIFE.NS
```

### Possible Causes

* Search API not called
* Debounce issue
* Wrong endpoint
* State not updating
* Empty response handling

### Priority

⭐⭐⭐⭐⭐

---

## 6. Signals Not Fully Populating

**Status:** ❌ Open

### User Feedback

Signal indicators appear incomplete.

### Current Behaviour

Observed:

* RSI → Neutral
* SMA → Trend direction unavailable
* Missing values
* Confidence = 0%

### Expected

Every indicator should calculate properly.

Required

* RSI
* SMA
* EMA
* MACD

Each should include

* Value
* Signal
* Confidence
* Explanation

### Possible Causes

* Market data missing
* Indicator calculations failing
* API response incomplete
* Mapping issue between backend & frontend

### Priority

⭐⭐⭐⭐⭐

---

# 🟡 P2 — Quality of Life Improvements

* Better loading animations
* Empty states with illustrations
* Toast notifications
* Better error messages
* Responsive improvements
* Keyboard shortcuts
* Dark/Light theme persistence

---

# 💡 Future Feature Requests

* Email alerts
* AI Stock Summary
* Portfolio Performance Graph
* Dividend Tracking
* Watchlist sharing
* News Sentiment
* Economic Calendar
* Paper Trading
* Price Alerts
* Watchlist folders

---

# 📊 Current Beta Progress

| Module         | Status                |
| -------------- | --------------------- |
| Authentication | ✅ Stable              |
| Registration   | ✅ Stable              |
| Login          | ✅ Stable              |
| Deployment     | ✅ Stable              |
| Database       | ✅ Stable              |
| Watchlists     | 🟡 Needs improvements |
| Search         | 🟡 Needs fixes        |
| Signals        | 🔴 Critical           |
| Dashboard      | 🟡 Needs enhancement  |
| Portfolio      | 🟡 In Progress        |
| Alerts         | ⏳ Planned             |

---

## 🎯 Next Milestone

Before adding new features:

* Fix all P0 issues
* Resolve major P1 issues
* Improve dashboard experience
* Complete signal engine
* Improve watchlist search reliability

**Goal:** Release **Insique Beta v0.2** with a polished and reliable user experience.
