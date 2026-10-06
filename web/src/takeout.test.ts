import { describe, expect, it } from "vitest";
import { addDays } from "./dates";
import { hourlyProfile, parseDailyCsv, parseHoursCsv } from "./takeout";

const DAILY = "Date,Move Minutes count,Low latitude (deg),Step count\n2026-01-01,40,28.61,10468\n2026-01-02,,,\n2026-01-04,10,,1200\n";
const HOURS = "Start time,End time,Step count\n00:00:00.000+05:30,00:15:00.000+05:30,11\n07:15:00.000+05:30,07:30:00.000+05:30,400\n07:30:00.000+05:30,07:45:00.000+05:30,600\n";

describe("takeout", () => {
  it("reads only date and steps", () => expect(parseDailyCsv(DAILY)).toEqual({ "2026-01-01": 10468, "2026-01-04": 1200 }));
  it("sums duplicate dates in a simple CSV", () => expect(parseDailyCsv("date,steps\n2026-01-01,100\n2026-01-01,50\n")).toEqual({ "2026-01-01": 150 }));
  it("buckets 15-minute rows into hours", () => { const h = parseHoursCsv(HOURS); expect(h[0]).toBe(11); expect(h[7]).toBe(1000); });
  const peak = (p: number) => Array.from({ length: 24 }, (_, h) => (h === p ? 100 : 0));
  it("needs ten bigger days for a profile", () => {
    const daily: Record<string, number> = {}; const hours: Record<string, number[]> = {};
    for (let i = 0; i < 40; i++) { const d = addDays("2026-01-01", i); daily[d] = 1000 * (i + 1); hours[d] = peak(17); }
    expect(hourlyProfile(hours, daily)![17]).toBe(1);
    expect(hourlyProfile({}, daily)).toBeNull();
  });
  it("uses only the last 90 days", () => {
    const daily: Record<string, number> = {}; const hours: Record<string, number[]> = {};
    for (let i = 0; i < 30; i++) { const d = addDays("2026-01-01", i); daily[d] = 50000; hours[d] = peak(8); }
    for (let i = 0; i < 90; i++) { const d = addDays("2026-01-31", i); daily[d] = 1000 * (i + 1); hours[d] = peak(17); }
    const p = hourlyProfile(hours, daily)!;
    expect(p[17]).toBe(1); expect(p[8]).toBe(0);
  });
  it("keeps no location from the export", () => expect(JSON.stringify(parseDailyCsv(DAILY))).not.toContain("28.61"));
});
