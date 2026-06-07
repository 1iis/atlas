# Atlas

> Atlas is a system for mapping and understanding codebases. Its first target is repository-level orientation: producing compact, accurate, information-rich cards and views that help a human or LLM understand what a repo is, how it works, whether it is useful, and where to begin reading.





---

> [!TIP]
> ## `uv` lifecycle
> 
> ### Setup
> 
> ```bash
> # Clone repo
> gh repo clone 1iis/py
> cd atlas
> ```
> 
> - To develop it, install deps (fastship, ruff, etc.) and create `.venv/`: `uv sync` reads `.python-version` (downloads it if missing), creates `.venv/`, resolves all deps, writes `uv.lock`.
> 
>    ```bash
>    uv sync --group dev
>    ```
> 
> - To use it, install the tool globally.
>    ```bash
>    uv tool install --editable .
>    ```
>
>    Check that it works:
>    ```bash
>    cd $some_repo
>    atlas
>    # You may need to add uv's tool exec dir to your PATH
>    uv tool update-shell
>    ```
> 
> ### Run
> 
> ```bash
> uv run pytest            # run tests
> uv run ruff check src/   # lint
> uv run ruff format src/  # format
> uv run atlas […]         # run CLI
> ```
> 
> `uv run` activates the virtual environment automatically for that command.
> 
> ### Adding dependencies
> 
> ```bash
> uv add requests              # runtime dep → pyproject.toml + uv.lock
> uv add --group dev pytest    # dev dep → [dependency-groups] dev
> uv sync                      # install everything
> ```
> 
> ### Shipping (with fastship)
> 
> ```bash
> ship-bump --part 2           # bump patch: 0.0.1 → 0.0.2
> ship-pypi                    # build + upload to PyPI
> ```
> 
> These are already installed via `uv sync --group dev`. No activation needed.
> 
> ### When to `uv sync`
> 
> Run it after:
> - `git pull` (someone changed deps)
> - switching branches
> - manually editing `pyproject.toml` deps
