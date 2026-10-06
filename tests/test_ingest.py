import zipfile
from datetime import date, timedelta

from bahaana.ingest import hourly_profile, parse_daily_csv, parse_hours_csv, read_export

DAILY = (
    "Date,Move Minutes count,Calories (kcal),Distance (m),Low latitude (deg),Low longitude (deg),Step count\n"
    "2026-01-01,40,2000,5000,28.61,77.2,10468\n"
    "2026-01-02,,,,,,\n"
    "2026-01-04,10,1900,800,,,1200\n"
)
HOURS = (
    "Start time,End time,Move Minutes count,Step count\n"
    "00:00:00.000+05:30,00:15:00.000+05:30,,11\n"
    "07:15:00.000+05:30,07:30:00.000+05:30,5,400\n"
    "07:30:00.000+05:30,07:45:00.000+05:30,5,600\n"
    "18:00:00.000+05:30,18:15:00.000+05:30,,\n"
)


def test_daily_csv_reads_only_date_and_steps():
    assert parse_daily_csv(DAILY) == {"2026-01-01": 10468.0, "2026-01-04": 1200.0}


def test_simple_csv_sums_duplicate_dates():
    assert parse_daily_csv("date,steps\n2026-01-01,100\n2026-01-01,50\n") == {"2026-01-01": 150.0}


def test_hours_csv_buckets_into_hours():
    h = parse_hours_csv(HOURS)
    assert len(h) == 24 and h[0] == 11 and h[7] == 1000 and h[18] == 0


def test_read_export_folder_and_zip(tmp_path):
    root = tmp_path / "Takeout" / "Fit" / "Daily activity metrics"
    root.mkdir(parents=True)
    (root / "Daily activity metrics.csv").write_text(DAILY, encoding="utf-8")
    (root / "2026-01-01.csv").write_text(HOURS, encoding="utf-8")
    data = read_export(tmp_path)
    assert data.daily["2026-01-01"] == 10468.0 and data.per_day_hours["2026-01-01"][7] == 1000
    z = tmp_path / "export.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(root / "Daily activity metrics.csv", "Takeout/Fit/Daily activity metrics/Daily activity metrics.csv")
        zf.write(root / "2026-01-01.csv", "Takeout/Fit/Daily activity metrics/2026-01-01.csv")
    assert read_export(z).daily == data.daily


def _day(i: int) -> str:
    return (date(2026, 1, 1) + timedelta(days=i)).isoformat()


def _peak(h: int) -> list[float]:
    return [100.0 if x == h else 0.0 for x in range(24)]


def test_profile_needs_ten_bigger_days():
    # 40 days of 1000..40000 steps: P70 = 28300, so 12 "bigger days" (>= 10 needed)
    daily = {_day(i): float(1000 * (i + 1)) for i in range(40)}
    hours = {d: _peak(17) for d in daily}
    prof = hourly_profile(hours, daily)
    assert prof is not None and prof[17] == 1.0
    assert hourly_profile({}, daily) is None


def test_profile_uses_only_the_last_90_days():
    # 30 old big days walk at 8 AM; the recent 90 days (1000..90000 steps) walk at 5 PM
    daily = {_day(i): 50000.0 for i in range(30)} | {_day(30 + i): float(1000 * (i + 1)) for i in range(90)}
    hours = {d: _peak(8 if d < _day(30) else 17) for d in daily}
    prof = hourly_profile(hours, daily)
    assert prof[17] == 1.0 and prof[8] == 0.0


def test_parsed_export_holds_no_location():
    data = parse_daily_csv(DAILY)
    assert "28.61" not in repr(data) and "77.2" not in repr(data)
