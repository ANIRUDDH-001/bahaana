import { EXCUSE_LABEL, evidenceLine, sensitivityLine, TIRED_NOTE } from "../copy";
import { esc, stampClass } from "../render";
import type { AppState } from "../state";

export function renderCourt(s: AppState): string {
  const cards = s.response!.verdicts.map((v) => {
    const ci = v.evidence.diff_ci ? `Precedent interval: ${Math.round(v.evidence.diff_ci[0] * 100)} to ${Math.round(v.evidence.diff_ci[1] * 100)} points (${v.evidence.ci_method}).` : "";
    return `
    <article class="case ${v.claimed ? "case--claimed" : ""}">
      <header><h2>${EXCUSE_LABEL[v.excuse]}</h2><span class="${stampClass(v.verdict)}">${v.verdict}</span></header>
      ${v.claimed ? `<p class="tag">Your usual excuse</p>` : ""}
      ${v.excuse === "tired" ? `<p class="note">${TIRED_NOTE}</p>` : ""}
      <p><strong>Today:</strong> ${esc(sensitivityLine(v))}</p>
      <p><strong>Precedent:</strong> ${esc(evidenceLine(v))}</p>
      ${ci ? `<p class="fine">${esc(ci)}</p>` : ""}
    </article>`;
  }).join("");
  return `
  <p class="kicker"><a href="#/today">← Today</a></p>
  <h1>Excuse Court</h1>
  <p class="lede">Today is the case. Your history is the precedent. A verdict needs the model and your past days to agree.</p>
  ${cards}
  <p class="fine">These are patterns in your history, not causes.</p>`;
}
