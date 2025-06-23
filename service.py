from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

@app.post("/run-script")
def run_script():
    script_path = os.path.abspath("0_Start.py")
    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True, text=True, check=True
        )
        return {"status": "ok", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "stdout": e.stdout, "stderr": e.stderr}
