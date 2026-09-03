# Resume Handoff — Logged-In Home Dashboard (Phase 4)

**Created:** 2026-09-03
**Status:** Design + plan ready. Implementation NOT started.
**Execution approach chosen:** Subagent-Driven (`superpowers:subagent-driven-development`).

## How to Resume

When ready to implement, in a fresh session:

1. Read this file.
2. Read the plan: `docs/superpowers/plans/2026-09-03-logged-in-dashboard.md`.
3. Load the `superpowers:subagent-driven-development` skill and follow it, executing the plan Task 1 → Task 6.
4. Load the `superpowers:executing-plans` skill as a fallback if subagents are unavailable.

## Current State

### Committed (HEAD = `a041600`)
- `a041600` docs: Add logged-in home dashboard design (Phase 4) — includes:
  - `docs/superpowers/specs/2026-09-03-logged-in-dashboard-design.md` (approved design)
  - `.gitignore` now ignores `.superpowers/`

### Uncommitted Phase 3 work (MUST be preserved — do not reset/clean)
The Phase 3 "login-gated access" implementation is complete and verified but **uncommitted**. Files:
- `Makefile` (docker-compose detection fix — macOS/Linux)
- `backend/app/api/agents.py`, `backend/app/api/mcp_servers.py`
- `backend/app/core/dependencies.py` (added `get_optional_user`)
- `backend/app/schemas/agent.py`
- `frontend/src/app/components/agent-detail/*`, `agents-list/*`, `mcp-server-detail/*`, `mcp-servers/*`
- `frontend/src/app/models/agent.model.ts`, `frontend/src/app/services/api.service.ts`
- Untracked: `docs/phase3-plan.md`, `frontend/src/app/components/login-wall/`

When committing dashboard tasks, stage **only** dashboard files (each plan task lists exact `git add` paths). Never `git add -A`.

### Untracked dashboard artifacts
- `docs/superpowers/plans/2026-09-03-logged-in-dashboard.md` — the implementation plan
- `docs/superpowers/plans/2026-09-03-logged-in-dashboard-RESUME.md` — this file

## Design Summary (approved)

Home route (`/`) becomes auth-aware:
- `@if (!authReady())` → loading skeleton (new `AuthService.initialized` signal prevents guest-page flash)
- `@else if (isAuthenticated())` → dashboard: `DashboardGreetingComponent` + `FavoritesSectionComponent` + `TrendingSectionComponent`
- `@else` → existing marketing page, unchanged

No backend changes. Frontend-only, all existing authenticated APIs.

## Environment / Verification Commands

- Frontend build (source volume-mounted into container): `docker exec ai_agent_hub_frontend npm run build`
- Dev server: `http://localhost:4200` (container `ai_agent_hub_frontend`, hot-reload)
- Backend API: `http://localhost:8333` (container `ai_agent_hub_backend`, hot-reload, `--reload`)
- Container names: `ai_agent_hub_backend`, `ai_agent_hub_db`, `ai_agent_hub_frontend`

## Relevant Services

- `AuthService` (`frontend/src/app/services/auth.service.ts`) — `user` signal, `isAuthenticated` computed, `initialized` signal (to add), `ensureInitialized()` called by `HeaderComponent`.
- `FavoritesService` (`.../services/favorites.service.ts`) — `getUserFavorites(page, limit)`, `FavoriteItem`.
- `ApiService` (`.../services/api.service.ts`) — `getAgents(page, limit, {sort_by, sort_order})`, `getMCPServers(...)`.
- `HomeComponent` (`frontend/src/app/components/home/home.component.ts|html|css`) — currently static marketing page.

## Notes

- Phase 3 guest gating means authenticated calls return full data (no 3-item cap) — dashboard relies on this.
- Budget WARNINGS from `ng build` are pre-existing and acceptable.
- The visual-companion mockups live in `.superpowers/` (git-ignored).