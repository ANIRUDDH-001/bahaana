"""Excuse Court (spec §6.2-6.3): today is the case, history is the precedent."""
from __future__ import annotations

import numpy as np
import pandas as pd

from bahaana.bootstrap import block_resamples
from bahaana.schema import EXCUSES, FEATURES

RAIN_MM = 2.5
PM25_LIMIT = 60.0
TIRED_REL = 1.5
HEAT_QUANTILE = 0.75
MIN_PRESENT = 8
UPHOLD_PTS = -10.0
OVERRULE_PTS = -5.0
CI_METHOD = "7-day block bootstrap"

_COLUMNS = {
    "heat": ["feels_max"], "rain": ["rain_mm"], "air": ["pm25_yday"],
    "workday": ["off_day"], "tired": ["steps_yday_rel", "active_yday"],
}


def _known(X: pd.DataFrame, excuse: str) -> pd.Series:
    return X[_COLUMNS[excuse]].notna().all(axis=1)


def presence(X: pd.DataFrame, excuse: str, ref: pd.DataFrame) -> pd.Series:
    if excuse == "heat":
        return X["feels_max"] >= ref["feels_max"].quantile(HEAT_QUANTILE)
    if excuse == "rain":
        return X["rain_mm"] >= RAIN_MM
    if excuse == "air":
        return X["pm25_yday"] >= PM25_LIMIT
    if excuse == "workday":
        return X["off_day"] == 0
    if excuse == "tired":
        return (X["steps_yday_rel"] >= TIRED_REL) & (X["active_yday"] == 1)
    raise KeyError(excuse)


def settings(excuse: str, X_hist: pd.DataFrame) -> tuple[list[dict], list[dict]] | None:
    known = _known(X_hist, excuse)
    pres = presence(X_hist, excuse, X_hist) & known
    absn = known & ~pres
    if not pres.any() or not absn.any():
        return None
    P, A = X_hist[pres], X_hist[absn]
    if excuse == "heat":
        return [{"feels_max": float(P["feels_max"].median())}], [{"feels_max": float(A["feels_max"].median())}]
    if excuse == "rain":
        return ([{"rain_mm": float(P["rain_mm"].median()), "rain_hours": float(P["rain_hours"].median())}],
                [{"rain_mm": 0.0, "rain_hours": 0.0}])
    if excuse == "air":
        return [{"pm25_yday": float(P["pm25_yday"].median())}], [{"pm25_yday": float(A["pm25_yday"].median())}]
    if excuse == "workday":
        return ([{"weekday": d, "off_day": 0} for d in range(5)],
                [{"weekday": d, "off_day": 1} for d in (5, 6)])
    return ([{"steps_yday_rel": float(P["steps_yday_rel"].median()), "active_yday": 1.0}],
            [{"steps_yday_rel": 1.0}])


def evidence(X_hist: pd.DataFrame, y_hist: pd.Series, excuse: str, n_boot: int = 1000) -> dict:
    """X_hist/y_hist are the full calendar (one row per day, y NaN when unlabelled), so blocks are calendar weeks."""
    y = y_hist.to_numpy(dtype=float)
    known = (_known(X_hist, excuse) & y_hist.notna()).to_numpy()
    pres = presence(X_hist, excuse, X_hist).to_numpy()
    g1, g0 = known & pres, known & ~pres
    out = {"n_present": int(g1.sum()), "k_present": int(y[g1].sum()),
           "n_absent": int(g0.sum()), "k_absent": int(y[g0].sum()), "diff_ci": None, "ci_method": CI_METHOD}
    if out["n_present"] and out["n_absent"]:
        diffs = []
        for idx in block_resamples(len(y), n_boot=n_boot):
            a, b = g1[idx], g0[idx]
            if a.any() and b.any():
                diffs.append(y[idx][a].mean() - y[idx][b].mean())
        if diffs:
            out["diff_ci"] = [round(float(np.percentile(diffs, 2.5)), 4), round(float(np.percentile(diffs, 97.5)), 4)]
    return out


def decide(n_present: int, sensitivity_pts: float | None, raw_diff_pts: float | None, diff_ci) -> str:
    if n_present < MIN_PRESENT or sensitivity_pts is None or raw_diff_pts is None:
        return "UNCLEAR"
    if sensitivity_pts <= UPHOLD_PTS and diff_ci is not None and diff_ci[1] < 0:
        return "UPHELD"
    if sensitivity_pts > OVERRULE_PTS and raw_diff_pts > OVERRULE_PTS:
        return "OVERRULED"
    return "UNCLEAR"


def _order(verdicts: list[dict]) -> list[dict]:
    def key(v: dict):
        s = v["sensitivity_pts"]
        return (not v["present_today"], not v["claimed"], float("inf") if s is None else s)
    return sorted(verdicts, key=key)


def judge(model, X_hist: pd.DataFrame, y_hist: pd.Series, X_today: pd.DataFrame,
          claimed: str | None = None, n_boot: int = 1000) -> list[dict]:
    base = X_today.iloc[0].to_dict()
    rows: list[dict] = []
    slots: dict[str, tuple[int, int, int]] = {}
    for excuse in EXCUSES:
        s = settings(excuse, X_hist)
        if s is None:
            continue
        start = len(rows)
        rows += [{**base, **a} for a in s[0]]
        mid = len(rows)
        rows += [{**base, **a} for a in s[1]]
        slots[excuse] = (start, mid, len(rows))
    probs = model.predict_proba(pd.DataFrame(rows, columns=FEATURES)) if rows else np.array([])

    out = []
    for excuse in EXCUSES:
        sens = None
        if excuse in slots:
            a, m, b = slots[excuse]
            sens = round(100 * float(probs[a:m].mean() - probs[m:b].mean()), 1)
        ev = evidence(X_hist, y_hist, excuse, n_boot=n_boot)
        raw = None
        if ev["n_present"] and ev["n_absent"]:
            raw = 100 * (ev["k_present"] / ev["n_present"] - ev["k_absent"] / ev["n_absent"])
        out.append({
            "excuse": excuse,
            "verdict": decide(ev["n_present"], sens, raw, ev["diff_ci"]),
            "present_today": bool(presence(X_today, excuse, X_hist).iloc[0]),
            "claimed": excuse == claimed,
            "sensitivity_pts": sens,
            "evidence": ev,
        })
    return _order(out)
