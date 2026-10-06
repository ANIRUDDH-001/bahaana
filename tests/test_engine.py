import numpy as np
import pytest

from bahaana.engine import EngineError, run_verdict
from bahaana.schema import RAW_DAY_FIELDS
from bahaana.synthetic import make_person
from tests.conftest import FakeModel

TODAY = {"weekday": 2, "holiday": 0, "feels_max": 30.0, "rain_mm": 4.0, "rain_hours": 3,
         "wind_max": 10.0, "cloud_mean": 80.0}


def history(n=200):
    return make_person("rain_shy", n_days=n, seed=1).to_dict("records")


def test_shape_with_fake_model():
    out = run_verdict(history(), TODAY, "rain", model_factory=FakeModel, n_boot=100)
    assert out["probability"] == 0.1
    assert out["model"] == "TabPFN v2 (PriorLabs)" and out["n_context_days"] > 100
    assert {v["excuse"] for v in out["verdicts"]} == {"heat", "rain", "air", "workday", "tired"}
    assert out["verdicts"][0]["excuse"] == "rain"


def test_rejects_short_history():
    with pytest.raises(EngineError, match="at least 60"):
        run_verdict(history(59), TODAY, None, model_factory=FakeModel)


def test_rejects_unknown_excuse():
    with pytest.raises(EngineError, match="Unknown excuse"):
        run_verdict(history(), TODAY, "laziness", model_factory=FakeModel)


def test_single_class_history_is_a_readable_error():
    flat = [{**r, "steps": 5000.0} for r in history()]
    with pytest.raises(EngineError, match="both"):
        run_verdict(flat, TODAY, None, model_factory=FakeModel)


def test_null_weather_is_allowed():
    h = history()
    for r in h[:30]:
        r["feels_max"] = None
    out = run_verdict(h, {**TODAY, "cloud_mean": None}, None, model_factory=FakeModel, n_boot=50)
    assert 0 <= out["probability"] <= 1
