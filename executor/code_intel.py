from pathlib import Path

def summarize_repo(root: str, depth: int = 3, max_files: int = 80):
    root_path = Path(root)
    summary = []
    for path in root_path.rglob("*"):
        if len(summary) >= max_files:
            summary.append("...truncated...")
            break
        if path.is_file():
            rel = path.relative_to(root_path)
            summary.append(f"{rel} ({path.stat().st_size} bytes)")
    return summary
