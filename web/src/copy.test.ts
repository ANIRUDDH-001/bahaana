import { describe, expect, it } from "vitest";
import { evidenceLine, sensitivityLine } from "./copy";
import type { Verdict } from "./types";

const v = (over: Partial<Verdict>): Verdict => ({ excuse: "rain", verdict: "OVERRULED", present_today: true, claimed: false, sensitivity_pts: -2.1,
  evidence: { n_present: 14, k_present: 8, n_absent: 237, k_absent: 123, diff_ci: [-0.21, 0.31], ci_method: "7-day block bootstrap" }, ...over });

describe("copy", () => {
  it("states the precedent with numbers", () => expect(evidenceLine(v({}))).toBe("You were active on 8 of 14 rainy days (57%), vs 52% on dry days."));
  it("handles an excuse that never happened", () => {
    const never = v({ excuse: "air", sensitivity_pts: null, verdict: "UNCLEAR", evidence: { n_present: 0, k_present: 0, n_absent: 200, k_absent: 60, diff_ci: null, ci_method: "7-day block bootstrap" } });
    expect(evidenceLine(never)).toContain("No bad-air days");
    expect(sensitivityLine(never)).toContain("nothing to compare");
  });
  it("words sensitivity in points", () => expect(sensitivityLine(v({ sensitivity_pts: -12.4 }))).toBe("Today, this excuse lowers the model's likelihood by 12.4 points."));
});
