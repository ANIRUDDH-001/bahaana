// takeout.ts — reads ONLY the date/start-time and step columns.
import JSZip from "jszip";
import { addDays } from "./dates";

export interface StepsData { daily: Record<string, number>; perDayHours: Record<string, number[]> }
const DAILY_NAME = "daily activity metrics.csv";
const DAY_FILE = /(\d{4}-\d{2}-\d{2})\.csv$/;
const MISSING_BELOW = 200;
const RECENT_DAYS = 90; // same as ingest.py: the profile describes your current routine, not January's

function columns(header: string[]): [number, number] {
  const low = header.map((h) => h.trim().toLowerCase());
  const d = low.findIndex((h) => h === "date" || h === "start time");
  const s = low.findIndex((h) => h === "step count" || h === "steps");
  if (d < 0 || s < 0) throw new Error("This file has no date and step columns.");
  return [d, s];
}
const rowsOf = (text: string) => text.split(/\r?\n/).filter((l) => l.trim()).map((l) => l.split(","));

export function parseDailyCsv(text: string): Record<string, number> {
  const rows = rowsOf(text);
  const [d, s] = columns(rows[0]);
  const out: Record<string, number> = {};
  for (const r of rows.slice(1)) {
    const v = (r[s] ?? "").trim();
    if (v) out[r[d].trim()] = (out[r[d].trim()] ?? 0) + Number(v);
  }
  return out;
}

export function parseHoursCsv(text: string): number[] {
  const rows = rowsOf(text);
  const [t, s] = columns(rows[0]);
  const hours = new Array(24).fill(0);
  for (const r of rows.slice(1)) {
    const v = (r[s] ?? "").trim();
    if (v) hours[Number(r[t].slice(0, 2))] += Number(v);
  }
  return hours;
}

function percentile(values: number[], q: number): number {
  const v = [...values].sort((a, b) => a - b);
  const pos = (v.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
  return v[lo] + (v[hi] - v[lo]) * (pos - lo);
}

export function hourlyProfile(perDay: Record<string, number[]>, daily: Record<string, number>, recentDays = RECENT_DAYS): number[] | null {
  const dates = Object.keys(daily).sort();
  if (!dates.length) return null;
  const start = addDays(dates[dates.length - 1], -(recentDays - 1));
  const recent: Record<string, number> = Object.fromEntries(Object.entries(daily).filter(([d]) => d >= start));
  const valid = Object.values(recent).filter((v) => v >= MISSING_BELOW);
  if (!valid.length) return null;
  const cut = Math.max(percentile(valid, 0.7), MISSING_BELOW);
  const shares = Object.entries(perDay)
    .filter(([d, h]) => (recent[d] ?? 0) >= cut && h.reduce((a, b) => a + b, 0) > 0)
    .map(([, h]) => { const t = h.reduce((a, b) => a + b, 0); return h.map((x) => x / t); });
  if (shares.length < 10) return null;
  return shares[0].map((_, i) => shares.reduce((a, s) => a + s[i], 0) / shares.length);
}

export async function readExport(file: File): Promise<StepsData> {
  if (!file.name.toLowerCase().endsWith(".zip")) return { daily: parseDailyCsv(await file.text()), perDayHours: {} };
  const zip = await JSZip.loadAsync(file);
  let daily: Record<string, number> | null = null;
  const perDayHours: Record<string, number[]> = {};
  for (const entry of Object.values(zip.files)) {
    if (entry.dir) continue;
    const name = entry.name.toLowerCase();
    const m = entry.name.match(DAY_FILE);
    if (name.endsWith(DAILY_NAME)) daily = parseDailyCsv(await entry.async("string"));
    else if (m) perDayHours[m[1]] = parseHoursCsv(await entry.async("string"));
  }
  if (!daily) throw new Error("No 'Daily activity metrics.csv' found. Export Google Fit with Google Takeout.");
  return { daily, perDayHours };
}
