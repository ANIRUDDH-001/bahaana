import { ATTRIBUTION, PRIVACY_LINES } from "../copy";
import { esc } from "../render";
import { forgetAll, KEYS, load } from "../store";
import type { AppState } from "../state";

export function renderHood(s: AppState): string {
  const bt = s.backtest;
  const table = bt ? `
    <div class="scroll"><table class="table"><thead><tr><th>Model</th><th>ROC-AUC</th><th>Brier</th></tr></thead><tbody>
    ${Object.entries(bt.models).map(([n, m]) => `<tr><td>${esc(n)}</td><td>${m.auc.toFixed(3)} <span class="fine">[${m.auc_ci.join(", ")}]</span></td><td>${m.brier.toFixed(3)} <span class="fine">[${m.brier_ci.join(", ")}]</span></td></tr>`).join("")}
    </tbody></table></div>
    <p class="fine">${bt.n_predictions} days predicted using only earlier days. Active share ${(bt.prevalence * 100).toFixed(0)}%. Intervals: ${esc(bt.ci_method)}.</p>
    <h3>Does "70%" mean 70%?</h3>
    <ul class="calib">${bt.calibration.map((c) => `<li><span>${c.lo.toFixed(1)}–${c.hi.toFixed(1)}</span><span>${c.n} days</span><span>${c.rate === null ? "—" : `${Math.round(c.rate * 100)}% active`}</span></li>`).join("")}</ul>` : `<p class="fine">Backtest results appear in the demo build.</p>`;
  const req = s.request;
  const preview = req ? JSON.stringify({ ...req, history: [...req.history.slice(0, 3), `… ${req.history.length - 3} more days`] }, null, 2) : "";
  const field = s.field.length ? `<div class="scroll"><table class="table"><thead><tr><th>Day</th><th>Likelihood</th><th>Top verdict</th><th>Went?</th><th>Steps</th></tr></thead><tbody>
    ${s.field.map((f) => `<tr><td>${f.date}</td><td>${f.probability === null ? "—" : Math.round(f.probability * 100) + "%"}</td><td>${esc(f.top ?? "—")}</td><td>${f.went === null ? "—" : f.went ? "Yes" : "No"}</td><td>${f.steps ?? "—"}</td></tr>`).join("")}</tbody></table></div>
    <p class="fine">This is not a validation set. It's a small test of whether seeing Bahaana changed what I did.</p>` : "";
  return `
  <p class="kicker"><a href="#/today">← Today</a></p>
  <h1>Under the hood</h1>
  <h2>How well does it predict?</h2>${table}
  <h2>What our server saw</h2>
  <pre class="json">${esc(preview)}</pre>
  ${req ? `<details><summary>Full payload (${req.history.length} days)</summary><pre class="json">${esc(JSON.stringify(req, null, 2))}</pre></details>` : ""}
  <h2>Privacy</h2><ul class="privacy">${PRIVACY_LINES.map((l) => `<li>${esc(l)}</li>`).join("")}</ul>
  ${load(KEYS.steps, null) ? `<button id="forget" class="btn">Forget my data</button>` : ""}
  ${field ? `<h2>Field test</h2>${field}` : ""}
  <h2>Model</h2><p>TabPFN v2 by Prior Labs, open weights, run on CPU. ${ATTRIBUTION}. <a href="https://huggingface.co/Prior-Labs/TabPFN-v2-clf">License</a>.</p>`;
}

export function bindHood(): void {
  document.getElementById("forget")?.addEventListener("click", () => { forgetAll(); location.hash = "/"; location.reload(); });
}
