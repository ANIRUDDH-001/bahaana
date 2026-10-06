import numpy as np
import pandas as pd

from bahaana.backtest import (LogisticBaseline, PersistenceBaseline, WeekdayBaseline, expanding_predictions,
                              summarize)
from bahaana.features import build_features
from bahaana.synthetic import make_person
from tests.conftest import FakeModel


def test_persistence_and_weekday_rates_are_smoothed():
    X = pd.DataFrame({"active_yday": [1, 1, 0, 0, np.nan], "weekday": [0, 0, 1, 1, 1]})
    y = pd.Series([1, 1, 0, 1, 0])
    p = PersistenceBaseline().fit(X, y).predict_proba(pd.DataFrame({"active_yday": [1, 0, np.nan], "weekday": [0, 1, 2]}))
    assert np.allclose(p, [3 / 4, 2 / 4, 4 / 7])
    w = WeekdayBaseline().fit(X, y).predict_proba(pd.DataFrame({"active_yday": [0, 0], "weekday": [0, 6]}))
    assert np.allclose(w, [3 / 4, 1 / 2])


def test_expanding_window_never_trains_on_the_future():
    days = make_person("weekend_walker", n_days=120, seed=2)
    X, y = build_features(days)
    seen = []

    class Spy(FakeModel):
        def fit(self, Xt, yt):
            seen.append(Xt.index.max())
            return self

    preds = expanding_predictions(X, y, {"spy": Spy}, min_train=42)
    assert len(preds) > 30
    assert all(m < p for m, p in zip(seen, preds["pos"]))


def test_summary_has_metrics_and_paired_difference():
    days = make_person("weekend_walker", n_days=200, seed=3)
    X, y = build_features(days)
    preds = expanding_predictions(X, y, {"Logistic regression": LogisticBaseline,
                                         "Weekday base rate": WeekdayBaseline}, min_train=42)
    s = summarize(preds, ["Logistic regression", "Weekday base rate"], n_boot=100)
    m = s["models"]["Weekday base rate"]
    assert {"auc", "brier", "f1", "auc_ci", "brier_ci"} <= set(m)
    assert m["auc"] > 0.65  # weekday-only ceiling is ~0.74 at these label rates (65% off-day vs 16% workday)
    assert "calibration" in s and s["n_predictions"] == len(preds)
