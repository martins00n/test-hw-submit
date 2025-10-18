#!/usr/bin/env python3
"""Execute homework notebooks and validate reported metrics."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import nbformat
from nbclient.client import NotebookClient
from nbclient.exceptions import CellExecutionError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run homework notebooks and compare metrics.")
    parser.add_argument(
        "--only-changed",
        action="store_true",
        help="Restrict execution to homework folders touched in the diff to the base ref.",
    )
    parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Git reference to diff against when --only-changed is set. Defaults to origin/main.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Cell execution timeout in seconds.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("artifacts"),
        help="Directory where executed notebooks will be written.",
    )
    return parser.parse_args()


def discover_homeworks(only_changed: bool, base_ref: str) -> list[Path]:
    if not only_changed:
        return sorted(path.parent for path in Path.cwd().glob("hw*/assignment.ipynb"))

    diff_target = ["git", "diff", "--name-only", f"{base_ref}..."]
    result = subprocess.run(diff_target, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print("Failed to determine changed files via git diff", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    homework_dirs: set[Path] = set()
    for line in result.stdout.splitlines():
        path = Path(line)
        if path.parts and path.parts[0].startswith("hw"):
            homework_dirs.add(Path(path.parts[0]))
    discovered = sorted(dir_path for dir_path in homework_dirs if (dir_path / "assignment.ipynb").exists())

    if len(discovered) > 1:
        joined = ", ".join(dir_path.name for dir_path in discovered)
        raise RuntimeError(
            "Pull requests must target a single homework folder. Found multiple assignments: " + joined
        )

    return discovered


def install_homework_requirements(homework_dir: Path) -> None:
    requirements_path = homework_dir / "requirements.txt"
    if not requirements_path.exists():
        return

    print(f"Installing dependencies for {homework_dir} from {requirements_path}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Dependency installation failed for {homework_dir}")


@contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def execute_notebook(nb_path: Path, timeout: int, output_dir: Path) -> None:
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name="python3")
    try:
        with working_directory(nb_path.parent):
            client.execute()
    except CellExecutionError as error:
        raise RuntimeError(f"Notebook execution failed for {nb_path}") from error

    destination = output_dir / nb_path.parent.name
    destination.mkdir(parents=True, exist_ok=True)
    executed_path = destination / nb_path.name
    nbformat.write(nb, executed_path)
    print(f"Executed {nb_path} -> {executed_path}")


def load_expected_metrics(expected_path: Path) -> dict[str, tuple[float | int, float]]:
    with expected_path.open() as handle:
        raw = json.load(handle)

    normalized: dict[str, tuple[float | int, float]] = {}
    for name, spec in raw.items():
        if isinstance(spec, dict):
            value = spec.get("value")
            tolerance = spec.get("tolerance", 0.0)
        else:
            value = spec
            tolerance = 0.0
        if value is None:
            raise ValueError(f"Expected metric '{name}' must define a value.")
        normalized[name] = (value, tolerance)
    return normalized


def compare_metrics(homework_dir: Path) -> None:
    metrics_path = homework_dir / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics file missing: {metrics_path}")

    expected_path = homework_dir / "expected_metrics.json"
    if not expected_path.exists():
        raise FileNotFoundError(f"Expected metrics file missing: {expected_path}")

    with metrics_path.open() as handle:
        reported = json.load(handle)
    expected = load_expected_metrics(expected_path)

    missing = [name for name in expected if name not in reported]
    if missing:
        raise AssertionError(f"Reported metrics missing keys: {', '.join(missing)}")

    for name, (target, tolerance) in expected.items():
        value = reported[name]
        if isinstance(value, (int, float)) and isinstance(target, (int, float)):
            if abs(value - target) > tolerance:
                raise AssertionError(
                    f"Metric '{name}' outside tolerance: got {value}, expected {target} ± {tolerance}"
                )
        else:
            if value != target:
                raise AssertionError(f"Metric '{name}' mismatch: got {value}, expected {target}")

    print(f"Metrics validated for {homework_dir}")


def main() -> None:
    args = parse_args()
    homework_dirs = discover_homeworks(args.only_changed, args.base_ref)

    if not homework_dirs:
        print("No homework notebooks found. Nothing to do.")
        return

    artifacts_dir = args.artifacts_dir
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    for hw_dir in homework_dirs:
        notebook_path = hw_dir / "assignment.ipynb"
        metrics_file = hw_dir / "metrics.json"
        if metrics_file.exists():
            metrics_file.unlink()
        try:
            install_homework_requirements(hw_dir)
            execute_notebook(notebook_path, args.timeout, artifacts_dir)
            compare_metrics(hw_dir)
        except Exception as error:  # noqa: BLE001 - we want readable aggregation here
            failures.append(f"{hw_dir}: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        sys.exit(1)

    print("All homework notebooks executed successfully.")


if __name__ == "__main__":
    main()
