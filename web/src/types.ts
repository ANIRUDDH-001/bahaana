export type ExcuseId = "heat" | "rain" | "air" | "workday" | "tired";
export type VerdictKind = "UPHELD" | "OVERRULED" | "UNCLEAR";
export interface DailyWeather { feels_max: number | null; rain_mm: number | null; rain_hours: number | null; wind_max: number | null; cloud_mean: number | null }
export interface Day extends DailyWeather { steps: number | null; weekday: number; holiday: 0 | 1; pm25: number | null }
export interface Today extends DailyWeather { weekday: number; holiday: 0 | 1 }
export interface VerdictRequest { history: Day[]; today: Today; claimed_excuse: ExcuseId | null }
export interface Evidence { n_present: number; k_present: number; n_absent: number; k_absent: number; diff_ci: [number, number] | null; ci_method: string }
export interface Verdict { excuse: ExcuseId; verdict: VerdictKind; present_today: boolean; claimed: boolean; sensitivity_pts: number | null; evidence: Evidence }
export interface VerdictResponse { probability: number; n_context_days: number; verdicts: Verdict[]; model: string }
export type Win = [number, number];
export interface HourWeather { hour: number; feels: number | null; precip: number | null }
export interface ModelScore { auc: number; brier: number; f1: number; auc_ci: [number, number]; brier_ci: [number, number]; f1_ci: [number, number] }
export interface BacktestSummary { n_predictions: number; prevalence: number; models: Record<string, ModelScore>; ci_method: string; calibration: { lo: number; hi: number; n: number; mean_p: number | null; rate: number | null }[]; auc_diff_tabpfn_minus_logistic?: { point: number; ci: [number, number] } }
export interface FieldEntry { date: string; probability: number | null; top: string | null; went: boolean | null; minutes: number | null; steps: number | null; note: string | null }
export interface DemoBundle { label: string; frozen_on: string; request: VerdictRequest; response: VerdictResponse; window: Win | null; backtest: BacktestSummary | null; field: FieldEntry[] }
