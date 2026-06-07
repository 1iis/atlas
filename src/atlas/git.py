import functools
import shutil
import subprocess
from pathlib import Path


def git_available() -> bool:
    return shutil.which("git") is not None


def run_cmd(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> str | None:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


@functools.lru_cache(maxsize=None)
def git_data(path_str: str) -> dict[str, str | None]:
    path = Path(path_str)

    data: dict[str, str | None] = {
        "first_commit": None,
        "last_commit": None,
        "total_commits": None,
        "branch": None,
        "remote": None,
        "contributors": None,
    }

    if not git_available() or not (path / ".git").exists():
        return data

    data["first_commit"] = run_cmd(["git", "log", "--reverse", "--format=%cI", "-1"], cwd=path)
    data["last_commit"] = run_cmd(["git", "log", "--format=%cI", "-1"], cwd=path)
    data["total_commits"] = run_cmd(["git", "rev-list", "--count", "HEAD"], cwd=path)
    data["branch"] = run_cmd(["git", "branch", "--show-current"], cwd=path)
    data["remote"] = run_cmd(["git", "remote", "get-url", "origin"], cwd=path)
    data["contributors"] = run_cmd(["git", "shortlog", "-sn", "HEAD"], cwd=path)

    return data


def git_markdown(repo: str | Path) -> str:
    repo = Path(repo).resolve()
    data = git_data(str(repo))

    if not any(data.values()):
        return "# Git\n\nNo git metadata available.\n"

    rows = [
        f"| First commit | {data.get('first_commit') or 'unknown'} |",
        f"| Last commit | {data.get('last_commit') or 'unknown'} |",
        f"| Total commits | {data.get('total_commits') or 'unknown'} |",
        f"| Current branch | {data.get('branch') or 'unknown'} |",
        f"| Remote URL | {data.get('remote') or 'none'} |",
    ]

    md = "# Git\n\n| Attribute | Value |\n|-----------|-------|\n"
    md += "\n".join(rows) + "\n"

    contrib = data.get("contributors")
    if contrib:
        md += "\n## Top contributors\n\n| Contributor | Commits |\n|-------------|---------|\n"
        for line in contrib.splitlines()[:10]:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                count, name = parts
                md += f"| {name} | {count} |\n"

    return md
