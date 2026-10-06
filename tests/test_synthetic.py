from collections import Counter

import pytest

from bahaana.features import build_features
from bahaana.model import TabPFNModel
from bahaana.schema import EXCUSES
from bahaana.synthetic import make_person, ordinary_todays
from bahaana.verdicts import judge

CASES = [
    ("rain_shy", {"rain"}, set()),
    ("indifferent", set(), set(EXCUSES)),
    ("weekend_walker", {"workday"}, {"rain"}),
]


@pytest.mark.slow
@pytest.mark.parametrize("kind, must_uphold, must_not_uphold", CASES)
def test_planted_behaviour_is_recovered(kind, must_uphold, must_not_uphold):
    days = make_person(kind, seed=7)
    X, y = build_features(days)
    keep = y.notna()
    Xh, yh = X[keep].reset_index(drop=True), y[keep].reset_index(drop=True)
    model = TabPFNModel().fit(Xh, yh)
    upheld = Counter()
    for t in ordinary_todays(Xh):
        for v in judge(model, X, y, t, n_boot=300):  # full calendar, as the engine does
            upheld[v["excuse"]] += v["verdict"] == "UPHELD"
    print(kind, dict(upheld))
    for e in must_uphold:
        assert upheld[e] >= 8, (kind, e, upheld)
    for e in must_not_uphold:
        assert upheld[e] <= 2, (kind, e, upheld)
