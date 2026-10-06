// window.ts — mirrors src/bahaana/window.py.
import type { HourWeather, Win } from "./types";

export function goodWindow(profile: number[], hours: HourWeather[], nowHour: number): Win | null {
  const ok = new Map(hours.map((h) => [h.hour, h.precip !== null && h.precip < 0.2 && h.feels !== null && h.feels <= 35]));
  let best: Win | null = null, bestScore = 0;
  for (let start = nowHour; start <= 21 - 2; start++) {
    let score = 0;
    for (let h = start; h < start + 2; h++) if (ok.get(h)) score += profile[h];
    if (score > bestScore) { best = [start, start + 2]; bestScore = score; }
  }
  return best;
}
