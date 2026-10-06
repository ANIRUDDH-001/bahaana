import { describe, expect, it } from "vitest";
import { addDays, dateRange, hourIn, todayIn, weekdayOf } from "./dates";

describe("dates", () => {
  it("uses Monday = 0 like Python", () => {
    expect(weekdayOf("2026-10-05")).toBe(0);
    expect(weekdayOf("2026-10-04")).toBe(6);
    expect(weekdayOf("2026-01-01")).toBe(3);
  });
  it("ranges across months", () => {
    expect(dateRange("2026-02-27", "2026-03-02")).toEqual(["2026-02-27", "2026-02-28", "2026-03-01", "2026-03-02"]);
    expect(addDays("2026-01-01", -1)).toBe("2025-12-31");
  });
  it("computes today in the city's timezone, not the browser's", () => {
    const now = new Date("2026-10-06T20:00:00Z"); // 01:30 on Oct 7 in Kolkata
    expect(todayIn("Asia/Kolkata", now)).toBe("2026-10-07");
    expect(todayIn("America/Los_Angeles", now)).toBe("2026-10-06");
    expect(hourIn("Asia/Kolkata", now)).toBe(1);
  });
});
