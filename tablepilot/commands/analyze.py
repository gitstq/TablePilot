"""
Analyze command - Comprehensive data analysis.
"""

import sys
import json

from tablepilot.data_loader import load_file
from tablepilot.stats_engine import descriptive_stats, correlation_matrix, detect_outliers_iqr
from tablepilot.visualizer import (
    data_overview_table, bar_chart, box_plot, colorize, Colors,
)
from tablepilot.report_gen import generate_analysis_data, to_markdown, to_html, save_report


def run_analyze(args) -> int:
    """Execute the analyze command."""
    try:
        table = load_file(args.file, max_rows=args.rows, columns=_parse_columns(args.columns))
    except Exception as e:
        print(f"❌ Failed to load file: {e}", file=sys.stderr)
        return 1

    print(colorize("\n📊 TablePilot - Data Analysis", Colors.BOLD + Colors.CYAN))
    print(colorize(f"   File: {args.file}", Colors.DIM))
    print()

    # Overview
    print(data_overview_table(table))
    print()

    # Column statistics
    print(colorize("  📈 Detailed Statistics", Colors.BOLD + Colors.CYAN))
    print(f"  {'─' * 60}")

    for col in table.columns:
        values = table.column(col)
        stats = descriptive_stats(values)

        print()
        print(colorize(f"  📌 {col}", Colors.BOLD + Colors.GREEN))
        print(f"     Type: {stats['type']}  |  Non-Null: {stats['count']['non_null']}  |  "
              f"Null: {stats['count']['null_pct']}%  |  Unique: {stats['unique']['unique']}")

        if stats["type"] == "numeric":
            print(f"     Mean: {stats.get('mean', 'N/A')}  |  Median: {stats.get('median', 'N/A')}  |  "
                  f"Std: {stats.get('std', 'N/A')}")
            print(f"     Min: {stats.get('min', 'N/A')}  |  Max: {stats.get('max', 'N/A')}  |  "
                  f"Range: {stats.get('range', 'N/A')}")

            if stats.get("skewness") is not None:
                skew = stats["skewness"]
                direction = "right" if skew > 0 else "left" if skew < 0 else "symmetric"
                print(f"     Skewness: {skew} ({direction})  |  Kurtosis: {stats.get('kurtosis', 'N/A')}")

            if args.outliers:
                outliers = detect_outliers_iqr(values)
                if outliers["count"] > 0:
                    print(colorize(f"     ⚠️  Outliers: {outliers['count']} detected ({outliers['pct']}%)", Colors.YELLOW))
                    print(f"        Bounds: [{outliers['lower_bound']}, {outliers['upper_bound']}]")
                else:
                    print(colorize("     ✅ No outliers detected (IQR method)", Colors.GREEN))

            # Show box plot
            from tablepilot.stats_engine import _numeric_values
            num_vals = _numeric_values(values)
            if len(num_vals) >= 4:
                print()
                print(box_plot(num_vals, title=f"Distribution of {col}"))

            # Show histogram
            print()
            print(bar_chart(values, title=f"Histogram of {col}", width=50, height=12))
        else:
            if "top_values" in stats:
                print("     Top values:")
                for item in stats["top_values"][:5]:
                    bar_len = int(item["pct"] / 100 * 30)
                    bar = "█" * bar_len
                    print(f"       {item['value']:<20} {bar} {item['pct']}%")

    # Correlation analysis
    if args.correlation:
        print()
        print(colorize("  🔗 Correlation Analysis", Colors.BOLD + Colors.CYAN))
        print(f"  {'─' * 60}")
        corr = correlation_matrix(table)
        if corr:
            from tablepilot.visualizer import heatmap
            print(heatmap(corr))
        else:
            print("  Not enough numeric columns for correlation analysis")

    # Generate report file
    if args.output or args.format in ("markdown", "html", "json"):
        analysis_data = generate_analysis_data(
            table,
            include_correlation=args.correlation,
            include_outliers=args.outliers,
        )

        if args.format == "markdown" or (args.output and args.output.endswith(".md")):
            content = to_markdown(analysis_data, title=f"Analysis of {args.file}")
            path = args.output or f"tablepilot_report.md"
            save_report(content, path)
            print()
            print(colorize(f"  📝 Markdown report saved to: {path}", Colors.GREEN))

        elif args.format == "html" or (args.output and args.output.endswith(".html")):
            content = to_html(analysis_data, title=f"Analysis of {args.file}")
            path = args.output or f"tablepilot_report.html"
            save_report(content, path)
            print()
            print(colorize(f"  📝 HTML report saved to: {path}", Colors.GREEN))

        elif args.format == "json" or (args.output and args.output.endswith(".json")):
            path = args.output or f"tablepilot_report.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
            print()
            print(colorize(f"  📝 JSON report saved to: {path}", Colors.GREEN))

    print()
    return 0


def _parse_columns(columns_str):
    """Parse comma-separated column names."""
    if not columns_str:
        return None
    return [c.strip() for c in columns_str.split(",")]
