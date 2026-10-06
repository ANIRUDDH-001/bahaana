# Backtest (60)

205 out-of-sample days; observed active share 27.8%. 95% intervals: 7-day block bootstrap, 1000 resamples.

| Model | ROC-AUC | Brier | F1 @0.5 |
|---|---|---|---|
| TabPFN v2 | 0.563 [0.4938, 0.6225] | 0.203 [0.1691, 0.2372] | 0.066 [0.0, 0.1482] |
| Same as yesterday | 0.494 [0.3902, 0.5863] | 0.200 [0.1663, 0.2315] | 0.000 [0.0, 0.0] |
| Weekday base rate | 0.532 [0.4646, 0.6007] | 0.211 [0.1822, 0.242] | 0.135 [0.0357, 0.2222] |
| Logistic regression | 0.577 [0.5013, 0.6469] | 0.226 [0.1868, 0.2645] | 0.276 [0.1481, 0.3826] |

TabPFN − logistic ROC-AUC: -0.013 (95% [-0.0749, 0.045], paired blocks).

| Predicted | n | mean predicted | observed |
|---|---|---|---|
| 0.0–0.2 | 60 | 0.158 | 0.217 |
| 0.2–0.4 | 135 | 0.289 | 0.296 |
| 0.4–0.6 | 8 | 0.484 | 0.5 |
| 0.6–0.8 | 2 | 0.65 | 0.0 |
| 0.8–1.0 | 0 | None | None |
