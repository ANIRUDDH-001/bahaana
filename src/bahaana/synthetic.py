"""Synthetic people with planted behaviour (spec §6.4). Weather has a hot May-June and a Jul-Sep monsoon."""
from __future__ import annotations

import numpy as np
import pandas as pd

from bahaana.schema import FEATURES, RAW_DAY_FIELDS

P_GO = {
    "indifferent": lambda rainy, off: np.full(rainy.shape, 0.30),
    "rain_shy": lambda rainy, off: np.where(rainy, 0.05, 0.40),
    "weekend_walker": lambda rainy, off: np.where(off, 0.75, 0.10),
}


def make_person(kind: str, n_days: int = 280, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    d = np.arange(n_days)
    weekday = (3 + d) % 7  # 2026-01-01 was a Thursday
    off = weekday >= 5
    feels = 24 + 14 * np.exp(-(((d - 150) / 45) ** 2)) + rng.normal(0, 2.5, n_days)
    rainy = rng.random(n_days) < np.where((d >= 180) & (d <= 270), 0.45, 0.12)
    rain_mm = np.where(rainy, 2.5 + rng.gamma(2.0, 6.0, n_days), rng.random(n_days))
    rain_hours = np.where(rainy, rng.integers(2, 9, n_days), 0)
    pm25 = np.clip(40 + 90 * np.exp(-((d / 40) ** 2)) + rng.normal(0, 10, n_days), 5, None)
    go = rng.random(n_days) < P_GO[kind](rainy, off)
    steps = np.where(go, rng.normal(10000, 1200, n_days), rng.normal(4500, 900, n_days)).clip(300)
    return pd.DataFrame({
        "steps": steps.round(), "weekday": weekday, "holiday": 0, "feels_max": feels.round(1),
        "rain_mm": rain_mm.round(2), "rain_hours": rain_hours, "wind_max": rng.uniform(5, 20, n_days).round(1),
        "cloud_mean": np.where(rainy, rng.uniform(60, 100, n_days), rng.uniform(0, 60, n_days)).round(),
        "pm25": pm25.round(1),
    })[RAW_DAY_FIELDS]


def ordinary_todays(X_hist: pd.DataFrame, n: int = 10) -> list[pd.DataFrame]:
    """Ten ordinary weekday mornings: typical weather, no rain, a normal yesterday."""
    out = []
    for i in range(n):
        row = {
            "steps_yday_rel": 1.0, "mean3_rel": 1.0, "mean7_rel": 1.0, "active_yday": 0.0, "streak": 0.0,
            "weekday": i % 5, "off_day": 0, "feels_max": float(X_hist["feels_max"].quantile(0.3 + 0.04 * i)),
            "rain_mm": 0.0, "rain_hours": 0.0, "wind_max": float(X_hist["wind_max"].median()),
            "cloud_mean": float(X_hist["cloud_mean"].median()), "pm25_yday": float(X_hist["pm25_yday"].median()),
        }
        out.append(pd.DataFrame([row], columns=FEATURES))
    return out
