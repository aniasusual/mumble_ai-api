# JWT Middleware Fix: Public Endpoints

## 🐛 The Problem

**Error:** 401 Unauthorized on `/api/auth/login` and `/api/auth/register`
**Error Message:** "Authorization header is missing"

### Root Cause

The JWT Middleware was configured to validate **ALL requests**, including the public authentication endpoints that don't require tokens (because users are trying to GET a token by logging in!).

```python
# BEFORE (BROKEN):
app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.JWT_SECRET],
    algorithm=settings.JWT_ALGORITHM,
    validate=True,  # ❌ Validates ALL requests
    # ... no excluded paths ...
)
```

**Result:**
```
User tries to login → JWT Middleware checks for token
                   → No token (user hasn't logged in yet!)
                   → 401 Unauthorized
                   → User can never login! 🔒
```

---

## ✅ The Solution

Added `excluded_route_paths` parameter to skip JWT validation for public endpoints:

```python
# AFTER (FIXED):
app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.JWT_SECRET],
    algorithm=settings.JWT_ALGORITHM,
    user_id_claim="sub",
    session_id_claim="session_id",
    validate=True,
    verify_audience=True,
    token_source=TokenSource.HEADER,
    excluded_route_paths=[
        "/health",              # Health check endpoint
        "/api/auth/login",      # Login endpoint (public)
        "/api/auth/register",   # Register endpoint (public)
    ],
)
```

---

## 🔄 How It Works Now

### Public Endpoints (No Token Required)

```
┌──────────────────────────────────────────────────────┐
│ 1. User registers/logs in                            │
│    POST /api/auth/login                              │
│    Body: { email, password }                         │
│    Headers: NO Authorization needed                  │
└──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ 2. JWT Middleware                                    │
│    ─────────────────                                 │
│    • Checks if path is in excluded_route_paths       │
│    • "/api/auth/login" IS excluded                   │
│    • ✅ SKIPS validation                             │
│    • Request proceeds without token check            │
└──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ 3. Backend validates credentials                     │
│    • Checks email/password                           │
│    • Creates JWT token with user_id                  │
│    • Returns: { access_token, user }                 │
└──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ 4. Frontend stores token                             │
│    • localStorage.setItem('token', access_token)     │
│    • axios.defaults.headers.common['Authorization']  │
│    • User is now authenticated! ✅                   │
└──────────────────────────────────────────────────────┘
```

### Protected Endpoints (Token Required)

```
┌──────────────────────────────────────────────────────┐
│ 1. User calls protected endpoint                     │
│    POST /teams/mumble-ai-coach/runs                  │
│    Headers: Authorization: Bearer <token>            │
└──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ 2. JWT Middleware                                    │
│    ─────────────────                                 │
│    • Checks if path is in excluded_route_paths       │
│    • "/teams/mumble-ai-coach/runs" NOT excluded      │
│    • ✅ VALIDATES token                              │
│    • Extracts user_id from token                     │
│    • Creates RunContext                              │
└──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ 3. Agent executes with user context                  │
│    • Tools can access run_context.user_id            │
│    • Personalized learning experience                │
└──────────────────────────────────────────────────────┘
```

---

## 📋 Endpoint Categories

### Public Endpoints (No Token)
- ✅ `POST /api/auth/login` - User login
- ✅ `POST /api/auth/register` - User registration
- ✅ `GET /health` - Health check

### Protected Endpoints (Token Required)
- 🔒 `GET /api/auth/me` - Get current user profile
- 🔒 `PUT /api/auth/me` - Update user profile
- 🔒 `GET /api/sessions` - Get user's learning sessions
- 🔒 `POST /api/sessions` - Create new session
- 🔒 `POST /teams/mumble-ai-coach/runs` - Chat with agent
- 🔒 `GET /teams/mumble-ai-coach/sessions` - Get AgentOS sessions

---

## 🔐 Security Considerations

### Why Exclude These Paths?

**1. `/api/auth/login` and `/api/auth/register`**
- **Must be public** - Users don't have tokens yet
- Without exclusion: Catch-22 situation (need token to get token!)
- Users authenticate with email/password instead

**2. `/health`**
- **Should be public** - Used by monitoring tools, load balancers
- Shouldn't require authentication
- Standard practice for health checks

### What About Other `/api/*` Routes?

Other `/api/*` routes use **FastAPI's `Depends(get_current_user)`** dependency:

```python
@router.get("/api/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user),  # ← Validates JWT here
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Only authenticated users can reach this
```

This provides **defense in depth**:
1. JWT Middleware checks AgentOS routes
2. FastAPI dependency checks custom API routes

---

## 🧪 Testing the Fix

### Test 1: Register (Should Work)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "base_language": "English"
  }'

# Expected: 200 OK with { access_token, user }
```

### Test 2: Login (Should Work)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Expected: 200 OK with { access_token, user }
```

### Test 3: Protected Route Without Token (Should Fail)
```bash
curl -X GET http://localhost:8000/api/sessions

# Expected: 401 Unauthorized - "Not authenticated"
```

### Test 4: Protected Route With Token (Should Work)
```bash
TOKEN="<your_token_from_login>"

curl -X GET http://localhost:8000/api/sessions \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with array of sessions
```

### Test 5: Agent Call With Token (Should Work)
```bash
curl -X POST http://localhost:8000/teams/mumble-ai-coach/runs \
  -H "Authorization: Bearer $TOKEN" \
  -F "message=Hello, I want to learn Spanish" \
  -F "session_id=session-123"

# Expected: 200 OK with agent response
```

---

## 🎯 Summary

### What Changed
✅ Added `excluded_route_paths` parameter to JWT Middleware
✅ Excluded `/api/auth/login` and `/api/auth/register`
✅ Excluded `/health` for monitoring

### What Now Works
✅ Users can register and login without tokens
✅ Protected routes still require authentication
✅ Agent calls work with JWT tokens
✅ Tools access user_id from RunContext

### Security Status
🔒 **Enhanced** - Defense in depth:
- JWT Middleware for AgentOS routes
- FastAPI dependencies for custom routes
- Public endpoints properly excluded
- Token validation on all protected routes

---

## 📚 Related Files

- **Configuration**: [src/main.py:61-74](src/main.py#L61-L74)
- **Auth Service**: [src/services/auth.py](src/services/auth.py)
- **Token Creation**: [src/core/security.py:28-50](src/core/security.py#L28-L50)
- **Frontend Auth**: [mumble-ai-ui/frontend/src/context/AuthContext.jsx](../../mumble-ai-ui/frontend/src/context/AuthContext.jsx)

---

## 🚀 Ready to Test!

Your authentication system is now properly configured:
- Public endpoints are accessible
- Protected endpoints require tokens
- JWT Middleware works correctly
- User context flows to agent tools

Try logging in from the frontend - it should work now! 🎉
