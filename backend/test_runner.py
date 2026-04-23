import os
import re
from code_runner import run_code


def normalize_output(text: str) -> str:
    if text is None:
        return ""

    text = text.strip()

    # collapse repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def outputs_match(expected: str, actual: str) -> bool:
    expected_norm = normalize_output(expected)
    actual_norm = normalize_output(actual)

    # exact normalized match
    if expected_norm == actual_norm:
        return True

    # case-insensitive match
    if expected_norm.lower() == actual_norm.lower():
        return True

    # numeric equivalence: 5 == 5.0
    try:
        if float(expected_norm) == float(actual_norm):
            return True
    except Exception:
        pass

    return False


def run_tests(file_path, tests):
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File {file_path} does not exist"}

    try:
        with open(file_path, "r") as f:
            code = f.read()
    except Exception as exc:
        return {"status": "error", "error": f"Could not read file: {exc}"}

    results = []

    for test in tests:
        input_data = test.get("input", "")
        expected = test.get("expected", "")

        execution = run_code(code, input_data)

        raw_output = execution.get("output", "")
        error = execution.get("error", "").strip()

        output = raw_output.strip()
        display_output = output if output else "(no output)"

        passed = (expected == "") or outputs_match(expected, output)

        result = {
            "input": input_data,
            "expected": expected,
            "output": display_output,
            "passed": passed,
        }

        if error:
            result["error"] = error

        results.append(result)

    overall_correct = all(r.get("passed", False) for r in results)

    return {
        "status": "completed",
        "correct": overall_correct,
        "results": results
    }
