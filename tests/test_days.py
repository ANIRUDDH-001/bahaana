import math

from bahaana.days import add_days, build_days, date_range, load_holidays, today_raw, weekday_of

W = {"feels_max": 30.0, "rain_mm": 0.0, "rain_hours": 0, "wind_max": 10.0, "cloud_mean": 20.0}


def test_weekday_monday_is_zero():
    assert weekday_of("2026-10-05") == 0  # Monday
    assert weekday_of("2026-10-04") == 6  # Sunday
    assert weekday_of("2026-01-01") == 3  # Thursday


def test_date_helpers():
    assert date_range("2026-02-27", "2026-03-02") == ["2026-02-27", "2026-02-28", "2026-03-01", "2026-03-02"]
    assert add_days("2026-01-01", -1) == "2025-12-31"


def test_holidays_loaded():
    h = load_holidays()
    assert "2026-01-26" in h and "2026-10-02" in h and len(h) == 17


def test_gaps_become_missing_rows_not_dropped():
    steps = {"2026-08-26": 9000.0, "2026-08-27": 8000.0, "2026-09-02": 7000.0}
    days = build_days(steps, {}, {}, "2026-08-26", "2026-09-02")
    assert list(days["date"]) == date_range("2026-08-26", "2026-09-02")
    assert math.isnan(days.loc[days.date == "2026-08-28", "steps"].iloc[0])
    assert days.loc[days.date == "2026-08-26", "holiday"].iloc[0] == 1


def test_today_raw_has_only_today_fields():
    t = today_raw("2026-10-07", {"2026-10-07": W})
    assert t == {"weekday": 2, "holiday": 0, **W}
