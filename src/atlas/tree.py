from pathlib import Path

SKIP_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".ipynb_checkpoints",
    "build",
    "dist",
    "node_modules",
    "atlas",
}


def repo_tree(repo: str | Path, max_children: int = 30) -> str:
    repo = Path(repo).resolve()
    lines: list[str] = []

    for p in sorted(repo.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        if p.name.startswith(".") or p.name in SKIP_NAMES:
            continue

        if p.is_dir():
            lines.append(f"{p.name}/")
            if p.name == "nbs":
                continue

            try:
                children = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))[:max_children]
            except PermissionError:
                continue

            for sub in children:
                if sub.name.startswith(".") or sub.name in SKIP_NAMES:
                    continue
                if sub.is_dir():
                    lines.append(f"    {sub.name}/")
                else:
                    lines.append(f"    {sub.name} ({sub.stat().st_size // 1024}k)")
        else:
            lines.append(f"{p.name} ({p.stat().st_size // 1024}k)")

    return "# Tree\n\n```text\n" + "\n".join(lines) + "\n```\n"
