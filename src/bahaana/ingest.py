"""Google Fit Takeout / simple CSV reader. Reads ONLY date/start-time and step columns (spec §11)."""
from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from bahaana.schema import MISSING_STEPS_BELOW

RECENT_DAYS = 90
DAILY_NAME = "daily activity metrics.csv"
DAY_FILE = re.compile(r"(\d{4}-\d{2}-\d{2})\.csv$")


@dataclass
class StepsData:
    daily: dict[str, float]
    per_day_hours: dict[str, list[float]] = field(default_factory=dict)


def _columns(header: list[str]) -> tuple[int, int]:
    low = [h.strip().lower() for h in header]
    date_col = next(i for i, h in enumerate(low) if h in ("date", "start time"))
    step_col = next(i for i, h in enumerate(low) if h in ("step count", "steps"))
    return date_col, step_col


def parse_daily_csv(text: str) -> dict[str, float]:
    rows = list(csv.reader(io.StringIO(text)))
    d, s = _columns(rows[0])
    out: dict[str, float] = {}
    for r in rows[1:]:
        if len(r) > max(d, s) and r[s].strip():
            out[r[d].strip()] = out.get(r[d].strip(), 0.0) + float(r[s])
    return out


def parse_hours_csv(text: str) -> list[float]:
    rows = list(csv.reader(io.StringIO(text)))
    t, s = _columns(rows[0])
    hours = [0.0] * 24
    for r in rows[1:]:
        if len(r) > max(t, s) and r[s].strip():
            hours[int(r[t][:2])] += float(r[s])
    return hours


def _from_files(files: dict[str, str]) -> StepsData:
    """files maps a path (any separator) to its text."""
    daily_key = next((k for k in files if k.replace("\\", "/").split("/")[-1].lower() == DAILY_NAME), None)
    if daily_key is None:
        raise ValueError("No 'Daily activity metrics.csv' found. Export Google Fit with Google Takeout.")
    hours = {}
    for k, text in files.items():
        m = DAY_FILE.search(k.replace("\\", "/"))
        if m:
            hours[m.group(1)] = parse_hours_csv(text)
    return StepsData(parse_daily_csv(files[daily_key]), hours)


def read_export(path: Path) -> StepsData:
    path = Path(path)
    if path.is_dir():
        files = {str(p): p.read_text(encoding="utf-8") for p in path.rglob("*.csv")
                 if p.name.lower() == DAILY_NAME or DAY_FILE.search(p.name)}
        return _from_files(files)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(DAILY_NAME) or DAY_FILE.search(n)]
            return _from_files({n: zf.read(n).decode("utf-8") for n in names})
    return StepsData(parse_daily_csv(path.read_text(encoding="utf-8")))


def hourly_profile(per_day_hours: dict[str, list[float]], daily: dict[str, float],
                   recent_days: int = RECENT_DAYS) -> list[float] | None:
    """Hourly share of steps on your bigger days (top 30%) within the last `recent_days` days.
    Recent only: activity drifts (Jan median ~10.4k, Sep ~7.1k), so a whole-year cut would describe January."""
    if not daily:
        return None
    start = (date.fromisoformat(max(daily)) - timedelta(days=recent_days - 1)).isoformat()
    recent = {d: v for d, v in daily.items() if d >= start}
    valid = [v for v in recent.values() if v >= MISSING_STEPS_BELOW]
    if not valid:
        return None
    cut = float(np.percentile(valid, 70))
    shares = [np.array(h) / sum(h) for d, h in per_day_hours.items()
              if recent.get(d, 0) >= max(cut, MISSING_STEPS_BELOW) and sum(h) > 0]
    if len(shares) < 10:
        return None
    return [float(x) for x in np.mean(shares, axis=0)]
