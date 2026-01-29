# User Context Implementation Guide

## Overview

This guide explains how we've implemented user_id and session_id access in the Mumble AI agents using AgentOS JWT middleware and RunContext.

## What We Implemented

### 1. JWT Middleware Integration (src/main.py)

Added AgentOS JWT middleware that automatically extracts `user_id` from JWT tokens and injects it into all agent runs.

```python
app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.JWT_SECRET],
    algorithm=settings.JWT_ALGORITHM,
    user_id_claim="sub",  # Extract user_id from 'sub' claim in JWT
    session_id_claim="session_id",  # Extract session_id from custom claim (optional)
    validate=True,
    verify_audience=True,
    token_source=TokenSource.HEADER,  # From Authorization: Bearer <token>
)
```

**Key Features:**
- ✅ Automatic user authentication
- ✅ User ID extraction from JWT tokens
- ✅ Session ID support (optional, per-request)
- ✅ Token validation and expiration checking
- ✅ Audience verification

### 2. Updated Token Generation (src/core/security.py)

Enhanced `create_access_token` to support optional session_id:

```python
def create_access_token(user_id: str, session_id: Optional[str] = None) -> str:
    payload = {
        "sub": user_id,  # User ID
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "aud": "mumble-ai",  # Must match AgentOS id
    }
    if session_id:
        payload["session_id"] = session_id
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

### 3. User Context Tools (src/agents/tools/)

Created tools that access user_id and session_id from RunContext:

#### `get_user_learning_profile(run_context: RunContext)`
- Accesses `run_context.user_id` to fetch user profile
- Returns learning preferences, goals, target language, etc.

#### `get_session_context(run_context: RunContext)`
- Accesses both `run_context.user_id` and `run_context.session_id`
- Returns current session information and chat history

#### `save_learning_progress(run_context: RunContext, progress_data: str)`
- Saves progress scoped to specific user and session
- Tracks completed lessons and achievements

### 4. Agent Integration

All three agents now have access to user context tools:
- **Main Agent** (Language Learning Coach)
- **Planning Agent** (Curriculum Designer)
- **Conversation Agent** (Practice Partner)

## How It Works

### Architecture Flow

```
1. User logs in → Gets JWT with user_id
2. Frontend sends request with JWT in Authorization header
3. JWT Middleware extracts user_id from token
4. AgentOS creates RunContext with user_id
5. Agent runs with RunContext
6. Tools access user_id via run_context.user_id
7. Database queries scoped to that user
```

### Example: Agent Run with User Context

**Request:**
```http
POST /api/v1/teams/mumble-ai-coach/runs
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "I want to learn Spanish",
  "session_id": "session-123"  // Optional, passed per-request
}
```

**What Happens:**
1. JWT middleware extracts `user_id` from token → `"user-456"`
2. Frontend passes `session_id` in request body → `"session-123"`
3. AgentOS creates RunContext:
   ```python
   RunContext(
       user_id="user-456",      # From JWT
       session_id="session-123", # From request
       run_id="run-789",
       dependencies={},
       metadata={},
       ...
   )
   ```
4. Agent can call tools:
   ```python
   get_user_learning_profile(run_context)
   # Returns profile for user-456

   get_session_context(run_context)
   # Returns session-123 details

   save_learning_progress(run_context, "Completed Lesson 1")
   # Saves to session-123 for user-456
   ```

## Session Management Strategy

We're using a **hybrid approach**:

### User ID: In JWT (Authentication)
- Set once at login
- Valid for 24 hours
- Automatically extracted by middleware

### Session ID: Per-Request (Context)
- Passed by frontend on each request
- Users can switch sessions without new JWT
- More flexible for multiple learning paths

### Why This Approach?

✅ **Flexible**: Users can switch between learning sessions easily
✅ **Secure**: User authentication via JWT
✅ **Simple**: No need to refresh JWT when changing sessions
✅ **Scalable**: Supports multiple concurrent learning paths

## How to Use in Your Frontend

### 1. Login and Store Token

```javascript
// Login
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});

const { access_token, user } = await response.json();

