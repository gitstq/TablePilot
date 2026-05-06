"""
Data cleaner module - Data preprocessing and cleaning operations.
Zero external dependencies - pure Python implementation.
"""

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from tablepilot.data_loader import DataTable
from tablepilot.stats_engine import _numeric_values, mean, median, mode, std_dev


def drop_null_rows(table: DataTable) -> DataTable:
    """Drop rows that contain any null/None values."""
    cleaned = [row for row in table._rows if all(v is not None for v in row)]
    return DataTable(table.columns[:], [row[:] for row in cleaned], table.source)


def drop_null_columns(table: DataTable, threshold: float = 0.5) -> DataTable:
    """Drop columns where null percentage exceeds threshold."""
    keep_cols = []
    for i, col in enumerate(table.columns):
        null_count = sum(1 for row in table._rows if row[i] is None)
        null_pct = null_count / len(table._rows) if table._rows else 0
        if null_pct <= threshold:
            keep_cols.append(i)

    new_cols = [table.columns[i] for i in keep_cols]
    new_rows = [[row[i] for i in keep_cols] for row in table._rows]
    return DataTable(new_cols, new_rows, table.source)


def fill_null_values(table: DataTable, strategy: str = "mean", custom_value: Any = None) -> DataTable:
    """Fill null values using specified strategy.

    Args:
        table: DataTable instance
        strategy: 'mean', 'median', 'mode', 'zero', 'forward', 'backward', or 'custom'
        custom_value: Value to use when strategy='custom'
    """
    new_rows = [row[:] for row in table._rows]

    for col_idx, col_name in enumerate(table.columns):
        values = table.column(col_name)
        non_none = [v for v in values if v is not None]

        if not non_none:
            continue

        fill_val = None

        if strategy == "mean":
            num_vals = _numeric_values(values)
            if num_vals:
                fill_val = mean(num_vals)
        elif strategy == "median":
            num_vals = _numeric_values(values)
            if num_vals:
                fill_val = median(num_vals)
        elif strategy == "mode":
            modes = mode(values)
            fill_val = modes[0] if modes else non_none[0]
        elif strategy == "zero":
            fill_val = 0
        elif strategy == "forward":
            last_valid = None
            for row_idx in range(len(new_rows)):
                if new_rows[row_idx][col_idx] is not None:
                    last_valid = new_rows[row_idx][col_idx]
                elif last_valid is not None:
                    new_rows[row_idx][col_idx] = last_valid
            continue
        elif strategy == "backward":
            last_valid = None
            for row_idx in range(len(new_rows) - 1, -1, -1):
                if new_rows[row_idx][col_idx] is not None:
                    last_valid = new_rows[row_idx][col_idx]
                elif last_valid is not None:
                    new_rows[row_idx][col_idx] = last_valid
            continue
        elif strategy == "custom":
            fill_val = custom_value

        if fill_val is not None:
            for row_idx in range(len(new_rows)):
                if new_rows[row_idx][col_idx] is None:
                    new_rows[row_idx][col_idx] = fill_val

    return DataTable(table.columns[:], new_rows, table.source)


def drop_duplicates(table: DataTable, subset: Optional[List[str]] = None) -> DataTable:
    """Drop duplicate rows.

    Args:
        subset: Columns to consider for duplicates (None = all columns)
    """
    if subset:
        indices = [table.columns.index(c) for c in subset if c in table.columns]
    else:
        indices = list(range(len(table.columns)))

    seen = set()
    unique_rows = []
    for row in table._rows:
        key = tuple(row[i] for i in indices)
        str_key = tuple(str(v) if v is not None else None for v in key)
        if str_key not in seen:
            seen.add(str_key)
            unique_rows.append(row[:])

    return DataTable(table.columns[:], unique_rows, table.source)


def strip_whitespace(table: DataTable) -> DataTable:
    """Strip leading/trailing whitespace from all string values."""
    new_rows = []
    for row in table._rows:
        new_row = []
        for v in row:
            if isinstance(v, str):
                new_row.append(v.strip())
            else:
                new_row.append(v)
        new_rows.append(new_row)
    return DataTable(table.columns[:], new_rows, table.source)


def normalize_column(values: List[Any], method: str = "minmax") -> List[float]:
    """Normalize numeric values.

    Args:
        values: List of values
        method: 'minmax' (0-1) or 'zscore' (standard score)
    """
    num_vals = _numeric_values(values)
    if not num_vals:
        return [0.0] * len(values)

    if method == "minmax":
        min_v = min(num_vals)
        max_v = max(num_vals)
        rng = max_v - min_v
        if rng == 0:
            return [0.5] * len(values)
        return [(v - min_v) / rng for v in num_vals]

    elif method == "zscore":
        m = mean(num_vals)
        s = std_dev(num_vals)
        if m is None or s is None or s == 0:
            return [0.0] * len(values)
        return [(v - m) / s for v in num_vals]

    raise ValueError(f"Unknown normalization method: {method}")


