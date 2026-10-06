import { EXCUSE_LABEL, evidenceLine, TIRED_NOTE } from "../copy";
import { esc, percent, stampClass, windowText } from "../render";
import { KEYS, save } from "../store";
import type { AppState, Go } from "../state";
import type { Today } from "../types";
import type { Run } from "../checkin";

function forecastLine(t: Today | undefined): string {
  if (!t) return "";
  const parts: string[] = [];
  if (t.feels_max !== null) parts.push(`feels like ${Math.round(t.feels_max)}°`);
  if (t.rain_mm !== null) parts.push(t.rain_mm >= 0.1 ? `${t.rain_mm.toFixed(1)} mm rain` : "dry");
  if (t.cloud_mean !== null) parts.push(`${Math.round(t.cloud_mean)}% cloud`);
  return parts.length ? `Today's forecast: ${parts.join(", ")}.` : "";
}

export function renderToday(s: AppState): string {
  const r = s.response!;
  const present = r.verdicts.some((v) => v.present_today);
  const rows = r.verdicts.slice(0, 3).map((v) => `
    <li class="verdict">
      <span class="verdict__name">${EXCUSE_LABEL[v.excuse]}
        ${v.present_today ? `<span class="chip">Forecast today</span>` : ""}${v.claimed ? `<span class="chip chip--yours">Your excuse</span>` : ""}
      </span>
      <span class="${stampClass(v.verdict)}">${v.verdict}</span>
      <span class="verdict__why">${esc(evidenceLine(v))}${v.excuse === "tired" ? ` ${TIRED_NOTE}` : ""}</span>
    </li>`).join("");
  return `
  <p class="kicker">${esc(s.label)}</p>
  <section class="today">
    <div class="today__score">
      <p class="big">${percent(r.probability)}</p>
      <p class="big__label">Active-day likelihood</p>
      <p class="forecast">${esc(forecastLine(s.request?.today))}</p>
    </div>
    <div class="today__docket">
      ${present ? "" : `<p class="none">No excuse available today.</p>`}
      <ol class="verdicts">${rows}</ol>
      <a class="link" href="#/court">Challenge my excuses</a>
    </div>
    <p class="window"><strong>${windowText(s.window)}</strong><span>Suggestion · your usual hours + today's forecast</span></p>
    <div class="today__go"><button id="go" class="btn btn--primary btn--huge">I'M GOING</button></div>
  </section>`;
}

export function bindToday(s: AppState, go: Go): void {
  document.getElementById("go")!.addEventListener("click", () => {
    const run: Run = { date: s.day ?? "", tz: s.tz ?? Intl.DateTimeFormat().resolvedOptions().timeZone, mode: s.mode };
    save(KEYS.run, run);
    save(KEYS.away, Date.now());
    go("/away");
  });
}
