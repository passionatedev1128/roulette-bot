"""
Web Interface Architecture Overview

This document outlines the planned architecture for the Roulette Bot web interface implementation covering backend services, realtime event handling, and the frontend dashboard.
"""

## Goals

- Deliver a responsive dashboard that visualises live roulette results, active bets, balances, and performance metrics.
- Enable full configuration management (strategy, gale, risk, maintenance) without editing JSON files.
- Provide remote bot control (start/stop/mode) with realtime status feedback.
- Establish a scalable API + WebSocket layer to integrate the existing automation bot with the UI.

## High-Level Architecture

- **Backend Service (FastAPI)**
  - REST endpoints for configuration, status, results, bets, balance, and statistics.
  - WebSocket endpoint that streams bot events (`new_result`, `bet_placed`, `bet_resolved`, `balance_update`, `status_change`, `error`).
  - `BotManager` orchestrator wraps `RouletteBot`, tracks bot lifecycle, and publishes events.
  - `ConfigStore` built on top of existing `ConfigLoader` handles presets and live updates.
  - Stats derived from `RouletteLogger` CSV/JSON logs using pandas.

- **Event Dispatching**
  - Thread-safe dispatcher bridges the bot thread and FastAPI event loop.
  - Maintains async queues per WebSocket client; leverages `loop.call_soon_threadsafe` for cross-thread safety.

- **Frontend Dashboard (React + Vite)**
  - SPA served separately via Vite dev server / static build.
  - React Query manages REST data; native WebSocket client ingests realtime events to keep widgets fresh.
  - Component layout: Status header, live results timeline, active bets, balance & P/L cards, performance charts, configuration forms, mode controls.
  - Charts implemented with Recharts; styling via CSS modules / utility classes.

- **Shared Models**
  - Pydantic schemas ensure typed responses and input validation for API operations.
  - Frontend TypeScript typings (or JS JSDoc) mirror schema structures.

## Backend Modules

```
backend/server/
  __init__.py
  app.py                 -> FastAPI app factory & router registration
  bot_manager.py         -> Lifecycle orchestration, config, stats, event publishing
  events.py              -> EventDispatcher for WebSocket subscribers
  schemas.py             -> Pydantic models for API contracts
  routes/
    config.py            -> /api/config endpoints, preset management
    status.py            -> /api/status, /api/balance
    results.py           -> /api/results/latest, /api/bets/*
    control.py           -> /api/bot/start|stop|mode
    stats.py             -> /api/stats/* endpoints
  websocket.py           -> /ws/events endpoint
```

Key responsibilities:

- **BotManager**
  - Load/save config via `ConfigLoader`.
  - Instantiate `RouletteBot` with optional `event_dispatcher`.
  - Provide thread-safe getters for realtime state (balance, history, active bets, status, last activity).
  - Aggregate stats from log files and maintain in-memory caches for quick responses.

- **EventDispatcher**
  - Maintains subscriber queues.
  - Receives events from bot thread and pushes to FastAPI loop.

## Frontend Structure

```
web/
  package.json
  vite.config.ts
  index.html
  src/
    main.tsx
    App.tsx
    api/client.ts        -> Axios instance + helpers
    hooks/useWebSocket.ts
    components/
      DashboardLayout.tsx
      StatusBar.tsx
      LiveResults.tsx
      ActiveBetsPanel.tsx
      BalanceCards.tsx
      PerformanceCharts.tsx
      ConfigForm.tsx
      ModeControls.tsx
    styles/
      globals.css
```

Data flow:

- React Query fetches REST endpoints on interval (status, balance, stats, config).
- WebSocket events update React state immediately (append latest results, refresh active bet, adjust balance and status badges).
- Config form uses controlled inputs with optimistic validation; submission triggers `PUT /api/config` and optional preset save.

## Deployment & Ops

- Backend served via `uvicorn backend.server.app:app --reload` (configurable host/port in `.env`).
- Frontend dev server via `npm install && npm run dev` (Vite default port 5173).
- Production build served as static assets (either via CDN or behind reverse proxy) while API remains on 8000.
- CORS configured for localhost dev and configurable origins for production.

## Next Steps

1. Implement backend modules & routes per structure above.
2. Extend `RouletteBot` to emit events and expose state required by the API.
3. Build frontend scaffolding and integrate API/WebSocket clients.
4. Verify end-to-end flow with simulated bot data (test mode) before connecting to live detection.


