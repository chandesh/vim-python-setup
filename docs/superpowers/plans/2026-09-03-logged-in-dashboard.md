# Logged-In Home Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the home route (`/`) render a personal dashboard (greeting + My Favorites + Trending) for authenticated users while leaving the guest marketing page unchanged.

**Architecture:** `HomeComponent` branches on auth state (via `AuthService`) using Angular control flow. Three new standalone components each fetch their own data from existing authenticated APIs and handle their own loading/error/empty states, so a failing section never breaks the page. No backend changes.

**Tech Stack:** Angular 20 standalone components + signals, existing `AuthService` / `FavoritesService` / `ApiService`, theme CSS variables.

---

**Repo state note:** There are uncommitted Phase 3 changes on `master`. Each commit step below stages **only** the files listed for that task — never `git add -A` or `git add .`.

**Build command used for verification** (frontend source is volume-mounted into the container):

```bash
docker exec ai_agent_hub_frontend npm run build
```

Expected on success: `✔ Building...` then `Application bundle generation complete. [...]`. Exit code 0. Budget WARNINGS are pre-existing and acceptable.

---

### Task 1: Add `initialized` signal to AuthService

**Files:**
- Modify: `frontend/src/app/services/auth.service.ts`

Purpose: expose an auth-ready signal so `HomeComponent` can show a loading state instead of flashing the guest page while the session restore (`GET /api/v1/auth/me`) is in flight.

- [ ] **Step 1: Replace the `initialized` boolean with a signal**

Current (lines 15-16 and 85-91):

```ts
  private currentUser = signal<User | null>(null);
  private initialized = false;
```

and

```ts
  /** Restore the session from a stored token exactly once per app run. */
  ensureInitialized(): void {
    if (!this.initialized) {
      this.initialized = true;
      this.loadCurrentUser().subscribe();
    }
  }
```

Replace with:

```ts
  private currentUser = signal<User | null>(null);
  private initStarted = false;

  /** True once the initial session restore attempt has completed. */
  readonly initialized = signal(false);
```

and

```ts
  /** Restore the session from a stored token exactly once per app run. */
  ensureInitialized(): void {
    if (this.initStarted) {
      return;
    }
    this.initStarted = true;
    this.loadCurrentUser().subscribe({
      complete: () => this.initialized.set(true)
    });
  }
```

Note: `loadCurrentUser()` always calls `observer.complete()` (missing token, success, and error paths), so `initialized` flips `true` exactly once after the restore attempt settles. `clearToken()` keeps `initialized` at its current value — correct, since the auth state has already been resolved once.

- [ ] **Step 2: Verify the change compiles**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/services/auth.service.ts
git commit -m "feat(auth): expose initialized signal for auth-ready state"
```

---

### Task 2: Create DashboardGreetingComponent

**Files:**
- Create: `frontend/src/app/components/dashboard-greeting/dashboard-greeting.component.ts`
- Create: `frontend/src/app/components/dashboard-greeting/dashboard-greeting.component.html`
- Create: `frontend/src/app/components/dashboard-greeting/dashboard-greeting.component.css`

Purpose: personalized, time-based greeting. Isolated so stat chips can be added to it later.

- [ ] **Step 1: Create the TypeScript file**

`frontend/src/app/components/dashboard-greeting/dashboard-greeting.component.ts`:

```ts
import { Component, input } from '@angular/core';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-dashboard-greeting',
  standalone: true,
  templateUrl: './dashboard-greeting.component.html',
  styleUrls: ['./dashboard-greeting.component.css']
})
export class DashboardGreetingComponent {
  user = input<User | null>(null);

  get greeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  get today(): string {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric'
    });
  }
}
```

- [ ] **Step 2: Create the template**

`frontend/src/app/components/dashboard-greeting/dashboard-greeting.component.html`:

```html
<section class="greeting-card">
  <div class="greeting-accent"></div>
  <div class="greeting-body">
    <h1 class="greeting-title">
      {{ greeting }}{{ user()?.username ? ', ' + user()?.username : '' }}
    </h1>
    <p class="greeting-subtitle">Here's what's new in your AI Agent Hub</p>
    <span class="greeting-date">{{ today }}</span>
  </div>
