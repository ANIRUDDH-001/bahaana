import { describe, expect, it } from "vitest";
import hourly from "../../shared/fixtures/weather_hourly.json";
import expected from "../../shared/fixtures/weather_daily.json";
import { aggregateDaily, aggregatePm25, r3 } from "./weather";

describe("weather parity with Python", () => {
  it("matches the shared fixture", () => expect(aggregateDaily(hourly as never)).toEqual(expected));
  it("rounds half up", () => { expect(r3(0.0005)).toBe(0.001); expect(r3(2.4999)).toBe(2.5); });
  it("pm25 skips nulls and keeps all-null days null", () =>
    expect(aggregatePm25({ time: ["2026-07-01T00:00", "2026-07-01T01:00", "2026-07-02T00:00"], pm2_5: [40, null, null] } as never))
      .toEqual({ "2026-07-01": 40, "2026-07-02": null }));
});
