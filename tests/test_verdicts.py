import numpy as np
import pandas as pd

from bahaana.schema import FEATURES
from bahaana.verdicts import decide, evidence, judge, presence, settings


def hist(n=140, seed=0):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame({
        "steps_yday_rel": rng.uniform(0.5, 2.0, n), "mean3_rel": 1.0, "mean7_rel": 1.0,
        "active_yday": rng.integers(0, 2, n).astype(float), "streak": 0.0,
        "weekday": np.arange(n) % 7, "off_day": (np.arange(n) % 7 >= 5).astype(int),
        "feels_max": rng.uniform(20, 42, n), "rain_mm": np.where(np.arange(n) % 5 == 0, 6.0, 0.0),
        "rain_hours": np.where(np.arange(n) % 5 == 0, 4.0, 0.0), "wind_max": 10.0, "cloud_mean": 50.0,
        "pm25_yday": rng.uniform(20, 50, n),  # never >= 60: bad air never happened
    })[FEATURES]
    y = pd.Series(np.where(X["rain_mm"] >= 2.5, 0.0, (np.arange(n) % 3 == 0).astype(float)))
    return X, y


def today(**over):
    row = {"steps_yday_rel": 1.0, "mean3_rel": 1.0, "mean7_rel": 1.0, "active_yday": 0.0, "streak": 0.0,
           "weekday": 2, "off_day": 0, "feels_max": 30.0, "rain_mm": 0.0, "rain_hours": 0.0, "wind_max": 10.0,
           "cloud_mean": 50.0, "pm25_yday": 30.0}
    row.update(over)
    return pd.DataFrame([row], columns=FEATURES)


def test_presence_rules():
    X, _ = hist()
    assert presence(X, "rain", X).sum() == 28
    assert presence(X, "workday", X).sum() == 100
    assert presence(X, "air", X).sum() == 0
    assert presence(today(rain_mm=3.0), "rain", X).iloc[0]


def test_settings_none_when_excuse_never_happened():
    X, _ = hist()
    assert settings("air", X) is None
    pres, absn = settings("rain", X)
    assert pres == [{"rain_mm": 6.0, "rain_hours": 4.0}] and absn == [{"rain_mm": 0.0, "rain_hours": 0.0}]


def test_evidence_counts_and_block_ci():
    X, y = hist()
    ev = evidence(X, y, "rain", n_boot=200)
    assert (ev["n_present"], ev["k_present"]) == (28, 0)
    assert ev["n_absent"] == 112
    assert ev["diff_ci"][1] < 0 and ev["ci_method"] == "7-day block bootstrap"


def test_evidence_skips_unlabelled_days_but_keeps_the_calendar():
    X, y = hist()
    y.iloc[10:15] = np.nan  # a 5-day gap, like late August in the real export
    ev = evidence(X, y, "rain", n_boot=200)
    assert ev["n_present"] + ev["n_absent"] == 135
    assert ev["n_present"] == 27  # day 10 was a rain day


def test_decide_table():
    assert decide(5, -30.0, -30.0, [-0.5, -0.1]) == "UNCLEAR"      # too few days
    assert decide(20, -12.0, -20.0, [-0.4, -0.05]) == "UPHELD"
    assert decide(20, -12.0, -20.0, [-0.4, 0.02]) == "UNCLEAR"     # CI crosses 0
    assert decide(20, -2.0, 3.0, [-0.1, 0.2]) == "OVERRULED"
    assert decide(20, -2.0, -8.0, [-0.3, 0.1]) == "UNCLEAR"        # model and counts disagree
    assert decide(20, None, -8.0, None) == "UNCLEAR"


def test_judge_with_fake_model(fake_model):
    X, y = hist()
    out = judge(fake_model, X, y, today(rain_mm=3.0, weekday=5, off_day=1), claimed="heat", n_boot=200)
    by = {v["excuse"]: v for v in out}
    assert by["rain"]["sensitivity_pts"] == -40.0 and by["rain"]["verdict"] == "UPHELD"
    assert by["rain"]["present_today"] is True
    assert by["heat"]["claimed"] is True and by["heat"]["sensitivity_pts"] == 0.0
    assert by["air"]["verdict"] == "UNCLEAR" and by["air"]["sensitivity_pts"] is None
    assert by["air"]["evidence"]["diff_ci"] is None
    assert [v["excuse"] for v in out][:2] == ["rain", "heat"]  # present today, then claimed
