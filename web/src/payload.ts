// payload.ts — builds the exact body the server sees: ordered days, no dates, no location.
import { addDays, dateRange, weekdayOf } from "./dates";
import { HOLIDAYS } from "./holidays";
import type { DailyWeather, Day, ExcuseId, VerdictRequest } from "./types";

const MAX_ROWS = 1000;
const EMPTY: DailyWeather = { feels_max: null, rain_mm: null, rain_hours: null, wind_max: null, cloud_mean: null };
const pick = (w?: DailyWeather): DailyWeather => (w ? { feels_max: w.feels_max, rain_mm: w.rain_mm, rain_hours: w.rain_hours, wind_max: w.wind_max, cloud_mean: w.cloud_mean } : { ...EMPTY });

const MIN_ROWS = 60;

/** Mirrors cli.usable_steps: the export's last day is the day it was taken (partial), unless a check-in supplies it.
 *  Complete export days win over check-ins. */
export function usableSteps(daily: Record<string, number>, checkins: Record<string, number>, today: string): Record<string, number> {
  const last = Object.keys(daily).sort().at(-1);
  const steps: Record<string, number> = { ...checkins, ...Object.fromEntries(Object.entries(daily).filter(([d]) => d !== last)) };
  return Object.fromEntries(Object.entries(steps).filter(([d]) => d < today));
}

/** Mirrors cli.history_start: at most MAX_ROWS days, so old exports never ask for unarchived forecasts. */
export function historyStart(daily: Record<string, number>, today: string): string {
  const first = Object.keys(daily).sort()[0];
  const floor = addDays(today, -MAX_ROWS);
  return first > floor ? first : floor;
}

/** Spec §13: a readable message before waking the server for a history it would reject. */
export const historyProblem = (req: VerdictRequest): string | null =>
  req.history.length < MIN_ROWS ? "Bahaana needs at least two months of steps." : null;

export function buildRequest(daily: Record<string, number>, weather: Record<string, DailyWeather>,
  pm25: Record<string, number | null>, todayDate: string, claimed: ExcuseId | null): VerdictRequest {
  const dates = Object.keys(daily).filter((d) => d < todayDate).sort();
  if (!dates.length) throw new Error("No step history before today.");
  const history: Day[] = dateRange(dates[0], addDays(todayDate, -1)).slice(-MAX_ROWS).map((d) => ({
    steps: daily[d] ?? null, weekday: weekdayOf(d), holiday: HOLIDAYS.has(d) ? 1 : 0, ...pick(weather[d]), pm25: pm25[d] ?? null,
  }));
  return { history, today: { weekday: weekdayOf(todayDate), holiday: HOLIDAYS.has(todayDate) ? 1 : 0, ...pick(weather[todayDate]) }, claimed_excuse: claimed };
}
