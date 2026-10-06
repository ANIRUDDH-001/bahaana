"""bahaana today | checkin | backtest | demo"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bahaana import field
from bahaana.days import add_days, build_days, today_raw
from bahaana.engine import run_verdict
from bahaana.ingest import hourly_profile, read_export
from bahaana.schema import RAW_DAY_FIELDS
from bahaana.weather import (aggregate_daily, aggregate_pm25, fetch_pm25_hourly, fetch_weather_hourly, geocode,
                             hours_for)
from bahaana.window import good_window


def history_end(export_last_day: str, today: str) -> str:
    """History always ends yesterday: the export's last day can be today's partial day."""
    return add_days(today, -1)


def usable_steps(daily: dict[str, float], checkins: dict[str, float], today: str) -> dict[str, float]:
    """The export's last day is the day it was taken, so it is partial: drop it unless a check-in supplies it."""
    export = {d: v for d, v in daily.items() if d != max(daily)} if daily else {}
    steps = {**export, **checkins}
    return {d: v for d, v in steps.items() if d < today}


def prepare(export: Path, city: str, today: str) -> dict:
    data = read_export(export)
    steps = usable_steps(data.daily, field.checkin_steps(), today)
    geo = geocode(city)
    start, end = min(steps), history_end(max(data.daily), today)
    hourly = fetch_weather_hourly(geo["lat"], geo["lon"], geo["timezone"], start, today)
    pm = aggregate_pm25(fetch_pm25_hourly(geo["lat"], geo["lon"], geo["timezone"], start, end))
    weather = aggregate_daily(hourly)
    return {
        "geo": geo, "start": start,
        "days": build_days(steps, weather, pm, start, end),
        "today_raw": today_raw(today, weather),
        "hourly": hourly,
        "profile": hourly_profile(data.per_day_hours, data.daily),
    }


def _local_now(tz: str) -> datetime:
    return datetime.now(ZoneInfo(tz))


def cmd_today(a: argparse.Namespace) -> None:
    tz = geocode(a.city)["timezone"]
    today = a.date or _local_now(tz).date().isoformat()
    p = prepare(Path(a.export), a.city, today)
    history = p["days"][RAW_DAY_FIELDS].to_dict("records")
    result = run_verdict(history, p["today_raw"], a.claimed)
    now_hour = 8 if a.date else _local_now(tz).hour
    window = good_window(p["profile"], hours_for(p["hourly"], today), now_hour) if p["profile"] else None
    record = {"city": p["geo"]["name"], "result": result, "window": window}
    path = field.save_prediction(today, record, force=a.force)
    print(f"{today}  active-day likelihood {result['probability']:.0%}  ({result['n_context_days']} days of context)")
    for v in result["verdicts"]:
        flag = " (today)" if v["present_today"] else ""
        print(f"  {v['excuse']:<8} {v['verdict']:<9} sensitivity {v['sensitivity_pts']} pts{flag}  {v['evidence']}")
    print(f"  window: {window}")
    print(f"saved {path}")


def cmd_checkin(a: argparse.Namespace) -> None:
    path = field.save_checkin(a.date, a.went == "yes", a.minutes, a.steps, a.note)
    print(f"saved {path}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="bahaana")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("today", help="predict today and save it before the day happens")
    t.add_argument("--export", required=True)
    t.add_argument("--city", required=True)
    t.add_argument("--claimed", choices=["heat", "rain", "air", "workday", "tired"])
    t.add_argument("--date", help="override today (YYYY-MM-DD); window then assumes 08:00")
    t.add_argument("--force", action="store_true")
    t.set_defaults(fn=cmd_today)
    c = sub.add_parser("checkin", help="log what actually happened")
    c.add_argument("--date", required=True)
    c.add_argument("--went", choices=["yes", "no"], required=True)
    c.add_argument("--minutes", type=int)
    c.add_argument("--steps", type=int)
    c.add_argument("--note")
    c.set_defaults(fn=cmd_checkin)
    _extra_commands(sub)
    a = ap.parse_args(argv)
    a.fn(a)


def cmd_backtest(a: argparse.Namespace) -> None:
    from bahaana.backtest import MODELS, expanding_predictions, summarize, write_report
    from bahaana.features import build_features

    tz = geocode(a.city)["timezone"]
    today = a.date or _local_now(tz).date().isoformat()
    p = prepare(Path(a.export), a.city, today)
    X, y = build_features(p["days"][RAW_DAY_FIELDS], target_window=a.target_window)
    preds = expanding_predictions(X, y, MODELS)
    out = Path("eval")
    out.mkdir(exist_ok=True)
    preds.to_csv(out / f"predictions_{a.target_window}.csv", index=False)
    summary = summarize(preds, list(MODELS))
    write_report(summary, out, str(a.target_window))
    print((out / f"backtest_{a.target_window}.md").read_text(encoding="utf-8"))


def field_rows(entries: list[dict]) -> list[dict]:
    rows = []
    for e in entries:
        res = (e.get("prediction") or {}).get("result") or {}
        top = (res.get("verdicts") or [None])[0]
        c = e.get("checkin") or {}
        rows.append({"date": e["date"], "probability": res.get("probability"),
                     "top": f"{top['excuse']} {top['verdict']}" if top else None,
                     "went": c.get("went"), "minutes": c.get("minutes"), "steps": c.get("steps"), "note": c.get("note")})
    return rows


def cmd_demo(a: argparse.Namespace) -> None:
    p = prepare(Path(a.export), a.city, a.freeze)
    history = p["days"][RAW_DAY_FIELDS].astype(object).where(p["days"][RAW_DAY_FIELDS].notna(), None).to_dict("records")
    request = {"history": history[-1000:], "today": p["today_raw"], "claimed_excuse": a.claimed}
    response = run_verdict(request["history"], request["today"], a.claimed)
    window = good_window(p["profile"], hours_for(p["hourly"], a.freeze), 8) if p["profile"] else None
    bt = Path("eval/backtest_28.json")
    bundle = {"label": a.label, "frozen_on": a.freeze, "request": request, "response": response,
              "window": list(window) if window else None,
              "backtest": json.loads(bt.read_text(encoding="utf-8")) if bt.exists() else None,
              "field": field_rows(field.entries())}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


def _extra_commands(sub) -> None:
    d = sub.add_parser("demo", help="write web/public/demo.json")
    d.add_argument("--export", required=True)
    d.add_argument("--city", required=True)
    d.add_argument("--freeze", required=True)
    d.add_argument("--claimed", choices=["heat", "rain", "air", "workday", "tired"])
    d.add_argument("--label", default="Demo · Aniruddh's real 2026")
    d.add_argument("--out", default="web/public/demo.json")
    d.set_defaults(fn=cmd_demo)
    b = sub.add_parser("backtest", help="expanding-window backtest vs baselines")
    b.add_argument("--export", required=True)
    b.add_argument("--city", required=True)
    b.add_argument("--target-window", type=int, default=28)
    b.add_argument("--date")
    b.set_defaults(fn=cmd_backtest)
