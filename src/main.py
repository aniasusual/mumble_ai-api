from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from dotenv import load_dotenv
from pathlib import Path

# from app.api.main import api_router
from .agents.mainAgent import get_main_agent
from agno.os import AgentOS



load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from .core.database import db_manager
    print(f"Connecting to MongoDB...")
    await db_manager.connect()
    try:
        yield
    finally:
        await db_manager.close()


app = FastAPI()


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

main_team = get_main_agent(
    native_language="English",
)


agent_os = AgentOS(
    id="mumble-ai",
    teams=[main_team],
    base_app=app,
    lifespan=lifespan,
)

app = agent_os.get_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    agent_os.serve(app="custom_fastapi_app:app", reload=True)
