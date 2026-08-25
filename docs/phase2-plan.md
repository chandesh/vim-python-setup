# Phase 2 Implementation Plan

## Problem Statement
The application currently has listing pages for AI Agents and MCP Servers, but lacks individual detail pages, user authentication, and the ability to save favorites. Users cannot view full details, create accounts, or bookmark items for later reference.

## Current State

### Completed Features
- Agent and MCP Server listing pages with search, filters, and pagination
- Homepage with hero section and feature cards
- Shared header and footer components
- Theme toggle (dark/light mode)
- Backend models for User, UserFavorite, Comparison
- Basic database schema with all necessary tables
- API endpoints for listing agents and servers

### What's Missing
- Individual detail pages for agents and servers
- User authentication system (registration, login, JWT)
- Favorites/bookmarking functionality
- User dashboard/profile
- Protected routes and auth guards
- Session management

## Proposed Implementation

### Step 1: Agent Detail Page (Frontend & Backend)

**Backend:**
- Endpoint `GET /api/v1/agents/{id}` already exists
- Add view count increment logic
- Return related agents based on category

**Frontend:**
- Create `agent-detail` component with route `/agents/:id`
- Display: logo, name, category, pricing, full description, tags, website link
- Show view count and created date
- Add "Visit Website" CTA button
- Display "Related Agents" section (same category)
- Responsive layout matching existing design system
- Use Solarized blue/cyan gradient theme

**Files to create:**
- `frontend/src/app/components/agent-detail/agent-detail.component.ts`
- `frontend/src/app/components/agent-detail/agent-detail.component.html`
- `frontend/src/app/components/agent-detail/agent-detail.component.css`

**Files to modify:**
- `frontend/src/app/app.routes.ts` - add agent detail route
- `frontend/src/app/services/api.service.ts` - add getAgentById method if missing
- `backend/app/api/agents.py` - enhance detail endpoint with view tracking

### Step 2: MCP Server Detail Page (Frontend & Backend)

**Backend:**
- Endpoint `GET /api/mcp-servers/{id}` already exists with view tracking
- Add related servers based on category and language

**Frontend:**
- Create `mcp-server-detail` component with route `/mcp-servers/:id`
- Display: logo, name, language, scope, category, repository URL, star count
- Show npm/PyPI package information
- Display tags and full description
- Show view count and created date
- Add "View on GitHub" button
- Display "Related Servers" section (same category or language)
- Use Solarized violet/magenta gradient theme

**Files to create:**
- `frontend/src/app/components/mcp-server-detail/mcp-server-detail.component.ts`
- `frontend/src/app/components/mcp-server-detail/mcp-server-detail.component.html`
- `frontend/src/app/components/mcp-server-detail/mcp-server-detail.component.css`

**Files to modify:**
- `frontend/src/app/app.routes.ts` - add server detail route
- `frontend/src/app/services/api.service.ts` - add getMCPServerById method if missing
- `backend/app/api/mcp_servers.py` - enhance with related servers

### Step 3: Authentication Backend

**Create authentication module:**
- JWT token generation and validation
- Password hashing with bcrypt/passlib
- User registration endpoint
- User login endpoint
- Token refresh endpoint
- Get current user endpoint

**Files to create:**
- `backend/app/core/security.py` - password hashing, JWT utilities
- `backend/app/core/dependencies.py` - auth dependencies (get_current_user)
- `backend/app/schemas/user.py` - Pydantic schemas (UserCreate, UserLogin, UserResponse, Token)
- `backend/app/api/auth.py` - authentication endpoints
- `backend/app/services/user_service.py` - user business logic

**Files to modify:**
- `backend/app/main.py` - register auth router
- `backend/app/core/config.py` - verify JWT settings exist

**Endpoints to implement:**
- `POST /api/v1/auth/register` - user registration
- `POST /api/v1/auth/login` - user login (returns JWT)
- `GET /api/v1/auth/me` - get current user (requires auth)
- `POST /api/v1/auth/logout` - logout (optional, mainly frontend)

### Step 4: Authentication Frontend

**Create auth service and components:**
- Auth service for login, register, logout, token management
- Login component
- Register component
- Auth guard for protected routes
- HTTP interceptor for attaching JWT to requests

**Files to create:**
- `frontend/src/app/services/auth.service.ts` - authentication logic
- `frontend/src/app/guards/auth.guard.ts` - route protection
- `frontend/src/app/interceptors/auth.interceptor.ts` - JWT attachment
- `frontend/src/app/components/login/login.component.ts|html|css`
- `frontend/src/app/components/register/register.component.ts|html|css`

