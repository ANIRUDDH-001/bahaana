// copy.ts — every sentence is filled from numbers; no free text.
import type { ExcuseId, Verdict } from "./types";

export const EXCUSE_LABEL: Record<ExcuseId, string> = { heat: "Too hot", rain: "Raining", air: "Bad air", workday: "Workday", tired: "Still tired" };
const GROUPS: Record<ExcuseId, [string, string]> = {
  heat: ["hot days", "cooler days"], rain: ["rainy days", "dry days"], air: ["bad-air days (PM2.5 modelled (CAMS))", "cleaner days"],
  workday: ["workdays", "days off"], tired: ["days after a big day", "other days"],
};
export const TIRED_NOTE = "Your 'still tired' excuse is represented by an unusually active yesterday.";
export const ATTRIBUTION = "Built with PriorLabs-TabPFN";
export const PRIVACY_LINES = [
  "Your export is opened in your browser. The file is never uploaded.",
  "Your browser fetches weather and air quality directly from Open-Meteo, which sees your approximate city.",
  "Our server receives only the daily feature values and, if you picked one, your usual excuse, exactly as shown in What our server saw: no dates, no location, no file. It keeps nothing.",
  "Your check-ins stay in this browser.",
];
const pct = (k: number, n: number) => Math.round((100 * k) / n);

export function evidenceLine(v: Verdict): string {
  const e = v.evidence, [yes, no] = GROUPS[v.excuse];
  if (!e.n_present) return `No ${yes} in your history yet, so there's no precedent.`;
  const head = `You were active on ${e.k_present} of ${e.n_present} ${yes} (${pct(e.k_present, e.n_present)}%)`;
  return e.n_absent ? `${head}, vs ${pct(e.k_absent, e.n_absent)}% on ${no}.` : `${head}.`;
}

export function sensitivityLine(v: Verdict): string {
  if (v.sensitivity_pts === null) return "The model has nothing to compare this excuse against yet.";
  const s = v.sensitivity_pts, size = Math.abs(s).toFixed(1);
  return s < 0 ? `Today, this excuse lowers the model's likelihood by ${size} points.` : `Today, this excuse doesn't lower the model's likelihood (${s >= 0 ? "+" : ""}${s.toFixed(1)} points).`;
}
