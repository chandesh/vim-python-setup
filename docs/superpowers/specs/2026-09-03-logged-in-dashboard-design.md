# Logged-In Home Dashboard — Design

**Date**: 2026-09-03
**Status**: Approved for planning
**Scope**: Phase 4 (frontend-only)

## Problem Statement

The home page (`/`) is a static marketing landing page (hero, features, stats, CTA). It works well for logged-out visitors, but for signed-in users it offers no personal value. This design makes the home page a lightweight, intuitive dashboard for authenticated users while leaving the guest experience untouched.

## Decisions (agreed)

- **Same route, conditional content**: `/` renders the marketing page for guests and a dashboard for authenticated users. No new route, no redirects.
- **Dashboard sections (v1)**: personalized greeting, My Favorites, Trending (Top AI Agents + Top MCP Servers in a two-column split).
- **Extensible**: sections are isolated standalone components so "Your Stats" and "Quick Navigation" can be added later without modifying existing sections.
- **No backend changes**: all data comes from existing authenticated endpoints.
- **Guest experience unchanged**: logged-out visitors see the current home page exactly as today.

## Current State (post Phase 3)

- `HomeComponent` is a static page: hero, stats bar, feature cards, CTA.
- `AuthService` exposes `user` (signal) and `isAuthenticated` (computed); `ensureInitialized()` restores the session via `GET /api/v1/auth/me` (called once by `HeaderComponent`).
- Data available via authenticated APIs:
  - `FavoritesService.getUserFavorites(page, limit)` → `{ favorites: FavoriteItem[], total, ... }`
  - `ApiService.getAgents(page, limit, { sort_by, sort_order })`
  - `ApiService.getMCPServers(page, limit, { sort_by, sort_order })`
- Phase 3 guest caps apply only to unauthenticated requests; authenticated dashboard calls return full data.

## Design

### Architecture

`HomeComponent` becomes the auth-aware orchestrator:

```
HomeComponent
├── @if (!authReady)        → loading skeleton
├── @else if (isAuthenticated) → dashboard
│     ├── DashboardGreetingComponent
│     ├── FavoritesSectionComponent
│     └── TrendingSectionComponent
└── @else                   → existing marketing page (unchanged)
```

**New standalone components:**
- `DashboardGreetingComponent` — time-based greeting + date. Future host for stat chips.
- `FavoritesSectionComponent` — "My Favorites" horizontal strip + "View all →" link to `/profile`.
- `TrendingSectionComponent` — two-column grid: Top AI Agents | Top MCP Servers (ranked lists).

**AuthService enhancement:** add `readonly initialized = signal(false)` set to `true` when the initial `loadCurrentUser()` completes (success or failure). Prevents a guest-page flash for logged-in users on first load. Reuses the existing `ensureInitialized()` guard; `HeaderComponent` continues to call it.

### Data Flow

All requests are authenticated; re-fetched on each dashboard render (no stale cache):

| Section | Call | Limit | Purpose |
|---------|------|-------|---------|
| Favorites | `getUserFavorites(1, 6)` | 6 | Most recent favorites |
| Top agents | `getAgents(1, 5, { sort_by: 'view_count', sort_order: 'desc' })` | 5 | Trending agents |
| Top servers | `getMCPServers(1, 5, { sort_by: 'star_count', sort_order: 'desc' })` | 5 | Trending servers |

Each section handles its own `loading` / `error` / `empty` states. A failing section shows an inline error with retry and never breaks the rest of the page.

### UI/UX

- **Greeting**: gradient accent bar (matches existing hero language), "Good morning/afternoon/evening, {username}" based on local time, subtitle "Here's what's new in your AI Agent Hub".
- **Favorites strip**: horizontally scrollable row of compact cards (logo, name, item-type badge, pricing/scope). Empty state → "No favorites yet" + Browse Agents / Browse MCP Servers CTAs.
- **Trending**: two cards side by side on desktop, stacked on mobile. Each card has a section header + 5 ranked rows: rank number, name (links to detail page), and metric (view count for agents, star count for servers).
- All styling uses existing theme CSS variables so all 5 themes remain consistent.

### Extensibility

Sections are isolated components behind a shared visual header pattern. Adding "Your Stats" or "Quick Navigation" later is a new component inserted into the dashboard grid — no changes to existing sections. The greeting component is the natural host for future stat chips.

### Error Handling

- Per-section loading/error/empty states with inline retry.
- No section failure can prevent others from rendering.
- Session expiry while on the page: existing interceptor/`/me` handling clears the token; a full reload lands on the guest page (Phase 3 behavior unchanged).

## Testing Strategy

- `ng build` passes.
- Backend untouched — no backend tests.
- Manual matrix:
  - Logged in → dashboard renders greeting + favorites + trending.
  - Logged out → marketing page identical to today.
  - Favorites empty vs populated.
  - Simulate one section failing → others still render.
  - Mobile width → favorites strip scrolls, trending stacks.
- `curl` sanity: authenticated trending endpoints return 5 items each (no guest cap).

## Success Criteria

- Authenticated users landing on `/` see a useful dashboard; guests see the unchanged marketing page.
- Favorites strip reflects the user's actual saved items with a clear path to `/profile`.
- Trending shows the 5 most-viewed agents and 5 most-starred MCP servers, each linking to its detail page.
- No flash of the guest page for logged-in users.
- All 5 themes render the dashboard legibly.
- Future sections (stats, quick nav) can be added without touching existing components.

## Out of Scope

- Per-user "recently viewed" tracking (needs new backend + DB table).
- Personal stats / quick navigation sections (design supports adding later).
- Any backend changes.