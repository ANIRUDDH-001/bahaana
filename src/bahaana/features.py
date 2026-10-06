"""The 13 morning-of features (spec §5.4). Row t uses only steps up to t-1 and the forecast for t."""
from __future__ import annotations

import numpy as np
import pandas as pd

from bahaana.schema import (FEATURES, MISSING_STEPS_BELOW, RAW_DAY_FIELDS, STREAK_CAP, TARGET_MIN_VALID,
                            TARGET_WINDOW, WEATHER_FIELDS)
from bahaana.target import active_labels


def clean_steps(steps: pd.Series) -> pd.Series:
    s = pd.to_numeric(steps, errors="coerce").astype(float)
    return s.where(s >= MISSING_STEPS_BELOW)


def _streak(labels: pd.Series) -> pd.Series:
    out, run = [], 0
    for v in labels:
        run = min(run + 1, STREAK_CAP) if v == 1 else 0
        out.append(run)
    return pd.Series(out, index=labels.index, dtype=float)


def build_features(days: pd.DataFrame, target_window: int = TARGET_WINDOW) -> tuple[pd.DataFrame, pd.Series]:
    d = days.reset_index(drop=True)
    steps = clean_steps(d["steps"])
    y = active_labels(steps, window=target_window)
    prev = steps.shift(1)
    median = prev.rolling(TARGET_WINDOW, min_periods=TARGET_MIN_VALID).median()
    weekday = pd.to_numeric(d["weekday"]).astype(int)
    holiday = pd.to_numeric(d["holiday"]).fillna(0).astype(int)

    X = pd.DataFrame(index=d.index)
    X["steps_yday_rel"] = prev / median
    X["mean3_rel"] = prev.rolling(3, min_periods=1).mean() / median
    X["mean7_rel"] = prev.rolling(7, min_periods=3).mean() / median
    X["active_yday"] = y.shift(1)
    X["streak"] = _streak(y).shift(1)
    X["weekday"] = weekday
    X["off_day"] = ((weekday >= 5) | (holiday == 1)).astype(int)
    for col in WEATHER_FIELDS:
        X[col] = pd.to_numeric(d[col], errors="coerce").astype(float)
    X["pm25_yday"] = pd.to_numeric(d["pm25"], errors="coerce").astype(float).shift(1)
    return X[FEATURES], y


def today_features(days: pd.DataFrame, today: dict) -> pd.DataFrame:
    row = {k: np.nan for k in RAW_DAY_FIELDS}
    row.update({k: (np.nan if v is None else v) for k, v in today.items()})
    row["steps"], row["pm25"] = np.nan, np.nan
    extended = pd.concat([days.reset_index(drop=True)[RAW_DAY_FIELDS], pd.DataFrame([row])[RAW_DAY_FIELDS]],
                         ignore_index=True)
    X, _ = build_features(extended)
    return X.iloc[[-1]].reset_index(drop=True)
