import json
from pathlib import Path

from bahaana.window import good_window

FIX = Path(__file__).resolve().parents[1] / "shared" / "fixtures" / "window_case.json"


def test_window_matches_shared_fixture():
    case = json.loads(FIX.read_text())
    assert list(good_window(case["profile"], case["hours"], case["now_hour"])) == case["expected"]


def test_no_ok_hour_means_no_window():
    profile = [1 / 24] * 24
    hours = [{"hour": h, "feels": 40.0, "precip": 0.0} for h in range(24)]
    assert good_window(profile, hours, 6) is None


def test_window_never_starts_in_the_past_or_ends_after_21():
    profile = [0.0] * 24
    profile[8] = profile[9] = 1.0
    profile[20] = 0.5
    hours = [{"hour": h, "feels": 25.0, "precip": 0.0} for h in range(24)]
    assert good_window(profile, hours, 12) == (19, 21)
