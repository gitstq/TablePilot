"""
Terminal visualization module - ASCII charts and visual representations.
Zero external dependencies - pure Python implementation.
"""

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from tablepilot.stats_engine import _numeric_values, percentile


# ANSI Color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"

    # Bar chart colors (gradient)
    BAR_COLORS = [
        "\033[94m",  # Blue
        "\033[96m",  # Cyan
        "\033[92m",  # Green
        "\033[93m",  # Yellow
        "\033[95m",  # Magenta
        "\033[91m",  # Red
    ]


def colorize(text: str, color: str) -> str:
    """Wrap text with ANSI color codes."""
    return f"{color}{text}{Colors.RESET}"


def supports_color() -> bool:
    """Check if terminal supports color."""
    import os
    return os.environ.get("NO_COLOR") is None and (
        hasattr(__import__("sys"), "stdout") and
        getattr(__import__("sys").stdout, "isatty", lambda: False)()
    )


def bar_chart(
    values: List[Any],
    title: str = "",
    width: int = 60,
    height: int = 20,
    horizontal: bool = True,
    show_values: bool = True,
    color: bool = True,
) -> str:
    """Generate an ASCII bar chart.

    Args:
        values: List of values (numeric or categorical)
        title: Chart title
        width: Chart width in characters
        height: Chart height in characters
        horizontal: True for horizontal bars, False for vertical
        show_values: Show value labels
        color: Use colors
    """
    lines = []

    if title:
        lines.append(colorize(f"  {title}", Colors.BOLD + Colors.CYAN))
        lines.append("")

    num_vals = _numeric_values(values)

    if not num_vals:
        # Categorical bar chart
        freq = Counter(str(v) for v in values if v is not None)
        items = freq.most_common(min(15, len(freq)))
        if not items:
            return "  No data to visualize"
        return _horizontal_bar_chart(items, width, show_values, color)

    if horizontal:
        return _horizontal_numeric_chart(num_vals, title, width, height, show_values, color, lines)
    else:
        return _vertical_bar_chart(num_vals, title, width, height, show_values, color)


def _horizontal_bar_chart(
    items: List[Tuple[str, int]],
    width: int,
    show_values: bool,
    color: bool,
) -> str:
    """Generate horizontal bar chart for categorical data."""
    lines = []
    max_label_len = max(len(str(item[0])) for item in items)
    bar_width = width - max_label_len - 15
    if bar_width < 10:
        bar_width = 10

    max_count = max(item[1] for item in items)

    for i, (label, count) in enumerate(items):
        bar_len = int(count / max_count * bar_width) if max_count > 0 else 0
        bar_len = max(bar_len, 1)

        c = Colors.BAR_COLORS[i % len(Colors.BAR_COLORS)] if color else ""
        label_str = f"  {label:>{max_label_len}} "
        bar_str = f"{c}{'█' * bar_len}{Colors.RESET}" if color else f"{'█' * bar_len}"

        if show_values:
            lines.append(f"{label_str}{bar_str} {count}")
        else:
            lines.append(f"{label_str}{bar_str}")

    return "\n".join(lines)


def _horizontal_numeric_chart(
    values: List[float],
    title: str,
    width: int,
    height: int,
    show_values: bool,
    color: bool,
    lines: List[str],
) -> str:
    """Generate horizontal histogram for numeric data."""
    if not values:
        return "  No numeric data to visualize"

    min_v = min(values)
    max_v = max(values)
    num_bins = min(height, 20)

    if max_v == min_v:
        lines.append(f"  All values are the same: {max_v}")
        return "\n".join(lines)

    bin_width = (max_v - min_v) / num_bins
    bins = [0] * num_bins

    for v in values:
        idx = min(int((v - min_v) / bin_width), num_bins - 1)
        bins[idx] += 1

    max_count = max(bins) if bins else 1
    bar_width = width - 25
    if bar_width < 10:
        bar_width = 10

    for i in range(num_bins):
        lo = min_v + i * bin_width
        hi = lo + bin_width
        count = bins[i]
        bar_len = int(count / max_count * bar_width) if max_count > 0 else 0

        c = Colors.BAR_COLORS[i % len(Colors.BAR_COLORS)] if color else ""
        label = f"  {lo:>8.1f} - {hi:>8.1f} │"
        bar = f"{c}{'█' * bar_len}{Colors.RESET}" if color else f"{'█' * bar_len}"

        if show_values:
            lines.append(f"{label}{bar} {count}")
        else:
            lines.append(f"{label}{bar}")

    return "\n".join(lines)


