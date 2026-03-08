import os
import ast
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CodebaseAnalyzer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.index = {}

    def analyze(self) -> Dict[str, Any]:
        logger.info(f"Analyzing codebase at: {self.root_dir}")
        summary = {
            "total_files": 0,
            "modules": [],
            "structure": {}
        }
        
        for root, _, files in os.walk(self.root_dir):
            if any(x in root for x in [".git", "__pycache__", "node_modules", ".venv"]):
                continue
                
            for file in files:
                if file.endswith(".py"):
                    summary["total_files"] += 1
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.root_dir)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read())
                            
                        module_info = {
                            "file": str(rel_path),
                            "classes": [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                            "functions": [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                        }
                        summary["modules"].append(module_info)
                    except Exception as e:
                        logger.warning(f"Could not parse {file}: {e}")
                        
        return summary

    def get_file_summary(self, rel_path: str) -> str:
        abs_path = self.root_dir / rel_path
        if not abs_path.exists():
            return "File not found."
            
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
                                                                 
                lines = content.splitlines()
                summary = f"File: {rel_path}\n"
                summary += "\n".join(lines[:30]) + "\n... [TRUNCATED]"
                return summary
        except:
            return "Error reading file."
