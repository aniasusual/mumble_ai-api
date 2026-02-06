from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from pathlib import Path

from agno.os import AgentOS
from agno.os.middleware import JWTMiddleware
from agno.os.middleware.jwt import TokenSource

from .agents.mainAgent import get_main_agent
from .agents.conversationAgent import get_conversation_agent, get_conversation_realtime_router
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


app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.JWT_SECRET],
    algorithm=settings.JWT_ALGORITHM,
    user_id_claim="sub", 
    validate=True,  
    verify_audience=True, 
    token_source=TokenSource.HEADER,  
    excluded_route_paths=[
        "/health",       
        "/api/*",         
        "/docs",
        "/openapi.json"
    ],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Realtime WebRTC endpoints (prefer EMERGENT_LLM_KEY proxy, fallback to OPENAI_API_KEY)
if settings.EMERGENT_LLM_KEY or settings.OPENAI_API_KEY:
    app.include_router(get_conversation_realtime_router(), prefix=settings.API_V1_PREFIX)
else:
    print("EMERGENT_LLM_KEY/OPENAI_API_KEY not set; realtime routes are disabled.")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mumble-ai-api"}

main_team = get_main_agent()

# Conversation agent for direct user interaction
# This allows users to talk directly to the conversation agent
# when the main agent triggers conversation practice mode
# Note: The same agent is also a team member in main_team
conversation_agent = get_conversation_agent()

# Initialize AgentOS with both team and standalone agents
agent_os = AgentOS(
    id="mumble-ai",
    teams=[main_team],
    agents=[conversation_agent],  # Register for direct access at /agents/conversation-agent/runs
    base_app=app,
    lifespan=lifespan,
)

# Get final app with AgentOS integration
app = agent_os.get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
