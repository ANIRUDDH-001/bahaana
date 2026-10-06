"""Expanding-window backtest (spec §8) with three baselines and 7-day block-bootstrap intervals."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from bahaana.bootstrap import block_resamples
from bahaana.model import TabPFNModel
from bahaana.schema import FEATURES

MIN_TRAIN = 42


def _rate(y: pd.Series) -> float:
    return (float(y.sum()) + 1) / (len(y) + 2)


class PersistenceBaseline:
    """P(active | yesterday's status), +1 smoothing."""
    name = "Same as yesterday"

    def fit(self, X, y):
        self.overall = _rate(y)
        self.rates = {v: _rate(y[X["active_yday"] == v]) for v in (0, 1)}
        return self

    def predict_proba(self, X):
        return np.array([self.rates.get(v, self.overall) if v == v else self.overall for v in X["active_yday"]])


class WeekdayBaseline:
    name = "Weekday base rate"

    def fit(self, X, y):
        self.rates = {d: _rate(y[X["weekday"] == d]) for d in range(7)}
        return self

    def predict_proba(self, X):
        return np.array([self.rates[int(d)] for d in X["weekday"]])


class LogisticBaseline:
    name = "Logistic regression"

    def fit(self, X, y):
        numeric = [c for c in FEATURES if c != "weekday"]
        pre = ColumnTransformer([
            ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric),
            ("wd", OneHotEncoder(handle_unknown="ignore"), ["weekday"]),
        ])
        self.pipe = Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=1000))]).fit(X, y.astype(int))
        return self

    def predict_proba(self, X):
        return self.pipe.predict_proba(X)[:, 1]


MODELS = {"TabPFN v2": TabPFNModel, "Same as yesterday": PersistenceBaseline,
          "Weekday base rate": WeekdayBaseline, "Logistic regression": LogisticBaseline}


def expanding_predictions(X: pd.DataFrame, y: pd.Series, factories: dict, min_train: int = MIN_TRAIN) -> pd.DataFrame:
    labelled = np.flatnonzero(y.notna().to_numpy())
    rows = []
    for j in range(min_train, len(labelled)):
        train, test = labelled[:j], labelled[j]
        y_train = y.iloc[train]
        if y_train.nunique() < 2:
            continue
        rec = {"pos": int(test), "y": int(y.iloc[test])}
        for name, factory in factories.items():
            rec[name] = float(factory().fit(X.iloc[train], y_train).predict_proba(X.iloc[[test]])[0])
        rows.append(rec)
    return pd.DataFrame(rows)


def _metrics(y: np.ndarray, p: np.ndarray) -> dict:
    out = {"brier": float(brier_score_loss(y, p)), "f1": float(f1_score(y, p >= 0.5, zero_division=0))}
    out["auc"] = float(roc_auc_score(y, p)) if len(set(y)) == 2 else float("nan")
    return out


def _ci(values: list[float]) -> list[float]:
    v = [x for x in values if x == x]
    return [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)] if v else [None, None]


def calibration(y: np.ndarray, p: np.ndarray, bins: int = 5) -> list[dict]:
    edges = np.linspace(0, 1, bins + 1)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        out.append({"lo": round(lo, 2), "hi": round(hi, 2), "n": int(m.sum()),
                    "mean_p": round(float(p[m].mean()), 3) if m.any() else None,
                    "rate": round(float(y[m].mean()), 3) if m.any() else None})
    return out


def summarize(preds: pd.DataFrame, names: list[str], n_boot: int = 1000) -> dict:
    y = preds["y"].to_numpy()
    boots = list(block_resamples(preds["pos"].to_numpy(), n_boot=n_boot))  # calendar weeks, not 7 predictions
    models = {}
    for name in names:
        p = preds[name].to_numpy()
        point = _metrics(y, p)
        samples = [_metrics(y[i], p[i]) for i in boots]
        models[name] = {**{k: round(v, 4) for k, v in point.items()},
                        **{f"{k}_ci": _ci([s[k] for s in samples]) for k in ("auc", "brier", "f1")}}
    summary = {"n_predictions": int(len(preds)), "prevalence": round(float(y.mean()), 4), "models": models,
               "ci_method": "7-day block bootstrap", "n_boot": n_boot}
    if "TabPFN v2" in names and "Logistic regression" in names:
        a, b = preds["TabPFN v2"].to_numpy(), preds["Logistic regression"].to_numpy()
        diffs = [_metrics(y[i], a[i])["auc"] - _metrics(y[i], b[i])["auc"] for i in boots]
        summary["auc_diff_tabpfn_minus_logistic"] = {
            "point": round(models["TabPFN v2"]["auc"] - models["Logistic regression"]["auc"], 4), "ci": _ci(diffs)}
    lead = "TabPFN v2" if "TabPFN v2" in names else names[0]
    summary["calibration"] = calibration(y, preds[lead].to_numpy())
    return summary


def write_report(summary: dict, out_dir: Path, tag: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"backtest_{tag}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [f"# Backtest ({tag})", "",
             f"{summary['n_predictions']} out-of-sample days; observed active share {summary['prevalence']:.1%}. "
             f"95% intervals: {summary['ci_method']}, {summary['n_boot']} resamples.", "",
             "| Model | ROC-AUC | Brier | F1 @0.5 |", "|---|---|---|---|"]
    for name, m in summary["models"].items():
        lines.append(f"| {name} | {m['auc']:.3f} [{m['auc_ci'][0]}, {m['auc_ci'][1]}] | "
                     f"{m['brier']:.3f} [{m['brier_ci'][0]}, {m['brier_ci'][1]}] | "
                     f"{m['f1']:.3f} [{m['f1_ci'][0]}, {m['f1_ci'][1]}] |")
    if "auc_diff_tabpfn_minus_logistic" in summary:
        d = summary["auc_diff_tabpfn_minus_logistic"]
        lines += ["", f"TabPFN − logistic ROC-AUC: {d['point']:+.3f} (95% {d['ci']}, paired blocks)."]
    lines += ["", "| Predicted | n | mean predicted | observed |", "|---|---|---|---|"]
    lines += [f"| {c['lo']:.1f}–{c['hi']:.1f} | {c['n']} | {c['mean_p']} | {c['rate']} |" for c in summary["calibration"]]
    (out_dir / f"backtest_{tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
