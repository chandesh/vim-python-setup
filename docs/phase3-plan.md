# Phase 3 Implementation Plan

## Problem Statement
The AI Agents and MCP Servers listings and their detail pages are fully public. Product direction requires these to be login-gated: logged-out users see only a small teaser (3 items per listing, limited detail previews), while the full catalog requires an account. Gating must be enforced on the backend (API cannot be bypassed) with supporting frontend UX (login walls, blur overlays, sign-in CTAs).

## Decisions (agreed)
- **Guest preview count**: 3 items per listing (agents and MCP servers)
- **Detail pages for guests**: teaser + blur overlay — basic identity stays visible, full content blurs behind a "Sign in to view full details" card
- **Enforcement**: backend + frontend. The API itself limits guests; the frontend renders walls/overlays

## Current State (post Phase 2)

### Completed Features
- Agent/MCP Server listing pages with search, filters, pagination
- Detail pages `/agents/:id` and `/mcp-servers/:id` with related items and view counting
- JWT auth (register/login/me/logout), auth guard, HTTP interceptor
- Favorites (backend CRUD + heart buttons + protected profile dashboard)
- Toasts, theme engine (5 themes), responsive layouts

### What's Missing
- Any concept of guest vs authenticated access in the API
- Listing truncation for unauthenticated users
- Restricted/teaser detail payloads
- Frontend login-wall and blur-overlay UX

---

## Proposed Implementation

### Step 1: Optional Auth Dependency (Backend)

Add a non-raising dependency that resolves the user but allows anonymous access. All gating decisions branch on its result.

**Files to modify:**
- `backend/app/core/dependencies.py` — add `get_optional_user`

```python
def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Resolve user from Bearer token, or None for anonymous requests.

    Unlike get_current_user, never raises 401 — used by endpoints that
    serve both guests (limited data) and signed-in users (full data).
    """
    if credentials is None:
        return None

    sub = decode_access_token(credentials.credentials)
    if not sub:
        return None

    try:
        user_id = UUID(sub)
    except ValueError:
        return None

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        return None
    return user
```

**Verification:**
```bash
sleep 3 && docker logs --tail 10 ai_agent_hub_backend 2>&1 | grep -iE "error|traceback" \
  && echo "IMPORT FAILED" || echo "reload OK"
# Smoke: anonymous request still succeeds (dependency returns None, no 401)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8333/api/v1/agents   # expect 200
```

### Step 2: Gate Agent Endpoints (Backend)

**Rules:**
- `GET /api/v1/agents` and `GET /api/v1/agents/search`: unauthenticated → return max 3 agents, keep real `total`, add `is_guest_preview: true`
- `GET /api/v1/agents/{id}`: unauthenticated → return teaser payload (`restricted: true`) with identity fields only; do NOT increment view count; omit description body, tags, related agents

**Files to modify:**
- `backend/app/api/agents.py`

**List/search change (both endpoints, identical pattern):**
```python
from app.core.dependencies import get_optional_user
from app.models.user import User

@router.get("", response_model=ApiResponse[AgentListResponse])
def list_agents(
    ...existing params...,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    query = db.query(Agent).options(joinedload(Agent.category), joinedload(Agent.tags))
    # ...filters unchanged...

    total = query.count()

    # Guests: cap preview window at 3 items regardless of requested page/limit
    effective_limit = limit
    is_guest_preview = False
    if current_user is None:
        is_guest_preview = True
        effective_limit = min(limit, 3)
        page = 1

    # ...sorting unchanged...
    agents = query.offset((page - 1) * limit).limit(effective_limit).all()

    return ApiResponse(
        success=True,
        data=AgentListResponse(
            agents=agents,
            total=total,
            page=page,
            limit=effective_limit,
            is_guest_preview=is_guest_preview,
        ),
    )
```

Apply the same `effective_limit`/`is_guest_preview` logic in `search_agents`.

**Schema addition** in `backend/app/schemas/agent.py`:
```python
class AgentListResponse(BaseSchema):
    agents: list[AgentResponse]
    total: int
    page: int
    limit: int
    is_guest_preview: bool = False
```

