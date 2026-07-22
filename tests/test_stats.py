import numpy as np
from app.stats import category_stats, price_zscores


def test_category_stats_numba() -> None:
    prices = np.array([10.0, 20.0, 30.0, 100.0], dtype=float)
    type_ids = np.array([1, 1, 1, 2], dtype=int)

    u_types, counts, mins, maxs, means, stds = category_stats(prices, type_ids)

    assert len(u_types) == 2
    assert counts[0] == 3
    assert mins[0] == 10.0
    assert maxs[0] == 30.0
    assert abs(means[0] - 20.0) < 1e-5
    assert counts[1] == 1
    assert mins[1] == 100.0


def test_price_zscores_numba() -> None:
    prices = np.array([10.0, 20.0, 30.0], dtype=float)
    type_ids = np.array([1, 1, 1], dtype=int)

    z_scores = price_zscores(prices, type_ids)

    assert len(z_scores) == 3
    assert abs(z_scores[1]) < 1e-5
    assert z_scores[0] < 0
    assert z_scores[2] > 0