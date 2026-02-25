import subprocess

"""
===============================================================================

    Git Ops: All git operations

===============================================================================
"""

def get_git_diff() -> str:
    diff = subprocess.check_output(["git", "diff"]).decode("utf-8")
    cached = subprocess.check_output(["git", "diff", "--cached"]).decode("utf-8")

    result = (diff + cached).strip()
    if not result:
        raise SystemExit("No staged changes.")
    return result