**Detail change — replace `get_agent` response handling** (drop `response_model`, mirror mcp_servers' plain-dict pattern):
```python
@router.get("/{agent_id}")
def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    agent = db.query(Agent).options(
        joinedload(Agent.category), joinedload(Agent.tags)
    ).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Agent with id {agent_id} not found")

    # Guests: teaser only, no view-count inflation
    if current_user is None:
        return {
            "success": True,
            "data": {
                "restricted": True,
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "slug": agent.slug,
                    "short_description": agent.short_description,
                    "logo_url": agent.logo_url,
                    "pricing_model": agent.pricing_model.value,
                    "featured": agent.featured,
                    "category": {"id": agent.category.id, "name": agent.category.name} if agent.category else None,
                    "view_count": agent.view_count,
                    "created_at": agent.created_at,
                },
            },
        }

    # Authenticated: existing behavior unchanged (increment, related, detail)
    agent.view_count += 1
    db.commit()
    db.refresh(agent)
    related_agents = db.query(Agent).options(
        joinedload(Agent.category), joinedload(Agent.tags)
    ).filter(Agent.category_id == agent.category_id, Agent.id != agent.id)\
     .order_by(Agent.view_count.desc()).limit(4).all()
    detail = AgentDetailResponse.model_validate(agent)
    detail.related_agents = [AgentSummary.model_validate(a) for a in related_agents]
    return ApiResponse(success=True, data=detail)
```

**Verification:**
```bash
AGENT_ID=$(curl -s "http://localhost:8333/api/v1/agents?limit=1" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['agents'][0]['id'])")
# Guest: 3 items max, flag set, real total preserved
curl -s "http://localhost:8333/api/v1/agents?limit=20" | python3 -c "
import json,sys; d=json.load(sys.stdin)['data']
assert len(d['agents']) <= 3 and d['is_guest_preview'] is True, 'guest cap failed'
print('guest preview OK:', len(d['agents']), 'of', d['total'])"
# Guest detail: restricted teaser, no description
curl -s "http://localhost:8333/api/v1/agents/$AGENT_ID" | python3 -c "
import json,sys; d=json.load(sys.stdin)['data']
assert d['restricted'] is True and 'description' not in d['agent'], 'teaser failed'
print('guest teaser OK')"
```

### Step 3: Gate MCP Server Endpoints (Backend)

Same rules as Step 2, applied to the three public endpoints in `backend/app/api/mcp_servers.py` (these return plain dicts already — no schema changes needed):

- `get_mcp_servers` / `search_mcp_servers`: add `current_user: User | None = Depends(get_optional_user)`; guests → fetch 3 (`offset = 0, limit = min(limit, 3)`), add `"is_guest_preview": True` to data dict, keep real `total`
- Authenticated paths remain byte-for-byte identical to today

**Detail guest branch (concrete):**
```python
if current_user is None:
    from urllib.parse import urlparse
    return {
        "success": True,
        "data": {
            "restricted": True,
            "server": {
                "id": server.id,
                "name": server.name,
                "slug": server.slug,
                "short_description": (server.description or "")[:160],
                "language": server.language,
                "logo_url": server.logo_url,
                "star_count": server.star_count,
                "scope": server.scope.value,
                "repository_host": urlparse(server.repository_url).netloc,  # e.g. github.com
                "category": {"id": server.category.id, "name": server.category.name} if server.category else None,
                "view_count": server.view_count,
                "created_at": server.created_at,
            },
        },
    }
```
Note: full `description`, `tags`, `npm_package`, `pypi_package`, and full `repository_url` are omitted for guests.

**Verification:**
```bash
curl -s "http://localhost:8333/api/mcp-servers?limit=12" | python3 -c "
import json,sys; d=json.load(sys.stdin)['data']
assert len(d['servers']) <= 3 and d.get('is_guest_preview') is True
print('server guest preview OK')"
```

### Step 4: Reusable Login Wall Component (Frontend)

One component serves both the listing wall (after item 3) and the detail blur overlay.

**Files to create:**
- `frontend/src/app/components/login-wall/login-wall.component.ts`
- `frontend/src/app/components/login-wall/login-wall.component.html`
- `frontend/src/app/components/login-wall/login-wall.component.css`

```typescript
// login-wall.component.ts
import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-login-wall',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './login-wall.component.html',
  styleUrls: ['./login-wall.component.css']
})
export class LoginWallComponent {
  /** 'card' fits into listing grids; 'overlay' floats over blurred content */
  variant = input<'card' | 'overlay'>('card');
  /** Item type shown in copy, e.g. 'agents', 'MCP servers' */
  itemType = input<string>('items');
  /** Total count for "sign in to see all N" copy */
  totalCount = input<number | null>(null);
}
```

Template:
```html
<div class="login-wall" [class.login-wall-overlay]="variant() === 'overlay'">
  <div class="wall-accent"></div>
  <div class="lock-circle" aria-hidden="true">
    <svg width="22" height="22" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 1a3.5 3.5 0 0 0-3.5 3.5V7H4a1.5 1.5 0 0 0-1.5 1.5v5A1.5 1.5 0 0 0 4 15h8a1.5 1.5 0 0 0 1.5-1.5v-5A1.5 1.5 0 0 0 12 7h-.5V4.5A3.5 3.5 0 0 0 8 1zm2 6H6V4.5a2 2 0 1 1 4 0V7z"/>
    </svg>
  </div>
  <h3 class="wall-title">Sign in to browse all {{ itemType() }}</h3>
  <p class="wall-subtitle">
    You're viewing a free preview.
    @if (totalCount(); as total) {
      Create a free account to see all {{ total }} {{ itemType() }} and full details.
    } @else {
      Create a free account to unlock full details.
    }
  </p>
  <div class="wall-actions">
    <a [routerLink]="['/login']" [queryParams]="{ returnUrl: currentUrl }" class="wall-cta-primary">Sign In</a>
    <a [routerLink]="['/register']" [queryParams]="{ returnUrl: currentUrl }" class="wall-cta-secondary">Create Account</a>
  </div>
</div>
```

Component injects `Router` and exposes `currentUrl = this.router.url`. Styling uses existing card language: `var(--bg-card)` background, `var(--border-color)` border, `border-radius: 0.875rem`, blue/cyan gradient accent bar, centered column layout; `overlay` variant drops the border and renders transparent-backed for use inside `overlay-backdrop`.

### Step 5: Guest Preview Mode on Listings (Frontend)

**Files to modify:**
- `frontend/src/app/models/agent.model.ts`
  ```typescript
  export interface AgentListResponse {
    agents: Agent[]; total: number; page: number; limit: number;
    is_guest_preview?: boolean;
  }
  // same optional field added to MCPServerListResponse
  ```
- `frontend/src/app/services/api.service.ts` — no URL changes; response generics already flow through
- `frontend/src/app/components/agents-list/agents-list.component.ts|html|css`
- `frontend/src/app/components/mcp-servers/mcp-servers.component.ts|html|css`

**Component logic (both listings):**
```typescript
isGuestPreview = false;

// in handleAgentsResponse / handleServersResponse:
this.isGuestPreview = !!response.data?.is_guest_preview;
```

**Template logic (both listings):**
- Banner when `isGuestPreview`: "Preview mode — showing {{ items.length }} of {{ totalCount }} {{ itemType }}. Sign in to see everything."
- Replace pagination block condition: `*ngIf="!loading && !error && totalPages > 1 && !isGuestPreview"`
- After the `*ngFor` grid, render:
```html
<app-login-wall
  *ngIf="isGuestPreview"
  variant="card"
  itemType="AI agents"
  [totalCount]="totalAgents">
</app-login-wall>
```

### Step 6: Blur Overlay on Detail Pages (Frontend)

**Files to modify:**
- `frontend/src/app/models/agent.model.ts`:
  ```typescript
  export interface AgentGuestTeaser {
    restricted: true;
    agent: { /* teaser fields from Step 2 */ };
  }
  ```
- `frontend/src/app/services/api.service.ts` — `getAgent`/`getMCPServer` return union type `AgentDetailResponse | GuestTeaser` shapes
- `frontend/src/app/components/agent-detail/agent-detail.component.ts|html|css`
- `frontend/src/app/components/mcp-server-detail/mcp-server-detail.component.ts|html|css`

**Component logic (both details):**
```typescript
restricted = false;
// in load success handler:
this.restricted = !!(response.data as any)?.restricted;
```

**Template logic:** when `restricted`, render hero card with teaser fields (logo, name, category, pricing badge) wrapped in `<div class="blurred-content">`, followed by:
```html
<div *ngIf="restricted" class="overlay-backdrop">
  <app-login-wall variant="overlay" itemType="AI agents"></app-login-wall>
</div>
```
Description, tags, packages, related sections, favorite button, and external CTA are **not rendered** for guests.

**CSS (both detail stylesheets):**
```css
.blurred-content {
  filter: blur(6px);
  pointer-events: none;
  user-select: none;
}

.overlay-backdrop {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--bg-primary) 55%, transparent);
  backdrop-filter: blur(2px);
  z-index: 10;
  border-radius: 1rem;
}
```
Wrap the hero section in a relatively-positioned container so the overlay anchors correctly.

### Step 7: Integration & Testing

**API checks (extend the Phase 2 E2E script):**
- [ ] Guest `GET /api/v1/agents?limit=100` → ≤ 3 items, `is_guest_preview=true`, `total` = full count
- [ ] Guest `GET /api/mcp-servers` → ≤ 3 items + flag
- [ ] Guest search endpoints → same caps
- [ ] Guest `GET /api/v1/agents/{id}` → `restricted=true`, no `description` key, view_count unchanged across two calls
- [ ] Guest `GET /api/mcp-servers/{id}` → `restricted=true`, no full `repository_url`
- [ ] Authed list/detail responses unchanged from Phase 2 (regression: favorites, view counting, related items still work)
- [ ] Favorites still require auth (401 without token)

**Frontend checks:**
- [ ] `npm run build` passes with no errors
- [ ] Logged out: listings show 3 cards + login wall, pagination hidden, banner visible
- [ ] Logged out: detail URLs show blurred hero + overlay CTAs
- [ ] Clicking Sign In from any gate → login → redirected back to original page (`returnUrl`)
- [ ] Logged in: full catalogs, working filters/pagination/details/favorites — no regressions
- [ ] Logout mid-session → next listing request flips to preview mode

### Step 8: Polish & Edge Cases

- [ ] Search-as-guest shows wall immediately under 3 results with query echoed ("Sign in to see all results for \"{{q}}\"")
- [ ] Deep-link to `/profile` while logged out still routes to login (Phase 2 guard, regression check)
- [ ] Expired token mid-browse → interceptor clears token; next page load renders guest preview instead of errors
- [ ] Theme check: wall/overlay legible in all 5 themes (uses CSS vars throughout)
- [ ] Mobile: overlay CTA buttons stack vertically; wall card fits 320px width

---

## Testing Strategy

**Backend (curl-based, consistent with Phase 2 verification):**
- Assert guest caps and flags on both listing endpoints + both search endpoints
- Assert restricted detail payloads omit sensitive/full fields
- Assert authenticated responses unchanged (regression suite from Phase 2 E2E script)

**Frontend:**
- `npm run build` after each step
- Manual matrix: {logged out, logged in} × {listing, search, agent detail, server detail} × light/dark themes

## Success Criteria

- Unauthenticated users can see exactly 3 agents and 3 servers per listing — never more, even with manipulated query params
- Unauthenticated detail access yields teaser content only; full descriptions, tags, package names, repo URLs, and related items are absent from API responses (not just hidden by CSS)
- Guest view counts are not inflated by teaser requests
- Signed-in experience is functionally identical to Phase 2 (no regressions in favorites, profile, themes)
- All gates funnel into the existing register/login flows with `returnUrl` round-tripping
- UI remains consistent with the Solarized-based multi-theme system in both modes

---

**Document Version**: 1.0
**Created**: 2026-08-25
**Status**: Ready for Implementation
