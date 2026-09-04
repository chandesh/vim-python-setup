# Trending Comparison Charts — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add horizontal bar comparison charts to the Trending section of the logged-in dashboard — one for Top AI Agents (by `view_count`) and one for Top MCP Servers (by `star_count`).

**Architecture:** Chart.js integrated directly (no `ng2-charts` wrapper, avoiding Angular-version lock) behind a small reusable standalone `app-chart` component that is theme-aware (colors from CSS variables, re-renders on theme change). The Trending section reuses its already-fetched top-5 data — no new API calls.

**Tech Stack:** Angular 20 standalone components + signals, Chart.js 4.5.1 (`chart.js/auto`), theme CSS variables.

**Design doc:** `docs/superpowers/specs/2026-09-04-trending-charts-design.md`

**Repo state note:** The working tree is currently clean (all prior work committed). Each commit step stages only the files listed for that task — never `git add -A` or `git add .`.

**Build command** (frontend source volume-mounted into container `ai_agent_hub_frontend`):

```bash
docker exec ai_agent_hub_frontend npm run build
```

Expected on success: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing and acceptable.

---

### Task 1: Install chart.js

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`

- [ ] **Step 1: Install chart.js inside the frontend container**

Run (from repo root; the container's `/app` is the mounted `frontend/` source):

```bash
docker exec -it ai_agent_hub_frontend npm install chart.js
```

Expected: `added N packages`, and `"chart.js": "^4.5.1"` appears in `frontend/package.json` dependencies.

- [ ] **Step 2: Verify the build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing.

- [ ] **Step 3: Confirm only the intended files changed**

Run: `git status --short`
Expected: only `frontend/package.json` and `frontend/package-lock.json` modified (and nothing else).

- [ ] **Step 4: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore(deps): add chart.js for dashboard charts"
```

---

### Task 2: Create the reusable ChartComponent

**Files:**
- Create: `frontend/src/app/components/chart/chart.component.ts`
- Create: `frontend/src/app/components/chart/chart.component.html`
- Create: `frontend/src/app/components/chart/chart.component.css`

Purpose: a theme-aware, reusable Chart.js wrapper that any future dashboard chart can use.

- [ ] **Step 1: Create the TypeScript file**

`frontend/src/app/components/chart/chart.component.ts`:

```ts
import { Component, ElementRef, ViewChild, effect, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, ChartData, ChartOptions, ChartType } from 'chart.js/auto';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.css']
})
export class ChartComponent {
  private themeService = inject(ThemeService);

  /** Chart.js chart type, e.g. 'bar' or 'line'. */
  type = input<ChartType>('bar');
  /** Chart.js data payload. */
  data = input<ChartData>({ labels: [], datasets: [] });
  /** Consumer-supplied Chart.js options (merged over the theme defaults). */
  options = input<ChartOptions>({});

  @ViewChild('canvas', { static: true }) private canvasRef!: ElementRef<HTMLCanvasElement>;

  private chart: Chart | null = null;

  /** Re-render whenever the theme or any chart input changes. */
  private renderEffect = effect(() => {
    this.themeService.theme();
    this.renderOrUpdate();
  });

  ngOnDestroy(): void {
    this.chart?.destroy();
    this.chart = null;
  }

  private renderOrUpdate(): void {
    const ctx = this.canvasRef.nativeElement.getContext('2d');
    if (!ctx) {
      return;
    }
    const data = this.applyThemeColors();
    const options = { ...this.buildOptions(), ...this.options() } as ChartOptions;
    if (this.chart && this.chart.config.type === this.type()) {
      this.chart.data = data;
      this.chart.options = options;
      this.chart.update();
    } else {
      this.chart?.destroy();
      this.chart = new Chart(ctx, { type: this.type(), data, options });
    }
  }

  /** Augment datasets with theme-aware rounded bars (gradient blue→cyan by default). */
  private applyThemeColors(): ChartData {
    const styles = getComputedStyle(document.documentElement);
    const blue = styles.getPropertyValue('--color-blue').trim() || '#268bd2';
    const cyan = styles.getPropertyValue('--color-cyan').trim() || '#2aa198';
    const data = this.data();
    return {
      ...data,
      datasets: (data.datasets ?? []).map(ds => ({
        ...ds,
        borderRadius: 6,
        backgroundColor: (ds as any).backgroundColor ?? ((context: any) => {
          const area = context.chart.chartArea;
          if (!area) {
            return blue;
          }
          const gradient = context.chart.ctx.createLinearGradient(area.left, 0, area.right, 0);
          gradient.addColorStop(0, blue);
          gradient.addColorStop(1, cyan);
          return gradient;
        })
      }))
    };
  }

  /** Theme-aware default options: label/grid colors come from CSS variables. */
  private buildOptions(): ChartOptions {
    const styles = getComputedStyle(document.documentElement);
    const text = styles.getPropertyValue('--text-secondary').trim() || '#586e75';
    const grid = styles.getPropertyValue('--border-color').trim() || '#dfd8c3';
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { ticks: { color: text }, grid: { display: false } }
      }
    };
  }
}
```

