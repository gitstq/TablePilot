"""
Report command - Generate comprehensive analysis reports.
"""

import sys
import os

from tablepilot.data_loader import load_file
from tablepilot.report_gen import (
    generate_analysis_data, to_markdown, to_html, save_report,
)
from tablepilot.visualizer import colorize, Colors


def run_report(args) -> int:
    """Execute the report command."""
    try:
        table = load_file(args.file)
    except Exception as e:
        print(f"❌ Failed to load file: {e}", file=sys.stderr)
        return 1

    print(colorize("\n📝 TablePilot - Report Generation", Colors.BOLD + Colors.CYAN))
    print(colorize(f"   Input: {args.file} ({table.num_rows:,} rows × {table.num_columns} cols)", Colors.DIM))
    print()

    # Generate analysis data
    analysis_data = generate_analysis_data(
        table,
        include_correlation=True,
        include_outliers=True,
    )

    title = args.title or f"Data Analysis Report — {os.path.basename(args.file)}"

    fmt = args.format
    output_path = args.output

    if fmt == "markdown":
        content = to_markdown(analysis_data, title=title)
        if not output_path:
            output_path = f"tablepilot_report_{os.path.splitext(os.path.basename(args.file))[0]}.md"
        save_report(content, output_path)

    elif fmt == "html":
        content = to_html(analysis_data, title=title)
        if not output_path:
            output_path = f"tablepilot_report_{os.path.splitext(os.path.basename(args.file))[0]}.html"
        save_report(content, output_path)

    else:
        print(f"❌ Unsupported format: {fmt}", file=sys.stderr)
        return 1

    file_size = os.path.getsize(output_path)
    print(colorize(f"  ✅ {fmt.upper()} report generated successfully!", Colors.GREEN))
    print(f"  📄 Path: {output_path}")
    print(f"  📦 Size: {file_size:,} bytes")
    print(f"  📊 Columns analyzed: {len(analysis_data['columns'])}")
    print(f"  🔗 Correlation matrix: {'Yes' if 'correlation_matrix' in analysis_data else 'No'}")
    print()

    return 0
