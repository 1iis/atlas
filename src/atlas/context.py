import json
from pathlib import Path

from .cards import card_markdown, repo_card
from .git import git_markdown
from .github import github_markdown
from .tree import repo_tree


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def fenced_file(path: Path, root: Path, lang: str | None = None, max_chars: int = 80_000) -> str:
    rel = path.relative_to(root)
    text = read_text(path)

    truncated = ""
    if len(text) > max_chars:
        text = text[:max_chars]
        truncated = f"\n\n<!-- truncated at {max_chars} chars -->"

    tag = lang or path.suffix.lstrip(".") or "text"
    fence = "`" * max(4, max_backtick_run(text) + 1)

    return f"## FILE: {rel}\n\n{fence}{tag}\n{text}{truncated}\n{fence}\n"


def max_backtick_run(text: str) -> int:
    max_run = current = 0
    for ch in text:
        if ch == "`":
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run


def key_source_files(repo: Path) -> list[Path]:
    candidates = [
        repo / "README.md",
        repo / repo.name / "__init__.py",
        repo / "__init__.py",
        repo / repo.name / "core.py",
        repo / "core.py",
        repo / repo.name / "_modidx.py",
        repo / "_modidx.py",
    ]

    seen: set[Path] = set()
    files: list[Path] = []

    for p in candidates:
        if p.exists() and p not in seen:
            seen.add(p)
            files.append(p)

    return files


def build_context(repo: str | Path, fallback_owner: str | None = "AnswerDotAI") -> str:
    repo = Path(repo).resolve()

    card = repo_card(repo)
    card_json = json.dumps(card, indent=2, default=str)
    tree_md = repo_tree(repo)
    git_md = git_markdown(repo)
    github_md = github_markdown(repo, fallback_owner=fallback_owner)

    file_blocks = []
    for p in key_source_files(repo):
        if p.name.lower() == "readme.md":
            file_blocks.append(fenced_file(p, repo, lang="markdown"))
        else:
            file_blocks.append(fenced_file(p, repo))

    return f"""# Atlas Context: {repo.name}

## Automated Card

```json
{card_json}
```

## Tree

{tree_md}

## Git

````markdown
{git_md}
````

## GitHub

````markdown
{github_md}
````

# Key Files

{chr(10).join(file_blocks)}
"""


def write_context(repo: str | Path, fallback_owner: str | None = "AnswerDotAI") -> dict[str, Path]:
    repo = Path(repo).resolve()
    out = repo / "atlas"
    out.mkdir(exist_ok=True)

    card = repo_card(repo)
    paths = {
        "card_json": out / "card.json",
        "card_md": out / "card.md",
        "tree": out / "tree.md",
        "git": out / "git.md",
        "github": out / "github.md",
        "context": out / "context.md",
    }

    paths["card_json"].write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    paths["card_md"].write_text(card_markdown(card), encoding="utf-8")
    paths["tree"].write_text(repo_tree(repo), encoding="utf-8")
    paths["git"].write_text(git_markdown(repo), encoding="utf-8")
    paths["github"].write_text(github_markdown(repo, fallback_owner=fallback_owner), encoding="utf-8")
    paths["context"].write_text(build_context(repo, fallback_owner=fallback_owner), encoding="utf-8")

    return paths
