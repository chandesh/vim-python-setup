# Date-Added Filter for Listing Pages — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users filter the AI Agents and MCP Servers listing pages (and their search results) by the date an item was added (`created_at`), via quick presets (7/30/90 days) or a custom From/To range.

**Architecture:** Server-side filtering. Add `date_from`/`date_to` query params (ISO `YYYY-MM-DD`) to the four list/search endpoints, backed by a shared helper that applies an inclusive day-range filter on `created_at`. The frontend computes dates from presets or custom inputs and sends them through ApiService. No DB changes.

**Tech Stack:** FastAPI (Python 3.11, SQLAlchemy), Angular 20 standalone components + signals/forms, theme CSS variables.

**Design doc:** `docs/superpowers/specs/2026-09-03-date-filter-listing-pages-design.md`

**Repo state note:** There are many uncommitted changes in the working tree (Phase 3 login-gating, dashboard, favorite fixes, logo fixes, ingest scripts). Each commit step below stages **only** the files listed for that task — never `git add -A` or `git add .`.

**Verification note:** The repo has no pytest scaffolding (empty `backend/tests/`, no conftest/fixtures), so backend verification uses the project's established curl pattern. Frontend verification uses the docker build. TDD is not practiced in this repo; do not scaffold a test harness as part of this plan.

**Backend build/verify:** backend hot-reloads via uvicorn `--reload` in container `ai_agent_hub_backend`; API at `http://localhost:8333`. Frontend source is volume-mounted into container `ai_agent_hub_frontend`; build with:

```bash
docker exec ai_agent_hub_frontend npm run build
```

Expected on success: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing and acceptable.

---

### Task 1: Create shared backend date-range helper

**Files:**
- Create: `backend/app/api/date_filter.py`

- [ ] **Step 1: Create the helper module**

`backend/app/api/date_filter.py`:

```python
"""Shared date-range filtering helpers for list/search endpoints."""
from datetime import date, datetime, time

from fastapi import HTTPException, status


def validate_date_range(date_from: date | None, date_to: date | None) -> None:
    """Raise 422 when the provided range is inverted."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from must be on or before date_to",
        )


def apply_created_at_range(query, model, date_from: date | None, date_to: date | None):
    """Filter `model.created_at` to the inclusive day range [date_from, date_to].

    `date_from` matches from 00:00:00; `date_to` matches through 23:59:59.999.
    Naive datetimes are interpreted by Postgres in the session timezone (UTC).
    """
    if date_from:
        query = query.filter(model.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.filter(model.created_at <= datetime.combine(date_to, time.max))
    return query
```

- [ ] **Step 2: Verify the module imports cleanly**

Run: `docker exec ai_agent_hub_backend python -c "from app.api.date_filter import apply_created_at_range, validate_date_range; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/date_filter.py
git commit -m "feat(api): add shared created_at date-range filter helper"
```

---

### Task 2: Add date filter to the agents endpoints

**Files:**
- Modify: `backend/app/api/agents.py`

- [ ] **Step 1: Update imports**

In `backend/app/api/agents.py`, add `from datetime import date` to the top import block, and add the helper import after the existing app imports:

```python
from datetime import date
```

and (with the other `app.` imports):

```python
from app.api.date_filter import apply_created_at_range, validate_date_range
```

- [ ] **Step 2: Add params to `list_agents`**

In `list_agents`, add these two query params after `featured` (before `sort_by`):

```python
    date_from: Optional[date] = Query(None, description="Only items created on or after this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Only items created on or before this date (YYYY-MM-DD)"),
```

- [ ] **Step 3: Apply the filter in `list_agents`**

After the `featured` filter block (line ~55) and before `# Get total count`:

```python
    validate_date_range(date_from, date_to)
    if date_from or date_to:
        query = apply_created_at_range(query, Agent, date_from, date_to)
```

- [ ] **Step 4: Add params to `search_agents`**

In `search_agents`, add the same two params after `sort_order` (before `db: Session`):

```python
    date_from: Optional[date] = Query(None, description="Only items created on or after this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Only items created on or before this date (YYYY-MM-DD)"),
```

- [ ] **Step 5: Apply the filter in `search_agents`**

