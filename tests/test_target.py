import numpy as np
import pandas as pd

from bahaana.target import active_labels, rolling_threshold


def test_threshold_uses_only_previous_days():
    s = pd.Series(np.arange(1, 41, dtype=float))
    thr = rolling_threshold(s)
    # row 20 sees rows 0..19 (values 1..20): linear P70 = 1 + 0.7*19 = 14.3
    assert np.isnan(thr.iloc[19])
    assert round(thr.iloc[20], 6) == 14.3
    # row 30 sees rows 2..29 (values 3..30): 3 + 0.7*27 = 21.9
    assert round(thr.iloc[30], 6) == 21.9


def test_labels_rising_and_falling():
    up = active_labels(pd.Series(np.arange(1, 41, dtype=float)))
    assert up.iloc[:20].isna().all()
    assert (up.iloc[20:] == 1.0).all()
    down = active_labels(pd.Series(np.arange(100, 60, -1, dtype=float)))
    assert (down.iloc[20:] == 0.0).all()


def test_day_t_never_affects_its_own_threshold_or_earlier_labels():
    rng = np.random.default_rng(1)
    s = pd.Series(rng.integers(2000, 12000, 80).astype(float))
    base_thr, base_lab = rolling_threshold(s), active_labels(s)
    t = 50
    s2 = s.copy()
    s2.iloc[t:] = s2.iloc[t:] * 10
    assert base_thr.iloc[: t + 1].equals(rolling_threshold(s2).iloc[: t + 1])
    assert base_lab.iloc[:t].equals(active_labels(s2).iloc[:t])


def test_missing_days_get_no_label_and_are_skipped_in_windows():
    s = pd.Series(np.arange(1, 41, dtype=float))
    s.iloc[25] = np.nan
    lab = active_labels(s)
    assert np.isnan(lab.iloc[25])
    assert lab.iloc[26] == 1.0  # window still has >= 20 valid days


def test_too_few_valid_days_means_no_label():
    s = pd.Series([5000.0] * 40)
    s.iloc[0:25] = np.nan
    lab = active_labels(s)
    assert lab.iloc[:45].isna().all()
