// dates.ts — dates are always 'YYYY-MM-DD' strings; arithmetic in UTC so the browser's timezone never matters.
const toUtc = (d: string) => new Date(`${d}T00:00:00Z`);
export const addDays = (d: string, n: number) => new Date(toUtc(d).getTime() + n * 86400000).toISOString().slice(0, 10);
export function dateRange(a: string, b: string): string[] {
  const out: string[] = [];
  for (let d = a; d <= b; d = addDays(d, 1)) out.push(d);
  return out;
}
export const weekdayOf = (d: string) => (toUtc(d).getUTCDay() + 6) % 7; // Monday = 0
export const todayIn = (tz: string, now: Date = new Date()) =>
  new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
export const hourIn = (tz: string, now: Date = new Date()) =>
  Number(new Intl.DateTimeFormat("en-GB", { timeZone: tz, hour: "2-digit", hourCycle: "h23" }).format(now));
