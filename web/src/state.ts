import type { BacktestSummary, DemoBundle, FieldEntry, VerdictRequest, VerdictResponse, Win } from "./types";

export interface AppState {
  mode: "demo" | "live"; label: string; city: string | null;
  request: VerdictRequest | null; response: VerdictResponse | null; window: Win | null;
  backtest: BacktestSummary | null; field: FieldEntry[];
}
export type Go = (route: string) => void;

export const state: AppState = { mode: "demo", label: "", city: null, request: null, response: null, window: null, backtest: null, field: [] };

export async function loadDemo(): Promise<void> {
  const b: DemoBundle = await (await fetch("/demo.json")).json();
  Object.assign(state, { mode: "demo", label: `${b.label}, frozen on ${b.frozen_on}.`, request: b.request, response: b.response, window: b.window, backtest: b.backtest, field: b.field });
}

export function setLive(req: VerdictRequest, res: VerdictResponse, win: Win | null, city: string): void {
  Object.assign(state, { mode: "live", label: `Live · ${city}`, city, request: req, response: res, window: win });
}
