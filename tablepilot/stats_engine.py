"""
Statistics engine module - Comprehensive statistical analysis for tabular data.
Zero external dependencies - pure Python implementation.
"""

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


def _is_numeric(values: List[Any]) -> bool:
    """Check if a list of values is predominantly numeric."""
    non_none = [v for v in values if v is not None]
    if not non_none:
        return False
    numeric_count = sum(1 for v in non_none if isinstance(v, (int, float)) and not isinstance(v, bool))
    return numeric_count / len(non_none) >= 0.8


def _numeric_values(values: List[Any]) -> List[float]:
    """Extract numeric values from a list, filtering out None and non-numeric."""
    result = []
    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            result.append(float(v))
        else:
            try:
                result.append(float(v))
            except (ValueError, TypeError):
                continue
    return result


def count(values: List[Any]) -> Dict[str, int]:
    """Count total, non-null, and null values."""
    total = len(values)
    non_null = sum(1 for v in values if v is not None)
    return {
        "total": total,
        "non_null": non_null,
        "null": total - non_null,
        "null_pct": round((total - non_null) / total * 100, 1) if total > 0 else 0,
    }


def unique_count(values: List[Any]) -> Dict[str, int]:
    """Count unique and duplicate values."""
    non_none = [v for v in values if v is not None]
    unique = set(str(v) for v in non_none)
    return {
        "unique": len(unique),
        "duplicates": len(non_none) - len(unique),
        "unique_pct": round(len(unique) / len(non_none) * 100, 1) if non_none else 0,
    }


def mean(values: List[float]) -> Optional[float]:
    """Calculate arithmetic mean."""
    if not values:
        return None
    return sum(values) / len(values)


