import subprocess
import tempfile

def run_code(code, input_data):

    with tempfile.TemporaryDirectory() as tmpdir:

        source = f"{tmpdir}/main.c"
        binary = f"{tmpdir}/main"

        with open(source,"w") as f:
            f.write(code)

        # compile
        compile_proc = subprocess.run(
            ["gcc", source, "-o", binary],
            capture_output=True,
            text=True
        )

        if compile_proc.returncode != 0:
            return {"output":"", "error":compile_proc.stderr}

        try:
            run_proc = subprocess.run(
                [binary],
                input=str(input_data),
                capture_output=True,
                text=True,
                timeout=2
            )

            return {
                "output": run_proc.stdout.strip(),
                "error": run_proc.stderr.strip()
            }

        except subprocess.TimeoutExpired:
            return {"output":"", "error":"Timeout"}
