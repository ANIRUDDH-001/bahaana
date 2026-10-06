from fastapi.testclient import TestClient

import api.main as main
from bahaana.synthetic import make_person
from tests.conftest import FakeModel

TODAY = {"weekday": 2, "holiday": 0, "feels_max": 30.0, "rain_mm": 4.0, "rain_hours": 3,
         "wind_max": 10.0, "cloud_mean": 80.0}


def client(monkeypatch):
    monkeypatch.setattr(main, "MODEL_FACTORY", FakeModel)
    return TestClient(main.app)


def test_healthz(monkeypatch):
    r = client(monkeypatch).get("/healthz")
    assert r.status_code == 200 and r.json()["ok"] is True and r.json()["rss_mb"] > 0


def test_verdict_roundtrip(monkeypatch):
    body = {"history": make_person("rain_shy", n_days=150, seed=1).to_dict("records"), "today": TODAY,
            "claimed_excuse": "rain"}
    r = client(monkeypatch).post("/v1/verdict", json=body)
    assert r.status_code == 200
    j = r.json()
    assert j["probability"] == 0.1 and j["verdicts"][0]["excuse"] == "rain"
    assert j["verdicts"][0]["evidence"]["ci_method"] == "7-day block bootstrap"


def test_short_history_is_422(monkeypatch):
    body = {"history": make_person("rain_shy", n_days=59).to_dict("records"), "today": TODAY}
    r = client(monkeypatch).post("/v1/verdict", json=body)
    assert r.status_code == 422


def test_rejects_dates_or_extra_fields(monkeypatch):
    rows = make_person("rain_shy", n_days=80).to_dict("records")
    rows[0]["date"] = "2026-01-01"
    r = client(monkeypatch).post("/v1/verdict", json={"history": rows, "today": TODAY})
    assert r.status_code == 422