After the `search_filter` query is built (after `.filter(search_filter)`, line ~128) and before `total = query.count()`:

```python
    validate_date_range(date_from, date_to)
    if date_from or date_to:
        query = apply_created_at_range(query, Agent, date_from, date_to)
```

- [ ] **Step 6: Verify the endpoints**

Backend hot-reloads. Register a throwaway user to authenticate (guests get a 3-item cap which also works, but authed calls show full totals):

```bash
EMAIL="df_agents_$(date +%s)@test.com"
curl -s -X POST http://localhost:8333/api/v1/auth/register -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"dfagentst\",\"password\":\"testpass123\"}" >/dev/null
TOKEN=$(curl -s -X POST http://localhost:8333/api/v1/auth/login -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"testpass123\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['access_token'])")

echo "=== list: date_from only ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/v1/agents?limit=5&date_from=2026-08-01" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('total=', d['total'])"

echo "=== list: date_to only (no items before 2026-01-01) ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/v1/agents?limit=5&date_to=2026-01-01" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('total=', d['total'])"

echo "=== search: date filter ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/v1/agents/search?q=AI&date_from=2026-08-01" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('total=', d['total'])"

echo "=== list: inverted range -> 422 ==="
curl -s -o /dev/null -w "HTTP=%{http_code}\n" -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8333/api/v1/agents?date_from=2026-09-01&date_to=2026-08-01"
```

Expected: `total=` is >= 0 and identical for the `date_from=2026-08-01` cases (all current data was seeded/ingested on/after 2026-08-25); the `date_to=2026-01-01` case returns `total= 0`; inverted range prints `HTTP=422`.

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/agents.py
git commit -m "feat(api): add created_at date filter to agents endpoints"
```

---

### Task 3: Add date filter to the MCP servers endpoints

**Files:**
- Modify: `backend/app/api/mcp_servers.py`

- [ ] **Step 1: Update imports**

In `backend/app/api/mcp_servers.py`, add `from datetime import date` to the top import block and add the helper import with the other `app.` imports:

```python
from app.api.date_filter import apply_created_at_range, validate_date_range
```

- [ ] **Step 2: Add params to `get_mcp_servers`**

Add after `featured` (before `sort_by`):

```python
    date_from: Optional[date] = Query(None, description="Only items created on or after this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Only items created on or before this date (YYYY-MM-DD)"),
```

- [ ] **Step 3: Apply the filter in `get_mcp_servers`**

After the `featured` filter block (line ~53) and before `# Get total count`:

```python
        validate_date_range(date_from, date_to)
        if date_from or date_to:
            query = apply_created_at_range(query, MCPServer, date_from, date_to)
```

- [ ] **Step 4: Add params to `search_mcp_servers`**

Add after `sort_order` (before `db: Session`):

```python
    date_from: Optional[date] = Query(None, description="Only items created on or after this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Only items created on or before this date (YYYY-MM-DD)"),
```

- [ ] **Step 5: Apply the filter in `search_mcp_servers`**

After the search query is built (after `.filter(search_filter)`, line ~120) and before `# Get total count`:

```python
        validate_date_range(date_from, date_to)
        if date_from or date_to:
            db_query = apply_created_at_range(db_query, MCPServer, date_from, date_to)
```

- [ ] **Step 6: Verify the endpoints**

```bash
EMAIL="df_servers_$(date +%s)@test.com"
curl -s -X POST http://localhost:8333/api/v1/auth/register -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"dfservert\",\"password\":\"testpass123\"}" >/dev/null
TOKEN=$(curl -s -X POST http://localhost:8333/api/v1/auth/login -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"testpass123\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['access_token'])")

echo "=== list: date_from only ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/mcp-servers?limit=5&date_from=2026-08-01" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('total=', d['total'])"

echo "=== list: date_to before all data -> 0 ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/mcp-servers?limit=5&date_to=2026-01-01" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('total=', d['total'])"

echo "=== search: date filter ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/mcp-servers/search?query=mcp&date_from=2026-08-01" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('total=', d['total'])"

echo "=== list: inverted range -> 422 ==="
curl -s -o /dev/null -w "HTTP=%{http_code}\n" -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8333/api/mcp-servers?date_from=2026-09-01&date_to=2026-08-01"
```

