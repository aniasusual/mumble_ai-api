from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from pathlib import Path

from agno.os import AgentOS

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

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mumble-ai-api"}

# Initialize Main Agent Team
main_team = get_main_agent(
    native_language="English",
)

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
