# Time Series Coursework Template

This repository provides a repeatable workflow for weekly time-series homeworks and projects. Each assignment ships with a README, a Jupyter notebook that students complete, and a set of expected metrics that the CI pipeline validates on every submission.

## Repository layout

- `hw*/` – one folder per assignment containing:
  - `README.md` with the student-facing brief
  - `assignment.ipynb` notebook students edit and submit
  - `expected_metrics.json` with the instructor-defined targets the CI uses for grading
  - `requirements.txt` (optional) for homework-specific Python dependencies
- `scripts/check_homeworks.py` – utility executed locally and in CI to run notebooks and compare metrics
- `.github/workflows/notebook-ci.yml` – GitHub Actions workflow that installs dependencies and invokes the checker on push/PR

## Weekly workflow

1. **Instructors** duplicate the latest `hwX` folder, update the instructions and notebook, and refresh the expected metrics once a reference solution is ready.
2. The new homework is published to students by merging into `main`.
3. **Students** fork the repository, complete the notebook, and commit both the notebook and generated `metrics.json` file.
4. Students open a pull request from their fork. The CI job re-runs the notebook and compares the reported metrics against `expected_metrics.json`.
5. If the metrics fall within tolerance, the workflow succeeds and instructors can record the grade; otherwise the logs highlight discrepancies for the student to address.

## Local checks

- Install dependencies once per machine: `pip install -r requirements.txt`
- Use `python scripts/check_homeworks.py` to execute every homework notebook locally or add `--only-changed` during active development.
- Always run "Restart & Run All" in Jupyter before committing so the CI sees a clean execution order.
- If a homework folder ships with its own `requirements.txt`, the checker installs it automatically before execution.

## Continuous integration

The GitHub Actions workflow runs on every push to `main` and every pull request targeting `main`. It performs the following steps:

- Checks out the repository with full history for accurate diffs
- Sets up Python 3.11 and installs notebook execution dependencies
- Executes either all assignment notebooks (on push) or the single assignment modified in the PR
- Validates that each notebook created a `metrics.json` file and that every expected metric is within its allowed tolerance

The workflow fails fast with descriptive messages if a notebook errors or metrics are missing or out of range.