def normalize_table(table: DataTable, method: str = "minmax") -> DataTable:
    """Normalize all numeric columns in the table."""
    new_rows = [row[:] for row in table._rows]

    for col_idx, col_name in enumerate(table.columns):
        values = table.column(col_name)
        if not _is_numeric(values):
            continue
        normalized = normalize_column(values, method)
        for row_idx, val in enumerate(normalized):
            if row_idx < len(new_rows):
                new_rows[row_idx][col_idx] = round(val, 6)

    return DataTable(table.columns[:], new_rows, table.source)


def remove_outliers_iqr(table: DataTable, columns: Optional[List[str]] = None) -> DataTable:
    """Remove rows with outlier values using IQR method."""
    from tablepilot.stats_engine import percentile

    if columns is None:
        columns = [c for c in table.columns if _is_numeric(table.column(c))]

    keep_indices = set(range(len(table._rows)))

    for col_name in columns:
        if col_name not in table.columns:
            continue
        values = table.column(col_name)
        num_vals = _numeric_values(values)
        if len(num_vals) < 4:
            continue

        q1 = percentile(num_vals, 25)
        q3 = percentile(num_vals, 75)
        iqr = (q3 or 0) - (q1 or 0)
        lower = (q1 or 0) - 1.5 * iqr
        upper = (q3 or 0) + 1.5 * iqr

        for i, v in enumerate(values):
            if v is None:
                continue
            try:
                fv = float(v)
                if fv < lower or fv > upper:
                    keep_indices.discard(i)
            except (ValueError, TypeError):
                continue

    sorted_indices = sorted(keep_indices)
    new_rows = [table._rows[i][:] for i in sorted_indices]
    return DataTable(table.columns[:], new_rows, table.source)


def rename_columns(table: DataTable, mapping: Dict[str, str]) -> DataTable:
    """Rename columns using a mapping dictionary."""
    new_cols = [mapping.get(c, c) for c in table.columns]
    return DataTable(new_cols, [row[:] for row in table._rows], table.source)


def cast_column_type(values: List[Any], target_type: str) -> List[Any]:
    """Cast column values to a specific type.

    Args:
        values: List of values
        target_type: 'int', 'float', 'str', 'bool'
    """
    result = []
    for v in values:
        if v is None:
            result.append(None)
            continue
        try:
            if target_type == "int":
                result.append(int(float(v)))
            elif target_type == "float":
                result.append(float(v))
            elif target_type == "str":
                result.append(str(v))
            elif target_type == "bool":
                if isinstance(v, bool):
                    result.append(v)
                elif isinstance(v, str):
                    result.append(v.lower() in ("true", "yes", "1"))
                else:
                    result.append(bool(v))
            else:
                result.append(v)
        except (ValueError, TypeError):
            result.append(None)
    return result


def data_quality_report(table: DataTable) -> Dict[str, Any]:
    """Generate a comprehensive data quality report."""
    report = {
        "shape": table.shape,
        "columns": [],
        "overall_quality_score": 0,
    }

    total_cells = table.num_rows * table.num_columns
    total_nulls = 0
    total_issues = 0

    for col in table.columns:
        values = table.column(col)
        non_none = [v for v in values if v is not None]
        null_count = len(values) - len(non_none)
        total_nulls += null_count

        col_report = {
            "name": col,
            "null_count": null_count,
            "null_pct": round(null_count / len(values) * 100, 1) if values else 0,
            "unique_count": len(set(str(v) for v in non_none)),
            "dtype": "numeric" if _is_numeric(values) else "categorical",
            "empty_strings": sum(1 for v in non_none if isinstance(v, str) and v.strip() == ""),
            "issues": [],
        }

        # Check for issues
        if col_report["null_pct"] > 30:
            col_report["issues"].append("high_null_rate")
            total_issues += 1
        if col_report["unique_count"] == 1 and len(non_none) > 1:
            col_report["issues"].append("constant_column")
            total_issues += 1
        if col_report["empty_strings"] > 0:
            col_report["issues"].append("empty_strings")
        if col_report["unique_count"] == len(non_none) and len(non_none) > 10:
            col_report["issues"].append("high_cardinality")

        report["columns"].append(col_report)

    # Overall quality score (0-100)
    null_score = max(0, 100 - (total_nulls / total_cells * 100)) if total_cells > 0 else 100
    issue_score = max(0, 100 - (total_issues / len(table.columns) * 25)) if table.columns else 100
    completeness = len(non_none) / total_cells if total_cells > 0 else 1
    report["overall_quality_score"] = round((null_score + issue_score) / 2, 1)
    report["total_nulls"] = total_nulls
    report["total_cells"] = total_cells
    report["completeness"] = round(completeness * 100, 1)

    return report


def _is_numeric(values: List[Any]) -> bool:
    """Check if values are predominantly numeric."""
    from tablepilot.stats_engine import _is_numeric as _check
    return _check(values)
