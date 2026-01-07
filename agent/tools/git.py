import subprocess
from typing import Optional, Tuple


def run_git_command(command: list) -> Tuple[bool, str]:
    """Runs a git command and returns (success, output)."""
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        success = result.returncode == 0
        output = result.stdout.strip() if success else result.stderr.strip()
        return success, output
    except Exception as e:
        return False, str(e)


def is_git_repo() -> bool:
    success, _ = run_git_command(["git", "rev-parse", "--is-inside-work-tree"])
    return success


def get_current_branch() -> Optional[str]:
    success, output = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return output if success else None


def checkout(branch: str, create_if_missing: bool = False) -> Tuple[bool, str]:
    """Checks out a branch, optionally creating it."""
    if create_if_missing:
        # Check if branch exists first
        success, _ = run_git_command(
            ["git", "show-ref", "--verify", f"refs/heads/{branch}"]
        )
        if not success:
            return run_git_command(["git", "checkout", "-b", branch])

    return run_git_command(["git", "checkout", branch])


def commit(message: str) -> Tuple[bool, str]:
    """Stages all changes and commits them."""
    # Add all changes
    success, output = run_git_command(["git", "add", "."])
    if not success:
        return False, f"Failed to add files: {output}"

    # Commit
    return run_git_command(["git", "commit", "-m", message])


def push(branch: str, set_upstream: bool = True) -> Tuple[bool, str]:
    """Pushes the current branch."""
    cmd = ["git", "push"]
    if set_upstream:
        cmd.extend(["-u", "origin", branch])
    else:
        cmd.append("origin", branch)

    return run_git_command(cmd)


def create_pr(title: str, body: str, base: str = "main") -> Tuple[bool, str]:
    """Creates a PR using GitHub CLI."""
    # First ensure we are pushed
    current = get_current_branch()
    if not current:
        return False, "Could not determine current branch"

    # Check if PR already exists
    check_cmd = ["gh", "pr", "view", "--json", "url"]
    success, output = run_git_command(check_cmd)
    if success:
        return True, f"PR already exists: {output}"

    # Create PR
    cmd = [
        "gh",
        "pr",
        "create",
        "--title",
        title,
        "--body",
        body,
        "--base",
        base,
        "--head",
        current,
    ]
    return run_git_command(cmd)
