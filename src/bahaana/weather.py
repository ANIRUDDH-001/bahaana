"""Open-Meteo access and per-day aggregation (spec §5.1-5.2). Must stay identical to web/src/weather.ts."""
from __future__ import annotations

import math

import httpx

PREVIOUS_RUNS = "https://previous-runs-api.open-meteo.com/v1/forecast"
AIR_QUALITY = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
FEELS, PRECIP, WIND, CLOUD = (
    "apparent_temperature_previous_day1", "precipitation_previous_day1",
    "wind_speed_10m_previous_day1", "cloud_cover_previous_day1",
)
RAIN_HOUR_MM = 0.1


def r3(x: float) -> float:
    return math.floor(x * 1000 + 0.5) / 1000


def _by_day(times: list[str]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for i, t in enumerate(times):
        out.setdefault(t[:10], []).append(i)
    return out


def _vals(col: list, idx: list[int]) -> list[float]:
    return [float(col[i]) for i in idx if col[i] is not None]


def aggregate_daily(hourly: dict) -> dict[str, dict]:
    out = {}
    for day, idx in _by_day(hourly["time"]).items():
        f, p, w, c = (_vals(hourly[k], idx) for k in (FEELS, PRECIP, WIND, CLOUD))
        out[day] = {
            "feels_max": r3(max(f)) if f else None,
            "rain_mm": r3(sum(p)) if p else None,
            "rain_hours": sum(1 for x in p if x >= RAIN_HOUR_MM) if p else None,
            "wind_max": r3(max(w)) if w else None,
            "cloud_mean": r3(sum(c) / len(c)) if c else None,
        }
    return out


def aggregate_pm25(hourly: dict) -> dict[str, float | None]:
    out = {}
    for day, idx in _by_day(hourly["time"]).items():
        v = _vals(hourly["pm2_5"], idx)
        out[day] = r3(sum(v) / len(v)) if v else None
    return out


def hours_for(hourly: dict, day: str) -> list[dict]:
    return [{"hour": int(t[11:13]), "feels": hourly[FEELS][i], "precip": hourly[PRECIP][i]}
            for i, t in enumerate(hourly["time"]) if t[:10] == day]


def _get(url: str, params: dict) -> dict:
    r = httpx.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def geocode(city: str) -> dict:
    res = _get(GEOCODING, {"name": city, "count": 1, "language": "en", "format": "json"}).get("results") or []
    if not res:
        raise ValueError(f"Couldn't find a place called '{city}'.")
    g = res[0]
    return {"name": g["name"], "lat": round(g["latitude"], 1), "lon": round(g["longitude"], 1),
            "timezone": g["timezone"]}


def fetch_weather_hourly(lat: float, lon: float, tz: str, start: str, end: str) -> dict:
    return _get(PREVIOUS_RUNS, {"latitude": lat, "longitude": lon, "timezone": tz, "start_date": start,
                                "end_date": end, "hourly": ",".join((FEELS, PRECIP, WIND, CLOUD))})["hourly"]


def fetch_pm25_hourly(lat: float, lon: float, tz: str, start: str, end: str) -> dict:
    return _get(AIR_QUALITY, {"latitude": lat, "longitude": lon, "timezone": tz, "start_date": start,
                              "end_date": end, "hourly": "pm2_5"})["hourly"]
