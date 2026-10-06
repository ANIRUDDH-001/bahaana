import { describe, expect, it } from "vitest";
import { buildRequest, historyProblem, historyStart, usableSteps } from "./payload";
import { parseDailyCsv } from "./takeout";

describe("buildRequest", () => {
  const daily = { "2026-08-26": 9000, "2026-08-27": 8000, "2026-09-02": 7000, "2026-09-03": 5000 };
  const req = buildRequest(daily, {}, {}, "2026-09-03", "rain");
  it("fills gaps with null steps instead of dropping days", () => {
    expect(req.history).toHaveLength(8); // Aug 26 .. Sep 2
    expect(req.history[2].steps).toBeNull();
  });
  it("never sends today's partial steps or any date string", () => {
    expect(req.history.at(-1)!.steps).toBe(7000);
    expect(JSON.stringify(req)).not.toMatch(/\d{4}-\d{2}-\d{2}/);
  });
  it("marks holidays and weekdays", () => {
    expect(req.history[0].holiday).toBe(1); // Aug 26 Milad-un-Nabi
    expect(req.today.weekday).toBe(3);      // Sep 3, 2026 is a Thursday
  });
});

describe("Takeout CSV to request (the real path, end to end)", () => {
  // Shaped like the real export: a missing 5-day stretch, a blank row, and location columns.
  const CSV = "Date,Move Minutes count,Low latitude (deg),Low longitude (deg),Step count\n" +
    "2026-08-26,30,28.61,77.2,9000\n2026-08-27,20,,,8000\n2026-08-28,,,,\n" +
    "2026-09-02,25,,,7000\n2026-09-03,5,,,1500\n";
  const req = buildRequest(parseDailyCsv(CSV), {}, {}, "2026-09-03", null);
  it("keeps every calendar day, in order, with nulls in the gap", () => {
    expect(req.history.map((d) => d.steps)).toEqual([9000, 8000, null, null, null, null, null, 7000]);
    expect(req.history.map((d) => d.weekday)).toEqual([2, 3, 4, 5, 6, 0, 1, 2]); // Wed Aug 26 .. Wed Sep 2
  });
  it("sends no dates and no location", () => {
    const body = JSON.stringify(req);
    expect(body).not.toMatch(/\d{4}-\d{2}-\d{2}/);
    expect(body).not.toContain("28.61");
    expect(body).not.toContain("77.2");
  });
});

describe("usableSteps (mirrors cli.usable_steps)", () => {
  const daily = { "2026-10-04": 9000, "2026-10-05": 8000, "2026-10-06": 1200 }; // export taken on Oct 6
  it("drops the export's partial last day", () =>
    expect(usableSteps(daily, {}, "2026-10-07")).toEqual({ "2026-10-04": 9000, "2026-10-05": 8000 }));
  it("lets a check-in supply that day", () => expect(usableSteps(daily, { "2026-10-06": 7400 }, "2026-10-08")["2026-10-06"]).toBe(7400));
  it("never includes today", () => expect(usableSteps(daily, { "2026-10-07": 5000 }, "2026-10-07")["2026-10-07"]).toBeUndefined());
  it("lets a complete export day win over a check-in", () => expect(usableSteps(daily, { "2026-10-04": 3100 }, "2026-10-07")["2026-10-04"]).toBe(9000));
});

describe("history limits", () => {
  it("starts at most 1000 days before today (mirrors cli.history_start)", () => {
    expect(historyStart({ "2014-03-01": 5000, "2026-10-01": 6000 }, "2026-10-07")).toBe("2024-01-11");
    expect(historyStart({ "2026-01-01": 5000 }, "2026-10-07")).toBe("2026-01-01");
  });
  it("explains a history that is too short before calling the server", () => {
    const short = buildRequest({ "2026-08-01": 5000 }, {}, {}, "2026-09-28", null); // 58 days
    expect(historyProblem(short)).toBe("Bahaana needs at least two months of steps.");
    expect(historyProblem(buildRequest({ "2026-07-01": 5000 }, {}, {}, "2026-09-28", null))).toBeNull();
  });
});
