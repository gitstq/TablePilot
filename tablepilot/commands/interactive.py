"""
Interactive command - Interactive data exploration mode.
"""

import sys

from tablepilot.data_loader import load_file
from tablepilot.stats_engine import descriptive_stats, correlation_matrix, _is_numeric, _numeric_values
from tablepilot.visualizer import (
    colorize, Colors, bar_chart, box_plot, data_overview_table,
    progress_bar,
)


def run_interactive(args) -> int:
    """Execute the interactive command."""
    try:
        table = load_file(args.file)
    except Exception as e:
        print(f"❌ Failed to load file: {e}", file=sys.stderr)
        return 1

    print(colorize("\n📊 TablePilot - Interactive Mode", Colors.BOLD + Colors.CYAN))
    print(colorize(f"   File: {args.file} ({table.num_rows:,} rows × {table.num_columns} cols)", Colors.DIM))
    print()
    print(data_overview_table(table))
    print()
    _print_help()

    while True:
        try:
            cmd = input(colorize("\n  tablepilot> ", Colors.GREEN)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action in ("quit", "exit", "q"):
            print(colorize("  👋 Goodbye!", Colors.CYAN))
            break

        elif action == "help":
            _print_help()

        elif action == "head":
            n = int(parts[1]) if len(parts) > 1 else 5
            _show_table(table.head(n))

        elif action == "tail":
            n = int(parts[1]) if len(parts) > 1 else 5
            _show_table(table.tail(n))

        elif action == "sample":
            n = int(parts[1]) if len(parts) > 1 else 10
            _show_table(table.sample(n))

        elif action == "stats":
            col = parts[1] if len(parts) > 1 else None
            if col:
                if col in table.columns:
                    _show_column_stats(table, col)
                else:
                    print(f"  ❌ Column '{col}' not found. Available: {table.columns}")
            else:
                for col in table.columns:
                    _show_column_stats(table, col)

        elif action == "hist" or action == "bar":
            col = parts[1] if len(parts) > 1 else None
            if not col:
                col = _first_numeric_col(table)
            if col and col in table.columns:
                print(bar_chart(table.column(col), title=f"Distribution of {col}", width=55, height=12))
            else:
                print(f"  ❌ Column not found or not numeric")

        elif action == "box":
            col = parts[1] if len(parts) > 1 else None
            if not col:
                col = _first_numeric_col(table)
            if col and col in table.columns:
                num_vals = _numeric_values(table.column(col))
                if len(num_vals) >= 4:
                    print(box_plot(num_vals, title=f"Box Plot of {col}"))
                else:
                    print("  ❌ Not enough data for box plot")
            else:
                print(f"  ❌ Column not found")

        elif action == "corr":
            corr = correlation_matrix(table)
            if corr:
                from tablepilot.visualizer import heatmap
                print(heatmap(corr))
            else:
                print("  ❌ Not enough numeric columns")

        elif action == "search":
            if len(parts) < 3:
                print("  Usage: search <column> <value>")
                continue
            col, val = parts[1], " ".join(parts[2:])
            if col in table.columns:
                values = table.column(col)
                matches = [i for i, v in enumerate(values) if v is not None and val.lower() in str(v).lower()]
                print(f"  🔍 Found {len(matches)} matches in '{col}' for '{val}'")
                if matches[:5]:
                    _show_table(table.head(0).filter_rows(lambda r: r.get(col) is not None and val.lower() in str(r[col]).lower()))
            else:
                print(f"  ❌ Column '{col}' not found")

        elif action == "shape":
            print(f"  📐 {table.num_rows:,} rows × {table.num_columns} columns")

        elif action == "columns":
            for i, col in enumerate(table.columns):
                vals = table.column(col)
                dtype = "num" if _is_numeric(vals) else "cat"
                nulls = sum(1 for v in vals if v is None)
                print(f"  {colorize(f'{i:>3}', Colors.DIM)} {col:<25} [{dtype}] nulls={nulls}")

        elif action == "overview":
            print(data_overview_table(table))

        else:
            print(f"  ❌ Unknown command: {action}. Type 'help' for available commands.")

    return 0


def _print_help():
    """Print interactive mode help."""
    help_text = f"""
  {colorize('Available Commands:', Colors.BOLD + Colors.YELLOW)}
  {colorize('Navigation:', Colors.CYAN)}
    head [n]       Show first n rows (default: 5)
    tail [n]       Show last n rows (default: 5)
    sample [n]     Show random sample of n rows
    columns        List all columns with types
    shape          Show dataset shape
    overview       Show full dataset overview

  {colorize('Analysis:', Colors.CYAN)}
    stats [col]    Show statistics for a column (or all)
    hist [col]     Show histogram/bar chart
    box [col]      Show box plot
    corr           Show correlation matrix
    search <col> <val>  Search for a value in a column

  {colorize('General:', Colors.CYAN)}
    help           Show this help message
    quit/exit      Exit interactive mode
"""
    print(help_text)


def _show_table(table):
    """Display a small table in the terminal."""
    if table.num_rows == 0:
        print("  (empty)")
        return

    cols = table.columns
    col_widths = [max(len(str(c)), 12) for c in cols]
    max_width = 80

    # Adjust widths
    total = sum(col_widths) + len(cols) * 3 + 2
    if total > max_width:
        scale = max_width / total
        col_widths = [max(8, int(w * scale)) for w in col_widths]

    # Header
    header = "  │ " + " │ ".join(str(c)[:w].ljust(w) for c, w in zip(cols, col_widths)) + " │"
    sep = "  ├" + "─┼".join("─" * (w + 2) for w in col_widths) + "─┤"

    print(colorize(header, Colors.BOLD + Colors.CYAN))
    print(colorize(sep, Colors.DIM))

    # Rows
    for row in table._rows[:10]:
        line = "  │ " + " │ ".join(str(v)[:w].ljust(w) if v is not None else "NULL".ljust(w)
                                  for v, w in zip(row, col_widths)) + " │"
        print(line)

    if table.num_rows > 10:
        print(f"  │ ... ({table.num_rows - 10} more rows)")


def _show_column_stats(table, col_name):
    """Show statistics for a single column."""
    values = table.column(col_name)
    stats = descriptive_stats(values)

    print(f"\n  {colorize(f'📌 {col_name}', Colors.BOLD + Colors.GREEN)} [{stats['type']}]")
    print(f"     Count: {stats['count']['non_null']:,}  |  Null: {stats['count']['null_pct']}%  |  Unique: {stats['unique']['unique']}")

    if stats["type"] == "numeric":
        print(f"     Mean: {stats.get('mean', 'N/A')}  |  Median: {stats.get('median', 'N/A')}  |  Std: {stats.get('std', 'N/A')}")
        print(f"     Min: {stats.get('min', 'N/A')}  |  Max: {stats.get('max', 'N/A')}  |  Range: {stats.get('range', 'N/A')}")
    else:
        if "top_values" in stats:
            for item in stats["top_values"][:3]:
                print(f"     {item['value']}: {item['count']} ({item['pct']}%)")


def _first_numeric_col(table):
    """Find the first numeric column."""
    for col in table.columns:
        if _is_numeric(table.column(col)):
            return col
    return None
