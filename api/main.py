"""Stateless verdict API (spec §10.3). Request bodies are never logged or stored."""
from __future__ import annotations

import os
from typing import Literal

import psutil
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from bahaana.engine import EngineError, run_verdict
from bahaana.model import TabPFNModel

MODEL_FACTORY = TabPFNModel
Excuse = Literal["heat", "rain", "air", "workday", "tired"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Day(Strict):
    steps: float | None
    weekday: int = Field(ge=0, le=6)
    holiday: int = Field(ge=0, le=1)
    feels_max: float | None = None
    rain_mm: float | None = None
    rain_hours: float | None = None
    wind_max: float | None = None
    cloud_mean: float | None = None
    pm25: float | None = None


class Today(Strict):
    weekday: int = Field(ge=0, le=6)
    holiday: int = Field(ge=0, le=1)
    feels_max: float | None = None
    rain_mm: float | None = None
    rain_hours: float | None = None
    wind_max: float | None = None
    cloud_mean: float | None = None


class VerdictRequest(Strict):
    history: list[Day] = Field(min_length=60, max_length=1000)
    today: Today
    claimed_excuse: Excuse | None = None


app = FastAPI(title="Bahaana", docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=[o for o in os.environ.get("FRONTEND_ORIGIN", "").split(",") if o],
                   allow_methods=["GET", "POST"], allow_headers=["content-type"])


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "rss_mb": round(psutil.Process().memory_info().rss / 2**20)}


@app.post("/v1/verdict")
def verdict(req: VerdictRequest) -> dict:
    try:
        return run_verdict([d.model_dump() for d in req.history], req.today.model_dump(), req.claimed_excuse,
                           model_factory=MODEL_FACTORY)
    except EngineError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
