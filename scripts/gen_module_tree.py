#!/usr/bin/env python3
# scripts/gen_module_tree.py

"""
Generate a JSON mapping from each Python module under given roots
to its full source text.
"""

import argparse
import json
from pathlib import Path
from typing import Iterator, Dict


IGNORE_DIRS: frozenset[str] = frozenset({"__pycache__", ".pytest_cache", ".git"})
IGNORE_PATTERNS: tuple[str, ...] = ("*.pyc", "*~")


def iter_python_files(root: Path) -> Iterator[Path]:
    """
    Yield all .py files under the given root, skipping ignored dirs and patterns.
    """
    for path in root.rglob("*.py"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if any(path.match(pat) for pat in IGNORE_PATTERNS):
            continue
        yield path


def read_file(path: Path) -> str:
    """
    Return the UTF-8-decoded source text of a given file.
    """
    return path.read_text(encoding="utf-8")


def build_tree(roots: list[Path], cwd: Path) -> Dict[str, str]:
    """
    Return a mapping of relative module paths to their source code.
    """
    tree: Dict[str, str] = {}
    for root in roots:
        for path in iter_python_files(root):
            rel = path.resolve().relative_to(cwd)
            tree[str(rel)] = read_file(path)
    return tree


def main() -> None:
    """
    Parse CLI arguments, generate the module tree, and write to JSON.
    """
    parser = argparse.ArgumentParser(
        description="Generate a JSON map of Python modules to source text."
    )
    parser.add_argument(
        "--roots",
        nargs="+",
        default=["src", "scripts"],
        help="Root directories to scan.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("module_tree.json"),
        help="Output file path for the module tree JSON.",
    )
    args = parser.parse_args()

    cwd = Path.cwd()
    roots = [Path(r) for r in args.roots]
    tree = build_tree(roots, cwd)

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    print(f"Module tree written to '{args.output}'")


if __name__ == "__main__":
    main()
