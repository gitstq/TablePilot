"""
Visualize command - Terminal data visualization.
"""

import sys

from tablepilot.data_loader import load_file
from tablepilot.stats_engine import _numeric_values, correlation_matrix
from tablepilot.visualizer import (
    bar_chart, box_plot, scatter_plot, heatmap, colorize, Colors,
)


def run_visualize(args) -> int:
    """Execute the visualize command."""
    try:
        table = load_file(args.file)
    except Exception as e:
        print(f"❌ Failed to load file: {e}", file=sys.stderr)
        return 1

    print(colorize("\n📊 TablePilot - Data Visualization", Colors.BOLD + Colors.CYAN))
    print()

    chart_type = args.chart
    title = args.title or f"{chart_type.title()} Chart"

    if chart_type == "heatmap":
        corr = correlation_matrix(table)
        if corr:
            print(heatmap(corr, title=title))
        else:
            print("  ❌ Not enough numeric columns for heatmap")
            return 1
        return 0

    if chart_type == "scatter":
        if args.columns:
            parts = args.columns.split(",")
            if len(parts) == 2:
                col_x, col_y = parts[0].strip(), parts[1].strip()
                if col_x in table.columns and col_y in table.columns:
                    x_vals = _numeric_values(table.column(col_x))
                    y_vals = _numeric_values(table.column(col_y))
                    print(scatter_plot(x_vals, y_vals, title=title or f"{col_x} vs {col_y}",
                                       width=args.width, height=args.height))
                    return 0
                else:
                    print(f"  ❌ Columns not found. Available: {table.columns}")
                    return 1
        print("  ❌ Scatter plot requires --columns col1,col2")
        return 1

    # Single column charts
    col_name = args.column
    if not col_name:
        # Auto-select first numeric column
        for col in table.columns:
            if _is_numeric_col(table.column(col)):
                col_name = col
                break
        if not col_name:
            col_name = table.columns[0] if table.columns else None

    if not col_name or col_name not in table.columns:
        print(f"  ❌ Column not found. Available: {table.columns}")
        return 1

    values = table.column(col_name)

    if chart_type == "bar":
        print(bar_chart(values, title=title or f"Distribution of {col_name}",
                        width=args.width, height=args.height))

    elif chart_type == "hist":
        num_vals = _numeric_values(values)
        if num_vals:
            print(bar_chart(num_vals, title=title or f"Histogram of {col_name}",
                            width=args.width, height=args.height))
        else:
            print("  ❌ Column is not numeric — cannot create histogram")

    elif chart_type == "box":
        num_vals = _numeric_values(values)
        if len(num_vals) >= 4:
            print(box_plot(num_vals, title=title or f"Box Plot of {col_name}"))
        else:
            print("  ❌ Not enough numeric data for box plot (need at least 4 values)")

    elif chart_type == "line":
        num_vals = _numeric_values(values)
        if num_vals:
            # Simple line visualization
            print(_line_chart(num_vals, title=title or f"Line Chart of {col_name}",
                              width=args.width, height=args.height))
        else:
            print("  ❌ Column is not numeric — cannot create line chart")

    else:
        print(f"  ❌ Unknown chart type: {chart_type}")
        return 1

    print()
    return 0


def _is_numeric_col(values) -> bool:
    """Check if column values are numeric."""
    from tablepilot.stats_engine import _is_numeric
    return _is_numeric(values)


def _line_chart(values, title="", width=60, height=20) -> str:
    """Generate a simple ASCII line chart."""
    lines = []

    if title:
        lines.append(colorize(f"  {title}", Colors.BOLD + Colors.CYAN))
        lines.append("")

    if not values:
        return "  No data"

    min_v = min(values)
    max_v = max(values)
    rng = max_v - min_v

    if rng == 0:
        return f"  All values are the same: {max_v}"

    # Sample values to fit width
    step = max(1, len(values) // width)
    sampled = values[::step][:width]

    chart_height = min(height, 20)
    grid = [[" "] * len(sampled) for _ in range(chart_height)]

    for i, v in enumerate(sampled):
        row = chart_height - 1 - int((v - min_v) / rng * (chart_height - 1))
        row = max(0, min(row, chart_height - 1))
        grid[row][i] = "●"

    # Render
    for row in grid:
        lines.append("  " + "".join(row))

    # Y-axis labels
    lines.append(f"  {min_v:.1f}" + " " * (len(sampled) - 15) + f"{max_v:.1f}")
    lines.append(f"  n={len(values)} points (sampled to {len(sampled)})")

    return "\n".join(lines)