def _vertical_bar_chart(
    values: List[float],
    title: str,
    width: int,
    height: int,
    show_values: bool,
    color: bool,
) -> str:
    """Generate vertical bar chart."""
    if not values:
        return "  No numeric data to visualize"

    # Bin the data
    min_v = min(values)
    max_v = max(values)
    num_bins = min(width - 10, 40)

    if max_v == min_v:
        return f"  All values are the same: {max_v}"

    bin_width = (max_v - min_v) / num_bins
    bins = [0] * num_bins

    for v in values:
        idx = min(int((v - min_v) / bin_width), num_bins - 1)
        bins[idx] += 1

    max_count = max(bins) if bins else 1
    chart_height = min(height - 4, 20)

    # Build chart grid
    grid = []
    for row in range(chart_height, -1, -1):
        threshold = max_count * row / chart_height
        line = "  "
        for count in bins:
            if count >= threshold:
                c = Colors.BAR_COLORS[row % len(Colors.BAR_COLORS)] if color else ""
                line += f"{c}██{Colors.RESET}" if color else "██"
            else:
                line += "  "
        grid.append(line)

    # Add value labels at top
    if show_values:
        top_line = "  "
        for count in bins:
            top_line += f"{count:>2}" if count > 0 else "  "
        grid.insert(0, top_line)

    # X-axis labels
    x_labels = "  "
    for i in range(0, num_bins, max(1, num_bins // 5)):
        val = min_v + i * bin_width
        x_labels += f"{val:.0f:>2}"

    grid.append("  " + "─" * (num_bins * 2))
    grid.append(x_labels)

    return "\n".join(grid)


def box_plot(values: List[float], title: str = "", color: bool = True) -> str:
    """Generate an ASCII box plot.

    Shows: min, Q1, median, Q3, max, and outliers.
    """
    lines = []

    if title:
        lines.append(colorize(f"  {title}", Colors.BOLD + Colors.CYAN))
        lines.append("")

    if len(values) < 4:
        lines.append("  Not enough data for box plot (need at least 4 values)")
        return "\n".join(lines)

    q1 = percentile(values, 25) or 0
    median = percentile(values, 50) or 0
    q3 = percentile(values, 75) or 0
    iqr = q3 - q1
    min_val = min(values)
    max_val = max(values)
    whisker_low = q1 - 1.5 * iqr
    whisker_high = q3 + 1.5 * iqr

    # Clamp whiskers to actual data range
    actual_min = min(v for v in values if v >= whisker_low)
    actual_max = max(v for v in values if v <= whisker_high)

    width = 60
    scale = width / (max_val - min_val) if max_val != min_val else 1

    def pos(v):
        return int((v - min_val) * scale)

    # Build the box plot
    def build_line(char_positions: Dict[int, str], fill: str = "─") -> str:
        line = [" "] * width
        for pos_val, char in char_positions.items():
            p = max(0, min(pos(pos_val), width - 1))
            line[p] = char
        # Fill between whiskers
        lo = max(0, pos(actual_min))
        hi = min(pos(actual_max), width - 1)
        for i in range(lo, hi + 1):
            if line[i] == " ":
                line[i] = fill
        return "  " + "".join(line)

    # Whisker line
    c = Colors.CYAN if color else ""
    r = Colors.RESET
    lines.append(build_line(
        {actual_min: "┤", actual_max: "├"},
        fill=f"{c}─{r}" if color else "─"
    ))

    # Box
    box_line = [" "] * width
    lo_p = max(0, pos(q1))
    hi_p = min(pos(q3), width - 1)
    med_p = max(0, min(pos(median), width - 1))

    for i in range(lo_p, hi_p + 1):
        box_line[i] = "─"
    box_line[lo_p] = "├"
    box_line[hi_p] = "┤"
    box_line[med_p] = "│"

    bc = Colors.GREEN if color else ""
    lines.append("  " + "".join(
        f"{bc}{ch}{r}" if ch != " " else ch for ch in box_line
    ))

    # Labels
    labels = [
        (min_val, f"min:{min_val:.1f}"),
        (q1, f"Q1:{q1:.1f}"),
        (median, f"med:{median:.1f}"),
        (q3, f"Q3:{q3:.1f}"),
        (max_val, f"max:{max_val:.1f}"),
    ]

    label_line = [" "] * width
    for val, text in labels:
        p = max(0, min(pos(val), width - len(text)))
        for j, ch in enumerate(text):
            if p + j < width:
                label_line[p + j] = ch

    lines.append("  " + "".join(label_line))

    # Stats summary
    lines.append("")
    lines.append(f"  {colorize('IQR', Colors.YELLOW)}: {iqr:.2f}  "
                 f"{colorize('Range', Colors.YELLOW)}: {max_val - min_val:.2f}  "
                 f"{colorize('n', Colors.YELLOW)}: {len(values)}")

    return "\n".join(lines)


def scatter_plot(
    x_values: List[float],
    y_values: List[float],
    title: str = "",
    width: int = 60,
    height: int = 20,
    color: bool = True,
) -> str:
    """Generate an ASCII scatter plot."""
    lines = []

    if title:
        lines.append(colorize(f"  {title}", Colors.BOLD + Colors.CYAN))
        lines.append("")

    # Align pairs
    pairs = [(float(x), float(y)) for x, y in zip(x_values, y_values)
             if x is not None and y is not None]
    try:
        pairs = [(float(x), float(y)) for x, y in pairs]
    except (ValueError, TypeError):
        pass

    if len(pairs) < 2:
        return "  Not enough data for scatter plot"

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    if max_x == min_x:
        max_x = min_x + 1
    if max_y == min_y:
        max_y = min_y + 1

    # Build grid
    grid = [[" "] * width for _ in range(height)]
    density = [[0] * width for _ in range(height)]

    for x, y in pairs:
        col = int((x - min_x) / (max_x - min_x) * (width - 1))
        row = height - 1 - int((y - min_y) / (max_y - min_y) * (height - 1))
        col = max(0, min(col, width - 1))
        row = max(0, min(row, height - 1))
        density[row][col] += 1

    for row in range(height):
        for col in range(width):
            d = density[row][col]
            if d == 0:
                continue
            elif d == 1:
                grid[row][col] = "·"
            elif d == 2:
                grid[row][col] = "•"
            elif d <= 5:
                grid[row][col] = "○"
            else:
                c = Colors.RED if color else ""
                grid[row][col] = f"{c}●{Colors.RESET}" if color else "●"

    # Render
    for row in grid:
        lines.append("  " + "".join(row))

    # Axis labels
    lines.append(f"  {min_x:.1f}" + " " * (width - 20) + f"{max_x:.1f}")
    lines.append(f"  {'↑ Y':>{width // 2}}")

    return "\n".join(lines)


def heatmap(
    matrix: Dict[str, Dict[str, float]],
    title: str = "Correlation Heatmap",
    color: bool = True,
) -> str:
    """Generate an ASCII heatmap for a correlation matrix."""
    lines = []

    if not matrix:
        return "  No data for heatmap"

    cols = list(matrix.keys())
    n = len(cols)

    if title:
        lines.append(colorize(f"  {title}", Colors.BOLD + Colors.CYAN))
        lines.append("")

    # Header
    header = "          "
    for col in cols:
        header += f"{col[:8]:>8}"
    lines.append(header)

    for i, row_name in enumerate(cols):
        row_str = f"{row_name[:10]:>10}"
        for j, col_name in enumerate(cols):
            val = matrix[row_name].get(col_name, 0)
            if val is None:
                cell = "    N/A"
            else:
                cell = f"{val:>8.2f}"
            row_str += cell
        lines.append(row_str)

    # Legend
    lines.append("")
    lines.append(f"  {colorize('Strong positive (+1.0)', Colors.RED)} ←→ "
                 f"{colorize('No correlation (0.0)', Colors.RESET)} ←→ "
                 f"{colorize('Strong negative (-1.0)', Colors.BLUE)}")

    return "\n".join(lines)


def data_overview_table(table) -> str:
    """Generate a formatted overview table of the dataset."""
    lines = []
    lines.append(colorize("  📊 Dataset Overview", Colors.BOLD + Colors.CYAN))
    lines.append(f"  {'─' * 50}")
    lines.append(f"  Source:     {table.source}")
    lines.append(f"  Shape:      {table.num_rows} rows × {table.num_columns} columns")
    lines.append(f"  Memory est: ~{table.num_rows * table.num_columns * 8 / 1024:.1f} KB")
    lines.append("")
    lines.append(colorize("  📋 Column Summary", Colors.BOLD + Colors.CYAN))
    lines.append(f"  {'─' * 78}")
    lines.append(f"  {'Column':<20} {'Type':<12} {'Non-Null':>10} {'Null%':>8} {'Unique':>8} {'Sample':>20}")
    lines.append(f"  {'─' * 78}")

    from tablepilot.stats_engine import _is_numeric

    for col in table.columns:
        values = table.column(col)
        non_null = sum(1 for v in values if v is not None)
        null_pct = (len(values) - non_null) / len(values) * 100 if values else 0
        unique = len(set(str(v) for v in values if v is not None))
        dtype = "numeric" if _is_numeric(values) else "categorical"

        # Sample value
        sample_vals = [v for v in values if v is not None][:3]
        sample = ", ".join(str(v)[:12] for v in sample_vals)
        if len(sample) > 20:
            sample = sample[:17] + "..."

        lines.append(
            f"  {col:<20} {dtype:<12} {non_null:>10} {null_pct:>7.1f}% {unique:>8} {sample:>20}"
        )

    lines.append(f"  {'─' * 78}")
    return "\n".join(lines)


def progress_bar(value: float, max_value: float, width: int = 30, label: str = "") -> str:
    """Generate a progress bar."""
    pct = value / max_value if max_value > 0 else 0
    filled = int(pct * width)
    empty = width - filled

    bar = f"{Colors.GREEN}{'█' * filled}{Colors.GRAY}{'░' * empty}{Colors.RESET}"
    if label:
        return f"  {label}: {bar} {pct:.1%}"
    return f"  {bar} {pct:.1%}"
