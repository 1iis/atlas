import json
import shutil
import subprocess
from pathlib import Path

from .git import git_data


def gh_available() -> bool:
    return shutil.which("gh") is not None


def run_cmd(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> str | None:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def owner_repo_from_remote(remote: str | None) -> tuple[str, str] | None:
    if not remote or "github.com" not in remote:
        return None

    cleaned = remote.replace(":", "/").removesuffix(".git")
    parts = cleaned.split("/")

    if len(parts) >= 2:
        return parts[-2], parts[-1]

    return None


def github_data(owner: str, repo: str) -> dict[str, str | None]:
    data: dict[str, str | None] = {}

    try:
        from ghapi.all import GhApi

        api = GhApi()
        info = api.repos.get(owner, repo)

        data["description"] = info.get("description")
        data["visibility"] = "private" if info.get("private") else "public"
        data["default_branch"] = info.get("default_branch")
        data["open_issues"] = str(info.get("open_issues_count", ""))
        data["stargazers"] = str(info.get("stargazers_count", ""))
        data["archived"] = "yes" if info.get("archived") else "no"

        license_info = info.get("license")
        data["license"] = license_info.get("spdx_id") if license_info else None

        try:
            releases = api.repos.list_releases(owner, repo, per_page=1)
            data["latest_release"] = releases[0].get("tag_name") if releases else None
        except Exception:
            data["latest_release"] = None

        return data
    except Exception:
        pass

    if not gh_available():
        return data

    repo_json = run_cmd(["gh", "api", f"repos/{owner}/{repo}"])
    if not repo_json:
        return data

    try:
        info = json.loads(repo_json)
    except json.JSONDecodeError:
        return data

    data["description"] = info.get("description")
    data["visibility"] = "private" if info.get("private") else "public"
    data["default_branch"] = info.get("default_branch")
    data["open_issues"] = str(info.get("open_issues_count", ""))
    data["stargazers"] = str(info.get("stargazers_count", ""))
    data["archived"] = "yes" if info.get("archived") else "no"

    license_info = info.get("license")
    data["license"] = license_info.get("spdx_id") if license_info else None

    release_json = run_cmd(["gh", "api", f"repos/{owner}/{repo}/releases/latest"])
    if release_json:
        try:
            rel = json.loads(release_json)
            data["latest_release"] = rel.get("tag_name")
        except json.JSONDecodeError:
            data["latest_release"] = None
    else:
        data["latest_release"] = None

    return data


def github_markdown(repo: str | Path, fallback_owner: str | None = None) -> str:
    repo = Path(repo).resolve()

    remote = git_data(str(repo)).get("remote")
    owner_repo = owner_repo_from_remote(remote)

    if owner_repo is None and fallback_owner:
        owner_repo = (fallback_owner, repo.name)

    if owner_repo is None:
        return "# GitHub\n\nNo GitHub metadata available.\n"

    owner, name = owner_repo
    data = github_data(owner, name)

    if not any(data.values()):
        return "# GitHub\n\nNo GitHub metadata available.\n"

    rows = [
        f"| Description | {data.get('description') or 'none'} |",
        f"| Visibility | {data.get('visibility') or 'unknown'} |",
        f"| Default branch | {data.get('default_branch') or 'unknown'} |",
        f"| Open issues | {data.get('open_issues') or 'unknown'} |",
        f"| Stargazers | {data.get('stargazers') or 'unknown'} |",
        f"| Latest release | {data.get('latest_release') or 'none'} |",
        f"| License | {data.get('license') or 'none'} |",
        f"| Archived | {data.get('archived') or 'unknown'} |",
    ]

    return "# GitHub\n\n| Attribute | Value |\n|-----------|-------|\n" + "\n".join(rows) + "\n"
