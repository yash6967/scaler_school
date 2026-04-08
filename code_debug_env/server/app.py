"""
FastAPI application for the Code Debug Environment.

Exposes /reset, /step, /state, /health, and /tasks endpoints.
Compatible with the OpenEnv spec (step/reset/state).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .environment import (
    CodeDebugEnvironment,
    Observation,
    ResetRequest,
    State,
    StepRequest,
)
from .tasks import TASK_ORDER, TASKS

app = FastAPI(
    title="Code Debug Environment",
    description="An OpenEnv environment where AI agents fix buggy Python code.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single environment instance (supports one session at a time for simplicity)
env = CodeDebugEnvironment()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    """Return metadata for all available tasks."""
    return [
        {
            "task_id": t["task_id"],
            "difficulty": t["difficulty"],
            "description": t["description"],
        }
        for t in (TASKS[tid] for tid in TASK_ORDER)
    ]


@app.post("/reset", response_model=Observation)
def reset(req: ResetRequest = ResetRequest()):
    return env.reset(task_id=req.task_id, episode_id=req.episode_id)


@app.post("/step", response_model=Observation)
def step(req: StepRequest):
    return env.step(req)


@app.get("/state", response_model=State)
def state():
    return env.state