Expected: `date_from=2026-08-01` returns the full server total; `date_to=2026-01-01` returns `total= 0`; inverted range prints `HTTP=422`.

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/mcp_servers.py
git commit -m "feat(api): add created_at date filter to MCP servers endpoints"
```

---

### Task 4: Extend ApiService with date filter params

**Files:**
- Modify: `frontend/src/app/services/api.service.ts`

- [ ] **Step 1: Add `date_from`/`date_to` to `getAgents`**

Extend the `getAgents` filter type and param building:

```ts
  getAgents(page: number = 1, limit: number = 20, filters?: {
    category_id?: string;
    pricing_model?: string;
    featured?: boolean;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_order?: string;
  }): Observable<ApiResponse<AgentListResponse>> {
```

Add after the `featured` param block:

```ts
    if (filters?.date_from) {
      params = params.set('date_from', filters.date_from);
    }
    if (filters?.date_to) {
      params = params.set('date_to', filters.date_to);
    }
```

- [ ] **Step 2: Add `date_from`/`date_to` to `getMCPServers`**

Extend the `getMCPServers` filter type and param building:

```ts
  getMCPServers(page: number = 1, limit: number = 12, filters?: {
    category_id?: string;
    language?: string;
    scope?: string;
    featured?: boolean;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_order?: string;
  }): Observable<ApiResponse<MCPServerListResponse>> {
```

Add after the `featured` param block:

```ts
    if (filters?.date_from) {
      params = params.set('date_from', filters.date_from);
    }
    if (filters?.date_to) {
      params = params.set('date_to', filters.date_to);
    }
```

- [ ] **Step 3: Add optional date params to `searchAgents`**

Change the signature and add param building:

```ts
  searchAgents(query: string, page: number = 1, limit: number = 20, sort_by?: string, sort_order?: string, date_from?: string, date_to?: string): Observable<ApiResponse<AgentListResponse>> {
```

Add after the `sort_order` block:

```ts
    if (date_from) {
      params = params.set('date_from', date_from);
    }
    if (date_to) {
      params = params.set('date_to', date_to);
    }
```

- [ ] **Step 4: Add optional date params to `searchMCPServers`**

Change the signature and add param building:

```ts
  searchMCPServers(query: string, page: number = 1, limit: number = 12, sort_by?: string, sort_order?: string, date_from?: string, date_to?: string): Observable<ApiResponse<MCPServerListResponse>> {
```

Add after the `sort_order` block:

```ts
    if (date_from) {
      params = params.set('date_from', date_from);
    }
    if (date_to) {
      params = params.set('date_to', date_to);
    }
```

- [ ] **Step 5: Verify the build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/app/services/api.service.ts
git commit -m "feat(api): support date_from/date_to in listing and search calls"
```

---

### Task 5: Add date filter UI to the Agents listing page

**Files:**
- Modify: `frontend/src/app/components/agents-list/agents-list.component.ts`
- Modify: `frontend/src/app/components/agents-list/agents-list.component.html`
- Modify: `frontend/src/app/components/agents-list/agents-list.component.css`

- [ ] **Step 1: Add filter state and helpers (TypeScript)**

In `agents-list.component.ts`, add state after `showFeaturedOnly = false;`:

```ts
  selectedDatePreset = '';
  customDateFrom = '';
  customDateTo = '';
```

Add helper methods to the class (after `clearFilters()`):

```ts
  /** Compute date_from/date_to from the preset or custom inputs. */
  resolveDateRange(): { date_from?: string; date_to?: string } {
    if (this.selectedDatePreset === 'custom') {
      if (!this.customDateFrom || !this.customDateTo) {
        return {};
      }
      return { date_from: this.customDateFrom, date_to: this.customDateTo };
    }
    if (!this.selectedDatePreset) {
      return {};
    }
    const days = parseInt(this.selectedDatePreset, 10);
    const from = new Date();
    from.setDate(from.getDate() - days);
    return { date_from: from.toISOString().slice(0, 10) };
  }

  getDateFilterLabel(): string {
    if (this.selectedDatePreset === 'custom') {
      return `Custom (${this.customDateFrom || '?'} → ${this.customDateTo || '?'})`;
    }
    return `Last ${this.selectedDatePreset} days`;
  }
```

- [ ] **Step 2: Wire the date range into `loadAgents`**

In `loadAgents`, add `const dateRange = this.resolveDateRange();` at the top of the method (right after `this.error = null;`). In search mode, pass the dates:

```ts
      this.apiService.searchAgents(this.searchQuery, this.currentPage, this.limit, actualSortBy, actualSortOrder, dateRange.date_from, dateRange.date_to).subscribe({
```

In the filters branch, add before `filters.sort_by = ...`:

```ts
      if (dateRange.date_from) filters.date_from = dateRange.date_from;
      if (dateRange.date_to) filters.date_to = dateRange.date_to;
```

- [ ] **Step 3: Reset in `clearFilters`**

Add to `clearFilters()` (with the other resets, before `this.currentPage = 1;`):

```ts
    this.selectedDatePreset = '';
    this.customDateFrom = '';
    this.customDateTo = '';
```

- [ ] **Step 4: Add the filter controls (HTML)**

In `agents-list.component.html`, inside the `<div class="filters-grid">`, add the "Date Added" group right before the `<!-- Clear Filters -->` comment block (after the Featured filter group). Two separate groups so From/To inputs only render in custom mode:

```html
          <!-- Date Added Filter -->
          <div class="filter-group">
            <label for="datePreset" class="filter-label">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="inline-block mr-1">
                <path d="M2 2a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V2zm2-1a1 1 0 00-1 1v12a1 1 0 001 1h8a1 1 0 001-1V2a1 1 0 00-1-1H4zm1 3a.5.5 0 01.5-.5h5a.5.5 0 010 1h-5A.5.5 0 015 4zm.5 2.5h5a.5.5 0 010 1h-5a.5.5 0 010-1zM6 9.5a.5.5 0 01.5-.5h3a.5.5 0 010 1h-3a.5.5 0 01-.5-.5z"/>
              </svg>
              Date Added
            </label>
            <select
              id="datePreset"
              [(ngModel)]="selectedDatePreset"
              (change)="onFilterChange()"
              class="filter-select"
            >
              <option value="">All time</option>
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="custom">Custom range</option>
            </select>
          </div>

          <div class="filter-group" *ngIf="selectedDatePreset === 'custom'">
            <label for="customDateFrom" class="filter-label">From</label>
            <input
              type="date"
              id="customDateFrom"
              [(ngModel)]="customDateFrom"
              (change)="onFilterChange()"
              class="filter-date-input"
            />
          </div>

          <div class="filter-group" *ngIf="selectedDatePreset === 'custom'">
            <label for="customDateTo" class="filter-label">To</label>
            <input
              type="date"
              id="customDateTo"
              [(ngModel)]="customDateTo"
              (change)="onFilterChange()"
              class="filter-date-input"
            />
          </div>
```

- [ ] **Step 5: Update the active-filters badge block (HTML)**

Change the active-filters `*ngIf` condition and add a badge inside the block:

Current:
```html
      <div *ngIf="searchQuery || selectedCategory || selectedPricing || showFeaturedOnly" class="active-filters">
```

Change to:
```html
      <div *ngIf="searchQuery || selectedCategory || selectedPricing || showFeaturedOnly || selectedDatePreset" class="active-filters">
```

Add this badge inside the `active-filters` div (e.g., after the featured badge):

```html
        <span class="filter-badge" *ngIf="selectedDatePreset">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <path d="M2 2a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V2zm2-1a1 1 0 00-1 1v12a1 1 0 001 1h8a1 1 0 001-1V2a1 1 0 00-1-1H4z"/>
          </svg>
          Date: {{ getDateFilterLabel() }}
        </span>
```

- [ ] **Step 6: Add date-input styles (CSS)**

Append to `agents-list.component.css`:

```css
/* Date filter inputs */
.filter-date-input {
  padding: 0.625rem 0.875rem;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 0.625rem;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.filter-date-input:hover {
  border-color: var(--color-violet);
}

.filter-date-input:focus {
  outline: none;
  border-color: var(--color-violet);
  box-shadow: 0 0 0 3px rgba(108, 113, 196, 0.15);
}
```

- [ ] **Step 7: Verify the build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/app/components/agents-list/
git commit -m "feat(agents): add date-added filter to agents listing"
```

---

### Task 6: Add date filter UI to the MCP Servers listing page

**Files:**
- Modify: `frontend/src/app/components/mcp-servers/mcp-servers.component.ts`
- Modify: `frontend/src/app/components/mcp-servers/mcp-servers.component.html`
- Modify: `frontend/src/app/components/mcp-servers/mcp-servers.component.css`

Mirror Task 5 exactly for `mcp-servers`.

- [ ] **Step 1: Add filter state and helpers (TypeScript)**

In `mcp-servers.component.ts`, add state after `showFeaturedOnly = false;`:

```ts
  selectedDatePreset = '';
  customDateFrom = '';
  customDateTo = '';
```

Add helper methods after `clearFilters()`:

```ts
  /** Compute date_from/date_to from the preset or custom inputs. */
  resolveDateRange(): { date_from?: string; date_to?: string } {
    if (this.selectedDatePreset === 'custom') {
      if (!this.customDateFrom || !this.customDateTo) {
        return {};
      }
      return { date_from: this.customDateFrom, date_to: this.customDateTo };
    }
    if (!this.selectedDatePreset) {
      return {};
    }
    const days = parseInt(this.selectedDatePreset, 10);
    const from = new Date();
    from.setDate(from.getDate() - days);
    return { date_from: from.toISOString().slice(0, 10) };
  }

  getDateFilterLabel(): string {
    if (this.selectedDatePreset === 'custom') {
      return `Custom (${this.customDateFrom || '?'} → ${this.customDateTo || '?'})`;
    }
    return `Last ${this.selectedDatePreset} days`;
  }
```

- [ ] **Step 2: Wire the date range into `loadServers`**

In `loadServers`, add `const dateRange = this.resolveDateRange();` right after `this.error = null;`. In search mode:

```ts
      this.apiService.searchMCPServers(this.searchQuery, this.currentPage, this.limit, sortBy, sortOrder, dateRange.date_from, dateRange.date_to).subscribe({
```

In the filters branch, add before `filters.sort_by = sortBy;`:

```ts
      if (dateRange.date_from) filters.date_from = dateRange.date_from;
      if (dateRange.date_to) filters.date_to = dateRange.date_to;
```

- [ ] **Step 3: Reset in `clearFilters`**

Add to `clearFilters()`:

```ts
    this.selectedDatePreset = '';
    this.customDateFrom = '';
    this.customDateTo = '';
```

- [ ] **Step 4: Add the filter controls (HTML)**

In `mcp-servers.component.html`, inside the `<div class="filters-grid">`, add the "Date Added" group right before the `<!-- Clear Filters -->` comment block (after the Featured filter group). Two separate groups so From/To inputs only render in custom mode:

```html
          <!-- Date Added Filter -->
          <div class="filter-group">
            <label for="datePreset" class="filter-label">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="inline-block mr-1">
                <path d="M2 2a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V2zm2-1a1 1 0 00-1 1v12a1 1 0 001 1h8a1 1 0 001-1V2a1 1 0 00-1-1H4zm1 3a.5.5 0 01.5-.5h5a.5.5 0 010 1h-5A.5.5 0 015 4zm.5 2.5h5a.5.5 0 010 1h-5a.5.5 0 010-1zM6 9.5a.5.5 0 01.5-.5h3a.5.5 0 010 1h-3a.5.5 0 01-.5-.5z"/>
              </svg>
              Date Added
            </label>
            <select
              id="datePreset"
              [(ngModel)]="selectedDatePreset"
              (change)="onFilterChange()"
              class="filter-select"
            >
              <option value="">All time</option>
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="custom">Custom range</option>
            </select>
          </div>

          <div class="filter-group" *ngIf="selectedDatePreset === 'custom'">
            <label for="customDateFrom" class="filter-label">From</label>
            <input
              type="date"
              id="customDateFrom"
              [(ngModel)]="customDateFrom"
              (change)="onFilterChange()"
              class="filter-date-input"
            />
          </div>

          <div class="filter-group" *ngIf="selectedDatePreset === 'custom'">
            <label for="customDateTo" class="filter-label">To</label>
            <input
              type="date"
              id="customDateTo"
              [(ngModel)]="customDateTo"
              (change)="onFilterChange()"
              class="filter-date-input"
            />
          </div>
```

- [ ] **Step 5: Update the active-filters badge block (HTML)**

Current condition (line ~172):

```html
      <div *ngIf="searchQuery || selectedCategory || selectedLanguage || selectedScope || showFeaturedOnly" class="active-filters">
```

Change to:

```html
      <div *ngIf="searchQuery || selectedCategory || selectedLanguage || selectedScope || showFeaturedOnly || selectedDatePreset" class="active-filters">
```

Add this badge inside the `active-filters` div (e.g., after the featured badge):

```html
        <span class="filter-badge" *ngIf="selectedDatePreset">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <path d="M2 2a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V2zm2-1a1 1 0 00-1 1v12a1 1 0 001 1h8a1 1 0 001-1V2a1 1 0 00-1-1H4z"/>
          </svg>
          Date: {{ getDateFilterLabel() }}
        </span>
```

- [ ] **Step 6: Add date-input styles (CSS)**

Append to `mcp-servers.component.css`:

```css
/* Date filter inputs */
.filter-date-input {
  padding: 0.625rem 0.875rem;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 0.625rem;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.filter-date-input:hover {
  border-color: var(--color-violet);
}

.filter-date-input:focus {
  outline: none;
  border-color: var(--color-violet);
  box-shadow: 0 0 0 3px rgba(108, 113, 196, 0.15);
}
```

- [ ] **Step 7: Verify the build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 8: Commit**

```bash
git add frontend/src/app/components/mcp-servers/
git commit -m "feat(mcp-servers): add date-added filter to servers listing"
```

---

### Task 7: Integration & verification

**Files:** none (verification only)

- [ ] **Step 1: Confirm both endpoints filter correctly (authenticated)**

```bash
EMAIL="df_final_$(date +%s)@test.com"
curl -s -X POST http://localhost:8333/api/v1/auth/register -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"dffinal\",\"password\":\"testpass123\"}" >/dev/null
TOKEN=$(curl -s -X POST http://localhost:8333/api/v1/auth/login -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"testpass123\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['access_token'])")

echo "agents date_from=2026-08-01:" \
  $(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/v1/agents?limit=5&date_from=2026-08-01" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['total'])")
echo "agents date_to=2026-01-01:" \
  $(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/v1/agents?limit=5&date_to=2026-01-01" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['total'])")
echo "servers date_from=2026-08-01:" \
  $(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/mcp-servers?limit=5&date_from=2026-08-01" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['total'])")
echo "servers date_to=2026-01-01:" \
  $(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8333/api/mcp-servers?limit=5&date_to=2026-01-01" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['total'])")
```

Expected: `agents date_to=2026-01-01` and `servers date_to=2026-01-01` both `0`; the `date_from=2026-08-01` totals match the unfiltered totals.

- [ ] **Step 2: Frontend build is clean**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing.

- [ ] **Step 3: Dev server reflects the changes**

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4200/`
Expected: `200`.

- [ ] **Step 4: Manual QA matrix** (browser at `http://localhost:4200`)

- [ ] On `/agents`, "Date Added" dropdown appears in the filter row.
- [ ] Last 7 / 30 / 90 days presets filter the list; counts change; results match server-side.
- [ ] Choosing "Custom range" reveals From/To date pickers; setting both filters; setting only one applies no date filter.
- [ ] The active-filters badge shows "Date: Last 30 days" (or the custom range); Clear All resets it.
- [ ] The same controls work on `/mcp-servers`.
- [ ] Typing a search query + applying a date preset filters search results too.
- [ ] An inverted custom range (From after To) shows the generic error message, not a crash.
- [ ] Guest (logged out) preview still works with the date filter applied.
- [ ] All 5 themes keep the new controls legible.

- [ ] **Step 5: No commit required** (verification task).