- [ ] **Step 2: Create the template**

`frontend/src/app/components/chart/chart.component.html`:

```html
<div class="chart-wrapper">
  <canvas #canvas class="chart-canvas"></canvas>
</div>
```

- [ ] **Step 3: Create the stylesheet**

`frontend/src/app/components/chart/chart.component.css`:

```css
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}
```

- [ ] **Step 4: Verify the build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). The component is standalone and not yet referenced anywhere — that's expected (wiring happens in Task 3).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/chart/
git commit -m "feat(chart): add reusable theme-aware chart component"
```

---

### Task 3: Integrate charts into the Trending section

**Files:**
- Modify: `frontend/src/app/components/trending-section/trending-section.component.ts`
- Modify: `frontend/src/app/components/trending-section/trending-section.component.html`
- Modify: `frontend/src/app/components/trending-section/trending-section.component.css`

- [ ] **Step 1: Update the component class**

`frontend/src/app/components/trending-section/trending-section.component.ts` — add the import, register the component, and add chart-data getters + tooltip options.

Import (with the other imports):

```ts
import { ChartData, ChartOptions } from 'chart.js/auto';
import { ChartComponent } from '../chart/chart.component';
```

Register in the `@Component` `imports` array (add after `RouterModule`):

```ts
  imports: [RouterModule, ChartComponent],
```

Add these getters to the class (e.g., after `formatCount`):

```ts
  get agentsChartData(): ChartData {
    return {
      labels: this.agents.map(agent => agent.name),
      datasets: [{ data: this.agents.map(agent => agent.view_count) }]
    };
  }

  get serversChartData(): ChartData {
    return {
      labels: this.servers.map(server => server.name),
      datasets: [{ data: this.servers.map(server => server.star_count) }]
    };
  }

  get agentsChartOptions(): ChartOptions {
    return {
      plugins: {
        tooltip: {
          callbacks: {
            label: (context: any) => `${this.formatCount(context.parsed.x)} views`
          }
        }
      }
    };
  }

  get serversChartOptions(): ChartOptions {
    return {
      plugins: {
        tooltip: {
          callbacks: {
            label: (context: any) => `★ ${this.formatCount(context.parsed.x)}`
          }
        }
      }
    };
  }
```

- [ ] **Step 2: Add the charts to the template**

`frontend/src/app/components/trending-section/trending-section.component.html` — inside the agents `@else` block, directly before the `<ol class="ranked-list">`:

```html
        <div class="trending-chart">
          <app-chart [data]="agentsChartData" [options]="agentsChartOptions"></app-chart>
        </div>
```

Inside the servers `@else` block, directly before its `<ol class="ranked-list">`:

```html
        <div class="trending-chart">
          <app-chart [data]="serversChartData" [options]="serversChartOptions"></app-chart>
        </div>
```

The loading/error/empty branches are unchanged; charts render only when data is present.

- [ ] **Step 3: Add chart styles**

Append to `frontend/src/app/components/trending-section/trending-section.component.css`:

```css
/* Comparison charts */
.trending-chart {
  height: 200px;
  margin-bottom: 1rem;
}
```

- [ ] **Step 4: Verify the build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/trending-section/
git commit -m "feat(home): add trending comparison charts to dashboard"
```

---

### Task 4: Integration & verification

**Files:** none (verification only)

- [ ] **Step 1: Frontend build is clean**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing.

- [ ] **Step 2: Dev server reflects the changes**

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4200/`
Expected: `200`.

- [ ] **Step 3: Manual QA matrix** (browser at `http://localhost:4200`, logged in)

- [ ] The Trending section's Top AI Agents card shows a horizontal bar chart above the ranked list; bar lengths visually rank the top 5 agents by views.
- [ ] The Top MCP Servers card shows the same for the top 5 servers by stars.
- [ ] Hovering a bar shows a tooltip with the formatted count (`1.2k views` / `★ 3.4k`).
- [ ] Clicking the ranked-list rows still navigates to the detail pages.
- [ ] Switching to each of the 5 themes recolors the charts (labels, grid, bars).
- [ ] At ~375px width the charts remain legible and the trending grid stacks to one column.
- [ ] Loading / error / empty states still behave as before.

- [ ] **Step 4: No commit required** (verification task).