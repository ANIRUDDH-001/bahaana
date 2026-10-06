import { checkinDay, stepsAllowed, type Run } from "../checkin";
import { KEYS, load, save } from "../store";
import type { Go } from "../state";

const runOf = () => load<Run | null>(KEYS.run, null);

export function renderCheckin(): string {
  let mins = "";
  try { mins = sessionStorage.getItem("bahaana.awayMinutes") ?? ""; } catch { /* storage unavailable */ }
  const run = runOf();
  const live = run?.mode === "live";
  const steps = run && stepsAllowed(run)
    ? `<label>Today's steps (from your Fit app)<input name="steps" type="number" min="0" inputmode="numeric"></label>`
    : live ? `<p class="fine">Come back after 6 PM to add today's step total. A partial count would look like a quiet day.</p>` : "";
  return `
  <section class="card">
    <h1>Did you go out?</h1>
    ${mins ? `<p class="lede">You were away ${mins} min.</p>` : ""}
    <form id="ci" class="form">
      <fieldset class="seg"><legend class="sr">Did you go out?</legend><label><input type="radio" name="went" value="yes" required> Yes</label><label><input type="radio" name="went" value="no"> No</label></fieldset>
      <label>Minutes outside<input name="minutes" type="number" min="0" inputmode="numeric" value="${mins}"></label>
      ${steps}
      <button class="btn btn--primary">Log it</button>
      ${live ? "" : `<p class="fine">This is the demo, so nothing is saved.</p>`}
    </form>
  </section>`;
}

export function bindCheckin(go: Go): void {
  const form = document.getElementById("ci") as HTMLFormElement;
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const run = runOf();
    if (run?.mode === "live") {
      const fd = new FormData(form);
      const num = (k: string) => (fd.get(k) ? Number(fd.get(k)) : null);
      const log = load<Record<string, unknown>>(KEYS.field, {});
      log[checkinDay(run)] = { went: fd.get("went") === "yes", minutes: num("minutes"), steps: stepsAllowed(run) ? num("steps") : null };
      save(KEYS.field, log);
    }
    go("/today");
  });
}
