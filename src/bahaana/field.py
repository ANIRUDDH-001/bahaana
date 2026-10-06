"""Field-test log (spec §9): predictions are saved before the day, check-ins after."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

FIELD_DIR = Path(__file__).resolve().parents[2] / "data" / "field"


def _path(day: str) -> Path:
    return FIELD_DIR / f"{day}.json"


def _read(day: str) -> dict:
    p = _path(day)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"date": day}


def _write(day: str, rec: dict) -> Path:
    FIELD_DIR.mkdir(parents=True, exist_ok=True)
    _path(day).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return _path(day)


def save_prediction(day: str, record: dict, force: bool = False) -> Path:
    rec = _read(day)
    if "prediction" in rec and not force:
        raise FileExistsError(f"A prediction for {day} already exists; it was made before the day. Use --force only to fix a mistake.")
    rec["prediction"] = {**record, "predicted_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return _write(day, rec)


def save_checkin(day: str, went: bool, minutes: int | None, steps: int | None, note: str | None = None) -> Path:
    rec = _read(day)
    rec["checkin"] = {"went": went, "minutes": minutes, "steps": steps, "note": note,
                      "logged_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return _write(day, rec)


def checkin_steps() -> dict[str, float]:
    out = {}
    for p in sorted(FIELD_DIR.glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8")).get("checkin") or {}
        if c.get("steps") is not None:
            out[p.stem] = float(c["steps"])
    return out


def entries() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(FIELD_DIR.glob("*.json"))]
