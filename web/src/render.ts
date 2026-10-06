import type { VerdictKind, Win } from "./types";

export const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
export const percent = (p: number) => `${Math.round(p * 100)}%`;
const hh = (h: number) => `${((h + 11) % 12) + 1} ${h < 12 ? "AM" : "PM"}`;
export const windowText = (w: Win | null) => (w ? `${hh(w[0])} – ${hh(w[1])}` : "No good window today");
export const stampClass = (k: VerdictKind) => `stamp stamp--${k.toLowerCase()}`;
