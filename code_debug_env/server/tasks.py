"""
Task definitions for the Code Debug Environment.

Each task provides buggy Python code that an AI agent must fix.
Tasks span three difficulty levels: easy, medium, hard.
"""

TASKS = {
    # ------------------------------------------------------------------ EASY
    "fix_greeting": {
        "task_id": "fix_greeting",
        "difficulty": "easy",
        "description": (
            "Fix the `greet` function so it returns a greeting string "
            "in the form 'Hello, <name>!'. The current code has syntax errors."
        ),
        "buggy_code": (
            "def greet(name)\n"
            '    message = "Hello, " + name + "!\n'
            "    return message\n"
        ),
        "function_name": "greet",
        "test_cases": [
            {"args": ["Alice"], "expected": "Hello, Alice!"},
            {"args": ["Bob"], "expected": "Hello, Bob!"},
            {"args": [""], "expected": "Hello, !"},
        ],
        "test_descriptions": [
            'greet("Alice") should return "Hello, Alice!"',
            'greet("Bob") should return "Hello, Bob!"',
            'greet("") should return "Hello, !"',
        ],
        "max_attempts": 3,
    },
    "fix_calculator": {
        "task_id": "fix_calculator",
        "difficulty": "easy",
        "description": (
            "Fix the `calculate_average` function so it returns the "
            "arithmetic mean of a list of numbers. Return 0 for an empty list. "
            "The current code has an assignment-vs-comparison bug and an "
            "arithmetic error."
        ),
        "buggy_code": (
            "def calculate_average(numbers):\n"
            "    if len(numbers) = 0:\n"
            "        return 0\n"
            "    total = sum(numbers)\n"
            "    return total / len(numbers) + 1\n"
        ),
        "function_name": "calculate_average",
        "test_cases": [
            {"args": [[1, 2, 3]], "expected": 2.0},
            {"args": [[10]], "expected": 10.0},
            {"args": [[]], "expected": 0},
            {"args": [[4, 8]], "expected": 6.0},
        ],
        "test_descriptions": [
            "calculate_average([1, 2, 3]) should return 2.0",
            "calculate_average([10]) should return 10.0",
            "calculate_average([]) should return 0",
            "calculate_average([4, 8]) should return 6.0",
        ],
        "max_attempts": 3,
    },
    # --------------------------------------------------------------- MEDIUM
    "fix_fibonacci": {
        "task_id": "fix_fibonacci",
        "difficulty": "medium",
        "description": (
            "Fix the `fibonacci` function so it returns the n-th Fibonacci "
            "number using 0-based indexing: fib(0)=0, fib(1)=1, fib(2)=1, "
            "fib(5)=5. The code has wrong base-case values and a wrong "
            "recursive offset."
        ),
        "buggy_code": (
            "def fibonacci(n):\n"
            "    if n <= 0:\n"
            "        return 1\n"
            "    if n == 1:\n"
            "        return 1\n"
            "    return fibonacci(n - 1) + fibonacci(n - 3)\n"
        ),
        "function_name": "fibonacci",
        "test_cases": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 1},
            {"args": [5], "expected": 5},
            {"args": [10], "expected": 55},
        ],
        "test_descriptions": [
            "fibonacci(0) should return 0",
            "fibonacci(1) should return 1",
            "fibonacci(2) should return 1",
            "fibonacci(5) should return 5",
            "fibonacci(10) should return 55",
        ],
        "max_attempts": 3,
    },
    "fix_list_filter": {
        "task_id": "fix_list_filter",
        "difficulty": "medium",
        "description": (
            "Fix the `filter_even_numbers` function so it returns only the "
            "even numbers from the input list, sorted in ascending order. "
            "The code currently filters odd numbers and sorts in reverse."
        ),
        "buggy_code": (
            "def filter_even_numbers(numbers):\n"
            "    result = []\n"
            "    for num in numbers:\n"
            "        if num % 2 != 0:\n"
            "            result.append(num)\n"
            "    result.sort(reverse=True)\n"
            "    return result\n"
        ),
        "function_name": "filter_even_numbers",
        "test_cases": [
            {"args": [[1, 2, 3, 4, 5, 6]], "expected": [2, 4, 6]},
            {"args": [[1, 3, 5]], "expected": []},
            {"args": [[2, 4, 6]], "expected": [2, 4, 6]},
            {"args": [[6, 2, 8, 4]], "expected": [2, 4, 6, 8]},
        ],
        "test_descriptions": [
            "filter_even_numbers([1,2,3,4,5,6]) should return [2,4,6]",
            "filter_even_numbers([1,3,5]) should return []",
            "filter_even_numbers([2,4,6]) should return [2,4,6]",
            "filter_even_numbers([6,2,8,4]) should return [2,4,6,8]",
        ],
        "max_attempts": 3,
    },
    # ----------------------------------------------------------------- HARD
    "fix_binary_search": {
        "task_id": "fix_binary_search",
        "difficulty": "hard",
        "description": (
            "Fix the `binary_search` function so it returns the index of "
            "`target` in a sorted list `arr`, or -1 if not found. The code "
            "has multiple bugs: wrong boundary initialization, integer "
            "division issue, infinite-loop potential, and wrong branch update."
        ),
        "buggy_code": (
            "def binary_search(arr, target):\n"
            "    left = 0\n"
            "    right = len(arr)\n"
            "    while left < right:\n"
            "        mid = (left + right) / 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            left = mid\n"
            "        else:\n"
            "            right = mid + 1\n"
            "    return -1\n"
        ),
        "function_name": "binary_search",
        "test_cases": [
            {"args": [[1, 2, 3, 4, 5], 3], "expected": 2},
            {"args": [[1, 2, 3, 4, 5], 1], "expected": 0},
            {"args": [[1, 2, 3, 4, 5], 5], "expected": 4},
            {"args": [[1, 2, 3, 4, 5], 6], "expected": -1},
            {"args": [[], 1], "expected": -1},
        ],
        "test_descriptions": [
            "binary_search([1,2,3,4,5], 3) should return 2",
            "binary_search([1,2,3,4,5], 1) should return 0",
            "binary_search([1,2,3,4,5], 5) should return 4",
            "binary_search([1,2,3,4,5], 6) should return -1",
            "binary_search([], 1) should return -1",
        ],
        "max_attempts": 2,
    },
    "fix_matrix_transpose": {
        "task_id": "fix_matrix_transpose",
        "difficulty": "hard",
        "description": (
            "Fix the `matrix_transpose` function so it returns the transpose "
            "of a 2-D list (list of lists). The code has a shallow-copy bug "
            "in the result initialization and swapped indices in the "
            "assignment."
        ),
        "buggy_code": (
            "def matrix_transpose(matrix):\n"
            "    if not matrix:\n"
            "        return matrix\n"
            "    rows = len(matrix)\n"
            "    cols = len(matrix[0])\n"
            "    result = [[0] * rows] * cols\n"
            "    for i in range(rows):\n"
            "        for j in range(cols):\n"
            "            result[j][i] = matrix[j][i]\n"
            "    return result\n"
        ),
        "function_name": "matrix_transpose",
        "test_cases": [
            {"args": [[[1, 2], [3, 4]]], "expected": [[1, 3], [2, 4]]},
            {"args": [[[1, 2, 3]]], "expected": [[1], [2], [3]]},
            {"args": [[[]]], "expected": [[]]},
            {
                "args": [[[1, 2], [3, 4], [5, 6]]],
                "expected": [[1, 3, 5], [2, 4, 6]],
            },
        ],
        "test_descriptions": [
            "matrix_transpose([[1,2],[3,4]]) should return [[1,3],[2,4]]",
            "matrix_transpose([[1,2,3]]) should return [[1],[2],[3]]",
            "matrix_transpose([[]]) should return [[]]",
            "matrix_transpose([[1,2],[3,4],[5,6]]) should return [[1,3,5],[2,4,6]]",
        ],
        "max_attempts": 2,
    },
}

# Ordered list for deterministic iteration
TASK_ORDER = [
    "fix_greeting",
    "fix_calculator",
    "fix_fibonacci",
    "fix_list_filter",
    "fix_binary_search",
    "fix_matrix_transpose",
]
