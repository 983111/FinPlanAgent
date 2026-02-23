# FinPlanAgent

FinPlanAgent is a Python toolkit for parsing transaction data, categorizing spending, analyzing patterns, optimizing monthly budgets, and generating plain-language financial insights.

## What the project does

- Parse and normalize bank transactions from CSV-style data.
- Categorize transactions with a rule-based analyzer.
- Detect spending anomalies and recurring payments.
- Build user spending profiles and scenario analyses.
- Optimize category-level budget allocations with constraints.
- Generate explainable summaries from computed financial signals.

Core package modules live in `src/`.

## Repository layout

- `main.py` – entrypoint/demo workflow.
- `config.yaml` – runtime/model/config defaults.
- `requirements.txt` – Python dependencies.
- `src/`
  - `parser.py` – transaction parsing and normalization.
  - `analyzer.py` – categorization, pattern analysis, anomaly/recurring detection.
  - `optimizer.py` – constrained budget optimization and fallback planning.
  - `profile_builder.py` – profile assembly from analyzed data.
  - `simulator.py` – what-if scenario simulation.
  - `explainer.py` – human-readable plan explanations.
  - `agent.py` – orchestration layer.
  - `utils.py` – shared helpers.
- `tests/` – unit tests.
- `data/sample_transactions.csv` – sample dataset.
- `notebooks/demo.ipynb` – notebook walkthrough.

## Setup

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

## Running the project

Run the main script:

```bash
python main.py
```

Depending on your local config and data path, you may also run modules directly for experimentation.

## Testing

Run the full test suite:

```bash
pytest -q
```

## Recent behavior fixes

The latest code includes the following fixes:

1. **Categorization over-match fix**
   - Removed a too-generic shopping keyword (`"store"`) so generic descriptions like `"random store"` are no longer incorrectly forced into `shopping`.

2. **Anomaly detection stability fix**
   - `detect_anomalies` now initializes `is_anomaly` as a DataFrame column before category loops and safely fills null values, preventing `AttributeError` from boolean fallback behavior.

3. **Optimizer solver compatibility fix**
   - Optimization now calls `problem.solve()` without hardcoding ECOS, allowing CVXPY to select an available installed solver.

4. **Fallback budget constraint fix**
   - Fallback allocation logic now:
     - initializes allocations for all constrained categories,
     - clamps values to per-category min/max bounds,
     - scales toward target budget,
     - and redistributes residuals while respecting bounds.

## Notes on model/config

Your requested model configuration is not changed by documentation updates in this commit. Runtime/model settings remain controlled by project code/config (for example `config.yaml`).
