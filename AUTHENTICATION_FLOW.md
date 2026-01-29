# Complete Authentication Flow: Frontend to Backend

## Overview

This document explains the complete authentication flow from frontend to backend, including how JWT tokens are generated, stored, and used to authenticate requests to both custom API routes and AgentOS endpoints.

---

## 🔑 Part 1: Initial Authentication (Login/Register)

### Step 1: User Login

```javascript
// Frontend: mumble-ai-ui/frontend/src/context/AuthContext.jsx

const login = async (email, password) => {
  // Call backend login endpoint
  const response = await axios.post(`${API}/auth/login`, {
    email,
    password
  });

  // Extract token and user from response
  const { access_token, user: userData } = response.data;

  // Store token in localStorage
  localStorage.setItem('token', access_token);

  // Set token in state
  setToken(access_token);
  setUser(userData);

  return userData;
};
```

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Step 2: Backend Validates & Generates Token

```python
# Backend: src/services/auth.py

async def login_user(self, login_data: UserLogin) -> TokenResponse:
    # Find user in database
    user = await self.db.users.find_one({"email": login_data.email})

    # Verify password
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token with user_id
    token = create_access_token(user["id"])

    return TokenResponse(access_token=token, user=UserResponse(...))
```

**JWT Token Generation:**
```python
# Backend: src/core/security.py

def create_access_token(user_id: str, session_id: Optional[str] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": user_id,              # Standard JWT claim for user ID
        "exp": expire,                # Expiration time
        "iat": datetime.now(timezone.utc),  # Issued at
        "aud": "mumble-ai",          # Audience - MUST match AgentOS id
    }

    if session_id:
        payload["session_id"] = session_id

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-456",
    "email": "user@example.com",
    "name": "John Doe",
    "base_language": "English"
  }
}
```

### Step 3: Frontend Stores Token & Sets Global Header

```javascript
// Frontend: mumble-ai-ui/frontend/src/context/AuthContext.jsx

useEffect(() => {
  if (token) {
    // ✅ CRITICAL: This makes ALL axios requests include Authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
}, [token]);
```

**What happens:**
- Token stored in `localStorage` → Persists across page refreshes
- Token stored in React state → Available for components
- **Axios global header configured** → All axios requests automatically authenticated

---

## 🔄 Part 2: Authenticated Requests

### Flow A: Custom API Routes (Sessions, Profile)

These are your custom FastAPI routes that use `Depends(get_current_user)`.

**Example: Get User Sessions**

```javascript
// Frontend: Calling your custom API
const getSessions = async () => {
  const response = await axios.get(`${API}/sessions`);
  // ✅ Authorization: Bearer <token> header automatically added by axios!
  return response.data;
};
```

**Request:**
```http
GET /api/sessions
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Backend Processing:**
```python
# Backend: src/api/routes/sessions.py

