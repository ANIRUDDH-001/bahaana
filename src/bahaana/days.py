"""Calendar helpers and the raw daily table (spec §5.2). Dates are always 'YYYY-MM-DD' strings."""
from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from bahaana.schema import RAW_DAY_FIELDS, WEATHER_FIELDS

SHARED = Path(__file__).resolve().parents[2] / "shared"


def add_days(day: str, n: int) -> str:
    return (date.fromisoformat(day) + timedelta(days=n)).isoformat()


def date_range(start: str, end: str) -> list[str]:
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    return [(d0 + timedelta(days=i)).isoformat() for i in range((d1 - d0).days + 1)]


def weekday_of(day: str) -> int:
    return date.fromisoformat(day).weekday()


@lru_cache(maxsize=1)
def load_holidays() -> frozenset[str]:
    return frozenset(json.loads((SHARED / "holidays_2026.json").read_text(encoding="utf-8"))["dates"])


def _weather_row(day: str, weather: dict[str, dict]) -> dict:
    w = weather.get(day) or {}
    return {k: (np.nan if w.get(k) is None else float(w[k])) for k in WEATHER_FIELDS}


def build_days(steps: dict[str, float], weather: dict[str, dict], pm25: dict[str, float | None],
               start: str, end: str) -> pd.DataFrame:
    holidays = load_holidays()
    rows = []
    for d in date_range(start, end):
        s, p = steps.get(d), pm25.get(d)
        rows.append({
            "date": d,
            "steps": np.nan if s is None else float(s),
            "weekday": weekday_of(d),
            "holiday": int(d in holidays),
            **_weather_row(d, weather),
            "pm25": np.nan if p is None else float(p),
        })
    return pd.DataFrame(rows, columns=["date", *RAW_DAY_FIELDS])


def today_raw(day: str, weather: dict[str, dict]) -> dict:
    w = _weather_row(day, weather)
    return {"weekday": weekday_of(day), "holiday": int(day in load_holidays()),
            **{k: (None if np.isnan(v) else v) for k, v in w.items()}}
