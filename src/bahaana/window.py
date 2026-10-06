"""Good-window suggestion (spec §7). A heuristic, never a model output."""
from __future__ import annotations

COMFORT_FEELS = 35.0
RAIN_OK_MM = 0.2
LAST_HOUR = 21
BLOCK = 2


def good_window(profile: list[float], hours_today: list[dict], now_hour: int) -> tuple[int, int] | None:
    ok = {h["hour"]: (h["precip"] is not None and h["precip"] < RAIN_OK_MM
                      and h["feels"] is not None and h["feels"] <= COMFORT_FEELS) for h in hours_today}
    best, best_score = None, 0.0
    for start in range(now_hour, LAST_HOUR - BLOCK + 1):
        score = sum(profile[h] for h in range(start, start + BLOCK) if ok.get(h, False))
        if score > best_score:
            best, best_score = (start, start + BLOCK), score
    return best
