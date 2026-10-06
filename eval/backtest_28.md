# Backtest (28)

205 out-of-sample days; observed active share 31.2%. 95% intervals: 7-day block bootstrap, 1000 resamples.

| Model | ROC-AUC | Brier | F1 @0.5 |
|---|---|---|---|
| TabPFN v2 | 0.557 [0.446, 0.6525] | 0.213 [0.1788, 0.2464] | 0.231 [0.0588, 0.3889] |
| Same as yesterday | 0.538 [0.4073, 0.6532] | 0.211 [0.1766, 0.2442] | 0.000 [0.0, 0.0] |
| Weekday base rate | 0.552 [0.4784, 0.6255] | 0.222 [0.1925, 0.2531] | 0.145 [0.0563, 0.2201] |
| Logistic regression | 0.594 [0.4758, 0.6934] | 0.228 [0.1867, 0.2672] | 0.407 [0.234, 0.5439] |

TabPFN − logistic ROC-AUC: -0.037 (95% [-0.0889, 0.0135], paired blocks).

| Predicted | n | mean predicted | observed |
|---|---|---|---|
| 0.0–0.2 | 30 | 0.166 | 0.4 |
| 0.2–0.4 | 147 | 0.282 | 0.259 |
| 0.4–0.6 | 19 | 0.463 | 0.421 |
| 0.6–0.8 | 6 | 0.693 | 0.833 |
| 0.8–1.0 | 3 | 0.841 | 0.333 |