def median(values: List[float]) -> Optional[float]:
    """Calculate median value."""
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return sorted_vals[n // 2]
    return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2


def mode(values: List[Any]) -> List[Any]:
    """Calculate mode (most frequent values)."""
    non_none = [v for v in values if v is not None]
    if not non_none:
        return []
    counter = Counter(non_none)
    max_count = counter.most_common(1)[0][1]
    return [v for v, c in counter.items() if c == max_count]


def variance(values: List[float], sample: bool = True) -> Optional[float]:
    """Calculate variance."""
    if len(values) < 2:
        return None
    m = mean(values)
    if m is None:
        return None
    n = len(values)
    divisor = n - 1 if sample else n
    return sum((x - m) ** 2 for x in values) / divisor


def std_dev(values: List[float], sample: bool = True) -> Optional[float]:
    """Calculate standard deviation."""
    v = variance(values, sample)
    return math.sqrt(v) if v is not None and v >= 0 else None


def skewness(values: List[float]) -> Optional[float]:
    """Calculate skewness (asymmetry of distribution)."""
    if len(values) < 3:
        return None
    m = mean(values)
    s = std_dev(values)
    if m is None or s is None or s == 0:
        return None
    n = len(values)
    return sum((x - m) ** 3 for x in values) / (n * s ** 3)


def kurtosis(values: List[float]) -> Optional[float]:
    """Calculate excess kurtosis (tailedness of distribution)."""
    if len(values) < 4:
        return None
    m = mean(values)
    s = std_dev(values)
    if m is None or s is None or s == 0:
        return None
    n = len(values)
    return sum((x - m) ** 4 for x in values) / (n * s ** 4) - 3


def percentile(values: List[float], p: float) -> Optional[float]:
    """Calculate percentile value (0-100)."""
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    k = (p / 100) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def min_max(values: List[float]) -> Dict[str, Optional[float]]:
    """Calculate minimum and maximum values."""
    if not values:
        return {"min": None, "max": None, "range": None}
    return {
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


def sum_values(values: List[float]) -> Optional[float]:
    """Calculate sum of values."""
    return sum(values) if values else None


def cv(values: List[float]) -> Optional[float]:
    """Calculate coefficient of variation."""
    m = mean(values)
    s = std_dev(values)
    if m is None or s is None or s == 0 or m == 0:
        return None
    return s / abs(m)


def descriptive_stats(values: List[Any]) -> Dict[str, Any]:
    """Calculate comprehensive descriptive statistics for a column."""
    counts = count(values)
    uniques = unique_count(values)
    numeric = _is_numeric(values)
    num_vals = _numeric_values(values) if numeric else []

    result = {
        "type": "numeric" if numeric else "categorical",
        "count": counts,
        "unique": uniques,
    }

    if numeric and num_vals:
        result.update({
            "mean": round(mean(num_vals), 4) if mean(num_vals) is not None else None,
            "median": round(median(num_vals), 4) if median(num_vals) is not None else None,
            "mode": mode(values),
            "std": round(std_dev(num_vals), 4) if std_dev(num_vals) is not None else None,
            "var": round(variance(num_vals), 4) if variance(num_vals) is not None else None,
            "min": round(min(num_vals), 4),
            "max": round(max(num_vals), 4),
            "range": round(max(num_vals) - min(num_vals), 4),
            "skewness": round(skewness(num_vals), 4) if skewness(num_vals) is not None else None,
            "kurtosis": round(kurtosis(num_vals), 4) if kurtosis(num_vals) is not None else None,
            "sum": round(sum(num_vals), 4),
            "cv": round(cv(num_vals), 4) if cv(num_vals) is not None else None,
            "percentiles": {
                "p1": round(percentile(num_vals, 1), 4) if percentile(num_vals, 1) is not None else None,
                "p5": round(percentile(num_vals, 5), 4) if percentile(num_vals, 5) is not None else None,
                "p25": round(percentile(num_vals, 25), 4) if percentile(num_vals, 25) is not None else None,
                "p50": round(percentile(num_vals, 50), 4) if percentile(num_vals, 50) is not None else None,
                "p75": round(percentile(num_vals, 75), 4) if percentile(num_vals, 75) is not None else None,
                "p95": round(percentile(num_vals, 95), 4) if percentile(num_vals, 95) is not None else None,
                "p99": round(percentile(num_vals, 99), 4) if percentile(num_vals, 99) is not None else None,
            },
            "iqr": round(
                (percentile(num_vals, 75) or 0) - (percentile(num_vals, 25) or 0), 4
            ),
        })
    else:
        # Categorical statistics
        non_none = [v for v in values if v is not None]
        freq = Counter(str(v) for v in non_none)
        top_n = freq.most_common(10)
        result.update({
            "top_values": [{"value": v, "count": c, "pct": round(c / len(non_none) * 100, 1)} for v, c in top_n],
            "cardinality": len(freq),
        })

    return result


def correlation(x: List[float], y: List[float]) -> Optional[float]:
    """Calculate Pearson correlation coefficient between two numeric lists."""
    # Align non-None pairs
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    pairs = [(float(a), float(b)) for a, b in pairs]

    if len(pairs) < 3:
        return None

    n = len(pairs)
    sum_x = sum(p[0] for p in pairs)
    sum_y = sum(p[1] for p in pairs)
    sum_xy = sum(p[0] * p[1] for p in pairs)
    sum_x2 = sum(p[0] ** 2 for p in pairs)
    sum_y2 = sum(p[1] ** 2 for p in pairs)

    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))

    if denominator == 0:
        return None

    return round(numerator / denominator, 4)


def correlation_matrix(table) -> Dict[str, Dict[str, Optional[float]]]:
    """Calculate pairwise Pearson correlation for all numeric columns.

    Args:
        table: DataTable instance

    Returns:
        Dictionary of correlation values
    """
    numeric_cols = []
    for col in table.columns:
        vals = table.column(col)
        if _is_numeric(vals):
            numeric_cols.append(col)

    if len(numeric_cols) < 2:
        return {}

    # Pre-extract numeric values
    col_data = {col: _numeric_values(table.column(col)) for col in numeric_cols}

    matrix = {}
    for col1 in numeric_cols:
        matrix[col1] = {}
        for col2 in numeric_cols:
            if col1 == col2:
                matrix[col1][col2] = 1.0
            else:
                matrix[col1][col2] = correlation(col_data[col1], col_data[col2])

    return matrix


