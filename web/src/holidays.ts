import data from "../../shared/holidays_2026.json";
export const HOLIDAYS: Set<string> = new Set(data.dates);
