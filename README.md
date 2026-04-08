---
title: Code Debug Environment
emoji: 🐛
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 🐛 Code Debug Environment

An **OpenEnv**-compatible reinforcement learning environment where AI agents
learn to **debug Python code**. Given buggy functions and test case
descriptions, the agent submits corrected code and receives a reward
proportional to the number of tests passed.

## Why This Environment?

Code debugging is one of the most common **real-world** tasks for software
engineers. Unlike toy environments, this environment:

- Simulates a **practical programming workflow** (read code → find bugs → fix them)
- Has a **natural difficulty progression** (syntax → logic → algorithm bugs)
- Produces **meaningful partial-credit signals** (reward = tests passed / total tests)
- Uses **automated, deterministic grading** (test execution, not heuristics)

---

## Environment Specification

### Action Space

| Field        | Type   | Description                    |
|:-------------|:-------|:-------------------------------|
| `fixed_code` | `str`  | The corrected Python source code |

### Observation Space

| Field                | Type        | Description                              |
|:---------------------|:------------|:-----------------------------------------|
| `done`               | `bool`      | Whether the episode is finished          |
| `reward`             | `float?`    | Reward in [0.0, 1.0]                    |
| `task_id`            | `str`       | Unique task identifier                   |
| `difficulty`         | `str`       | `easy`, `medium`, or `hard`              |
| `description`        | `str`       | What the function should do              |
| `buggy_code`         | `str`       | The buggy Python code to fix             |
| `test_descriptions`  | `list[str]` | Human-readable test case descriptions    |
| `feedback`           | `str`       | Grader output (pass/fail per test)       |
| `tests_passed`       | `int`       | Number of tests passed                   |
| `tests_total`        | `int`       | Total number of tests                    |
| `attempts_remaining` | `int`       | Remaining submission attempts            |
| `attempts_used`      | `int`       | Attempts used so far                     |

### Reward Function

```
reward = tests_passed / tests_total   (range: 0.0 – 1.0)
```

Partial credit is awarded: passing 2 out of 4 tests gives reward = 0.5.

### State

| Field             | Type        | Description                      |
|:------------------|:------------|:---------------------------------|
| `episode_id`      | `str?`      | Current episode UUID             |
| `step_count`      | `int`       | Steps taken in current episode   |
| `current_task_id` | `str`       | Active task identifier           |
| `tasks_completed` | `list[str]` | Tasks completed with full score  |
| `total_reward`    | `float`     | Cumulative reward across steps   |

---

## Tasks

| # | Task ID                | Difficulty | Description                          | Tests | Attempts |
|:-:|:-----------------------|:-----------|:-------------------------------------|:-----:|:--------:|
| 1 | `fix_greeting`         | Easy       | Fix syntax errors in a greet function | 3     | 3        |
| 2 | `fix_calculator`       | Easy       | Fix average calculation bugs          | 4     | 3        |
| 3 | `fix_fibonacci`        | Medium     | Fix recursive Fibonacci function      | 5     | 3        |
| 4 | `fix_list_filter`      | Medium     | Fix list filtering and sorting        | 4     | 3        |
| 5 | `fix_binary_search`    | Hard       | Fix binary search algorithm           | 5     | 2        |
| 6 | `fix_matrix_transpose` | Hard       | Fix matrix transpose logic            | 4     | 2        |

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server Locally

```bash
uvicorn code_debug_env.server.app:app --host 0.0.0.0 --port 7860
```

### 3. Test with curl

```bash
# Health check
curl http://localhost:7860/health

# List tasks
curl http://localhost:7860/tasks

# Reset to a task
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "fix_greeting"}'

# Submit a fix
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"fixed_code": "def greet(name):\n    message = \"Hello, \" + name + \"!\"\n    return message\n"}'
```

### 4. Run the Inference Script

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
export HF_TOKEN="hf_..."

python inference.py --env-url http://localhost:7860
```

---

## Docker Deployment

### Build and Run Locally

```bash
docker build -t code-debug-env .
docker run -p 7860:7860 code-debug-env
```

### Deploy to Hugging Face Spaces

```bash
pip install huggingface_hub
huggingface-cli login
# Create a new Docker Space and push
```

---

## Project Structure

```
.
├── code_debug_env/
│   ├── __init__.py            # Package exports
│   ├── models.py              # Action, Observation, State types
│   ├── client.py              # HTTP client for the environment
│   ├── openenv.yaml           # OpenEnv manifest
│   ├── pyproject.toml         # Package metadata
│   └── server/
│       ├── __init__.py
│       ├── app.py             # FastAPI application
│       ├── environment.py     # Core environment logic + grader
│       ├── tasks.py           # Task definitions (6 tasks)
│       └── requirements.txt   # Server dependencies
├── inference.py               # Baseline LLM inference script
├── Dockerfile                 # HF Spaces container
├── requirements.txt           # Project dependencies
├── .dockerignore
└── README.md                  # This file
```

---

## API Endpoints

| Method | Path      | Description                    |
|:-------|:----------|:-------------------------------|
| GET    | `/health` | Health check                   |
| GET    | `/tasks`  | List all available tasks       |
| POST   | `/reset`  | Reset environment to a task    |
| POST   | `/step`   | Submit fixed code for grading  |
| GET    | `/state`  | Get current environment state  |

---

## License

MIT
