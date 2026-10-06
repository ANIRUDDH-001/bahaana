import numpy as np
import pytest


class FakeModel:
    """Deterministic stand-in for TabPFN: P = 0.1 on rainy rows (rain_mm >= 2.5), otherwise 0.5."""

    def fit(self, X, y):
        return self

    def predict_proba(self, X):
        rain = X["rain_mm"].fillna(0).to_numpy(dtype=float)
        return np.where(rain >= 2.5, 0.1, 0.5)


@pytest.fixture
def fake_model():
    return FakeModel()
