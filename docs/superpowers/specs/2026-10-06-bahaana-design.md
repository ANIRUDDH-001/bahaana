# Bahaana: The AI That Predicts Your Excuses

**Design spec** · 2026-10-06 · DEV Hacktoberfest 2026, Week 1 "Touch Grass"
**Deadline:** Oct 11, 11:59 PM PDT = **Oct 12, 12:29 PM IST** (target submit: Oct 12, ~10:00 IST)
**Status:** Frozen 2026-10-06 after two external review passes (ChatGPT). Two items are gated (see §15).
Changes from here on are logged in §18.

---

## 1. The idea in one paragraph

Bahaana (बहाना, "excuse") reads about ten months of my own Google Fit step history, joins it with the weather
forecast and air quality for each of those days, and uses **TabPFN v2**, an open-weight tabular foundation model, to
predict how likely today is to be an *active day* for me. It then tries my usual excuses against my own history
(heat, rain, bad air, workday, "still tired") and returns a verdict for each: **UPHELD**, **OVERRULED** or
**UNCLEAR**, with the evidence. Then it gets out of the way: one button, *I'M GOING*, starts a phone-away timer.

**Thesis for the article:** *Maybe we don't need an AI that motivates us. Maybe we need one with enough evidence to
call our bluff.*

## 2. Goals, success criteria, non-goals

**Goals**
1. A working, deployed product that a judge can try in under 10 seconds, with no sign-up and no data of their own.
2. A real result: an honest backtest of TabPFN v2 against three simpler baselines on my own data.
3. Real outdoor use: a prospective field log from Oct 7–11 (target 5 days, minimum 3).
4. A strong DEV post built around the thesis, the verdicts and the numbers.

**Success criteria**
- The demo loads instantly from the DEV post link (precomputed, no backend needed).
- Bring-your-own mode works end to end on a real Google Fit Takeout export.
- The backtest tables (with 95% intervals) and the field log are published, whatever they show.
- $0 spent. Every service is on a free tier.

**Non-goals (explicitly out)**
- No LLM, no chatbot, no voice.
- No database, no accounts, no login.
- No maps, routes, feeds or social features.
- No health, fitness or wellness claims. The language is "activity" and "going out".
- No causal claims. The language is "predicts", "correlates with", "in your history".
- No step-count regression. The product predicts one yes/no outcome.
- No support for Samsung Health or Apple Health exports this week. Google Fit Takeout, plus a plain `date,steps` CSV.

**Prize categories entered:** Best Use of TabPFN (primary), Best Use of Render (secondary). Nothing else.

## 3. Who it is for

- **Primary user:** someone with a phone step history who keeps "meaning to go out". Me first.
- **Judges:** need the instant demo, a clear story, and visible proof that the AI is central and the claims are honest.

## 4. Product

### 4.1 Screens

| Screen | Purpose | Content |
|---|---|---|
| **Start** | Choose a path | Hero line, two buttons: *See my real year (demo)* and *Use my Google Fit export*. For bring-your-own: a city field (rough location only) and an optional "What's your usual excuse?" pick. |
| **Today** (hero) | The verdict, in seconds | Big active-day likelihood (%), 2–3 verdict rows, the good window, **I'M GOING** button. |
| **Away** | Get off the screen | Only a countdown (30 min). On return: "You were away 34 min." |
| **Check-in** | Close the loop | Shown after 6 PM or next morning: "Did you go out?" Yes/No + today's steps (from the Fit app). |
| **Excuse Court** | The evidence, one tap deeper | One card per excuse: verdict, today's model sensitivity, the precedent (raw counts and interval). Your claimed excuse is highlighted, never filtered. |
| **Under the hood** | Trust | Backtest results vs baselines, calibration chart, *What our server saw* (exact JSON), privacy statement, field-test table, license attribution. |

Footer on every screen: **"Built with PriorLabs-TabPFN"** (required by the TabPFN v2 license).

### 4.2 The Today screen order