</section>
```

- [ ] **Step 3: Create the stylesheet**

`frontend/src/app/components/dashboard-greeting/dashboard-greeting.component.css`:

```css
.greeting-card {
  position: relative;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.greeting-accent {
  height: 6px;
  background: linear-gradient(90deg, var(--color-blue), var(--color-cyan));
}

.greeting-body {
  padding: 2rem;
}

.greeting-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.greeting-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.greeting-date {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

@media (max-width: 640px) {
  .greeting-body {
    padding: 1.25rem;
  }

  .greeting-title {
    font-size: 1.4rem;
  }
}
```

- [ ] **Step 4: Verify build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/dashboard-greeting/
git commit -m "feat(home): add dashboard greeting component"
```

---

### Task 3: Create FavoritesSectionComponent

**Files:**
- Create: `frontend/src/app/components/favorites-section/favorites-section.component.ts`
- Create: `frontend/src/app/components/favorites-section/favorites-section.component.html`
- Create: `frontend/src/app/components/favorites-section/favorites-section.component.css`

Purpose: horizontal strip of the 6 most recent favorites with a "View all" link to `/profile`. Uses `FavoriteItem` from `favorites.service.ts`.

- [ ] **Step 1: Create the TypeScript file**

`frontend/src/app/components/favorites-section/favorites-section.component.ts`:

```ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FavoritesService, FavoriteItem } from '../../services/favorites.service';

@Component({
  selector: 'app-favorites-section',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './favorites-section.component.html',
  styleUrls: ['./favorites-section.component.css']
})
export class FavoritesSectionComponent implements OnInit {
  favorites: FavoriteItem[] = [];
  loading = true;
  error: string | null = null;

  constructor(private favoritesService: FavoritesService) {}

  ngOnInit(): void {
    this.loadFavorites();
  }

  loadFavorites(): void {
    this.loading = true;
    this.error = null;
    this.favoritesService.getUserFavorites(1, 6).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success && response.data) {
          this.favorites = response.data.favorites;
        } else {
          this.error = 'Could not load your favorites.';
        }
      },
      error: () => {
        this.loading = false;
        this.error = 'Could not load your favorites.';
      }
    });
  }

  getItemName(item: FavoriteItem): string {
    return item.agent?.name ?? item.mcp_server?.name ?? 'Unknown item';
  }

  getItemRoute(item: FavoriteItem): string[] {
    return item.agent
      ? ['/agents', item.agent.id]
      : ['/mcp-servers', item.mcp_server!.id];
  }

  getItemTypeLabel(item: FavoriteItem): string {
    return item.agent ? 'AI Agent' : 'MCP Server';
  }
}
```

- [ ] **Step 2: Create the template**

`frontend/src/app/components/favorites-section/favorites-section.component.html`:

```html
<section class="favorites-section">
  <div class="section-heading">
    <h2 class="section-title">My Favorites</h2>
    <a routerLink="/profile" class="view-all-link">View all →</a>
  </div>

  @if (loading) {
    <div class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Loading favorites...</p>
    </div>
  } @else if (error) {
    <div class="state-container">
      <p class="state-text">{{ error }}</p>
      <button (click)="loadFavorites()" class="retry-button">Try Again</button>
    </div>
  } @else if (favorites.length === 0) {
    <div class="empty-state">
      <div class="empty-icon">☆</div>
      <h3 class="empty-title">No favorites yet</h3>
      <p class="state-text">Browse agents and MCP servers, then tap the heart icon to save them here.</p>
      <div class="empty-actions">
        <a routerLink="/agents" class="browse-link">Explore AI Agents</a>
        <a routerLink="/mcp-servers" class="browse-link browse-link-secondary">Explore MCP Servers</a>
      </div>
    </div>
  } @else {
    <div class="favorites-strip">
      @for (item of favorites; track item.id) {
        <a [routerLink]="getItemRoute(item)" class="favorite-card">
          <span class="item-type-badge" [class.item-type-agent]="item.agent" [class.item-type-server]="!item.agent">
            {{ getItemTypeLabel(item) }}
          </span>
          <div class="favorite-card-body">
            @if (item.agent?.logo_url || item.mcp_server?.logo_url; as logoUrl) {
              <img
                [src]="logoUrl"
                [alt]="getItemName(item) + ' logo'"
                (error)="$any($event.target).style.display = 'none'"
                class="favorite-logo"
              />
            }
            <h3 class="favorite-name">{{ getItemName(item) }}</h3>
            <p class="favorite-description line-clamp-2">
              {{ item.agent?.short_description || item.mcp_server?.description }}
            </p>
            <div class="favorite-badges">
              @if (item.agent) {
                <span class="pricing-badge">{{ item.agent.pricing_model | titlecase }}</span>
              }
              @if (item.mcp_server) {
                <span class="language-badge">{{ item.mcp_server.language }}</span>
              }
            </div>
          </div>
        </a>
      }
    </div>
  }
</section>
```

- [ ] **Step 3: Create the stylesheet**

`frontend/src/app/components/favorites-section/favorites-section.component.css`:

```css
.favorites-section {
  margin-bottom: 2rem;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
}

.view-all-link {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-blue);
  text-decoration: none;
  transition: color 0.2s;
}

.view-all-link:hover {
  color: var(--color-cyan);
}

.favorites-strip {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  -webkit-overflow-scrolling: touch;
}

.favorite-card {
  flex: 0 0 220px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.875rem;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.favorite-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.item-type-badge {
  align-self: flex-start;
  padding: 0.15rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-radius: 0.375rem;
}

.item-type-agent {
  background-color: rgba(38, 139, 210, 0.15);
  color: var(--color-blue);
}

.item-type-server {
  background-color: rgba(108, 113, 196, 0.15);
  color: var(--color-violet);
}

.favorite-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.favorite-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 0.5rem;
  background-color: var(--bg-primary);
  padding: 0.25rem;
  border: 1px solid var(--border-color);
}

.favorite-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.favorite-description {
  font-size: 0.8rem;
  line-height: 1.4;
  color: var(--text-secondary);
}

.favorite-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.pricing-badge,
.language-badge {
  padding: 0.125rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 0.375rem;
}

.pricing-badge {
  background-color: rgba(38, 139, 210, 0.15);
  color: var(--color-blue);
}

.language-badge {
  background-color: var(--bg-highlight);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.state-container {
  text-align: center;
  padding: 2rem 1rem;
}

.spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-text {
  margin-top: 0.75rem;
  color: var(--text-secondary);
}

.retry-button {
  margin-top: 0.75rem;
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-primary);
  background-color: transparent;
  border: 1px solid var(--accent-primary);
  border-radius: 0.5rem;
  cursor: pointer;
}

.retry-button:hover {
  background-color: var(--accent-soft);
}

.empty-state {
  text-align: center;
  padding: 2.5rem 1rem;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.875rem;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.empty-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.browse-link {
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent-contrast);
  background: linear-gradient(135deg, var(--color-blue), var(--color-cyan));
  border-radius: 0.625rem;
  text-decoration: none;
}

.browse-link-secondary {
  color: var(--text-primary);
  background-color: var(--bg-highlight);
  border: 1px solid var(--border-color);
}
```

- [ ] **Step 4: Verify build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/favorites-section/
git commit -m "feat(home): add favorites section to dashboard"
```

---

### Task 4: Create TrendingSectionComponent

**Files:**
- Create: `frontend/src/app/components/trending-section/trending-section.component.ts`
- Create: `frontend/src/app/components/trending-section/trending-section.component.html`
- Create: `frontend/src/app/components/trending-section/trending-section.component.css`

Purpose: two-column grid — Top AI Agents (by view_count) and Top MCP Servers (by star_count), each a 5-row ranked list linking to detail pages. Each column has independent loading/error state.

- [ ] **Step 1: Create the TypeScript file**

`frontend/src/app/components/trending-section/trending-section.component.ts`:

```ts
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Agent, MCPServer } from '../../models/agent.model';

@Component({
  selector: 'app-trending-section',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './trending-section.component.html',
  styleUrls: ['./trending-section.component.css']
})
export class TrendingSectionComponent implements OnInit {
  agents: Agent[] = [];
  servers: MCPServer[] = [];
  agentsLoading = true;
  serversLoading = true;
  agentsError: string | null = null;
  serversError: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadTrendingAgents();
    this.loadTrendingServers();
  }

  loadTrendingAgents(): void {
    this.agentsLoading = true;
    this.agentsError = null;
    this.apiService.getAgents(1, 5, { sort_by: 'view_count', sort_order: 'desc' }).subscribe({
      next: (response) => {
        this.agentsLoading = false;
        if (response.success && response.data) {
          this.agents = response.data.agents;
        } else {
          this.agentsError = 'Could not load trending agents.';
        }
      },
      error: () => {
        this.agentsLoading = false;
        this.agentsError = 'Could not load trending agents.';
      }
    });
  }

  loadTrendingServers(): void {
    this.serversLoading = true;
    this.serversError = null;
    this.apiService.getMCPServers(1, 5, { sort_by: 'star_count', sort_order: 'desc' }).subscribe({
      next: (response) => {
        this.serversLoading = false;
        if (response.success && response.data) {
          this.servers = response.data.servers;
        } else {
          this.serversError = 'Could not load trending MCP servers.';
        }
      },
      error: () => {
        this.serversLoading = false;
        this.serversError = 'Could not load trending MCP servers.';
      }
    });
  }

  formatCount(count: number): string {
    if (count >= 1000) {
      return (count / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return count.toString();
  }
}
```

- [ ] **Step 2: Create the template**

`frontend/src/app/components/trending-section/trending-section.component.html`:

```html
<section class="trending-section">
  <div class="section-heading">
    <h2 class="section-title">Trending</h2>
  </div>

  <div class="trending-grid">
    <div class="trending-card">
      <div class="trending-header">
        <h3 class="trending-title">Top AI Agents</h3>
        <div class="trending-accent"></div>
      </div>

      @if (agentsLoading) {
        <div class="state-container">
          <div class="spinner"></div>
        </div>
      } @else if (agentsError) {
        <div class="state-container">
          <p class="state-text">{{ agentsError }}</p>
          <button (click)="loadTrendingAgents()" class="retry-button">Try Again</button>
        </div>
      } @else if (agents.length === 0) {
        <p class="state-text">No agents yet.</p>
      } @else {
        <ol class="ranked-list">
          @for (agent of agents; track agent.id; let i = $index) {
            <li>
              <a [routerLink]="['/agents', agent.id]" class="ranked-row">
                <span class="rank">{{ i + 1 }}</span>
                <span class="ranked-name">{{ agent.name }}</span>
                <span class="ranked-metric">{{ formatCount(agent.view_count) }} views</span>
              </a>
            </li>
          }
        </ol>
      }
    </div>

    <div class="trending-card">
      <div class="trending-header">
        <h3 class="trending-title">Top MCP Servers</h3>
        <div class="trending-accent"></div>
      </div>

      @if (serversLoading) {
        <div class="state-container">
          <div class="spinner"></div>
        </div>
      } @else if (serversError) {
        <div class="state-container">
          <p class="state-text">{{ serversError }}</p>
          <button (click)="loadTrendingServers()" class="retry-button">Try Again</button>
        </div>
      } @else if (servers.length === 0) {
        <p class="state-text">No MCP servers yet.</p>
      } @else {
        <ol class="ranked-list">
          @for (server of servers; track server.id; let i = $index) {
            <li>
              <a [routerLink]="['/mcp-servers', server.id]" class="ranked-row">
                <span class="rank">{{ i + 1 }}</span>
                <span class="ranked-name">{{ server.name }}</span>
                <span class="ranked-metric">★ {{ formatCount(server.star_count) }}</span>
              </a>
            </li>
          }
        </ol>
      }
    </div>
  </div>
</section>
```

- [ ] **Step 3: Create the stylesheet**

`frontend/src/app/components/trending-section/trending-section.component.css`:

```css
.trending-section {
  margin-bottom: 2rem;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
}

.trending-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .trending-grid {
    grid-template-columns: 1fr;
  }
}

.trending-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.trending-header {
  margin-bottom: 0.75rem;
}

.trending-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
}

