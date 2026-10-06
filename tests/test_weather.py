import json
from pathlib import Path

import pytest

from bahaana.weather import aggregate_daily, aggregate_pm25, fetch_weather_hourly, geocode, hours_for, r3

FIX = Path(__file__).resolve().parents[1] / "shared" / "fixtures"


def test_aggregate_matches_shared_fixture():
    hourly = json.loads((FIX / "weather_hourly.json").read_text())
    expected = json.loads((FIX / "weather_daily.json").read_text())
    assert aggregate_daily(hourly) == expected


def test_r3_rounds_half_up():
    assert r3(0.0005) == 0.001 and r3(2.4999) == 2.5 and r3(1.0) == 1.0


def test_pm25_daily_mean_skips_nulls():
    out = aggregate_pm25({"time": ["2026-07-01T00:00", "2026-07-01T01:00", "2026-07-02T00:00"],
                          "pm2_5": [40.0, None, None]})
    assert out == {"2026-07-01": 40.0, "2026-07-02": None}


def test_hours_for_day():
    hourly = json.loads((FIX / "weather_hourly.json").read_text())
    assert hours_for(hourly, "2026-07-01")[2] == {"hour": 2, "feels": 33.0, "precip": 2.4}


@pytest.mark.network
def test_live_previous_runs_variables_exist():
    g = geocode("New Delhi")
    assert g["timezone"] == "Asia/Kolkata"
    h = fetch_weather_hourly(g["lat"], g["lon"], g["timezone"], "2026-03-01", "2026-03-02")
    assert len(h["time"]) == 48 and h["apparent_temperature_previous_day1"][12] is not None
