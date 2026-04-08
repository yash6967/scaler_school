"""Typed models for the Code Debug Environment."""

from typing import List, Optional
from pydantic import BaseModel


class CodeDebugAction(BaseModel):
    """Action: submit fixed Python code."""
    fixed_code: str


class CodeDebugObservation(BaseModel):
    """Observation returned after reset() or step()."""
    done: bool = False
    reward: Optional[float] = None

    task_id: str = ""
    difficulty: str = ""
    description: str = ""
    buggy_code: str = ""
    test_descriptions: List[str] = []
    feedback: str = ""
    tests_passed: int = 0
    tests_total: int = 0
    attempts_remaining: int = 0
    attempts_used: int = 0


class CodeDebugState(BaseModel):
    """Internal state of the environment."""
    episode_id: Optional[str] = None
    step_count: int = 0
    current_task_id: str = ""
    tasks_completed: List[str] = []
    total_reward: float = 0.0
