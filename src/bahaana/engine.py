"""The one entry point used by the CLI, the demo builder and the API."""
from __future__ import annotations

import pandas as pd

from bahaana.features import build_features, today_features
from bahaana.model import TabPFNModel
from bahaana.schema import EXCUSES, MAX_HISTORY_ROWS, MIN_HISTORY_ROWS, MIN_LABELLED, RAW_DAY_FIELDS
from bahaana.verdicts import judge

MODEL_LABEL = "TabPFN v2 (PriorLabs)"


class EngineError(ValueError):
    """A problem with the input that the person can understand and fix."""


def run_verdict(history: list[dict], today: dict, claimed: str | None = None,
                model_factory=TabPFNModel, n_boot: int = 1000) -> dict:
    if not MIN_HISTORY_ROWS <= len(history) <= MAX_HISTORY_ROWS:
        raise EngineError(f"Bahaana needs at least {MIN_HISTORY_ROWS} and at most {MAX_HISTORY_ROWS} days of history.")
    if claimed is not None and claimed not in EXCUSES:
        raise EngineError(f"Unknown excuse '{claimed}'.")
    days = pd.DataFrame(history).reindex(columns=RAW_DAY_FIELDS)
    X, y = build_features(days)
    keep = y.notna()
    if keep.sum() < MIN_LABELLED:
        raise EngineError(f"Only {int(keep.sum())} days could be labelled; Bahaana needs at least {MIN_LABELLED}.")
    yk = y[keep].reset_index(drop=True)
    if yk.nunique() < 2:
        raise EngineError("Your history needs both active and quieter days to learn from.")
    Xk = X[keep].reset_index(drop=True)
    X_today = today_features(days, today)
    model = model_factory().fit(Xk, yk)
    return {
        "probability": round(float(model.predict_proba(X_today)[0]), 4),
        "n_context_days": int(keep.sum()),
        "verdicts": judge(model, X, y, X_today, claimed, n_boot=n_boot),  # full calendar: weekly blocks
        "model": MODEL_LABEL,
    }
