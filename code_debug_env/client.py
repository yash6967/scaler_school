"""
HTTP client for the Code Debug Environment.

Provides a simple synchronous wrapper around the /reset, /step, /state
endpoints exposed by the FastAPI server.
"""

import requests
from typing import Optional

from .models import CodeDebugAction, CodeDebugObservation, CodeDebugState


class CodeDebugEnv:
    """Synchronous HTTP client for the Code Debug Environment."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health(self) -> dict:
        resp = self.session.get(f"{self.base_url}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def reset(self, task_id: Optional[str] = None,
              episode_id: Optional[str] = None) -> CodeDebugObservation:
        payload = {}
        if task_id is not None:
            payload["task_id"] = task_id
        if episode_id is not None:
            payload["episode_id"] = episode_id
        resp = self.session.post(
            f"{self.base_url}/reset", json=payload, timeout=30,
        )
        resp.raise_for_status()
        return CodeDebugObservation(**resp.json())

    def step(self, action: CodeDebugAction) -> CodeDebugObservation:
        resp = self.session.post(
            f"{self.base_url}/step",
            json={"fixed_code": action.fixed_code},
            timeout=30,
        )
        resp.raise_for_status()
        return CodeDebugObservation(**resp.json())

    def state(self) -> CodeDebugState:
        resp = self.session.get(f"{self.base_url}/state", timeout=10)
        resp.raise_for_status()
        return CodeDebugState(**resp.json())

    def list_tasks(self) -> list[dict]:
        resp = self.session.get(f"{self.base_url}/tasks", timeout=10)
        resp.raise_for_status()
        return resp.json()
