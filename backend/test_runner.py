import subprocess
import os

TIMEOUT = 3


def run_tests(file_path, tests):
    try:
        executable = file_path.replace(".c", "")

        # Compile
        compile_proc = subprocess.run(
            ["gcc", file_path, "-o", executable],
            capture_output=True,
            text=True
        )

        if compile_proc.returncode != 0:
            return {
                "status": "compile_error",
                "error": compile_proc.stderr
            }

        results = []

        for test in tests:
            try:
                run_proc = subprocess.run(
                    [executable],
                    input=test.get("input", ""),
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT
                )

                output = run_proc.stdout.strip()

                results.append({
                    "input": test.get("input", ""),
                    "expected": test.get("expected", ""),
                    "output": output,
                    "passed": output == test.get("expected", "")
                })

            except subprocess.TimeoutExpired:
                results.append({
                    "input": test.get("input", ""),
                    "error": "Timeout"
                })

        return {
            "status": "completed",
            "results": results
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
