import os
import sys
import time
import textwrap
from typing import List, Optional

from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
BENCHMARK = os.getenv("BENCHMARK", "code_debug_env")

MAX_RETRIES = 3
MAX_STEPS = 10
TEMPERATURE = 0.2
MAX_TOKENS = 1024
SUCCESS_SCORE_THRESHOLD = 1.0


SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert Python debugger. You will receive:
    1. A description of what a Python function should do.
    2. The buggy source code.
    3. Descriptions of the test cases that must pass.

    Your job is to return ONLY the corrected Python code — no explanations,
    no markdown fences, no comments about what you changed. Just the raw,
    valid Python source code that defines the function correctly.
    """
).strip()


# ---------------------------------------------------------------------------
# Logging formats EXACTLY as required by the hackathon evaluation
# ---------------------------------------------------------------------------

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # To keep action legible in 1 line, we escape newlines
    action_single_line = action.replace('\n', '\\n').replace('\r', '')
    print(
        f"[STEP] step={step} action={action_single_line} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_code(response_text: str) -> str:
    """Strip markdown fences if the LLM wraps them anyway."""
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Drop first and last fence lines
        start = 1
        end = len(lines)
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip().startswith("```"):
                end = i
                break
        text = "\n".join(lines[start:end]).strip()
    return text


def build_user_prompt(obs: dict) -> str:
    tests = "\n".join(f"  - {t}" for t in obs.get("test_descriptions", []))
    prompt = (
        f"## Description\n{obs['description']}\n\n"
        f"## Buggy Code\n```python\n{obs['buggy_code']}\n```\n\n"
        f"## Test Cases\n{tests}\n\n"
        "Return ONLY the fixed Python code."
    )
    if obs.get("feedback") and "Environment reset" not in obs.get("feedback"):
        prompt += f"\n\n## Previous Attempt Feedback\n{obs['feedback']}"
        
    return prompt


def env_reset(base_url: str, task_id: str) -> dict:
    resp = requests.post(
        f"{base_url}/reset",
        json={"task_id": task_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(base_url: str, fixed_code: str) -> dict:
    resp = requests.post(
        f"{base_url}/step",
        json={"fixed_code": fixed_code},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_list_tasks(base_url: str) -> list[dict]:
    resp = requests.get(f"{base_url}/tasks", timeout=10)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

def main():
    if not API_KEY:
        print("ERROR: Set HF_TOKEN or API_KEY env var.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Discover tasks
    try:
        tasks = env_list_tasks(ENV_URL)
    except Exception as e:
        print(f"Failed to connect to environment server at {ENV_URL}: {e}", file=sys.stderr)
        sys.exit(1)
        
    for task_meta in tasks:
        task_id = task_meta["task_id"]
        
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False

        log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
        
        try:
            obs = env_reset(ENV_URL, task_id)
            
            for step in range(1, MAX_STEPS + 1):
                if obs.get("done", False):
                    break

                user_prompt = build_user_prompt(obs)
                
                fixed_code = None
                error_msg = None
                
                # LLM request
                for retry in range(MAX_RETRIES):
                    try:
                        completion = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=TEMPERATURE,
                            max_tokens=MAX_TOKENS,
                        )
                        raw = completion.choices[0].message.content or ""
                        fixed_code = extract_code(raw)
                        if fixed_code:
                            break
                    except Exception as exc:
                        error_msg = f"LLM error: {exc}"
                        time.sleep(2)
                
                # If LLM failed utterly, fallback
                if not fixed_code:
                    fixed_code = obs.get("buggy_code", "")
                    
                # Submit action
                try:
                    obs = env_step(ENV_URL, fixed_code)
                    reward = obs.get("reward", 0.0)
                    done = obs.get("done", False)
                except Exception as e:
                    error_msg = f"Env step error: {e}"
                    reward = 0.0
                    done = True

                rewards.append(reward)
                steps_taken = step
                # For this environment, final reward is best reward or last reward
                # Actually, our env returns exactly fraction of tests passed
                score = reward

                log_step(step=step, action=fixed_code, reward=reward, done=done, error=error_msg)

                if done:
                    break

            success = score >= SUCCESS_SCORE_THRESHOLD
            
        except Exception as e:
            print(f"[DEBUG] Error running episode: {e}", file=sys.stderr)
        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