1. Likelihood, e.g. **78%**, labelled "Active-day likelihood".
2. Verdict rows, at most 3, in this order:
   (a) excuses that are actually present today (e.g. it is forecast to rain),
   (b) the excuse the user said they usually use,
   (c) the remaining excuses, strongest effect first.
   If no excuse is present today, show the line: **"No excuse available today."**
3. Good window, labelled as a suggestion (see §7).
4. **I'M GOING**.

Example copy (filled from numbers, never free text):
> **Raining · OVERRULED** · You were active on 8 of 14 rainy days (57%), about the same as dry days (52%).

### 4.3 Visual direction

Premium, editorial "verdict" look: big type, a stamp-like verdict mark, generous space, little chrome.
Light and dark themes from the start, mobile-first, no horizontal scroll at phone width. The exact visual system is
designed at the start of the UI work with the frontend-design skill. This spec fixes the content and the hierarchy,
not the pixels.

## 5. Data

### 5.1 Sources

| Source | What | Cost |
|---|---|---|
| Google Fit **Takeout** export | Daily step totals; 15-minute step buckets if present (gate §15) | Free |
| Open-Meteo **Previous Runs API** | Hourly weather **as forecast 24 h earlier** (`*_previous_day1`), archived from Jan 2024 | Free, no key, non-commercial |
| Open-Meteo **Air Quality API** | Hourly PM2.5 (CAMS global, from Aug 2022) | Free, no key |
| Open-Meteo **Geocoding API** | City name → rough coordinates | Free, no key |
| Indian central-government gazetted holidays 2026 | Static list, committed as `shared/holidays_2026.json` (sourced from the official order) | Free |

