import numpy as np

from bahaana.bootstrap import block_resamples


def test_resamples_are_whole_weekly_blocks():
    out = list(block_resamples(20, block=7, n_boot=50, seed=3))
    assert len(out) == 50
    for idx in out:
        assert idx.min() >= 0 and idx.max() < 20
        starts = [i for i in range(len(idx)) if i == 0 or idx[i] != idx[i - 1] + 1]
        assert all(idx[s] in (0, 7, 14) for s in starts)


def test_deterministic_with_seed():
    a = [x.tolist() for x in block_resamples(30, n_boot=5, seed=1)]
    b = [x.tolist() for x in block_resamples(30, n_boot=5, seed=1)]
    assert a == b


def test_blocks_follow_calendar_positions_across_gaps():
    # rows sit on calendar days 0,1,2 | 9,10 | 15: a gap must not pull day 9 into the first week
    pos = np.array([0, 1, 2, 9, 10, 15])
    groups = {0: [0, 1, 2], 3: [3, 4], 5: [5]}  # row indices per calendar week, keyed by first row
    for idx in block_resamples(pos, block=7, n_boot=30, seed=0):
        i = 0
        while i < len(idx):
            g = groups[int(idx[i])]
            assert idx[i:i + len(g)].tolist() == g
            i += len(g)