@router.get("", response_model=List[LearningSession])
async def get_sessions(
    current_user: dict = Depends(get_current_user),  # ← Extracts user from JWT
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # current_user["id"] is extracted from JWT token
    session_service = SessionService(db)
    return await session_service.get_user_sessions(current_user["id"])
```

**Authentication Dependency:**
```python
# Backend: src/core/dependencies.py

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    token = credentials.credentials  # Extract token from "Bearer <token>"
    user_id = decode_token(token)    # Decode JWT → get user_id from "sub" claim

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user  # Returns full user object
```

---

### Flow B: AgentOS Routes (Agent Runs) - WITH JWT MIDDLEWARE

These are AgentOS endpoints that use the JWT middleware we implemented.

**Example: Send Message to Agent (Non-Streaming)**

```javascript
// Frontend: mumble-ai-ui/frontend/src/services/agentService.js

export const sendMessageToAgent = async (message, sessionId, user) => {
  const formData = new FormData();
  formData.append('message', message);
  formData.append('session_id', sessionId);
  formData.append('dependencies', JSON.stringify({
    base_language: user.base_language
  }));

  const response = await axios.post(
    `${BACKEND_URL}/teams/mumble-ai-coach/runs`,
    formData
  );
  // ✅ Authorization: Bearer <token> header automatically added!

  return response.data;
};
```

**Request:**
```http
POST /teams/mumble-ai-coach/runs
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

message=I want to learn Spanish
session_id=session-123
dependencies={"base_language":"English"}
```

**Backend Processing with JWT Middleware:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. Request arrives at FastAPI                           │
│    Authorization: Bearer eyJhbGc...                      │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 2. JWT Middleware (main.py:61-70)                       │
│    ─────────────────────────────────────────            │
│    app.add_middleware(                                  │
│        JWTMiddleware,                                   │
│        verification_keys=[settings.JWT_SECRET],         │
│        algorithm=settings.JWT_ALGORITHM,                │
│        user_id_claim="sub",                            │
│        session_id_claim="session_id",                  │
│        validate=True,                                   │
│        verify_audience=True,                            │
│        token_source=TokenSource.HEADER                  │
│    )                                                    │
│                                                         │
│    Actions:                                             │
│    ✓ Extracts token from Authorization header          │
│    ✓ Validates JWT signature                           │
│    ✓ Checks token expiration                           │
│    ✓ Verifies audience = "mumble-ai"                   │
│    ✓ Extracts user_id from "sub" claim                 │
│    ✓ Extracts session_id from request body             │
│    ✓ Creates RunContext                                │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 3. RunContext Created                                   │
│    ────────────────────────────────────────             │
│    RunContext(                                          │
│        user_id="user-456",        ← From JWT "sub"      │
│        session_id="session-123",  ← From request body   │
│        run_id="run-789",          ← Generated by AgentOS│
│        dependencies={             ← From request body   │
│            "base_language": "English"                   │
│        },                                               │
│        metadata={},                                     │
│        session_state={}                                 │
│    )                                                    │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 4. AgentOS Routes Handler                               │
│    Request reaches AgentOS with RunContext              │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Main Agent Executes                                  │
│    ─────────────────────────────────────────            │
│    Team(                                                │
│        id="mumble-ai-coach",                           │
│        tools=[                                          │
│            get_user_learning_profile,                  │
│            get_session_context,                        │
│            save_learning_progress                      │
│        ]                                               │
│    )                                                   │
│                                                        │
│    Agent receives:                                     │
│    • User message                                      │
│    • RunContext with user_id & session_id              │
│    • Can call tools that access context                │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Tools Execute with RunContext                        │
│    ──────────────────────────────────────────           │
│    def get_user_learning_profile(                       │
│        run_context: RunContext                          │
│    ) -> str:                                            │
│        user_id = run_context.user_id  # "user-456"     │
│                                                         │
│        # Query database with user_id                    │
│        user = db.users.find_one({"id": user_id})       │
│                                                         │
│        return f"User: {user['name']}, ..."             │
│                                                         │
│    def get_session_context(                             │
│        run_context: RunContext                          │
│    ) -> str:                                            │
│        user_id = run_context.user_id                   │
│        session_id = run_context.session_id             │
│                                                         │
│        # Query session scoped to user                   │
│        session = db.sessions.find_one({                │
│            "id": session_id,                            │
│            "user_id": user_id  # Security!             │
│        })                                              │
│                                                         │
│        return f"Session: {session['title']}, ..."      │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 7. Response Sent Back                                   │
│    {                                                    │
│        "content": "Great! I'll help you learn Spanish...",│
│        "session_id": "session-123",                    │
│        "metrics": {...}                                │
│    }                                                   │
└─────────────────────────────────────────────────────────┘
```

---

### Flow C: AgentOS Routes (Streaming) - FIXED!

**Example: Send Message with Streaming Response**

```javascript
// Frontend: mumble-ai-ui/frontend/src/services/agentService.js
// ✅ FIXED: Now includes Authorization header!

export const sendMessageToAgentStreaming = async (message, sessionId, onChunk, user) => {
  const formData = new FormData();
  formData.append('message', message);
  formData.append('stream', 'true');
  formData.append('session_id', sessionId);

  // ✅ Get token from localStorage
  const token = localStorage.getItem('token');
  const headers = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // ✅ Include Authorization header in fetch request
  const response = await fetch(`${BACKEND_URL}/teams/mumble-ai-coach/runs`, {
    method: 'POST',
    headers: headers,  // ← Authorization header included!
    body: formData,
  });

  // Stream processing...
};
```

**Why This Was Needed:**
- `fetch()` API doesn't use axios defaults
- Axios global headers only apply to axios requests
- Streaming uses `fetch()` → needs manual Authorization header

---

## 🔐 Security Summary

### Token Lifecycle

```
1. User logs in
   ↓
2. Backend generates JWT with user_id in "sub" claim
   ↓
3. Frontend stores token in localStorage
   ↓
4. Frontend sets axios.defaults.headers.common['Authorization']
   ↓
5. Every request includes "Authorization: Bearer <token>"
   ↓
6. Backend validates token on each request
   ↓
7. Token expires after 24 hours
   ↓
8. User must re-login
```

### Two Authentication Mechanisms

| Route Type | Authentication Method | Usage |
|------------|----------------------|-------|
| Custom API Routes | `Depends(get_current_user)` | Sessions, Profile, Auth endpoints |
| AgentOS Routes | JWT Middleware | Agent runs, AgentOS sessions |

### Where User ID is Available

**Custom Routes:**
```python
@router.get("/sessions")
async def get_sessions(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]  # ← Available here
```

**AgentOS Routes + Tools:**
```python
def get_user_learning_profile(run_context: RunContext) -> str:
    user_id = run_context.user_id  # ← Available here
    session_id = run_context.session_id  # ← Also available
```

---

## ✅ What Was Fixed

### Before Fix: Streaming Endpoint Not Authenticated ❌

```javascript
// OLD CODE (BROKEN)
const response = await fetch(`${BACKEND_URL}/teams/mumble-ai-coach/runs`, {
  method: 'POST',
  body: formData,
});
// ❌ No Authorization header → JWT middleware rejects request
```

### After Fix: Streaming Endpoint Authenticated ✅

```javascript
// NEW CODE (FIXED)
const token = localStorage.getItem('token');
const headers = {};

if (token) {
  headers['Authorization'] = `Bearer ${token}`;
}

const response = await fetch(`${BACKEND_URL}/teams/mumble-ai-coach/runs`, {
  method: 'POST',
  headers: headers,  // ✅ Authorization header included
  body: formData,
});
```

---

## 📊 Complete Request Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│                                                                 │
│  User Login                                                     │
│    ↓                                                            │
│  Store JWT Token                                                │
│    ↓                                                            │
│  Set axios.defaults.headers.common['Authorization']            │
│                                                                 │
│  ┌──────────────────────┬──────────────────────────────────┐  │
│  │                      │                                   │  │
│  │  axios.post()        │  fetch() with manual header       │  │
│  │  (Auto Auth)         │  (Manual Auth)                    │  │
│  └──────────────────────┴──────────────────────────────────┘  │
│           │                            │                        │
└───────────┼────────────────────────────┼────────────────────────┘
            │                            │
            │ Authorization: Bearer ...  │ Authorization: Bearer ...
            │                            │
┌───────────▼────────────────────────────▼────────────────────────┐
│                         BACKEND                                  │
│                                                                  │
│  ┌──────────────────────┬──────────────────────────────────┐   │
│  │                      │                                   │   │
│  │  Custom API Routes   │  AgentOS Routes                   │   │
│  │  ──────────────────  │  ────────────────                 │   │
│  │  /api/auth/*         │  /teams/*/runs                    │   │
│  │  /api/sessions/*     │  /teams/*/sessions                │   │
│  │                      │                                   │   │
│  │  Uses:               │  Uses:                            │   │
│  │  get_current_user()  │  JWT Middleware                   │   │
│  │  dependency          │                                   │   │
│  │                      │                                   │   │
│  │  Returns:            │  Returns:                         │   │
│  │  current_user dict   │  RunContext with user_id          │   │
│  └──────────────────────┴──────────────────────────────────┘   │
│                                                                  │
│  Both mechanisms validate JWT token and extract user_id         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **YES, Bearer Token is Sent on Every Request**
   - Axios: Automatically via `axios.defaults.headers.common['Authorization']`
   - Fetch: Manually added in request headers

2. **Two Authentication Flows, Same Token**
   - Custom routes: FastAPI Depends → `get_current_user()`
   - AgentOS routes: JWT Middleware → `RunContext`

3. **User Context is Always Available**
   - In custom routes: `current_user["id"]`
   - In agent tools: `run_context.user_id`

4. **Security is Enforced**
   - Token validation on every request
   - Audience verification
   - Expiration checking
   - User-scoped data access

5. **Streaming Fixed**
   - Now includes Authorization header
   - Works with JWT middleware
   - User context available in streaming responses

---

## 📝 Testing the Complete Flow

### 1. Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Save the access_token from response
TOKEN="eyJhbGc..."
```

### 2. Call Custom API Route
```bash
curl -X GET http://localhost:8000/api/sessions \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Call AgentOS Route
```bash
curl -X POST http://localhost:8000/teams/mumble-ai-coach/runs \
  -H "Authorization: Bearer $TOKEN" \
  -F "message=Check my profile" \
  -F "session_id=session-123"
```

The agent will use `get_user_learning_profile` tool and access your user_id automatically!

---

## 🚀 Summary

Your authentication system is now **fully implemented and working**:

✅ JWT tokens generated on login
✅ Tokens stored in localStorage
✅ Axios automatically includes Authorization header
✅ Fetch manually includes Authorization header (FIXED!)
✅ JWT Middleware extracts user_id for AgentOS routes
✅ Tools can access user_id and session_id via RunContext
✅ Custom routes use get_current_user dependency
✅ All requests are authenticated and secure

Your agents now have complete access to user context for personalized learning experiences!
