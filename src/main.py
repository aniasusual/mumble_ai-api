from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from pathlib import Path

from agno.os import AgentOS
from agno.os.middleware import JWTMiddleware
from agno.os.middleware.jwt import TokenSource

from .agents.mainAgent import get_main_agent
from .api import api_router
from .core import settings, db_manager


# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for database connection."""
    print(f"Connecting to MongoDB...")
    await db_manager.connect()
    try:
        yield
    finally:
        await db_manager.close()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://ui-facelift-16.preview.emergentagent.com",
#         "http://localhost:3000",
#         "https://*.preview.emergentagent.com",  # Allow all preview domains
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=["*"],
# )

# JWT middleware for AgentOS - Automatically injects user_id and session_id from JWT tokens
# IMPORTANT: Must be added BEFORE AgentOS initialization
# NOTE: JWT Middleware is for AgentOS routes (/teams/*, /agents/*, etc.)
#       Custom API routes (/api/*) use FastAPI Depends(get_current_user) instead
app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.JWT_SECRET],
    algorithm=settings.JWT_ALGORITHM,
    user_id_claim="sub",  # Extract user_id from 'sub' claim in JWT
    session_id_claim="session_id",  # Extract session_id from custom claim
    validate=True,  # Enable token validation
    verify_audience=True,  # Verify audience matches AgentOS ID
    token_source=TokenSource.HEADER,  # Extract from Authorization header
    excluded_route_paths=[
        "/health",        # Health check endpoint
        "/api/*",         # All custom API routes (use FastAPI dependencies)
        "/docs",          # OpenAPI docs
        "/openapi.json"
    ],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mumble-ai-api"}

# Initialize Main Agent Team
# Note: {base_language} template variable in team instructions will be replaced
# at runtime with the value from dependencies parameter (passed from frontend)
main_team = get_main_agent()

# Initialize AgentOS
agent_os = AgentOS(
    id="mumble-ai",
    teams=[main_team],
    base_app=app,
    lifespan=lifespan,
)

# Get final app with AgentOS integration
app = agent_os.get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
