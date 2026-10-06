from bahaana.cli import field_rows


def test_field_rows_flattens_prediction_and_checkin():
    entries = [{"date": "2026-10-07",
                "prediction": {"result": {"probability": 0.71, "verdicts": [{"excuse": "rain", "verdict": "OVERRULED"}]}},
                "checkin": {"went": True, "minutes": 35, "steps": 8123, "note": "park"}},
               {"date": "2026-10-08", "prediction": {"result": {"probability": 0.3, "verdicts": []}}}]
    rows = field_rows(entries)
    assert rows[0] == {"date": "2026-10-07", "probability": 0.71, "top": "rain OVERRULED", "went": True,
                       "minutes": 35, "steps": 8123, "note": "park"}
    assert rows[1]["went"] is None and rows[1]["top"] is None
