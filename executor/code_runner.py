import logging
import asyncio
import os
import sys
import tempfile

                   
logger = logging.getLogger(__name__)

async def run_command(cmd: str, cwd: str = None):
    logger.info(f"Executing shell command (async): {cmd} in {cwd or 'current dir'}")
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        try:
                                                 
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            
            status = "success" if process.returncode == 0 else "error"
            message = "Command executed successfully" if status == "success" else f"Command failed with exit code {process.returncode}"
            
            return {
                "status": status,
                "stdout": stdout.decode(errors='replace'),
                "stderr": stderr.decode(errors='replace'),
                "message": message
            }
        except asyncio.TimeoutExpired:
            process.kill()
            logger.error(f"Command timed out: {cmd}")
            return {"status": "error", "message": "Command timed out after 120 seconds", "stdout": "", "stderr": "Timeout"}
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {"status": "error", "message": str(e), "stdout": "", "stderr": str(e)}

async def run_python(file_path: str, cwd: str = None):
    if not os.path.exists(file_path) and not cwd:
        return {"status": "error", "message": f"File not found: {file_path}"}
    
    python_exe = sys.executable
    return await run_command(f'"{python_exe}" "{file_path}"', cwd=cwd)

async def run_python_snippet(code: str):
    logger.info("Executing Python snippet")
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tmp:
        tmp.write(code)
        tmp_path = tmp.name
        
    try:
        result = await run_python(tmp_path)
        return result
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {tmp_path}: {e}")

async def launch_command(cmd: str, cwd: str = None):
    logger.info(f"Launching command (detached): {cmd} in {cwd or 'current dir'}")
    try:
        if sys.platform == "win32":
                                                       
            full_cmd = f'start cmd /c "{cmd}"'
            import subprocess
            subprocess.Popen(full_cmd, shell=True, cwd=cwd)
        else:
                       
            import subprocess
            subprocess.Popen(f"{cmd} &", shell=True, cwd=cwd)
            
        return {
            "status": "success",
            "message": f"Launched: {cmd}. The application should be visible on the screen shortly."
        }
    except Exception as e:
        logger.error(f"Error launching command: {e}")
        return {"status": "error", "message": str(e)}
