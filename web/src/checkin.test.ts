import { describe, expect, it } from "vitest";
import { checkinDay, stepsAllowed } from "./checkin";

const run = { date: "2026-10-07", tz: "Asia/Kolkata", mode: "live" as const };

describe("check-in timing (spec §4.1: after 6 PM or next morning)", () => {
  it("files the check-in under the run's date, not the browser's", () => {
    expect(checkinDay(run, new Date("2026-10-07T20:00:00Z"))).toBe("2026-10-07"); // 01:30 Oct 8 in Kolkata, next morning
  });
  it("refuses today's step total before 6 PM in the city's timezone", () => {
    expect(stepsAllowed(run, new Date("2026-10-07T03:05:00Z"))).toBe(false); // 08:35 IST
    expect(stepsAllowed(run, new Date("2026-10-07T12:31:00Z"))).toBe(true);  // 18:01 IST
  });
  it("accepts the total the next morning", () => expect(stepsAllowed(run, new Date("2026-10-08T02:00:00Z"))).toBe(true));
  it("never saves steps from the demo", () => expect(stepsAllowed({ ...run, mode: "demo" }, new Date("2026-10-07T15:00:00Z"))).toBe(false));
});
