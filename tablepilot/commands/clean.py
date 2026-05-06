"""
Clean command - Data cleaning and preprocessing.
"""

import sys

from tablepilot.data_loader import load_file
from tablepilot.data_cleaner import (
    drop_null_rows, drop_duplicates, fill_null_values,
    strip_whitespace, normalize_table, remove_outliers_iqr,
)
from tablepilot.visualizer import colorize, Colors


def run_clean(args) -> int:
    """Execute the clean command."""
    try:
        table = load_file(args.file)
    except Exception as e:
        print(f"❌ Failed to load file: {e}", file=sys.stderr)
        return 1

    original_rows = table.num_rows
    original_cols = table.num_columns

    print(colorize("\n🧹 TablePilot - Data Cleaning", Colors.BOLD + Colors.CYAN))
    print(colorize(f"   Input: {args.file} ({original_rows:,} rows × {original_cols} cols)", Colors.DIM))
    print()

    operations = []

    # Strip whitespace
    if args.strip_whitespace:
        table = strip_whitespace(table)
        operations.append("✅ Stripped whitespace from string values")

    # Fill NA values
    if args.fill_na:
        strategy = args.fill_na
        custom_value = None

        if strategy.startswith("value:"):
            custom_value = strategy[6:]
            strategy = "custom"
        elif strategy not in ("mean", "median", "mode", "zero", "forward", "backward"):
            print(f"❌ Unknown fill strategy: {strategy}", file=sys.stderr)
            print("   Valid options: mean, median, mode, zero, forward, backward, value:XXX")
            return 1

        table = fill_null_values(table, strategy=strategy, custom_value=custom_value)
        operations.append(f"✅ Filled null values using '{strategy}' strategy")

    # Drop NA rows
    if args.drop_na:
        before = table.num_rows
        table = drop_null_rows(table)
        dropped = before - table.num_rows
        operations.append(f"✅ Dropped {dropped:,} rows with null values")

    # Drop duplicates
    if args.drop_duplicates:
        before = table.num_rows
        table = drop_duplicates(table)
        dropped = before - table.num_rows
        operations.append(f"✅ Dropped {dropped:,} duplicate rows")

    # Normalize
    if args.normalize:
        method = args.normalize
        if method not in ("minmax", "zscore"):
            print(f"❌ Unknown normalization method: {method}", file=sys.stderr)
            print("   Valid options: minmax, zscore")
            return 1
        table = normalize_table(table, method=method)
        operations.append(f"✅ Normalized numeric columns using '{method}'")

    # Remove outliers
    if any(hasattr(args, attr) and getattr(args, attr) for attr in ["drop_na"]):
        pass  # Already handled

    # Print operations summary
    if not operations:
        operations.append("ℹ️  No cleaning operations specified — data unchanged")

    for op in operations:
        print(f"  {op}")

    print()
    print(colorize(f"  📊 Result: {table.num_rows:,} rows × {table.num_columns} cols "
                   f"(removed {original_rows - table.num_rows:,} rows)", Colors.GREEN))

    # Save output
    output_path = args.output
    if output_path.endswith(".csv"):
        table.to_csv(output_path)
    elif output_path.endswith(".json"):
        table.to_json(output_path)
    elif output_path.endswith(".tsv"):
        table.to_tsv(output_path)
    else:
        table.to_csv(output_path)

    print(colorize(f"  💾 Saved to: {output_path}", Colors.GREEN))
    print()
    return 0
