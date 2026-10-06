import { expect, it } from "vitest";
import c from "../../shared/fixtures/window_case.json";
import { goodWindow } from "./window";

it("matches the shared fixture", () => expect(goodWindow(c.profile, c.hours, c.now_hour)).toEqual(c.expected));
it("returns null when no hour is comfortable", () =>
  expect(goodWindow(new Array(24).fill(1 / 24), Array.from({ length: 24 }, (_, h) => ({ hour: h, feels: 40, precip: 0 })), 6)).toBeNull());
