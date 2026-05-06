"""
Compare command - Compare two data files.
"""

import sys
import json

from tablepilot.data_loader import load_file
from tablepilot.stats_engine import descriptive_stats, _is_numeric, _numeric_values, mean, std_dev
from tablepilot.visualizer import colorize, Colors


def run_compare(args) -> int:
    """Execute the compare command."""
    try:
        table1 = load_file(args.file1)
        table2 = load_file(args.file2)
    except Exception as e:
        print(f"❌ Failed to load files: {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        result = _compare_data(table1, table2)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0

    # Terminal output
    print(colorize("\n📊 TablePilot - Data Comparison", Colors.BOLD + Colors.CYAN))
    print(f"  File A: {args.file1} ({table1.num_rows:,} rows × {table1.num_columns} cols)")
    print(f"  File B: {args.file2} ({table2.num_rows:,} rows × {table2.num_columns} cols)")
    print()

    result = _compare_data(table1, table2)

    # Shape comparison
    print(colorize("  📐 Shape Comparison", Colors.BOLD + Colors.CYAN))
    print(f"  {'─' * 50}")
    print(f"  Rows:    A={table1.num_rows:,}  B={table2.num_rows:,}  "
          f"Δ={table2.num_rows - table1.num_rows:+,}")
    print(f"  Columns: A={table1.num_columns}  B={table2.num_columns}  "
          f"Δ={table2.num_columns - table1.num_columns:+}")
    print()

    # Column comparison
    print(colorize("  📋 Column Comparison", Colors.BOLD + Colors.CYAN))
    print(f"  {'─' * 70}")

    common_cols = set(table1.columns) & set(table2.columns)
    only_a = set(table1.columns) - set(table2.columns)
    only_b = set(table2.columns) - set(table1.columns)

    if only_a:
        print(f"  {colorize('Only in A:', Colors.YELLOW)} {', '.join(sorted(only_a))}")
    if only_b:
        print(f"  {colorize('Only in B:', Colors.YELLOW)} {', '.join(sorted(only_b))}")
    if common_cols:
        print(f"  {colorize(f'Common columns ({len(common_cols)}):', Colors.GREEN)} {', '.join(sorted(common_cols))}")

    print()

    # Statistical comparison for common columns
    if common_cols:
        print(colorize("  📈 Statistical Comparison (Common Columns)", Colors.BOLD + Colors.CYAN))
        print(f"  {'─' * 70}")
        print(f"  {'Column':<20} {'Metric':<12} {'File A':>12} {'File B':>12} {'Δ':>12}")
        print(f"  {'─' * 70}")

        for col in sorted(common_cols):
            vals_a = table1.column(col)
            vals_b = table2.column(col)

            if _is_numeric(vals_a) and _is_numeric(vals_b):
                num_a = _numeric_values(vals_a)
                num_b = _numeric_values(vals_b)

                for label, fn in [("Mean", mean), ("Std Dev", std_dev)]:
                    va = fn(num_a)
                    vb = fn(num_b)
                    if va is not None and vb is not None:
                        delta = vb - va
                        print(f"  {col:<20} {label:<12} {va:>12.4f} {vb:>12.4f} {delta:>+12.4f}")

                # Min/Max
                if num_a and num_b:
                    print(f"  {col:<20} {'Min':<12} {min(num_a):>12.4f} {min(num_b):>12.4f} "
                          f"{min(num_b) - min(num_a):>+12.4f}")
                    print(f"  {col:<20} {'Max':<12} {max(num_a):>12.4f} {max(num_b):>12.4f} "
                          f"{max(num_b) - max(num_a):>+12.4f}")
            else:
                # Categorical comparison
                unique_a = len(set(str(v) for v in vals_a if v is not None))
                unique_b = len(set(str(v) for v in vals_b if v is not None))
                null_a = sum(1 for v in vals_a if v is None)
                null_b = sum(1 for v in vals_b if v is None)
                print(f"  {col:<20} {'Unique':<12} {unique_a:>12} {unique_b:>12} {unique_b - unique_a:>+12}")
                print(f"  {col:<20} {'Nulls':<12} {null_a:>12} {null_b:>12} {null_b - null_a:>+12}")

            print()

    print()
    return 0


def _compare_data(table1, table2) -> dict:
    """Generate comparison data dict."""
    common_cols = sorted(set(table1.columns) & set(table2.columns))
    only_a = sorted(set(table1.columns) - set(table2.columns))
    only_b = sorted(set(table2.columns) - set(table1.columns))

    col_comparison = {}
    for col in common_cols:
        vals_a = table1.column(col)
        vals_b = table2.column(col)

        comparison = {"type": "numeric" if (_is_numeric(vals_a) and _is_numeric(vals_b)) else "categorical"}

        if comparison["type"] == "numeric":
            num_a = _numeric_values(vals_a)
            num_b = _numeric_values(vals_b)
            if num_a and num_b:
                comparison["mean_a"] = round(mean(num_a), 4)
                comparison["mean_b"] = round(mean(num_b), 4)
                comparison["std_a"] = round(std_dev(num_a), 4) if std_dev(num_a) else None
                comparison["std_b"] = round(std_dev(num_b), 4) if std_dev(num_b) else None
                comparison["min_a"] = round(min(num_a), 4)
                comparison["min_b"] = round(min(num_b), 4)
                comparison["max_a"] = round(max(num_a), 4)
                comparison["max_b"] = round(max(num_b), 4)

        col_comparison[col] = comparison

    return {
        "file_a": table1.source,
        "file_b": table2.source,
        "shape_a": table1.shape,
        "shape_b": table2.shape,
        "common_columns": common_cols,
        "only_in_a": only_a,
        "only_in_b": only_b,
        "column_comparison": col_comparison,
    }
