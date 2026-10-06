"""Causal active-day label (spec §5.3): today's steps vs the 70th percentile of the valid days before it."""
from __future__ import annotations

import numpy as np
import pandas as pd

from bahaana.schema import TARGET_MIN_VALID, TARGET_PCT, TARGET_WINDOW


def rolling_threshold(steps: pd.Series, window: int = TARGET_WINDOW, min_valid: int = TARGET_MIN_VALID,
                      pct: int = TARGET_PCT) -> pd.Series:
    previous = steps.astype(float).shift(1)
    return previous.rolling(window, min_periods=min_valid).quantile(pct / 100, interpolation="linear")


def active_labels(steps: pd.Series, window: int = TARGET_WINDOW, min_valid: int = TARGET_MIN_VALID,
                  pct: int = TARGET_PCT) -> pd.Series:
    s = steps.astype(float)
    threshold = rolling_threshold(s, window, min_valid, pct)
    labels = (s >= threshold).astype(float)
    labels[threshold.isna() | s.isna()] = np.nan
    return labels