def detect_outliers_iqr(values: List[Any]) -> Dict[str, Any]:
    """Detect outliers using IQR (Interquartile Range) method.

    Returns dict with outlier indices, values, and bounds.
    """
    num_vals = _numeric_values(values)
    if len(num_vals) < 4:
        return {"outliers": [], "count": 0, "lower_bound": None, "upper_bound": None, "method": "iqr"}

    q1 = percentile(num_vals, 25)
    q3 = percentile(num_vals, 75)
    iqr = q3 - q1 if q1 is not None and q3 is not None else 0

    lower = q1 - 1.5 * iqr if q1 is not None else None
    upper = q3 + 1.5 * iqr if q3 is not None else None

    outlier_indices = []
    outlier_values = []
    for i, v in enumerate(values):
        if v is None:
            continue
        try:
            fv = float(v)
            if lower is not None and fv < lower:
                outlier_indices.append(i)
                outlier_values.append(fv)
            elif upper is not None and fv > upper:
                outlier_indices.append(i)
                outlier_values.append(fv)
        except (ValueError, TypeError):
            continue

    return {
        "outliers": outlier_values,
        "count": len(outlier_values),
        "lower_bound": round(lower, 4) if lower is not None else None,
        "upper_bound": round(upper, 4) if upper is not None else None,
        "method": "iqr",
        "pct": round(len(outlier_values) / len(num_vals) * 100, 1) if num_vals else 0,
    }


def detect_outliers_zscore(values: List[Any], threshold: float = 3.0) -> Dict[str, Any]:
    """Detect outliers using Z-score method.

    Returns dict with outlier indices, values, and threshold.
    """
    num_vals = _numeric_values(values)
    if len(num_vals) < 3:
        return {"outliers": [], "count": 0, "threshold": threshold, "method": "zscore"}

    m = mean(num_vals)
    s = std_dev(num_vals)
    if m is None or s is None or s == 0:
        return {"outliers": [], "count": 0, "threshold": threshold, "method": "zscore"}

    outlier_values = []
    for v in num_vals:
        z = abs((v - m) / s)
        if z > threshold:
            outlier_values.append(v)

    return {
        "outliers": outlier_values,
        "count": len(outlier_values),
        "threshold": threshold,
        "method": "zscore",
        "pct": round(len(outlier_values) / len(num_vals) * 100, 1) if num_vals else 0,
    }


def chi_squared_independence(col1: List[Any], col2: List[Any]) -> Optional[float]:
    """Perform chi-squared test of independence for two categorical columns.

    Returns chi-squared statistic (no p-value calculation to avoid scipy dependency).
    """
    # Align non-None pairs
    pairs = [(a, b) for a, b in zip(col1, col2) if a is not None and b is not None]
    if len(pairs) < 10:
        return None

    # Build contingency table
    cat1 = [p[0] for p in pairs]
    cat2 = [p[1] for p in pairs]

    cats1 = list(set(cat1))
    cats2 = list(set(cat2))

    if len(cats1) < 2 or len(cats2) < 2:
        return None

    # Observed frequencies
    observed = {}
    for a, b in pairs:
        key = (str(a), str(b))
        observed[key] = observed.get(key, 0) + 1

    # Row and column totals
    row_totals = Counter(str(a) for a in cat1)
    col_totals = Counter(str(b) for b in cat2)
    n = len(pairs)

    # Expected frequencies and chi-squared
    chi2 = 0.0
    for (a, b), obs in observed.items():
        expected = row_totals[a] * col_totals[b] / n
        if expected > 0:
            chi2 += (obs - expected) ** 2 / expected

    return round(chi2, 4)
