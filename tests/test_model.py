import numpy as np
import pandas as pd
import pytest

from bahaana.model import TabPFNModel, ckpt_path
from bahaana.schema import FEATURES


def test_checkpoint_present():
    assert ckpt_path().exists(), "run scripts/fetch_model.py first"


@pytest.mark.slow
def test_tabpfn_v2_learns_a_simple_rule():
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.normal(size=(120, len(FEATURES))), columns=FEATURES)
    X["weekday"] = rng.integers(0, 7, 120)
    y = pd.Series((X["rain_mm"] < 0).astype(int))
    model = TabPFNModel().fit(X.iloc[:100], y.iloc[:100])
    p = model.predict_proba(X.iloc[100:])
    assert p.shape == (20,)
    assert ((p > 0.5).astype(int) == y.iloc[100:].to_numpy()).mean() >= 0.8
