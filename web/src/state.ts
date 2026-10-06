import type { BacktestSummary, DemoBundle, FieldEntry, VerdictRequest, VerdictResponse, Win } from "./types";

export interface AppState {
  mode: "demo" | "live"; label: string; city: string | null;
  day: string | null; tz: string | null; demoMissing: boolean;
  request: VerdictRequest | null; response: VerdictResponse | null; window: Win | null;
  backtest: BacktestSummary | null; field: FieldEntry[];
}
export type Go = (route: string) => void;

export const state: AppState = { mode: "demo", label: "", city: null, day: null, tz: null, demoMissing: false, request: null, response: null, window: null, backtest: null, field: [] };

export async function loadDemo(): Promise<void> {
  const r = await fetch("/demo.json");
  if (!r.ok) { state.demoMissing = true; return; }
  const b: DemoBundle = await r.json();
  Object.assign(state, { mode: "demo", label: `${b.label}, frozen on ${b.frozen_on}.`, day: b.frozen_on, tz: null, request: b.request, response: b.response, window: b.window, backtest: b.backtest, field: b.field });
}

export function setLive(req: VerdictRequest, res: VerdictResponse, win: Win | null, city: string, day: string, tz: string): void {
  Object.assign(state, { mode: "live", label: `Live · ${city}`, city, day, tz, request: req, response: res, window: win });
}