**Files to modify:**
- `frontend/src/app/app.routes.ts` - add login, register routes
- `frontend/src/app/app.config.ts` - register interceptor and guards
- `frontend/src/app/components/header/header.component.ts|html` - add login/logout buttons

**Auth service methods:**
- `register(email, username, password)`
- `login(email, password)`
- `logout()`
- `getCurrentUser()`
- `isAuthenticated()` - observable for auth state
- `getToken()` - retrieve stored JWT
- `setToken(token)` - store JWT in localStorage

### Step 5: Favorites Backend

**Create favorites endpoints:**
- Add agent/server to favorites
- Remove from favorites
- List user's favorites
- Check if item is favorited

**Files to create:**
- `backend/app/schemas/favorite.py` - Pydantic schemas
- `backend/app/api/favorites.py` - favorites endpoints
- `backend/app/services/favorite_service.py` - favorites business logic

**Files to modify:**
- `backend/app/main.py` - register favorites router
- `backend/app/models/agent.py` - add favorites relationship if missing
- `backend/app/models/mcp_server.py` - add favorites relationship if missing

**Endpoints to implement:**
- `POST /api/v1/favorites` - add to favorites (body: {agent_id} or {mcp_server_id})
- `DELETE /api/v1/favorites/{id}` - remove from favorites
- `GET /api/v1/favorites` - list user's favorites (paginated)
- `GET /api/v1/favorites/check` - check if item is favorited (query: agent_id or mcp_server_id)

### Step 6: Favorites Frontend

**Add favorite functionality to UI:**
- Favorite button/icon on agent cards (listing page)
- Favorite button on agent detail page
- Favorite button/icon on server cards (listing page)
- Favorite button on server detail page
- User dashboard/profile page showing favorites

**Files to create:**
- `frontend/src/app/components/user-profile/user-profile.component.ts|html|css`
- `frontend/src/app/services/favorites.service.ts`

**Files to modify:**
- `frontend/src/app/components/agents-list/agents-list.component.ts|html|css` - add favorite icons
- `frontend/src/app/components/mcp-servers/mcp-servers.component.ts|html|css` - add favorite icons
- `frontend/src/app/components/agent-detail/*` - add favorite button
- `frontend/src/app/components/mcp-server-detail/*` - add favorite button
- `frontend/src/app/app.routes.ts` - add profile route (protected)
- `frontend/src/app/components/header/header.component.html` - add profile link

**Favorites service methods:**
- `addToFavorites(agentId?, mcpServerId?)`
- `removeFromFavorites(favoriteId)`
- `getUserFavorites(page, limit)`
- `isFavorited(agentId?, mcpServerId?)` - returns observable

### Step 7: Integration & Testing

**Connect all pieces:**
- Ensure detail pages link from listing pages
- Test authentication flow (register → login → access protected routes)
- Test favorites flow (add → view in profile → remove)
- Verify JWT is attached to protected API calls
- Test logout clears token and redirects
- Verify auth guard prevents unauthorized access

**Manual testing checklist:**
- Click agent card → navigates to detail page
- Click server card → navigates to detail page
- Register new user → redirects to login or auto-login
- Login → token stored, header shows logout button
- Add agent to favorites (authenticated) → success
- View favorites in profile → displays favorited items
- Remove favorite → removed from list
- Logout → token cleared, redirected to home
- Try accessing profile when logged out → redirected to login

### Step 8: UI Polish & Error Handling

**Enhancements:**
- Loading states for all async operations
- Error messages for failed authentication
- Success toasts/notifications for favorites actions
- Form validation for login/register (email format, password strength)
- 404 page for invalid agent/server IDs
- Back button on detail pages
- Breadcrumb navigation
- Smooth animations for favorite icon state changes

**Error scenarios to handle:**
- Invalid credentials on login
- Email already exists on registration
- Network errors during API calls
- Expired JWT token (redirect to login)
- Agent/server not found (404 page)
- Unauthorized access to favorites (redirect to login)

## Testing Strategy

**Backend Testing:**
- Test auth endpoints (registration, login, token validation)
- Test favorites endpoints (add, remove, list)
- Test detail endpoints with view count increment
- Test JWT expiration and refresh

**Frontend Testing:**
- Test navigation to detail pages
- Test login/register form validation
- Test auth guard redirects
- Test favorite button state changes
- Test logout clears session

## Success Criteria

- Users can view full details for any agent or server
- Users can register and login with email/password
- Authenticated users can add/remove favorites
- Favorites persist across sessions
- Protected routes redirect to login when unauthenticated
- UI is consistent with existing Solarized theme
- All features work in both dark and light modes
- No console errors or broken links

---

**Document Version**: 1.0  
**Created**: 2025-11-27  
**Status**: Ready for Implementation
