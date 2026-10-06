// checkin.ts — when and under which date a check-in may record the day's step total (spec §4.1, §9).
import { hourIn, todayIn } from "./dates";

/** Saved when the person taps I'M GOING: the day that was predicted, in the city's timezone. */
export interface Run { date: string; tz: string; mode: "demo" | "live" }
const EVENING = 18;

export const checkinDay = (run: Run, _now: Date = new Date()) => run.date;

/** A step total is only complete after 6 PM on the day, or any time after it. Demo runs never write steps. */
export function stepsAllowed(run: Run, now: Date = new Date()): boolean {
  if (run.mode !== "live") return false;
  return todayIn(run.tz, now) > run.date || hourIn(run.tz, now) >= EVENING;
}
