# Design — Trending Comparison Charts on the Dashboard

**Date:** 2026-09-04
**Status:** Approved design (pre-implementation)
**Scope:** Frontend-only (adds one npm dependency, no backend/DB changes)

## Goal

Add comparison charts to the Trending section of the logged-in dashboard: a horizontal bar chart for Top AI Agents (by `view_count`) and one for Top MCP Servers (by `star_count`), letting users visually compare the top-5 items in each category.

## Current State

- The Trending section (`trending-section.component`) fetches the top 5 agents (sorted by `view_count` desc) and top 5 MCP servers (sorted by `star_count` desc) and renders two ranked `<ol>` lists, each row linking to the detail page.
- Data is a single current metric per item — no time-series history, so trend-over-time charts are out of scope.
- No chart library is installed. The app is Angular 20.2 (standalone components, signals). Theme system: `ThemeService.theme` signal + CSS variables scoped by `data-theme` on `<html>`.
- Most Angular chart wrappers (ng2-charts, ngx-echarts, @swimlane/ngx-charts) currently require Angular 21/22+, so they are incompatible with this project.

## Library Decision

**Chart.js, integrated directly** (no `ng2-charts` wrapper). Rationale:
- Chart.js is framework-agnostic (canvas-based), so it has **no Angular-version lock** — safe through future framework upgrades.
- Industry default for standard charts (line/bar/pie/doughnut): ~92 kB gzipped, MIT licensed, actively maintained.
- Our need (ranked bar comparisons of 5 items) is squarely in its sweet spot.
- Avoids wrapper version-matching risk and the ApexCharts dual-license boundary.

A single small Angular wrapper component makes it reusable for all future dashboard charts.

## Design

### 1. New reusable `ChartComponent` (`frontend/src/app/components/chart/`)

Standalone component, selector `app-chart`, imports `[CommonModule]`.

**Inputs:**
- `type: ChartType = 'bar'` (Chart.js chart type)
- `data: ChartData`
- `options: ChartOptions`

**Behavior:**
- Renders a `<canvas class="chart-canvas">` in a sized wrapper.
- `ngOnInit` / input-change handling: creates `new Chart(ctx, { type, data, options })`; on later input changes calls `chart.update()`; if `type` changes, destroys and recreates.
- `ngOnDestroy`: calls `chart.destroy()`.
- **Theme awareness:** injects `ThemeService`. Reads CSS-variable colors from `getComputedStyle(document.documentElement)` (`--text-secondary`, `--border-color`, `--color-blue`, `--color-cyan`, `--accent-contrast`, `--bg-card`). Subscribes to `themeService.theme` signal; on change re-reads colors and updates the chart (ticks, grid, legend, bar colors).
- Resizes responsively (Chart.js `responsive: true`, `maintainAspectRatio: false`).

### 2. Trending section changes (`trending-section.component.ts|html|css`)

- Add chart-data getters mapping the already-fetched top 5:
  - agents → labels = `agent.name`, values = `agent.view_count`
  - servers → labels = `server.name`, values = `server.star_count`
- In each `trending-card`, render `<app-chart>` **above** the existing ranked list, only in the data-loaded branch (`@else`).
- Chart config (shared helper or inline):
  - Horizontal bars: `indexAxis: 'y'`
  - Rounded bars (`borderRadius`), gradient blue→cyan fill matching the app accent
  - No legend; compact tooltips formatted with the existing `formatCount` (e.g. `1.2k views` / `★ 1.2k`)
  - `responsive: true`, `maintainAspectRatio: false`, fixed chart height (~200px) via the wrapper
  - Category axis labels = agent/server names (ellipsized if long)
- Ranked list stays below the chart (it is the clickable navigation); the chart is the comparison visual.
- Loading / error / empty states unchanged.

### 3. Dependency

Add `chart.js` to `frontend/package.json` via `npm install chart.js` run inside the `ai_agent_hub_frontend` container (source volume-mounted). `package.json` and `package-lock.json` are committed.

## Edge Cases

- Fewer than 5 items in a category: chart renders with the items present (Chart.js handles small arrays).
- All-zero metrics: chart renders empty bars; acceptable (no special-casing).
- Theme switch while viewing: chart recolors via the `theme` signal subscription.
- Mobile (~375px): charts remain legible (responsive canvas, horizontal bars fit narrow widths; the trending grid already stacks to one column).
- Chart.js not loaded / build failure: covered by build verification; the wrapper degrades gracefully (canvas hidden) if inputs are empty.

## Verification

- `docker exec ai_agent_hub_frontend npm run build` → exit 0 (`Application bundle generation complete.`); budget WARNINGS pre-existing/acceptable.
- Browser QA on `/` (logged in): both cards show a bar chart + ranked list; bar lengths visually rank the top 5; tooltips show formatted counts; clicking list rows still navigates to detail pages.
- All 5 themes: chart recolors correctly.
- Mobile width: charts legible, grid stacks.

## Out of Scope

- Time-series/trend-over-time charts (no historical data exists).
- Extra metrics beyond the existing `view_count` / `star_count`.
- Interactive drilldown from chart to detail page (list rows already navigate).
- Backend changes.

## Files

- Create: `frontend/src/app/components/chart/chart.component.ts`
- Create: `frontend/src/app/components/chart/chart.component.html`
- Create: `frontend/src/app/components/chart/chart.component.css`
- Modify: `frontend/src/app/components/trending-section/trending-section.component.ts`
- Modify: `frontend/src/app/components/trending-section/trending-section.component.html`
- Modify: `frontend/src/app/components/trending-section/trending-section.component.css`
- Modify: `frontend/package.json`, `frontend/package-lock.json`