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
