import subprocess
import logging
import sys
import os

logger = logging.getLogger(__name__)

def run_project_file(file_path: str, cwd: str = None):
    logger.info(f"Running test for: {file_path}")
    
    try:
                                              
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Test timed out: {file_path}")
        return {"success": False, "stdout": "", "stderr": "Timeout expired", "exit_code": -1}
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -2}
