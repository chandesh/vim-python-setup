# Design — Date-Added Filter for Listing Pages

**Date:** 2026-09-03
**Status:** Approved design (pre-implementation)
**Scope:** Frontend + backend (no DB changes)

## Goal

Let users filter the AI Agents and MCP Servers listing pages by the date an item was added to the directory (`created_at`), using either quick presets or a custom date range. Search results must honor the same filter.

## Current Architecture

- `GET /api/v1/agents` and `GET /api/v1/agents/search` — filter params: `category_id`, `pricing_model`, `featured`; sort by name/created_at/view_count.
- `GET /api/mcp-servers` and `GET /api/mcp-servers/search` — filter params: `category_id`, `language`, `scope`, `featured`; sort by name/created_at/star_count/view_count.
- Both `Agent` and `MCPServer` models have an indexed `created_at` column.
- Both listing components (`agents-list`, `mcp-servers`) share a filter pattern: state vars → filters object → ApiService; reset on change/clear; active-filter badges.
- `ApiService.getAgents`/`getMCPServers` whitelist their filter keys; `searchAgents`/`searchMCPServers` accept no filters today.

## Design

### Backend

1. **Shared helper** — new module `backend/app/api/date_filter.py`:

   ```python
   def apply_created_at_range(query, model, date_from: date | None, date_to: date | None):
       if date_from:
           query = query.filter(model.created_at >= datetime.combine(date_from, time.min))
       if date_to:
           query = query.filter(model.created_at <= datetime.combine(date_to, time.max))
       return query
   ```

   Day-inclusive: `date_from` matches from 00:00:00, `date_to` matches through 23:59:59.999.

   **Timezone semantics:** `created_at` is a `timestamptz` column; the helper builds naive datetimes which Postgres interprets in the session timezone (UTC for the app). The frontend sends date-only strings computed in the client's local timezone, so "last 7 days" maps to UTC day boundaries. A small skew near midnight is acceptable for this feature and not worth a tz-conversion pass.

2. **Endpoint params** — add `date_from: Optional[date]` and `date_to: Optional[date]` to all four endpoints (agents list, agents search, mcp-servers list, mcp-servers search). Apply the helper after existing filters, before count/sort.

3. **Validation** — if both are provided and `date_from > date_to`, raise `HTTPException(422, "date_from must be on or before date_to")`. Guard added before the query runs.

### Frontend

1. **ApiService**
   - `getAgents` filter type: add `date_from?: string; date_to?: string` and append as query params.
   - `getMCPServers` filter type: same additions.
   - `searchAgents`/`searchMCPServers`: add optional `date_from?`/`date_to?` params and append.

2. **Listing components** (`agents-list`, `mcp-servers`) — add a "Date Added" filter group to the existing filter row:
   - State: `selectedDatePreset = ''` ('' = All time), `customDateFrom = ''`, `customDateTo = ''`.
   - `<select>` options: All time, Last 7 days, Last 30 days, Last 90 days, Custom.
   - When `selectedDatePreset === 'custom'`, show two `<input type="date">` (From / To).
   - Helper `resolveDateRange()` → `{ date_from?, date_to? }`:
     - Presets compute from today (`today - N days`, date only) with no upper bound.
     - Custom requires both inputs; empty/incomplete custom input is ignored (falls back to no date filter).
   - Wire into the existing `filters` object in the list load path, and pass to the search method in search mode.
   - Add to the active-filter badges condition and `clearFilters()`.

### Edge Cases

- Inverted range → 422 from backend; frontend shows the existing generic error path ("Failed to load …").
- Custom mode with only one date set → no date filter applied (inputs ignored).
- Guest preview: filter applies server-side before the 3-item cap, so guests see matching preview items.
- Search + date filter: both endpoints accept the params, so the filter works in search mode too.

### Verification

- Backend: curl each endpoint with `date_from`/`date_to` (inclusive boundaries, inverted-range 422).
- Frontend: `docker exec ai_agent_hub_frontend npm run build` (exit 0).
- Manual QA: preset filters return expected counts; custom range filters; badges appear; Clear All resets; search respects the date filter; guest preview still works.

### Out of Scope

- Filtering by `updated_at` (chosen field is `created_at`).
- Server-side date facet/counts in the response.
- Preserving filters across navigation/URL query strings.
- Changes to seed/ingest data.

## Files Touched

- Backend: `backend/app/api/date_filter.py` (new), `backend/app/api/agents.py`, `backend/app/api/mcp_servers.py`
- Frontend: `frontend/src/app/services/api.service.ts`, `frontend/src/app/components/agents-list/agents-list.component.{ts,html,css}`, `frontend/src/app/components/mcp-servers/mcp-servers.component.{ts,html,css}`