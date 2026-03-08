"""
tool_registry.py

Canonical list of tool metadata for reasoning/planning.
"""
TOOL_REGISTRY = [
    {"name": "run_shell", "desc": "Execute shell command", "params": ["cmd", "cwd"]},
    {"name": "execute_python", "desc": "Run a Python file", "params": ["file", "cwd"]},
    {"name": "write_file", "desc": "Write content to a file", "params": ["path", "content"]},
    {"name": "read_file", "desc": "Read file content", "params": ["path"]},
    {"name": "list_dir", "desc": "List directory", "params": ["path"]},
    {"name": "search_google", "desc": "Background web search", "params": ["query"]},
    {"name": "open_url", "desc": "Fetch page content headless", "params": ["url"]},
    {"name": "dom_action", "desc": "Playwright DOM automation", "params": ["url", "steps", "action", "selector", "text", "value"]},
    {"name": "open_app", "desc": "Launch desktop app", "params": ["target"]},
    {"name": "send_email", "desc": "Send email", "params": ["to", "subject", "body"]},
    {"name": "read_screen", "desc": "OCR the screen", "params": []},
    {"name": "take_screenshot", "desc": "Capture screenshot", "params": ["filename"]},
]

def list_tools():
    return TOOL_REGISTRY
