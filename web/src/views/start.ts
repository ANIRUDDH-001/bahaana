import { postVerdict, hasApi } from "../api";
import { hourIn, todayIn, addDays } from "../dates";
import { EXCUSE_LABEL } from "../copy";
import { buildRequest, usableSteps } from "../payload";
import { esc, stampClass } from "../render";
import { KEYS, load, save } from "../store";
import { hourlyProfile, readExport, type StepsData } from "../takeout";
import type { ExcuseId } from "../types";
import { aggregateDaily, aggregatePm25, fetchPm25Hourly, fetchWeatherHourly, geocode, hoursFor } from "../weather";
import { goodWindow } from "../window";
import { setLive, type AppState, type Go } from "../state";

export function renderStart(s: AppState): string {
  const city = load<string>(KEYS.city, "");
  const claimed = load<string>(KEYS.claimed, "");
  const excuses = (Object.keys(EXCUSE_LABEL) as ExcuseId[])
    .map((e) => `<option value="${e}" ${e === claimed ? "selected" : ""}>${EXCUSE_LABEL[e]}</option>`).join("");
  const sample = s.response?.verdicts.find((v) => v.claimed) ?? s.response?.verdicts[0];
  const cached = load<StepsData | null>(KEYS.steps, null);
  return `
  <section class="hero">
    <p class="wordmark" lang="hi">बहाना</p>
    <h1>The AI that predicts your excuses.</h1>
    <p class="lede">Bahaana reads your own step history, tries your usual excuses against it, then gets out of your way.</p>
    ${sample ? `<p class="specimen" aria-hidden="true"><span>${EXCUSE_LABEL[sample.excuse]}</span><span class="${stampClass(sample.verdict)}">${sample.verdict}</span></p>` : ""}
    <a class="btn btn--primary" href="#/today" ${s.response ? "" : "aria-disabled=true"}>See my real year (demo)</a>
  </section>
  <section class="card">
    <h2>Use your Google Fit export</h2>
    <p class="fine">Opened in this browser. The file is never uploaded.</p>
    <form id="live" class="form">
      <label>Takeout .zip (or a date,steps CSV)<input name="file" type="file" accept=".zip,.csv" ${cached ? "" : "required"}></label>
      ${cached ? `<p class="fine">Using the steps saved in this browser. Pick a file to replace them.</p>` : ""}
      <label>Your town or city<input name="city" required value="${esc(city)}" placeholder="e.g. Jaipur" autocomplete="address-level2"></label>
      <label>Your usual excuse (optional)<select name="claimed"><option value="">Not sure</option>${excuses}</select></label>
      <button class="btn" ${hasApi() ? "" : "disabled"}>Judge my excuses</button>
      ${hasApi() ? "" : `<p class="fine">Live mode needs the model server, which isn't connected here. The demo works.</p>`}
      <p id="progress" class="progress" role="status"></p>
    </form>
  </section>`;
}

export function bindStart(_s: AppState, go: Go): void {
  const form = document.getElementById("live") as HTMLFormElement;
  const say = (t: string) => { document.getElementById("progress")!.textContent = t; };
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(form);
    try {
      const file = fd.get("file") as File;
      say("Opening your export in this browser…");
      const data: StepsData = file && file.size ? await readExport(file) : load<StepsData>(KEYS.steps, { daily: {}, perDayHours: {} });
      save(KEYS.steps, data);
      const cityName = String(fd.get("city"));
      save(KEYS.city, cityName);
      const claimed = (String(fd.get("claimed")) || null) as ExcuseId | null;
      save(KEYS.claimed, claimed ?? "");
      say("Finding your city…");
      const g = await geocode(cityName);
      const today = todayIn(g.timezone);
      const field = load<Record<string, { steps: number | null }>>(KEYS.field, {});
      const checkins = Object.fromEntries(Object.entries(field).filter(([, v]) => v.steps !== null).map(([d, v]) => [d, v.steps as number]));
      const daily = usableSteps(data.daily, checkins, today);
      const start = Object.keys(daily).sort()[0];
      if (!start) throw new Error("No step history found before today.");
      say("Fetching the forecasts that were made for each day…");
      const hourly = await fetchWeatherHourly(g.lat, g.lon, g.timezone, start, today);
      const pm = aggregatePm25(await fetchPm25Hourly(g.lat, g.lon, g.timezone, start, addDays(today, -1)));
      const req = buildRequest(daily, aggregateDaily(hourly), pm, today, claimed);
      say("Waking the model. It runs on a free server that naps, so this can take a minute or two…");
      const res = await postVerdict(req);
      const profile = hourlyProfile(data.perDayHours, data.daily);
      const win = profile ? goodWindow(profile, hoursFor(hourly, today), hourIn(g.timezone)) : null;
      setLive(req, res, win, g.name);
      go("/today");
    } catch (e) {
      say(`${(e as Error).message} The demo is still one tap away.`);
    }
  });
}
