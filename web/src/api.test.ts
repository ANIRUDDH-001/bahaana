import { expect, it } from "vitest";
import { errorDetail } from "./api";

it("passes the engine's readable message through", () =>
  expect(errorDetail({ detail: "Your history needs both active and quieter days to learn from." })).toBe("Your history needs both active and quieter days to learn from."));
it("turns a validation list into a sentence instead of a generic error", () =>
  expect(errorDetail({ detail: [{ msg: "List should have at least 60 items after validation, not 45" }] })).toBe("Bahaana needs at least two months of steps."));
it("falls back to a plain message", () => expect(errorDetail({})).toBe("The model couldn't read that history."));
