import { KEYS, load, save } from "../store";
import type { Go } from "../state";

const MINUTES = 30;
export const renderAway = () => `
  <section class="away">
    <p id="clock" class="clock">30:00</p>
    <p class="lede">Phone down. Go.</p>
    <button id="back" class="btn">I'm back</button>
  </section>`;

export function bindAway(go: Go): void {
  const started = load<number>(KEYS.away, Date.now());
  const clock = document.getElementById("clock")!;
  const tick = () => {
    const left = Math.max(0, MINUTES * 60 - Math.floor((Date.now() - started) / 1000));
    clock.textContent = `${String(Math.floor(left / 60)).padStart(2, "0")}:${String(left % 60).padStart(2, "0")}`;
  };
  tick();
  const timer = setInterval(tick, 1000);
  window.addEventListener("hashchange", () => clearInterval(timer), { once: true });
  document.getElementById("back")!.addEventListener("click", () => {
    clearInterval(timer);
    save(KEYS.away, null);
    try { sessionStorage.setItem("bahaana.awayMinutes", String(Math.round((Date.now() - started) / 60000))); } catch { /* storage unavailable */ }
    go("/checkin");
  });
}
