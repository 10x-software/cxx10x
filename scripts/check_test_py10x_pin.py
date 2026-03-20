#!/usr/bin/env python3
"""Fail CI if cxx package test py10x pins drift."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def load_test_py10x_deps(pyproject: Path) -> list[str]:
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    return (
        data.get("project", {})
        .get("optional-dependencies", {})
        .get("test-py10x", [])
    )


def main() -> int:
    core = Path("core_10x/pyproject.toml")
    infra = Path("infra_10x/pyproject.toml")

    core_deps = load_test_py10x_deps(core)
    infra_deps = load_test_py10x_deps(infra)

    if core_deps != infra_deps:
        print("test-py10x dependency pins are inconsistent.")
        print(f"{core}: {core_deps}")
        print(f"{infra}: {infra_deps}")
        return 1

    print(f"test-py10x dependency pins are consistent: {core_deps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
