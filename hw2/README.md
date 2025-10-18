# Homework 1 – Moving Average Warmup

Use this starter to get familiar with the homework workflow. The notebook in this folder walks you through computing a simple moving average on a short time series and reporting the mean absolute error (MAE).

## What you need to do

1. Work inside `assignment.ipynb` and follow the instructions in the markdown cells.
2. Run every cell locally before creating a pull request. The final cell writes your metrics to `metrics.json` – do not delete it.
3. Commit both the updated notebook and the generated `metrics.json` file.
4. Open a pull request from your fork back to the course repository. The automated checks will re-run your notebook and compare your metrics with the expected values in `expected_metrics.json`.
5. If you add any extra Python dependencies, list them in `requirements.txt` inside this folder so the checker installs them.

## Tips

- Use `Restart & Run All` in Jupyter before committing so that execution order is clean.
- If the CI check fails, open the workflow logs to see which metric is outside the tolerance band.
- Leave the `expected_metrics.json` file unchanged; instructors maintain it.
