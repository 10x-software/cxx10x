#!/usr/bin/env python3
"""Validate installed cxx package versions against py10x-core requirements."""

from __future__ import annotations

import importlib.metadata as md
import sys

from packaging.requirements import Requirement

TARGET_PACKAGES = ("py10x-kernel", "py10x-infra")


def main() -> int:
    try:
        core_version = md.version("py10x-core")
    except md.PackageNotFoundError:
        print("py10x-core is not installed in the current environment.")
        return 1

    raw_requirements = md.requires("py10x-core") or []
    required_specifiers: dict[str, object] = {}

    for raw in raw_requirements:
        req = Requirement(raw)
        if req.name not in TARGET_PACKAGES:
            continue
        if req.marker is not None and not req.marker.evaluate():
            continue
        required_specifiers[req.name] = req.specifier

    print(f"Validating installed versions against py10x-core=={core_version}")

    failures: list[str] = []
    for package_name in TARGET_PACKAGES:
        try:
            installed_version = md.version(package_name)
        except md.PackageNotFoundError:
            failures.append(f"{package_name} is not installed.")
            continue

        specifier = required_specifiers.get(package_name)
        if specifier is None:
            failures.append(
                f"py10x-core does not declare a requirement for {package_name}."
            )
            continue

        if not specifier.contains(installed_version, prereleases=True):
            failures.append(
                f"{package_name}=={installed_version} does not satisfy "
                f"py10x-core requirement {package_name}{specifier}"
            )
        else:
            print(
                f"OK: {package_name}=={installed_version} satisfies "
                f"{package_name}{specifier}"
            )

    if failures:
        print("Compatibility validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("py10x-core compatibility validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
