import subprocess

"""
===============================================================================

    Git Ops: All git operations

===============================================================================
"""

def get_git_diff() -> str:
    diff = subprocess.check_output(
            ["git", "diff", "--cached"]
            ).decode("utf-8")
    
    if not diff.strip():
        raise SystemExit("No staged changes.")
    return diff
