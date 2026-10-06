"""TabPFN v2 wrapper. Loads the checkpoint by absolute path so no Prior Labs login is needed."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from bahaana.schema import WEEKDAY_IDX

ROOT = Path(__file__).resolve().parents[2]


def ckpt_path() -> Path:
    return Path(os.environ.get("BAHAANA_TABPFN_CKPT", ROOT / "models" / "tabpfn-v2-classifier.ckpt")).resolve()


def make_classifier():
    from tabpfn import TabPFNClassifier
    from tabpfn.constants import ModelVersion

    return TabPFNClassifier.create_default_for_version(
        ModelVersion.V2,
        model_path=str(ckpt_path()),
        device="cpu",
        categorical_features_indices=[WEEKDAY_IDX],
        random_state=0,
    )


class TabPFNModel:
    name = "TabPFN v2"

    def __init__(self) -> None:
        self._clf = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "TabPFNModel":
        self._clf = make_classifier()
        self._clf.fit(X.to_numpy(dtype=float), y.to_numpy(dtype=int))
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        proba = self._clf.predict_proba(X.to_numpy(dtype=float))
        return proba[:, list(self._clf.classes_).index(1)]
