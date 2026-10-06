// weather.ts — must stay identical to src/bahaana/weather.py (shared fixture test).
import type { DailyWeather, HourWeather } from "./types";

const PREVIOUS_RUNS = "https://previous-runs-api.open-meteo.com/v1/forecast";
const AIR_QUALITY = "https://air-quality-api.open-meteo.com/v1/air-quality";
const GEOCODING = "https://geocoding-api.open-meteo.com/v1/search";
export const FEELS = "apparent_temperature_previous_day1", PRECIP = "precipitation_previous_day1",
  WIND = "wind_speed_10m_previous_day1", CLOUD = "cloud_cover_previous_day1";
export type Hourly = Record<string, (number | null)[]> & { time: string[] };

export const r3 = (x: number) => Math.floor(x * 1000 + 0.5) / 1000;

function byDay(times: string[]): Map<string, number[]> {
  const m = new Map<string, number[]>();
  times.forEach((t, i) => { const d = t.slice(0, 10); (m.get(d) ?? m.set(d, []).get(d)!).push(i); });
  return m;
}
const vals = (col: (number | null)[], idx: number[]) => idx.map((i) => col[i]).filter((v): v is number => v !== null);
const sum = (a: number[]) => a.reduce((x, y) => x + y, 0);

export function aggregateDaily(h: Hourly): Record<string, DailyWeather> {
  const out: Record<string, DailyWeather> = {};
  for (const [day, idx] of byDay(h.time)) {
    const f = vals(h[FEELS], idx), p = vals(h[PRECIP], idx), w = vals(h[WIND], idx), c = vals(h[CLOUD], idx);
    out[day] = {
      feels_max: f.length ? r3(Math.max(...f)) : null,
      rain_mm: p.length ? r3(sum(p)) : null,
      rain_hours: p.length ? p.filter((x) => x >= 0.1).length : null,
      wind_max: w.length ? r3(Math.max(...w)) : null,
      cloud_mean: c.length ? r3(sum(c) / c.length) : null,
    };
  }
  return out;
}

export function aggregatePm25(h: Hourly): Record<string, number | null> {
  const out: Record<string, number | null> = {};
  for (const [day, idx] of byDay(h.time)) { const v = vals(h.pm2_5, idx); out[day] = v.length ? r3(sum(v) / v.length) : null; }
  return out;
}

export const hoursFor = (h: Hourly, day: string): HourWeather[] =>
  h.time.flatMap((t, i) => (t.slice(0, 10) === day ? [{ hour: Number(t.slice(11, 13)), feels: h[FEELS][i], precip: h[PRECIP][i] }] : []));

async function getJson(url: string, params: Record<string, string | number>) {
  const r = await fetch(`${url}?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`);
  if (!r.ok) throw new Error(`Weather service error (${r.status}).`);
  return r.json();
}

export async function geocode(city: string) {
  const res = (await getJson(GEOCODING, { name: city, count: 1, language: "en", format: "json" })).results ?? [];
  if (!res.length) throw new Error(`Couldn't find a place called '${city}'.`);
  const g = res[0];
  return { name: g.name as string, lat: Math.round(g.latitude * 10) / 10, lon: Math.round(g.longitude * 10) / 10, timezone: g.timezone as string };
}

export const fetchWeatherHourly = async (lat: number, lon: number, tz: string, start: string, end: string): Promise<Hourly> =>
  (await getJson(PREVIOUS_RUNS, { latitude: lat, longitude: lon, timezone: tz, start_date: start, end_date: end, hourly: [FEELS, PRECIP, WIND, CLOUD].join(",") })).hourly;

export const fetchPm25Hourly = async (lat: number, lon: number, tz: string, start: string, end: string): Promise<Hourly> =>
  (await getJson(AIR_QUALITY, { latitude: lat, longitude: lon, timezone: tz, start_date: start, end_date: end, hourly: "pm2_5" })).hourly;