All weather is aggregated per local day, timezone `Asia/Kolkata` (or the city's timezone).

### 5.2 Daily raw values (one row per calendar day)

`steps`, `weekday` (0–6), `holiday` (0/1), `feels_max` (max apparent temperature, °C), `rain_mm` (daily sum),
`rain_hours` (hours with ≥ 0.1 mm), `wind_max` (km/h), `cloud_mean` (%), `pm25` (daily mean, µg/m³).
The weather values use the 24-hour-earlier forecast. PM2.5 uses the day's modelled value.

**Missing days:** a day with fewer than 200 steps is treated as "phone not carried" and becomes missing. It gets no
label and is skipped in rolling windows. The 200 cut-off is confirmed when the export is inspected (§15).

### 5.3 Target (strictly causal)

```
threshold(t) = 70th percentile of valid steps in days [t-28, t-1]   (needs ≥ 20 valid days)
active(t)    = steps(t) >= threshold(t)
```

Day `t` is never part of its own threshold. Days whose window has fewer than 20 valid days get no label (this
includes the first 20 days). A 70th-percentile threshold implies roughly 30% active days in an idealised case; the
real share depends on gaps and ties, so the **observed** share is reported, not assumed. A 60-day version is run once
as a side check in the evaluation.

### 5.4 Features: only what is known on the morning of day t

| # | Feature | Definition |
|---|---|---|
| 1 | `steps_yday_rel` | steps(t-1) ÷ median of valid steps in [t-28, t-1] |
| 2 | `mean3_rel` | mean steps over [t-3, t-1] ÷ same median |
| 3 | `mean7_rel` | mean steps over [t-7, t-1] ÷ same median |
| 4 | `active_yday` | active(t-1), 0/1 |
| 5 | `streak` | consecutive active days ending at t-1, capped at 7 |
| 6 | `weekday` | 0–6, passed to TabPFN as categorical |
| 7 | `off_day` | weekend or holiday |
| 8–12 | `feels_max`, `rain_mm`, `rain_hours`, `wind_max`, `cloud_mean` | for day t, from the 24-hour-earlier forecast |
| 13 | `pm25_yday` | Yesterday's **modelled** PM2.5 (CAMS estimate, ~45 km grid), daily mean for t-1. Archived air-quality *forecasts* aren't available, and yesterday's estimate is known each morning, so it's used in training and live alike. It is not a local sensor reading. |

Missing values stay as NaN; TabPFN handles them.
**Deliberately excluded (a design choice, stated as a limitation):** month, because in North India the season tracks
heat and monsoon and a month feature could soak up the weather signal we want to test; and same-day outcomes such as
distance or move minutes (they would give the answer away).

## 6. Model and the verdict engine

### 6.1 Model

`TabPFNClassifier.create_default_for_version(ModelVersion.V2)` on CPU with default settings. TabPFN does not train:
"fitting" stores the labelled rows as context, and each prediction is one forward pass. An ensemble is added only if
the backtest shows a measurable gain that is worth its memory and time.

### 6.2 Excuse catalog (fixed)

| Excuse | Present when | "Present" setting | "Absent" setting |
|---|---|---|---|
| Too hot | `feels_max` in your top 25% of days | median `feels_max` of present days | median of the other days |
| Raining | `rain_mm` ≥ 2.5 (IMD's "rainy day") | median `rain_mm` of rainy days, with matching `rain_hours` | 0 mm, 0 h |
| Bad air | `pm25_yday` ≥ 60 µg/m³ (India's 24-h PM2.5 standard, applied to the modelled estimate) | median of present days | median of the other days |
| Workday | `off_day` = 0 | each of Mon–Fri with `off_day`=0, averaged | Sat and Sun with `off_day`=1, averaged |
| Still tired | `steps_yday_rel` ≥ 1.5 **and** `active_yday` = 1 | median `steps_yday_rel` of present days, `active_yday`=1 | `steps_yday_rel`=1.0, `active_yday` unchanged |

**"Still tired" is a behavioural proxy, not a fatigue measurement.** Bahaana cannot observe tiredness. The UI always
says: *"Your 'still tired' excuse is represented by an unusually active yesterday."*

### 6.3 Verdict rules (fixed now, before any result is seen)

**Framing: today is the case, your history is the precedent.** A verdict rules on *today's* excuse, so it can differ
from one day to the next. That is intended, and the demo is frozen on one date.

For each excuse:
- **Model sensitivity Δ (today only):** fit TabPFN on all labelled historical days. Take today's feature vector, set
  the excuse to its "present" setting and predict; set it to "absent" and predict. Δ = P(present) − P(absent), in
  percentage points. Today is never in the model's context, so the model isn't asked about rows it already holds.
  This is a model perturbation, not a causal estimate. (Limitation, stated in the post: correlated features such as
  `mean3_rel` aren't moved together.)
- **Evidence (the precedent):** active rate on historical days where the excuse was present (k₁/n₁) vs absent
  (k₀/n₀); 95% interval for the difference from 1,000 **7-day block bootstrap** resamples. Blocks are needed because
  excuses cluster in time (rain in the monsoon, heat in May–June). Blocks are **calendar weeks**: the evidence runs
  on the full calendar with gap days kept (unlabelled, so not counted), so a missing stretch never stretches a block.

| Verdict | Rule |
|---|---|
| **UNCLEAR** | n₁ < 8 (not enough days), or neither rule below matches |
| **UPHELD** | Δ ≤ −10 points **and** the evidence interval's upper end is below 0 |
| **OVERRULED** | Δ > −5 points **and** the raw difference > −5 points |

The model and the raw counts must agree before a verdict is anything but UNCLEAR. These thresholds are not tuned
after seeing the data. If they are changed, the post says so and why.

### 6.4 Proving the verdict engine works

Before it touches real data, the engine runs on **synthetic people** with planted behaviour (about 280 days each,
with realistic rain and heat seasons). Because verdicts are per day, each person is judged on 10 ordinary "today"
vectors (median weather, a weekday, `steps_yday_rel` ≈ 1), and the rule must hold on at least 8 of them:
- *Rain-shy:* going out drops from about 2 in 5 to 1 in 20 on rainy days → Raining must be **UPHELD**. (Raised from 1 in 3 → 1 in 10 during implementation: at that strength TabPFN's sensitivity was −6 to −7.5 points, short of the fixed −10 rule, because rainy days are also cloudy and sensitivity moves only the rain columns. Thresholds were not changed.)
- *Indifferent:* activity independent of all excuses → no excuse may be **UPHELD**.
- *Weekend walker:* active mostly on off-days → Workday must be **UPHELD**, Raining must not be.

These are automated tests. The post reports them as "synthetic sanity checks for the verdict engine": they show the
pipeline recovers a planted pattern and stays quiet when there is none. They are not evidence about real people;
the backtest (§8) and the field test (§9) carry that.

## 7. The good window (a suggestion, not a model output)

Only built if the export has 15-minute buckets (gate §15).
- **Your hours:** each hour's share of steps, averaged over your bigger days (days at or above the 70th percentile of your valid days **in the last 90 days**; needs at least 10 such days with 15-minute data). Recent only because activity drifts (January median about 10.4k, September about 7.1k); a whole-year cut would mostly describe January's routine.
- **Today's forecast:** an hour counts as "OK" if rain < 0.2 mm and feels-like ≤ 35 °C, between now and 21:00.
- **Window:** the best 2-hour block, scored as (share of your steps in that hour) × OK.
  If no hour is OK: "No good window today."
- **Label:** "Suggestion · your usual hours + today's forecast."

## 8. Evaluation protocol (fixed now)

**Backtest:** expanding window. For each labelled day d, starting once 42 labelled days exist before it:
fit on all labelled days before d, predict d. Expect about 200 out-of-sample predictions.

**Baselines (same protocol, same days)**
1. *Same as yesterday:* P(active | yesterday's status), estimated from the training days.
2. *Weekday base rate:* P(active | weekday), with +1 smoothing.
3. *Logistic regression:* same 13 features, standardised, weekday one-hot, default regularisation.

**Metrics**
- Primary: ROC-AUC and Brier score.
- Secondary: F1 at a 0.5 threshold, and a 5-bin calibration chart.
- 95% intervals from 1,000 **7-day block bootstrap** resamples: the test days are grouped into calendar weeks (by
  calendar position, so gaps don't merge weeks) and whole weeks are resampled, because neighbouring days share rolling features and weather and are not
  independent. TabPFN − logistic uses the **same** resampled blocks for both models (paired).
- Side checks: 28-day vs 60-day target window. Memory and time per prediction on Render's free web service.

**Reporting:** every metric for every model, whichever wins. If TabPFN does not beat the baselines, the post says
so plainly.

## 9. Field test protocol (prospective)

- **When:** every morning from the first morning after the export is processed, through Oct 11. Target 5 days,
  minimum 3.
- **Morning, before 9 AM:** run Bahaana. The prediction, verdicts and window are saved to
  `data/field/<date>.json` with a timestamp *before* the day happens.
- **Evening:** check-in records: went out (Y/N), minutes away, steps (read from the Fit app), and one optional photo.
  The steps also feed the next morning's features.
- **Framing in the post:** "This is not a validation set. It's a small test of whether seeing Bahaana changed what I
  did." Accuracy claims come only from the backtest.

## 10. Architecture

### 10.1 Components

```
bahaana/
  src/bahaana/        Python core (one engine for CLI, demo build and API)
    ingest.py           Takeout / CSV  -> daily steps (+ hourly profile)
    weather.py          Open-Meteo fetch + daily aggregation (offline use)
    features.py         rolling features, off_day
    target.py           causal active-day label
    model.py            TabPFN v2 wrapper
    verdicts.py         excuse catalog, today-only sensitivity, block-bootstrap evidence, rules
    window.py           good-window suggestion
    backtest.py         protocol of §8, baselines, metrics
    cli.py              `bahaana today`, `bahaana checkin`, `bahaana backtest`
    build_demo.py       writes web/public/demo.json
  api/main.py         FastAPI app (Render free web service)
  web/                Vite + TypeScript static site (Render static site)
  shared/             holidays_2026.json, weather aggregation fixtures
  tests/              pytest (core) ; web/ has vitest
  eval/               backtest results as Markdown + CSV
  data/raw/           Takeout export (never committed)
  data/field/         field-test log
  docs/superpowers/specs/
  render.yaml
```

### 10.2 Who does what (this split is the privacy design)

| Step | Where | Why there |
|---|---|---|
| Unzip and read the Takeout export | **Browser** (JSZip) | The file is never uploaded |
| City → coordinates | Browser → Open-Meteo | Our server never sees location |
| Fetch weather and PM2.5, aggregate per day | **Browser** → Open-Meteo | Same |
| Weekday and holiday flags | Browser | Needs dates, which never leave the browser |
| Strip dates, send an ordered list of daily values | Browser → API | — |
| Rolling features, target, TabPFN, verdicts | **API** (Python core) | Feature logic lives in one place |
| Good window | Browser | Uses the hourly profile and today's hourly forecast, all local |

The daily weather aggregation exists twice (TypeScript for live mode, Python for the backtest and demo). Both are
tested against the same golden fixture in `shared/` so they cannot drift apart.

### 10.3 API

`GET /healthz` → `{"ok": true}`. The static site calls this on page load to wake the free service.

`POST /v1/verdict`

```json
{
  "history": [
    {"steps": 6120, "weekday": 2, "holiday": 0, "feels_max": 33.1, "rain_mm": 0.0,
     "rain_hours": 0, "wind_max": 11.2, "cloud_mean": 40, "pm25": 52.3}
  ],
  "today": {"weekday": 3, "holiday": 0, "feels_max": 31.0, "rain_mm": 4.2,
            "rain_hours": 3, "wind_max": 14.0, "cloud_mean": 85},
  "claimed_excuse": "rain"
}
```

- `history` is ordered oldest → newest and ends yesterday. No dates, no location.
- 60–1,000 rows (TabPFN v2's CPU limit is 1,000). Outside that range → `422` with a readable message.
- `null` allowed for any weather value.

Response:

```json
{
  "probability": 0.78,
  "n_context_days": 251,
  "verdicts": [
    {"excuse": "rain", "verdict": "OVERRULED", "present_today": true, "claimed": true,
     "sensitivity_pts": -2.1,
     "evidence": {"n_present": 14, "k_present": 8, "n_absent": 237, "k_absent": 123,
                  "diff_ci": [-0.21, 0.31], "ci_method": "7-day block bootstrap"}}
  ],
  "model": "TabPFN v2 (PriorLabs)"
}
```

Stateless. Request bodies are never logged or stored; access logs keep only path, status and duration.
CORS allows only the static site's origin.

### 10.4 Demo mode

`python -m bahaana.build_demo` runs the full pipeline offline on my data, frozen at a chosen date, and writes
`web/public/demo.json`. It contains everything Today, Excuse Court and Under the hood need, plus the backtest
results and the field-test table. The demo uses the same components as live mode and is labelled
**"Demo · Aniruddh's real 2026, frozen on <date>."** It needs no backend, so it opens instantly.

### 10.5 Browser storage

Field log, check-ins, the chosen city, the claimed excuse and the parsed daily steps (so you do not re-upload every morning) live in `localStorage`, with a "Forget my data" button, wrapped so the app still works
if storage is unavailable. The field log can be exported as CSV.

## 11. Privacy: the exact claims we make

Allowed (all true by design):
- "Your export is opened in your browser. The file is never uploaded."
- "Your browser fetches weather and air quality directly from Open-Meteo, which sees your approximate city."
- "Our server receives only the daily feature values and, if you picked one, your usual excuse, exactly as shown in
  *What our server saw*: no dates, no location, no file. It keeps nothing."
- "Your check-ins stay in this browser."

Never said: "never leaves your device", "100% private", "anonymous" (a step sequence is personal; we say "no dates,
no location" instead).

## 12. Hosting and cost ($0)

| Piece | Service | Free-tier facts we design around |
|---|---|---|
| Static site + demo | Render Static Site | Free, served from a CDN, does not sleep |
| TabPFN API | Hugging Face Docker Space (free CPU) | 2 vCPU, 16 GB RAM, sleeps after 48 h idle. Moved from Render free (512 MB) on 2026-10-06: one request peaked at 538 MB on Linux and Render restarted the service |
| Weather, air, geocoding | Open-Meteo | Free for non-commercial use, no key |
| Model weights | TabPFN v2 from Hugging Face | Prior Labs License (Apache 2.0 + attribution) |
| Code | GitHub (user handles all git) | Free |

**Budgets checked on Day 2:** API memory under 450 MB. Verdict time once awake is a benchmark with three bands:
under 30 s is the target; 30–90 s is acceptable if three calls in a row succeed (the waiting screen says it's a free
server, and the post reports the time); out of memory, crashes, timeouts or over 90 s trigger §14. The demo is
always instant because it never calls the API. A call is
one TabPFN fit (about 250 context rows) plus about 12 single-row predictions (today, and today with each excuse
present or absent), so time should be small; the bootstrap evidence is plain counting. If memory doesn't fit, see §14.

## 13. Error handling

- **Export unreadable / no step data found:** say which file was expected and link to the Takeout instructions.
- **Fewer than 60 usable days:** "Bahaana needs at least two months of steps." Offer the demo.
- **Open-Meteo unreachable:** retry once; then show the demo and keep the uploaded data in memory for a retry.
- **API asleep:** a warm-up state ("Waking the model. Free hosting naps.") with progress; a 90 s timeout, then a
  retry button.
- **API error:** human-readable message; the demo stays one tap away.

## 14. Risks and fallbacks

| Risk | Fallback |
|---|---|
| TabPFN v2 doesn't fit Render's 512 MB | Hosted site runs the demo only; live mode becomes a one-command local run (`bahaana today`). The static site still runs on Render. |
| TabPFN doesn't beat the baselines | Report it plainly; the verdicts and story still stand. |
| Export has no 15-minute buckets | Drop the good window (§7). |
| Takeout arrives late | Synthetic-data work continues; field test shrinks (minimum 3 days); if fewer, the post says so. |
| Every excuse comes out UNCLEAR | Report it; widen nothing silently. |
| Season and weather are tangled (heat → summer, rain → monsoon) | No month feature; the limitation is stated in the post. |
| The 28-day target follows your recent normal, so a whole season of lower activity becomes the new normal | Verdicts compare day against day within a season, not season against season. Stated in the post; the 60-day side check shows how much this matters. |

## 15. Open items (gates)

1. **Takeout export inspection: PASSED 2026-10-06.** Findings:
   - `Takeout/Fit/Daily activity metrics/Daily activity metrics.csv`: one row per day, columns `Date` and
     `Step count` (plus about 30 others we ignore). 272 rows, 2025-12-26 to 2026-10-06.
   - 13 dates missing entirely (2025-12-27 to 12-31, 2026-01-02, 01-03, 01-06, 2026-08-28 to 09-01) → become missing
     rows, never dropped. 2 blank step cells; 2 days under 200 steps (the 200 cut-off stands).
   - 15-minute buckets exist: one `YYYY-MM-DD.csv` per day, 96 rows, `Start time` like `00:00:00.000+05:30`, column
     `Step count`. Their sum matches the daily total (median difference 7 steps). **The good window is in scope.**
   - Timezone is +05:30 throughout. Steps come from phone + watch, already merged by Fit; we use Fit's merged totals.
   - The export date (2026-10-06) is a **partial day** and must be excluded; history ends the day before.
   - The summary also holds latitude/longitude columns on 10 days. **The parsers keep only `Date` / `Start time` and
     `Step count`, never anything else**, and tests assert no location value survives parsing or reaches the request.
   - Monthly median steps fall from about 10,400 (Jan) to about 7,100 (Sep): real drift, which the rolling target is
     built to handle.
2. **Demo consent.** The public demo shows my real 2026 step year: months visible (needed for the heat and monsoon
   story), city shown only roughly. Needs a yes before `build_demo` is published.

## 16. Schedule

| Date | Build | Field |
|---|---|---|
| Oct 6 | Spec approved → implementation plan. Then: project setup, synthetic people, target + features + verdict engine with tests, weather fetch + aggregation, holiday list | Export requested |
| Oct 7 | Ingest the real export (gate 1), first TabPFN run, `bahaana today` | Day 1 if the export is ready |
| Oct 8 | Backtest + baselines; API; Render memory and time check | Day 2 |
| Oct 9 | Web app: Start, Today, Away, Check-in, Excuse Court, Under the hood; demo build | Day 3 |
| Oct 10 | Deploy both Render services; polish; screenshots | Day 4 |
| Oct 11 | Write the DEV post with final numbers | Day 5 |
| Oct 12 | Log the last check-in; submit by ~10:00 IST | — |

## 17. DEV post outline (submission template)

1. **What I Built:** the thesis; the screens; who it's for.
2. **Demo:** the Render link (opens the instant demo) + screenshots.
3. **Code:** GitHub embed.
4. **How I Built It:** TabPFN v2 and why a tabular foundation model fits one person's 250 days; the causal target;
   the 24-hour-earlier forecasts; the verdict engine and the synthetic-people test; the backtest tables.
5. **Why Does Open Innovation Matter?** Open weights let me run the model on my own laptop and on a free server I
   control. A closed API would need my year of movement uploaded to someone else. Plus *What our server saw*.
6. **Field test:** the prospective log and photos, with the honest framing from §9.
7. **Prize categories:** Best Use of TabPFN, Best Use of Render.

## 18. Decisions log

| Decision | Reason |
|---|---|
| Bahaana over a footpath-audit idea and a Tinker-tuned bird guide | Freshest angle in a field crowded with Gemma trail and bird apps; feasible in 5 days; TabPFN is central, not bolted on |
| TabPFN **v2**, not 2.5+ | v2 weights are Apache-based with attribution; later weights are non-commercial |
| No LLM | Templates from computed numbers can't hallucinate; avoids the crowded Gemma category |
| 28-day target window (60 as side check) | Ten months of data; a 60-day warm-up would discard 21% of it |
| Forecasts made 24 h earlier, not actual weather | The live app only ever has forecasts; actual weather in the backtest would be cheating |
| Yesterday's PM2.5 | No archived air-quality forecasts exist; yesterday's value is known each morning |
| No month feature | Season and weather are tangled in North India |
| Ask the claimed excuse, never filter by it | Enables "you blame rain; it's actually workdays" without hiding other verdicts |
| Verdicts need model and raw counts to agree | Guards against verdicts from either one alone |
| Model sensitivity on **today's** vector only, not averaged over history | Historical rows are the model's own context; perturbing them lets it partly recall their labels. Today-only is cleaner, cheaper, and fits "today is the case, history is the precedent" |
| 7-day block bootstrap for backtest and evidence intervals | Days share rolling features and weather; excuses cluster by season. Day-by-day resampling would overstate certainty |
| PM2.5 called "modelled (CAMS)" everywhere | It's a ~45 km model estimate, not a sensor reading |
| "Still tired" shown as a behavioural proxy | Tiredness isn't observable; only an unusually active yesterday is |
| Observed active-day share reported, not assumed | P70 implies ~30% only in an idealised case |
| Plan-review edits (2026-10-06): bootstrap blocks are calendar weeks (gaps kept); TabPFN runtime benchmarked in Task 1 before the backtest is scheduled (protocol never shortened); window profile limited to the last 90 days; verdict time judged in three bands, not a hard 30 s; synthetic tests reported as sanity checks only; tests assert no location survives parsing | Second outside review of the plan. Calendar blocks keep the "7-day" claim true across the 13 missing dates; the 90-day window handles the Jan→Sep activity drift better than reusing the causal labels, and keeps the labelling code out of the browser |
| Plan-stage edits (2026-10-06): label starts after 20 valid days; synthetic rain effect 1-in-3 → 1-in-10; window profile uses "bigger days"; parsed steps cached in the browser with a Forget button | Found while writing the implementation plan; keeps browser logic free of the labelling code and the synthetic test unambiguous |
| Thresholds fixed before results | No tuning until the story looks good |
| Instant precomputed demo + live API only for your own data | Render's free service sleeps; a judge's first click must be instant |
| Browser does parsing, location and weather | The server never sees dates, location or the file |
