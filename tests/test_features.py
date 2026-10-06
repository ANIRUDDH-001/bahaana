import numpy as np
import pandas as pd

from bahaana.features import build_features, clean_steps, today_features
from bahaana.schema import FEATURES, RAW_DAY_FIELDS


def make_days(n=60, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "steps": rng.integers(3000, 12000, n).astype(float),
        "weekday": np.arange(n) % 7,
        "holiday": 0,
        "feels_max": rng.uniform(20, 40, n),
        "rain_mm": rng.uniform(0, 5, n),
        "rain_hours": rng.integers(0, 6, n),
        "wind_max": rng.uniform(5, 20, n),
        "cloud_mean": rng.uniform(0, 100, n),
        "pm25": rng.uniform(20, 120, n),
    })[RAW_DAY_FIELDS]


def test_clean_steps_marks_low_days_missing():
    out = clean_steps(pd.Series([150, 200, 5000]))
    assert np.isnan(out.iloc[0]) and out.iloc[1] == 200 and out.iloc[2] == 5000


def test_columns_and_off_day():
    days = make_days()
    days.loc[3, "holiday"] = 1
    X, y = build_features(days)
    assert list(X.columns) == FEATURES and len(X) == len(y) == 60
    assert X.loc[5, "off_day"] == 1 and X.loc[6, "off_day"] == 1  # Sat, Sun
    assert X.loc[3, "off_day"] == 1 and X.loc[2, "off_day"] == 0  # holiday, Wednesday


def test_no_lookahead_from_steps():
    days = make_days()
    X1, _ = build_features(days)
    k = 40
    d2 = days.copy()
    d2.loc[k:, "steps"] = d2.loc[k:, "steps"] * 3
    X2, _ = build_features(d2)
    pd.testing.assert_frame_equal(X1.iloc[: k + 1], X2.iloc[: k + 1])


def test_pm25_is_yesterdays_and_weather_is_todays():
    days = make_days()
    X, _ = build_features(days)
    assert X.loc[10, "pm25_yday"] == days.loc[9, "pm25"]
    assert X.loc[10, "rain_mm"] == days.loc[10, "rain_mm"]


def test_streak_counts_active_days_ending_yesterday():
    days = make_days(n=50)
    days["steps"] = np.random.default_rng(5).uniform(3500, 6000, 50).round()
    days.loc[44, "steps"] = 3000.0      # surely below its threshold: breaks any earlier streak
    days.loc[45:47, "steps"] = 20000.0  # rows 45,46,47 active
    X, y = build_features(days)
    assert y.loc[45] == 1 and y.loc[46] == 1 and y.loc[47] == 1
    assert X.loc[48, "streak"] == 3 and X.loc[48, "active_yday"] == 1


def test_today_vector_matches_extended_history():
    days = make_days()
    today = {"weekday": 4, "holiday": 0, "feels_max": 31.0, "rain_mm": 3.0, "rain_hours": 2,
             "wind_max": 12.0, "cloud_mean": 80.0}
    t = today_features(days, today)
    assert list(t.columns) == FEATURES and len(t) == 1
    assert t.loc[0, "pm25_yday"] == days.iloc[-1]["pm25"]
    assert t.loc[0, "rain_mm"] == 3.0 and t.loc[0, "weekday"] == 4
