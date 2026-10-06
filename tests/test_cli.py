from bahaana.cli import history_end


def test_history_ends_the_day_before_today_even_if_export_has_today():
    assert history_end("2026-10-06", "2026-10-06") == "2026-10-05"
    assert history_end("2026-10-06", "2026-10-09") == "2026-10-08"


def test_partial_export_day_is_dropped_unless_a_checkin_supplies_it():
    from bahaana.cli import usable_steps

    daily = {"2026-10-04": 9000.0, "2026-10-05": 8000.0, "2026-10-06": 1200.0}  # export taken on Oct 6
    assert usable_steps(daily, {}, "2026-10-07") == {"2026-10-04": 9000.0, "2026-10-05": 8000.0}
    assert usable_steps(daily, {"2026-10-06": 7400.0}, "2026-10-08")["2026-10-06"] == 7400.0
    assert "2026-10-07" not in usable_steps(daily, {"2026-10-07": 5000.0}, "2026-10-07")


def test_a_complete_export_day_wins_over_a_checkin():
    from bahaana.cli import usable_steps

    daily = {"2026-10-04": 9000.0, "2026-10-05": 8000.0, "2026-10-06": 1200.0}
    assert usable_steps(daily, {"2026-10-04": 3100.0}, "2026-10-07")["2026-10-04"] == 9000.0


def test_history_starts_at_most_1000_days_before_today():
    from bahaana.cli import history_start

    assert history_start({"2014-03-01": 5000.0, "2026-10-01": 6000.0}, "2026-10-07") == "2024-01-11"
    assert history_start({"2026-01-01": 5000.0}, "2026-10-07") == "2026-01-01"