.trending-accent {
  height: 3px;
  background: linear-gradient(90deg, var(--color-blue), var(--color-cyan));
  border-radius: 2px;
}

.ranked-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.ranked-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.625rem;
  border-radius: 0.5rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.ranked-row:hover {
  background-color: var(--bg-highlight);
}

.rank {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--accent-contrast);
  background: linear-gradient(135deg, var(--color-blue), var(--color-cyan));
  border-radius: 0.5rem;
}

.ranked-name {
  flex: 1;
  min-width: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ranked-row:hover .ranked-name {
  color: var(--color-blue);
}

.ranked-metric {
  flex-shrink: 0;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.state-container {
  text-align: center;
  padding: 1.5rem 1rem;
}

.spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-text {
  margin-top: 0.75rem;
  color: var(--text-secondary);
}

.retry-button {
  margin-top: 0.75rem;
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-primary);
  background-color: transparent;
  border: 1px solid var(--accent-primary);
  border-radius: 0.5rem;
  cursor: pointer;
}

.retry-button:hover {
  background-color: var(--accent-soft);
}
```

- [ ] **Step 4: Verify build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/trending-section/
git commit -m "feat(home): add trending section to dashboard"
```

---

### Task 5: Wire up conditional Home page

**Files:**
- Modify: `frontend/src/app/components/home/home.component.ts`
- Modify: `frontend/src/app/components/home/home.component.html`
- Modify: `frontend/src/app/components/home/home.component.css`

Purpose: branch the home route on auth state and render the three dashboard components for authenticated users, a loading skeleton while auth restores, and the existing marketing page for guests.

- [ ] **Step 1: Update the component class**

`frontend/src/app/components/home/home.component.ts` — add `inject` to the imports, import `AuthService` and the three new components, inject the service, and expose the auth signals. Keep the existing `features` and `stats` arrays exactly as they are.

New top of file and class header:

```ts
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';
import { AuthService } from '../../services/auth.service';
import { DashboardGreetingComponent } from '../dashboard-greeting/dashboard-greeting.component';
import { FavoritesSectionComponent } from '../favorites-section/favorites-section.component';
import { TrendingSectionComponent } from '../trending-section/trending-section.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent, FooterComponent, DashboardGreetingComponent, FavoritesSectionComponent, TrendingSectionComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  private authService = inject(AuthService);

  readonly authReady = this.authService.initialized;
  readonly isAuthenticated = this.authService.isAuthenticated;
  readonly user = this.authService.user;

  features = [ ...existing array unchanged... ];
  stats = [ ...existing array unchanged... ];
}
```

- [ ] **Step 2: Update the template**

`frontend/src/app/components/home/home.component.html` — keep the `<div class="page-container">`, `<app-header>`, and `<app-footer>` in place. Inside `<main class="home-content">`, wrap the **three existing marketing sections** (`hero-section`, `features-section`, `cta-section`) in an `@else` block, and add the auth-branch before it. The three marketing `<section>` blocks move into the `@else` branch **verbatim** (unchanged).

Resulting structure (marketing section internals preserved verbatim):

```html
<div class="page-container">
  <app-header></app-header>

  <main class="home-content">
    @if (!authReady()) {
      <div class="dashboard-loading">
        <div class="spinner"></div>
        <p class="loading-text">Loading your dashboard...</p>
      </div>
    } @else if (isAuthenticated()) {
      <app-dashboard-greeting [user]="user()"></app-dashboard-greeting>
      <app-favorites-section></app-favorites-section>
      <app-trending-section></app-trending-section>
    } @else {
      <!-- existing <section class="hero-section"> ... </section> (verbatim) -->
      <!-- existing <section class="features-section"> ... </section> (verbatim) -->
      <!-- existing <section class="cta-section"> ... </section> (verbatim) -->
    }
  </main>

  <app-footer></app-footer>
</div>
```

- [ ] **Step 3: Add dashboard-loading styles**

Append to `frontend/src/app/components/home/home.component.css`:

```css
/* Dashboard auth-loading state */
.dashboard-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  gap: 1rem;
}

.spinner {
  display: inline-block;
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--text-secondary);
}
```

- [ ] **Step 4: Verify build**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/home/
git commit -m "feat(home): render dashboard for authenticated users"
```

---

### Task 6: Integration & verification

**Files:** none (verification only)

- [ ] **Step 1: Confirm backend trending endpoints return full data for authenticated users**

Register/login a throwaway user, then verify both trending queries return 5 items each (no guest cap):

```bash
EMAIL="dash_$(date +%s)@test.com"
curl -s -X POST http://localhost:8333/api/v1/auth/register -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"dashtest\",\"password\":\"testpass123\"}" >/dev/null
TOKEN=$(curl -s -X POST http://localhost:8333/api/v1/auth/login -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"testpass123\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['access_token'])")

echo "=== Trending agents ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8333/api/v1/agents?limit=5&sort_by=view_count&sort_order=desc" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; assert len(d['agents'])==5 and d['is_guest_preview'] is False; print('OK: 5 trending agents, preview=', d['is_guest_preview'])"

echo "=== Trending servers ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8333/api/mcp-servers?limit=5&sort_by=star_count&sort_order=desc" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; assert len(d['servers'])==5 and d.get('is_guest_preview') is False; print('OK: 5 trending servers, preview=', d.get('is_guest_preview'))"
```

Expected: both print `OK: 5 trending ...`.

- [ ] **Step 2: Frontend build is clean**

Run: `docker exec ai_agent_hub_frontend npm run build`
Expected: `Application bundle generation complete.` (exit 0). Budget WARNINGS are pre-existing.

- [ ] **Step 3: Dev server reflects the changes**

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4200/`
Expected: `200`. Then check the dev-server logs compiled without errors:

```bash
docker logs --tail 10 ai_agent_hub_frontend 2>&1 | grep -iE "error|Application bundle" | tail -3
```

- [ ] **Step 4: Manual QA matrix** (browser at `http://localhost:4200`)

- [ ] Logged out → marketing page renders exactly as before (hero, features, CTA).
- [ ] Logged in → `Loading your dashboard...` flashes briefly, then greeting, My Favorites, and Trending render.
- [ ] Greeting shows correct time-of-day and username.
- [ ] Favorites strip shows the user's saved items; card click opens detail; "View all →" goes to `/profile`.
- [ ] Empty favorites (fresh account) → empty state with Browse CTAs.
- [ ] Trending shows 5 agents (ranked by views) and 5 servers (ranked by stars); each row links to its detail page.
- [ ] All 5 themes: dashboard remains legible.
- [ ] Mobile width (~375px): favorites strip scrolls horizontally, trending stacks to one column.
- [ ] Reload while logged in → no permanent guest-page flash (brief skeleton only).

- [ ] **Step 5: No commit required** (verification task).