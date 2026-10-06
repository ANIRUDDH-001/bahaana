import { expect, it } from "vitest";
import { esc, percent, windowText } from "./render";

it("escapes city names", () => expect(esc(`<b>"x"</b>`)).toBe("&lt;b&gt;&quot;x&quot;&lt;/b&gt;"));
it("formats", () => { expect(percent(0.784)).toBe("78%"); expect(windowText([17, 19])).toBe("5 PM – 7 PM"); expect(windowText(null)).toBe("No good window today"); });
