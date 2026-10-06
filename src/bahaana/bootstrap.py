"""7-day block bootstrap: neighbouring days share rolling features and weather, so resample whole weeks."""
from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def block_resamples(positions, block: int = 7, n_boot: int = 1000, seed: int = 0) -> Iterator[np.ndarray]:
    """positions: an int n (rows are consecutive calendar days 0..n-1) or each row's calendar-day position.
    Blocks are calendar weeks (position // block), so a gap never stretches a block past 7 calendar days."""
    rng = np.random.default_rng(seed)
    pos = np.arange(positions) if np.isscalar(positions) else np.asarray(positions)
    week = pos // block
    blocks = [np.flatnonzero(week == w) for w in np.unique(week)]
    for _ in range(n_boot):
        pick = rng.integers(0, len(blocks), size=len(blocks))
        yield np.concatenate([blocks[i] for i in pick])
