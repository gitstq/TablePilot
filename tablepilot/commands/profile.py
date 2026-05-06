"""
Profile command - Quick data profiling summary.
"""

import sys
import json

from tablepilot.data_loader import load_file
from tablepilot.stats_engine import descriptive_stats
from tablepilot.visualizer import colorize, Colors, progress_bar
from tablepilot.data_cleaner import data_quality_report


def run_profile(args) -> int:
    """Execute the profile command."""
    try:
        table = load_file(args.file)
    except Exception as e:
        print(f"❌ Failed to load file: {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        quality = data_quality_report(table)
        profile = {
            "source": table.source,
            "shape": table.shape,
            "quality": quality,
            "columns": [],
        }
        for col in table.columns:
            profile["columns"].append({
                "name": col,
                "statistics": descriptive_stats(table.column(col)),
            })
        print(json.dumps(profile, ensure_ascii=False, indent=2, default=str))
        return 0

    # Terminal output
    print(colorize("\n📊 TablePilot - Data Profile", Colors.BOLD + Colors.CYAN))
    print(colorize(f"   File: {table.source}", Colors.DIM))
    print()

    # Basic info
    print(f"  📐 Shape: {colorize(f'{table.num_rows:,}', Colors.GREEN)} rows × "
          f"{colorize(f'{table.num_columns}', Colors.GREEN)} columns")
    print()

    # Data quality
    quality = data_quality_report(table)
    score = quality["overall_quality_score"]
    score_color = Colors.GREEN if score >= 80 else Colors.YELLOW if score >= 60 else Colors.RED
    print(f"  🏆 Quality Score: {colorize(f'{score}/100', score_color)}")
    print(f"  📋 Completeness:  {quality['completeness']}%")
    print(f"  🕳️  Total Nulls:   {quality['total_nulls']:,} / {quality['total_cells']:,}")
    print()

    # Column overview
    print(colorize("  📋 Column Profiles", Colors.BOLD + Colors.CYAN))
    print(f"  {'─' * 70}")

    for col_info in quality["columns"]:
        name = col_info["name"]
        null_pct = col_info["null_pct"]
        unique = col_info["unique_count"]
        dtype = col_info["dtype"]

        dtype_color = Colors.CYAN if dtype == "numeric" else Colors.GREEN
        issues_str = ""
        if col_info["issues"]:
            issues_str = colorize(f" ⚠️ {', '.join(col_info['issues'])}", Colors.YELLOW)

        print(f"\n  {colorize(name, Colors.BOLD)} {colorize(f'[{dtype}]', dtype_color)}")
        print(f"    Null: {null_pct}%  |  Unique: {unique}  |  Empty strings: {col_info['empty_strings']}{issues_str}")

        # Progress bar for completeness
        completeness = 100 - null_pct
        print(progress_bar(completeness, 100, width=30, label="    Complete"))

    print()
    return 0
