"""
Code Debug Environment — server-side logic.

Implements reset(), step(), and state for the OpenEnv spec.
The grader executes submitted code against test cases in a sandboxed
subprocess and returns fraction-of-tests-passed as the reward.
"""

import threading
import traceback
import uuid
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .tasks import TASKS, TASK_ORDER


# ---------------------------------------------------------------------------
# Pydantic models (shared with the client via the HTTP/WS API)
# ---------------------------------------------------------------------------

class Observation(BaseModel):
    done: bool = False
    reward: Optional[float] = None
    task_id: str = ""
    difficulty: str = ""
    description: str = ""
    buggy_code: str = ""
    test_descriptions: list[str] = []
    feedback: str = ""
    tests_passed: int = 0
    tests_total: int = 0
    attempts_remaining: int = 0
    attempts_used: int = 0


class State(BaseModel):
    episode_id: Optional[str] = None
    step_count: int = 0
    current_task_id: str = ""
    tasks_completed: list[str] = []
    total_reward: float = 0.0


class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    episode_id: Optional[str] = None


class StepRequest(BaseModel):
    fixed_code: str


# ---------------------------------------------------------------------------
# Grader — runs submitted code against test cases
# ---------------------------------------------------------------------------

def _run_tests(code: str, function_name: str, test_cases: list[dict],
               timeout: float = 10.0) -> dict:
    """Execute *code*, call *function_name* with each test case, and return
    a summary dict with keys: passed, total, details, error."""

    results = {
        "passed": 0,
        "total": len(test_cases),
        "details": [],
        "error": None,
    }

    # First, try to compile the code to catch syntax errors early.
    try:
        compiled = compile(code, "<submitted>", "exec")
    except SyntaxError as exc:
        results["error"] = f"SyntaxError: {exc}"
        results["details"] = [
            {"input": str(tc["args"]), "passed": False, "error": str(exc)}
            for tc in test_cases
        ]
        return results

    # Execute the code in a restricted namespace.
    namespace: dict = {}
    try:
        exec(compiled, namespace)  # noqa: S102
    except Exception as exc:
        results["error"] = f"RuntimeError during definition: {exc}"
        results["details"] = [
            {"input": str(tc["args"]), "passed": False, "error": str(exc)}
            for tc in test_cases
        ]
        return results

    func = namespace.get(function_name)
    if func is None:
        results["error"] = (
            f"Function '{function_name}' not found after executing the code."
        )
        results["details"] = [
            {"input": str(tc["args"]), "passed": False,
             "error": results["error"]}
            for tc in test_cases
        ]
        return results

    # Run each test case in a thread with a timeout.
    for tc in test_cases:
        test_result = {"input": str(tc["args"]), "passed": False, "error": None}
        actual = None
        error_msg = None

        def _exec():
            nonlocal actual, error_msg
            try:
                actual = func(*tc["args"])
            except Exception:
                error_msg = traceback.format_exc()

        t = threading.Thread(target=_exec, daemon=True)
        t.start()
        t.join(timeout=timeout)

        if t.is_alive():
            test_result["error"] = "Execution timed out"
        elif error_msg:
            test_result["error"] = error_msg.strip().split("\n")[-1]
        elif actual == tc["expected"]:
            test_result["passed"] = True
            results["passed"] += 1
        else:
            test_result["error"] = (
                f"Expected {tc['expected']!r}, got {actual!r}"
            )

        results["details"].append(test_result)

    return results


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class CodeDebugEnvironment:
    """An OpenEnv-compatible environment for code debugging tasks."""

    def __init__(self):
        self._state = State()
        self._current_task: Optional[dict] = None
        self._attempts_used = 0
        self._max_attempts = 0
        self._best_reward = 0.0

    # -- reset --
    def reset(self, task_id: Optional[str] = None,
              episode_id: Optional[str] = None) -> Observation:
        if task_id is None:
            task_id = TASK_ORDER[0]

        if task_id not in TASKS:
            return Observation(
                done=True,
                reward=0.0,
                feedback=f"Unknown task_id '{task_id}'. "
                         f"Available: {', '.join(TASK_ORDER)}",
            )

        task = TASKS[task_id]
        self._current_task = task
        self._attempts_used = 0
        self._max_attempts = task["max_attempts"]
        self._best_reward = 0.0

        self._state = State(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task_id=task_id,
        )

        return Observation(
            done=False,
            reward=None,
            task_id=task["task_id"],
            difficulty=task["difficulty"],
            description=task["description"],
            buggy_code=task["buggy_code"],
            test_descriptions=task["test_descriptions"],
            feedback="Environment reset. Submit your fixed code.",
            tests_passed=0,
            tests_total=len(task["test_cases"]),
            attempts_remaining=self._max_attempts,
            attempts_used=0,
        )

    # -- step --
    def step(self, action: StepRequest) -> Observation:
        if self._current_task is None:
            return Observation(
                done=True, reward=0.0,
                feedback="No active task. Call reset() first.",
            )

        task = self._current_task
        self._attempts_used += 1
        self._state.step_count += 1

        # Grade the submission
        result = _run_tests(
            action.fixed_code,
            task["function_name"],
            task["test_cases"],
        )

        reward = (
            result["passed"] / result["total"] if result["total"] > 0 else 0.0
        )
        self._best_reward = max(self._best_reward, reward)

        # Build feedback string
        feedback_lines = []
        if result["error"]:
            feedback_lines.append(f"Error: {result['error']}")
        for i, detail in enumerate(result["details"]):
            status = "PASS" if detail["passed"] else "FAIL"
            line = f"  Test {i+1}: {status}"
            if detail.get("error"):
                line += f" — {detail['error']}"
            feedback_lines.append(line)
        feedback_lines.append(
            f"Score: {result['passed']}/{result['total']} "
            f"(reward={reward:.2f})"
        )

        all_passed = result["passed"] == result["total"]
        out_of_attempts = self._attempts_used >= self._max_attempts
        done = all_passed or out_of_attempts

        if all_passed:
            feedback_lines.append("All tests passed!")
            if task["task_id"] not in self._state.tasks_completed:
                self._state.tasks_completed.append(task["task_id"])
        elif out_of_attempts:
            feedback_lines.append("Out of attempts.")

        self._state.total_reward += reward

        return Observation(
            done=done,
            reward=reward,
            task_id=task["task_id"],
            difficulty=task["difficulty"],
            description=task["description"],
            buggy_code=task["buggy_code"],
            test_descriptions=task["test_descriptions"],
            feedback="\n".join(feedback_lines),
            tests_passed=result["passed"],
            tests_total=result["total"],
            attempts_remaining=self._max_attempts - self._attempts_used,
            attempts_used=self._attempts_used,
        )

    # -- state --
    @property
    def state(self) -> State:
        return self._state
