"""
TablePilot - Lightweight Tabular Data Intelligent Analysis Engine CLI
轻量级表格数据智能分析引擎CLI工具

A zero-dependency CLI tool for intelligent tabular data analysis,
featuring data profiling, statistical analysis, data cleaning,
terminal visualization, and multi-format report generation.

Usage:
    tablepilot analyze data.csv
    tablepilot profile data.json --format html
    tablepilot clean data.csv --output cleaned.csv
    tablepilot visualize data.csv --chart bar --column sales
    tablepilot report data.csv --format markdown
    tablepilot interactive data.csv
"""

import sys
import argparse

from tablepilot import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the main CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="tablepilot",
        description="📊 TablePilot - Lightweight Tabular Data Intelligent Analysis Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tablepilot analyze data.csv              Full analysis of a CSV file
  tablepilot profile data.json             Quick data profiling
  tablepilot clean data.csv --drop-na      Clean data and drop NaN rows
  tablepilot visualize data.csv --chart bar --column sales
  tablepilot report data.csv --format html Generate HTML report
  tablepilot interactive data.csv          Interactive exploration mode
        """,
    )

    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Perform comprehensive data analysis", aliases=["a"]
    )
    analyze_parser.add_argument("file", help="Path to data file (CSV, JSON, TSV)")
    analyze_parser.add_argument("--output", "-o", help="Output file path for report")
    analyze_parser.add_argument("--format", "-f", choices=["markdown", "html", "json", "terminal"],
                                default="terminal", help="Output format (default: terminal)")
    analyze_parser.add_argument("--columns", "-c", help="Comma-separated columns to analyze")
    analyze_parser.add_argument("--rows", "-r", type=int, default=0, help="Max rows to analyze (0=all)")
    analyze_parser.add_argument("--correlation", action="store_true", help="Include correlation analysis")
    analyze_parser.add_argument("--outliers", action="store_true", help="Detect outliers")

    # profile command
    profile_parser = subparsers.add_parser(
        "profile", help="Quick data profiling summary", aliases=["p"]
    )
    profile_parser.add_argument("file", help="Path to data file")
    profile_parser.add_argument("--format", "-f", choices=["terminal", "json", "markdown"],
                                default="terminal", help="Output format (default: terminal)")

    # clean command
    clean_parser = subparsers.add_parser(
        "clean", help="Clean and preprocess data", aliases=["cl"]
    )
    clean_parser.add_argument("file", help="Path to data file")
    clean_parser.add_argument("--output", "-o", required=True, help="Output file path")
    clean_parser.add_argument("--drop-na", action="store_true", help="Drop rows with NaN values")
    clean_parser.add_argument("--drop-duplicates", action="store_true", help="Drop duplicate rows")
    clean_parser.add_argument("--fill-na", help="Fill NaN values (mean|median|mode|zero|value:XXX)")
    clean_parser.add_argument("--strip-whitespace", action="store_true", help="Strip whitespace from strings")
    clean_parser.add_argument("--normalize", help="Normalize numeric columns (minmax|zscore)")

    # visualize command
    viz_parser = subparsers.add_parser(
        "visualize", help="Generate terminal visualization", aliases=["v", "viz"]
    )
    viz_parser.add_argument("file", help="Path to data file")
    viz_parser.add_argument("--chart", choices=["bar", "hist", "scatter", "heatmap", "box", "line"],
                            default="bar", help="Chart type (default: bar)")
    viz_parser.add_argument("--column", "-c", help="Column to visualize")
    viz_parser.add_argument("--columns", help="Two columns for scatter (col1,col2)")
    viz_parser.add_argument("--width", type=int, default=60, help="Chart width (default: 60)")
    viz_parser.add_argument("--height", type=int, default=20, help="Chart height (default: 20)")
    viz_parser.add_argument("--title", "-t", help="Chart title")
    viz_parser.add_argument("--bins", type=int, default=10, help="Number of bins for histogram")

    # report command
    report_parser = subparsers.add_parser(
        "report", help="Generate comprehensive analysis report", aliases=["r"]
    )
    report_parser.add_argument("file", help="Path to data file")
    report_parser.add_argument("--output", "-o", help="Output file path")
    report_parser.add_argument("--format", "-f", choices=["markdown", "html", "json"],
                                default="markdown", help="Report format (default: markdown)")
    report_parser.add_argument("--title", "-t", help="Report title")

    # interactive command
    inter_parser = subparsers.add_parser(
        "interactive", help="Interactive data exploration mode", aliases=["i"]
    )
    inter_parser.add_argument("file", help="Path to data file")

    # compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare two data files", aliases=["cmp"]
    )
    compare_parser.add_argument("file1", help="Path to first data file")
    compare_parser.add_argument("file2", help="Path to second data file")
    compare_parser.add_argument("--format", "-f", choices=["terminal", "json", "markdown"],
                                default="terminal", help="Output format")

    return parser


def main() -> int:
    """Main entry point for TablePilot CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command in ("analyze", "a"):
            from tablepilot.commands.analyze import run_analyze
            return run_analyze(args)
        elif args.command in ("profile", "p"):
            from tablepilot.commands.profile import run_profile
            return run_profile(args)
        elif args.command in ("clean", "cl"):
            from tablepilot.commands.clean import run_clean
            return run_clean(args)
        elif args.command in ("visualize", "v", "viz"):
            from tablepilot.commands.visualize import run_visualize
            return run_visualize(args)
        elif args.command in ("report", "r"):
            from tablepilot.commands.report import run_report
            return run_report(args)
        elif args.command in ("interactive", "i"):
            from tablepilot.commands.interactive import run_interactive
            return run_interactive(args)
        elif args.command in ("compare", "cmp"):
            from tablepilot.commands.compare import run_compare
            return run_compare(args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
