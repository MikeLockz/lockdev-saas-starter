import subprocess
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def run_command(command: str) -> dict:
    """
    Runs a shell command in the 'app' directory.
    Returns: {'success': bool, 'output': str}
    """
    try:
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,  # Prevent hanging
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout + "\n" + result.stderr,
        }
    except Exception as e:
        return {"success": False, "output": str(e)}
