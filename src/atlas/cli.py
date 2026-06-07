import argparse
import sys
from pathlib import Path

from . import __version__
from .context import write_context


def cmd_context(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()

    if not repo.exists():
        print(f"error: repo not found: {repo}", file=sys.stderr)
        return 1

    if not repo.is_dir():
        print(f"error: repo is not a directory: {repo}", file=sys.stderr)
        return 1

    paths = write_context(repo, fallback_owner=args.fallback_owner)

    for name, path in paths.items():
        print(f"wrote {name}: {path}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlas", description="Atlas — maps for codebases")
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    sub = parser.add_subparsers(dest="command")

    p_context = sub.add_parser("context", help="Generate repo Atlas context files")
    p_context.add_argument("repo", help="Path to repository")
    p_context.add_argument("--fallback-owner", default="AnswerDotAI", help="Fallback GitHub owner if remote is unavailable")
    p_context.set_defaults(func=cmd_context)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"atlas v{__version__}")
        return 0

    if not args.command:
        print(f"atlas v{__version__}")
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
