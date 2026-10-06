import type { VerdictRequest, VerdictResponse } from "./types";

const API = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");
export const hasApi = () => Boolean(API);
export function warm(): void { if (API) fetch(`${API}/healthz`).catch(() => undefined); }
/** The engine sends a sentence; request validation sends a list, which only fails on history length here. */
export function errorDetail(body: { detail?: unknown }): string {
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail) && body.detail.some((d) => /at (least|most) \d+ items/.test(String(d?.msg)))) {
    return "Bahaana needs at least two months of steps.";
  }
  return "The model couldn't read that history.";
}

export async function postVerdict(req: VerdictRequest, timeoutMs = 180000): Promise<VerdictResponse> { // ~1 min wake + up to 90 s
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), timeoutMs);
  try {
    const r = await fetch(`${API}/v1/verdict`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(req), signal: ctl.signal });
    const body = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(errorDetail(body));
    return body as VerdictResponse;
  } catch (e) {
    if ((e as Error).name === "AbortError") throw new Error("The model took too long to wake up. Try again.");
    throw e;
  } finally { clearTimeout(timer); }
}
