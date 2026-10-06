import { todayIn } from "../dates";
import { KEYS, load, save } from "../store";
import type { Go } from "../state";

export function renderCheckin(): string {
  let mins = "";
  try { mins = sessionStorage.getItem("bahaana.awayMinutes") ?? ""; } catch { /* storage unavailable */ }
  return `
  <section class="card">
    <h1>Did you go out?</h1>
    ${mins ? `<p class="lede">You were away ${mins} min.</p>` : ""}
    <form id="ci" class="form">
      <fieldset class="seg"><legend class="sr">Did you go out?</legend><label><input type="radio" name="went" value="yes" required> Yes</label><label><input type="radio" name="went" value="no"> No</label></fieldset>
      <label>Minutes outside<input name="minutes" type="number" min="0" inputmode="numeric" value="${mins}"></label>
      <label>Today's steps (from your Fit app)<input name="steps" type="number" min="0" inputmode="numeric"></label>
      <button class="btn btn--primary">Log it</button>
    </form>
  </section>`;
}

export function bindCheckin(go: Go): void {
  const form = document.getElementById("ci") as HTMLFormElement;
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const fd = new FormData(form);
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const log = load<Record<string, unknown>>(KEYS.field, {});
    const num = (k: string) => (fd.get(k) ? Number(fd.get(k)) : null);
    log[todayIn(tz)] = { went: fd.get("went") === "yes", minutes: num("minutes"), steps: num("steps") };
    save(KEYS.field, log);
    go("/today");
  });
}
