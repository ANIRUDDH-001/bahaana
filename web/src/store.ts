// store.ts — localStorage that never throws (private windows, blocked storage).
export const KEYS = { steps: "bahaana.steps", city: "bahaana.city", claimed: "bahaana.claimed", field: "bahaana.field", away: "bahaana.away", run: "bahaana.run" } as const;
export function load<T>(key: string, fallback: T): T {
  try { const v = localStorage.getItem(key); return v === null ? fallback : (JSON.parse(v) as T); } catch { return fallback; }
}
export function save(key: string, value: unknown): void { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* storage unavailable */ } }
export function forgetAll(): void { try { Object.values(KEYS).forEach((k) => localStorage.removeItem(k)); } catch { /* nothing to forget */ } }
