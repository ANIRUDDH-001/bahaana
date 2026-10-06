import json

import pytest

import bahaana.field as field


@pytest.fixture(autouse=True)
def tmp_field(tmp_path, monkeypatch):
    monkeypatch.setattr(field, "FIELD_DIR", tmp_path)


def test_prediction_is_not_overwritten_without_force():
    field.save_prediction("2026-10-07", {"probability": 0.7})
    with pytest.raises(FileExistsError):
        field.save_prediction("2026-10-07", {"probability": 0.2})
    field.save_prediction("2026-10-07", {"probability": 0.2}, force=True)


def test_checkin_adds_steps_and_keeps_prediction(tmp_path):
    field.save_prediction("2026-10-07", {"probability": 0.7})
    field.save_checkin("2026-10-07", went=True, minutes=35, steps=8123, note="park")
    rec = json.loads((tmp_path / "2026-10-07.json").read_text())
    assert rec["prediction"]["probability"] == 0.7 and rec["checkin"]["went"] is True
    assert field.checkin_steps() == {"2026-10-07": 8123.0}
    assert field.entries()[0]["date"] == "2026-10-07"
