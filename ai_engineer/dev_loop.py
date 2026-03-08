import os
import logging
import asyncio
import subprocess
import time
import pyautogui
from pathlib import Path

from ai_engineer.project_planner import plan_project
from ai_engineer.code_generator import generate_file_content
from ai_engineer.test_runner import run_project_file
from ai_engineer.error_fixer import suggest_fix
from executor.file_manager import create_folder, write_file

logger = logging.getLogger(__name__)

                                          
PROJECTS_ROOT = Path("e:/SohanCore/sohan_ai_agent/projects")

async def build_software(prompt: str, progress_callback=None):
    try:
        if progress_callback: await progress_callback("🔍 *Phase 1: Project Architecture Planning*")

                 
        plan = await plan_project(prompt)
        project_name = plan.get("project_name", "gen_project")
        project_dir = PROJECTS_ROOT / project_name
        
                                                                       
        if project_dir.exists():
            counter = 2
            while (PROJECTS_ROOT / f"{project_name}_{counter}").exists():
                counter += 1
            project_name = f"{project_name}_{counter}"
            project_dir = PROJECTS_ROOT / project_name
            
        create_folder(str(project_dir))
        
        if progress_callback: await progress_callback(f"📂 *Project Workspace Ready:* `{project_name}`\n🖥️ Initializing VS Code Environment...")
        
                                            
        subprocess.Popen(f'code "{project_dir}"', shell=True)
        await asyncio.sleep(4)                                       

                                 
        deps = plan.get("dependencies", [])
        if deps:
            if progress_callback: await progress_callback(f"📦 *Setting up Environment:* Installing dependencies...")
            for dep in deps:
                proc = await asyncio.create_subprocess_exec(
                    os.sys.executable, "-m", "pip", "install", dep,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await proc.wait()

                                        
        files_content = {}
        project_files = plan.get("files", ["main.py"])
        
        if progress_callback: await progress_callback("✍️ *Phase 2: Generating Full Functional Logic*")

        for filename in project_files:
                                                                                
            context = "\n".join([f"Full content of previous file {fn}:\n{c}" for fn, c in files_content.items()])
            content = await generate_file_content(filename, prompt, file_context=context)
            
                                                                              
            if not content or len(content.split("\n")) < 15:
                logger.warning(f"Detection of weak code in {filename}. Forcing emergency regenerate...")
                content = await generate_file_content(filename, prompt + " (MUST BE 50+ LINES OF CODE. NO PLACEHOLDERS.)", file_context=context or "FULL CODE ONLY.")

            file_path = project_dir / filename
            write_file(str(file_path), content)
            files_content[filename] = content
            
                                     
            if os.path.getsize(file_path) < 100:
                 logger.error(f"Integrity check failed: {filename} is too small on disk.")
                                
                 content = await generate_file_content(filename, "COMPLETE CODE ONLY.", file_context=context)
                 write_file(str(file_path), content)
            
                                                                      
            if progress_callback: await progress_callback(f"📝 Developing `{filename}` with full logic...")
            pyautogui.hotkey('ctrl', 'p')
            time.sleep(0.5)
            pyautogui.typewrite(filename)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)

                                  
        main_file = "main.py" if "main.py" in files_content else project_files[0]
        max_attempts = 10                                 
        
        if progress_callback: await progress_callback("🧪 *Phase 3: Autonomous Debugging & Execution Check*")

        for attempt in range(1, max_attempts + 1):
            if progress_callback: await progress_callback(f"🚀 Execution Test (Attempt {attempt}/{max_attempts})...")
            
            result = run_project_file(str(project_dir / main_file), cwd=str(project_dir))
            
            if result["success"]:
                if progress_callback: await progress_callback(f"✨ *Project Fully Functional!* Verified stable code in VS Code.")
                                                 
                if result["stdout"]:
                    await progress_callback(f"📊 *Program Output:*\n`{result['stdout'][:200]}`")
                return {"status": "success", "dir": str(project_dir), "message": "Development complete!"}
            
                                               
            error_msg = (result["stderr"] or result["stdout"]).strip()
            if progress_callback: await progress_callback(f"⚠️ *Crash Detected:* Analyzing logic error...")
            
            current_code = files_content.get(main_file, "")
            fix_suggestion = await suggest_fix(main_file, current_code, error_msg)
            
            if fix_suggestion["action"] == "install_dependency":
                os.system(fix_suggestion["command"])
                if progress_callback: await progress_callback(f"🔧 Missing package fixed.")
            elif fix_suggestion["action"] == "modify_code":
                new_code = fix_suggestion["new_code"]
                write_file(str(project_dir / main_file), new_code)
                files_content[main_file] = new_code
                if progress_callback: await progress_callback(f"🔧 Logic fixed: {fix_suggestion.get('explanation')}")
                                                    
                from memory.experience_learning import update_experience_with_fix
                update_experience_with_fix(prompt, error_msg, [{"action": "build_software", "prompt": prompt}])
            
            await asyncio.sleep(1)

        return {"status": "success", "dir": str(project_dir), "message": "Project is ready, but might need one final manual click to start."}

    except Exception as e:
        logger.error(f"Dev Loop Error: {e}")
        if progress_callback: await progress_callback(f"❌ *Critical Failure:* {str(e)}")
        return {"status": "error", "message": f"Dev Loop Issue: {str(e)}"}
