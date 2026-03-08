
import os
import sys
import logging
import asyncio
import psutil
from pathlib import Path

                                       
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

                                                                                    
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

                                
import config
from utils.logger import setup_logger
from bot_bridge.bot_listener import run_bot

def _detect_workspace_dir():
    if getattr(sys, "frozen", False):
        root_dir = Path(sys.executable).resolve().parent
    else:
        root_dir = Path(__file__).resolve().parent
    candidates = [
        Path.cwd().resolve(),
        root_dir,
        root_dir.parent,
    ]
    for c in candidates:
        if (c / ".env").exists() or (c / "run_sohancore_background.bat").exists() or (c / "projects").exists():
            return c
    return Path.cwd().resolve()


WORKSPACE_DIR = _detect_workspace_dir()
LOG_FILE = WORKSPACE_DIR / "sohan_ai.log"
LOCK_FILE = WORKSPACE_DIR / "logs" / "sohan_ai.lock"

                          
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(config.AGENT_LOGGER_NAME)

def _other_local_instance_running() -> bool:
    current_pid = os.getpid()
    try:
        if getattr(sys, "frozen", False):
            current_exe = str(Path(sys.executable).resolve()).lower()
            for p in psutil.process_iter(["pid", "exe", "name"]):
                if p.info["pid"] == current_pid:
                    continue
                exe = (p.info.get("exe") or "").lower()
                if exe and exe == current_exe:
                    return True
        else:
            main_path = str((Path(__file__).resolve())).lower()
            for p in psutil.process_iter(["pid", "name", "cmdline"]):
                if p.info["pid"] == current_pid:
                    continue
                name = (p.info.get("name") or "").lower()
                if not name.startswith("python"):
                    continue
                cmdline = [str(x).lower() for x in (p.info.get("cmdline") or [])]
                if any(part.endswith("main.py") and main_path.endswith("main.py") for part in cmdline):
                    return True
    except Exception:
        pass
    return False

def check_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if _other_local_instance_running():
        return False
    if os.path.exists(LOCK_FILE):
        try:
                                               
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
                if psutil.pid_exists(old_pid):
                    return False
        except:
            pass
    
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True

def remove_lock():
    if os.path.exists(LOCK_FILE):
        try: os.remove(LOCK_FILE)
        except: pass

async def initialize_system():
    logger.info("==========================================")
    logger.info(f"Initializing {config.AGENT_NAME} Personal Desktop Agent")
    logger.info("==========================================")
    
                             
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("CRITICAL: TELEGRAM_BOT_TOKEN is missing in config.py!")
        return False
        
                                       
    folders = [
        "projects",                                 
        "memory",                                         
        "logs",                        
        "temp"                                            
    ]
    for folder in folders:
        (WORKSPACE_DIR / folder).mkdir(parents=True, exist_ok=True)
        
                                
    from memory.experience_learning import _load_db
    exp_count = len(_load_db())
    logger.info(f"Experience Database Loaded: {exp_count} learned records found.")

                             
    logger.info("Screen Vision and Virtual Hardware layers initialized.")

    return True

def start_sohan_ai():
    if not check_lock():
        print(f"{config.AGENT_NAME} is already running in another process.")
        return

    try:
        restart_count = 0
        max_restarts = 999999                       
        
        while restart_count < max_restarts:
            try:
                                    
                if not asyncio.run(initialize_system()):
                    logger.critical("System failed to initialize. Retrying in 10 seconds...")
                    import time
                    time.sleep(10)
                    restart_count += 1
                    continue

                                                   
                logger.info(f"{config.AGENT_NAME} is now ONLINE (Launch #{restart_count + 1})")
                logger.info("Workflow: Telegram -> Parser -> Planner -> Safety -> Executor -> Progress -> Memory")
                
                                         
                run_bot()
                
                                                       
                logger.warning("Bot listener exited. Restarting loop...")
                restart_count += 1
                import time
                time.sleep(2)

            except KeyboardInterrupt:
                logger.info(f"{config.AGENT_NAME} shutting down gracefully via user interrupt...")
                break
            except Exception as e:
                if str(e).startswith("TELEGRAM_CONFLICT:"):
                    logger.critical(
                        "Telegram conflict detected: another bot instance is polling this token. "
                        "Stop the other instance, then start SohanCore again."
                    )
                    break
                restart_count += 1
                logger.critical(f"UNEXPECTED SYSTEM CRASH (Attempt {restart_count}): {e}")
                logger.info("Restarting system in 5 seconds...")
                import time
                time.sleep(5)
    finally:
        remove_lock()

if __name__ == "__main__":
    start_sohan_ai()
