# Bahaana (बहाना): the AI that predicts your excuses

Bahaana reads your own Google Fit step history and joins it with the weather forecast and modelled air quality for
each of those days. It then uses **TabPFN v2**, an open-weight tabular foundation model, to predict how likely today
is to be an *active day* for you. It tries your usual excuses (heat, rain, bad air, workday, "still tired") against
your own history and rules on each one: **UPHELD**, **OVERRULED** or **UNCLEAR**, with the evidence. Then it gets out
of the way: one button, *I'M GOING*, starts a phone-away timer.

Built for DEV Hacktoberfest 2026, Week 1 "Touch Grass".

## Privacy

- Your export is opened in your browser. The file is never uploaded.
- Your browser fetches weather and air quality directly from Open-Meteo, which sees your approximate city.
- Our server receives only the daily feature values and, if you picked one, your usual excuse, exactly as shown in
  *What our server saw*: no dates, no location, no file. It keeps nothing.
- Your check-ins stay in this browser.

## Run it locally

Everything below assumes Git Bash on Windows (or any POSIX shell), Python 3.11 and Node 22.

```bash
source scripts/env.sh                      # keeps pip/HF/temp caches on D:
py -3.11 -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python scripts/fetch_model.py  # TabPFN v2 checkpoint from Hugging Face, no login
.venv/Scripts/python -m pytest              # add -m "not slow" to skip the real-model tests
```

Put your Google Takeout (Fit) export in `data/raw/` (git-ignored), then:

```bash
# morning: predict today and save it before the day happens
.venv/Scripts/python -m bahaana today --export data/raw/<takeout-folder-or-zip> --city "<your city>" --claimed tired
# evening: log what actually happened
.venv/Scripts/python -m bahaana checkin --date 2026-10-07 --went yes --minutes 35 --steps 8123 --note "park"
# expanding-window backtest against three baselines (writes eval/)
.venv/Scripts/python -m bahaana backtest --export data/raw/<export> --city "<your city>" --date 2026-10-07
# precomputed demo bundle for the static site
.venv/Scripts/python -m bahaana demo --export data/raw/<export> --city "<your city>" --freeze 2026-10-11 --claimed tired
```

Web app:

```bash
cd web && npm ci && npm run dev    # http://localhost:5173
npm test                          # vitest
```

For live mode locally, run the API (`uvicorn api.main:app --port 8765` with `FRONTEND_ORIGIN=http://localhost:5173`)
and start Vite with `VITE_API_URL=http://localhost:8765`.

## Deploy (Render, free tier)

`render.yaml` is a Render Blueprint with two services:

- **bahaana-api**: Python web service (free plan). Set `FRONTEND_ORIGIN` to the static site's URL.
- **bahaana**: static site built from `web/`. Set `VITE_API_URL` to the API's URL.

The demo is precomputed (`web/public/demo.json`), so the public link opens instantly even while the free API sleeps.
`web/public/demo.json` is git-ignored until its owner agrees to publish their real step year; remove that line from
`.gitignore` to ship it.

## How it works

- **Target:** a day is *active* if its steps reach the 70th percentile of the valid days in the previous 28.
- **Features:** 13 values known on the morning of the day: recent steps relative to your own median, streaks,
  weekday, day off, the weather **as forecast 24 hours earlier**, and yesterday's modelled PM2.5 (CAMS).
- **Verdicts:** the model's sensitivity to each excuse on *today's* vector, and the precedent in your history
  (7-day block bootstrap). Both have to agree before a verdict is anything but UNCLEAR.
- **Evaluation:** expanding-window backtest against "same as yesterday", weekday base rate and logistic
  regression, with block-bootstrap intervals. Results in `eval/`, reported whichever model wins.

## License and attribution

Built with PriorLabs-TabPFN. TabPFN v2 weights are released by Prior Labs under the
[Prior Labs License](https://huggingface.co/Prior-Labs/TabPFN-v2-clf) (Apache 2.0 with an attribution clause).
Weather and air quality: [Open-Meteo](https://open-meteo.com/) (CC BY 4.0).
