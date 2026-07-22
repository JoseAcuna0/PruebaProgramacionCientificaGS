import math
import time
from typing import Dict, Tuple

import numba
import numpy as np


@numba.njit
def category_stats(
    prices: np.ndarray, type_ids: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    unique_types = np.unique(type_ids)
    num_types = len(unique_types)

    counts = np.zeros(num_types, dtype=np.int64)
    mins = np.zeros(num_types, dtype=np.float64)
    maxs = np.zeros(num_types, dtype=np.float64)
    means = np.zeros(num_types, dtype=np.float64)
    stds = np.zeros(num_types, dtype=np.float64)

    for i in range(num_types):
        t_id = unique_types[i]
        n = 0
        sum_val = 0.0
        min_val = 1e12
        max_val = -1e12

        for j in range(len(prices)):
            if type_ids[j] == t_id:
                val = prices[j]
                n += 1
                sum_val += val
                if val < min_val:
                    min_val = val
                if val > max_val:
                    max_val = val

        if n > 0:
            mean_val = sum_val / n
            sum_sq_diff = 0.0
            for j in range(len(prices)):
                if type_ids[j] == t_id:
                    diff = prices[j] - mean_val
                    sum_sq_diff += diff * diff

            var_val = sum_sq_diff / n
            std_val = math.sqrt(var_val)

            counts[i] = n
            mins[i] = min_val
            maxs[i] = max_val
            means[i] = mean_val
            stds[i] = std_val

    return unique_types, counts, mins, maxs, means, stds


@numba.njit
def price_zscores(prices: np.ndarray, type_ids: np.ndarray) -> np.ndarray:
    unique_types, _, _, _, means, stds = category_stats(prices, type_ids)
    n_samples = len(prices)
    z_scores = np.zeros(n_samples, dtype=np.float64)

    for i in range(n_samples):
        p = prices[i]
        t_id = type_ids[i]

        cat_index = -1
        for j in range(len(unique_types)):
            if unique_types[j] == t_id:
                cat_index = j
                break

        if cat_index != -1:
            m = means[cat_index]
            s = stds[cat_index]
            if s > 1e-9:
                z_scores[i] = (p - m) / s
            else:
                z_scores[i] = 0.0

    return z_scores


def price_zscores_pure_python(prices: np.ndarray, type_ids: np.ndarray) -> np.ndarray:
    n_samples = len(prices)
    unique_types_list = []
    for t in type_ids:
        if t not in unique_types_list:
            unique_types_list.append(t)

    means_dict = {}
    stds_dict = {}

    for t_id in unique_types_list:
        cat_prices = []
        for i in range(n_samples):
            if type_ids[i] == t_id:
                cat_prices.append(prices[i])

        if len(cat_prices) > 0:
            m = sum(cat_prices) / len(cat_prices)
            var = sum((x - m) ** 2 for x in cat_prices) / len(cat_prices)
            s = math.sqrt(var)
            means_dict[t_id] = m
            stds_dict[t_id] = s

    z_scores = np.zeros(n_samples, dtype=np.float64)
    for i in range(n_samples):
        t_id = type_ids[i]
        p = prices[i]
        m = means_dict[t_id]
        s = stds_dict[t_id]
        if s > 1e-9:
            z_scores[i] = (p - m) / s
        else:
            z_scores[i] = 0.0

    return z_scores


def run_benchmark(prices: np.ndarray, type_ids: np.ndarray) -> Dict[str, float]:
    _ = price_zscores(prices, type_ids)

    start_py = time.perf_counter()
    _ = price_zscores_pure_python(prices, type_ids)
    end_py = time.perf_counter()
    time_py = end_py - start_py

    start_nb = time.perf_counter()
    _ = price_zscores(prices, type_ids)
    end_nb = time.perf_counter()
    time_nb = end_nb - start_nb

    speedup = time_py / time_nb if time_nb > 0 else 0.0

    return {
        "python_time_sec": time_py,
        "numba_time_sec": time_nb,
        "speedup": speedup,
    }