// Store token
localStorage.setItem('token', access_token);
localStorage.setItem('user_id', user.id);
```

### 2. Call Agent with Session

```javascript
// Select or create session
const sessionId = "session-123"; // From your session list

// Call agent
const response = await fetch('/api/v1/teams/mumble-ai-coach/runs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: "I want to practice Spanish conversation",
    session_id: sessionId  // Pass session per-request
  })
});

const result = await response.json();
```

### 3. Agent Automatically Has User Context

The agent now has access to:
- `user_id`: From JWT token (automatic)
- `session_id`: From request body (passed by you)
- User profile, preferences, history (via tools)

## Database Query Examples

### Tools Can Query User-Specific Data

```python
def get_user_learning_profile(run_context: RunContext) -> str:
    user_id = run_context.user_id

    # Query MongoDB
    user = await db.users.find_one({"id": user_id})

    return f"""
    User: {user['name']}
    Native Language: {user['base_language']}
    Target Language: {user.get('target_language', 'Not set')}
    Level: {user.get('proficiency_level', 'Unknown')}
    """

def get_session_context(run_context: RunContext) -> str:
    user_id = run_context.user_id
    session_id = run_context.session_id

    # Query session scoped to user
    session = await db.sessions.find_one({
        "id": session_id,
        "user_id": user_id  # Security: Only user's own sessions
    })

    return f"""
    Session: {session['title']}
    Created: {session['created_at']}
    Messages: {len(session['chat_history'])}
    Progress: {session.get('progress', 'Not tracked')}
    """
```

## Testing the Implementation

### 1. Start the Server

```bash
cd /Users/animeshdhillon/myProjects/mumble_ai-api
python -m uvicorn src.main:app --reload
```

### 2. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "base_language": "English"
  }'
```

Save the `access_token` from the response.

### 3. Create a Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learning Spanish - Week 1",
    "notes": "Beginner level"
  }'
```

Save the session `id`.

### 4. Call the Agent

```bash
curl -X POST http://localhost:8000/api/v1/teams/mumble-ai-coach/runs \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check my user profile",
    "session_id": "YOUR_SESSION_ID"
  }'
```

The agent will use the `get_user_learning_profile` tool and show your user_id!

## Benefits of This Implementation

1. **Security**: User authentication via JWT
2. **Automatic Context**: user_id automatically available in all tools
3. **Personalization**: Tools can fetch user-specific data
4. **Session Management**: Track different learning paths per user
5. **Scalability**: Works with AgentOS session persistence
6. **Clean Code**: No need to manually pass user_id everywhere

## Next Steps

To fully implement the tools with database access:

1. **Connect to MongoDB in tools**:
   ```python
   from motor.motor_asyncio import AsyncIOMotorClient
   import os

   def get_user_learning_profile(run_context: RunContext) -> str:
       db_url = os.getenv("MONGODB_URL")
       client = AsyncIOMotorClient(db_url)
       db = client.get_database()

       user = await db.users.find_one({"id": run_context.user_id})
       # ... return user profile
   ```

2. **Add more specialized tools**:
   - `get_learning_goals(run_context)`
   - `get_completed_lessons(run_context)`
   - `update_proficiency_level(run_context, new_level)`
   - `get_vocabulary_progress(run_context)`

3. **Implement progress tracking**:
   - Track completed exercises
   - Monitor speaking practice time
   - Measure vocabulary retention

## Troubleshooting

### "User not authenticated" Error
- Check that JWT token is in Authorization header
- Verify token hasn't expired (24 hours)
- Ensure JWT_SECRET matches in .env

### "No session selected" Error
- Pass `session_id` in request body
- Or include session_id in JWT token payload

### Tools Not Working
- Check AgentOS logs for tool execution
- Verify tools are imported in agent files
- Ensure RunContext is passed correctly

## Summary

You now have:
- ✅ JWT middleware automatically extracting user_id
- ✅ Tools that access user_id and session_id from RunContext
- ✅ All three agents equipped with user context tools
- ✅ Secure, scalable user authentication and session management

The agents can now personalize learning experiences based on user profiles and track progress across sessions!
