#!/usr/bin/env python3
"""
Dispute Response Pipeline — Conference Demo
"Both Sides of the Letter"

One command, full pipeline, live progress.

Usage:
    python3 run.py                    # Run full pipeline (50 records, LLM drafting)
    python3 run.py --records 10       # Fewer records for quick test
    python3 run.py --no-llm           # Skip LLM calls, use templates only
    python3 run.py --no-fix-balances  # Leave string balances broken (demo)
    python3 run.py --loose-review     # Loosen review gate (demo)
    python3 run.py --output results   # Output directory (default: output/)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from pipeline import intake, validate, classify, draft, review, consumer_view
from offline.llm import get_current_tier, tier_status_line
from pipeline import remediate


def main():
    parser = argparse.ArgumentParser(description="Dispute Response Pipeline Demo")
    parser.add_argument("--records", type=int, default=50,
                        help="Number of records to process (default: 50)")
    parser.add_argument("--no-llm", action="store_true",
                        help="Skip LLM calls, use template letters")
    parser.add_argument("--no-fix-balances", action="store_true",
                        help="Leave string balances uncorrected (break demo)")
    parser.add_argument("--loose-review", action="store_true",
                        help="Loosen review gate (hallucination break demo)")
    parser.add_argument("--output", default="output",
                        help="Output directory (default: output/)")
    parser.add_argument("--max-drafts", type=int, default=None,
                        help="Limit number of LLM-drafted letters")
    parser.add_argument("--remediate", action="store_true", help="Re-draft flagged letters with their findings as constraints")
    parser.add_argument("--remediation-passes", type=int, default=2, help="Max remediation attempts per letter")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(exist_ok=True)

    start = time.time()

    print("=" * 60)
    print("  DISPUTE RESPONSE PIPELINE")
    print("  \"Both Sides of the Letter\"")
    print("=" * 60)
    print(f"  Records: {args.records}")
    print(f"  LLM: {'disabled (template only)' if args.no_llm else 'enabled'}")
    print(f"  Balance fix: {'OFF (break mode)' if args.no_fix_balances else 'ON'}")
    print(f"  Review gate: {'LOOSE (break mode)' if args.loose_review else 'STRICT'}")
    print(f"  Output: {output_dir}")
    print("=" * 60)

    # Stage 1: Intake
    records = intake.run(max_records=args.records)

    # Stage 2: Validate
    records, fix_log, val_stats = validate.run(
        records,
        fix_balances=not args.no_fix_balances
    )

    # Stage 3: Classify
    records = classify.run(records, use_llm=not args.no_llm)

    # Stage 4: Draft
    max_drafts = args.max_drafts if args.max_drafts else args.records
    records = draft.run(records, max_drafts=max_drafts, use_llm=not args.no_llm)

    # Stage 5: Review
    records = review.run(records, strict=not args.loose_review)

    # Stage 6: Consumer View
    records = consumer_view.run(records)

    # Save results
    if args.remediate:
        records, _ = remediate.run(records, max_passes=args.remediation_passes, use_llm=not args.no_llm, strict=not args.loose_review)

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s")
    print(f"{'=' * 60}")

    _save_results(records, fix_log, val_stats, output_dir, elapsed, args)
    _build_ui(records, output_dir, elapsed, args, val_stats)

    print(f"\n  Results saved to {output_dir}/")
    print(f"  Open ui/index.html to view results (works from file://)")
    print(f"  LLM tier: {tier_status_line()}")


def _save_results(records, fix_log, val_stats, output_dir, elapsed, args):
    """Save pipeline results as JSON for the UI."""

    # Summary
    drafted = [r for r in records if r.get("draft_letter")]
    reviewed = [r for r in records if r.get("review_findings") is not None]
    flagged = [r for r in records if not r.get("review_passed", True)]

    summary = {
        "total_records": len(records),
        "drafted": len(drafted),
        "reviewed": len(reviewed),
        "review_passed": len(reviewed) - len(flagged),
        "review_flagged": len(flagged),
        "high_risk_letters": len([r for r in records if r.get("engagement_risk_level") == "high"]),
        "elapsed_seconds": round(elapsed, 1),
        "validation_stats": val_stats,
        "settings": {
            "llm_enabled": not args.no_llm,
            "fix_balances": not args.no_fix_balances,
            "strict_review": not args.loose_review,
        }
    }

    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Full records (for UI)
    # Strip very long narratives for JSON size
    output_records = []
    for rec in records:
        out = dict(rec)
        if len(out.get("narrative", "")) > 2000:
            out["narrative"] = out["narrative"][:2000] + "..."
        output_records.append(out)

    with open(output_dir / "records.json", "w") as f:
        json.dump(output_records, f, indent=2)

    # Fix log
    with open(output_dir / "fix_log.json", "w") as f:
        json.dump(fix_log, f, indent=2)

    # Summary to terminal
    print(f"\n  📊 SUMMARY")
    print(f"  Records processed: {summary['total_records']}")
    print(f"  Letters drafted:   {summary['drafted']}")
    print(f"  Review passed:     {summary['review_passed']}")
    print(f"  Review flagged:    {summary['review_flagged']}")
    print(f"  High-risk letters: {summary['high_risk_letters']}")


def _build_ui(records, output_dir, elapsed, args, val_stats):
    """Write self-contained ui/index.html with data inlined."""
    ui_template = ROOT / "ui" / "_template.html"

    if not ui_template.exists():
        print("  ⚠ ui/_template.html not found, skipping UI build")
        return

    template = ui_template.read_text(encoding="utf-8")

    # Build the records and summary JSON for inlining
    output_records = []
    for rec in records:
        out = dict(rec)
        if len(out.get("narrative", "")) > 2000:
            out["narrative"] = out["narrative"][:2000] + "..."
        output_records.append(out)

    drafted = [r for r in records if r.get("draft_letter")]
    reviewed = [r for r in records if r.get("review_findings") is not None]
    flagged = [r for r in records if not r.get("review_passed", True)]

    summary = {
        "total_records": len(records),
        "drafted": len(drafted),
        "reviewed": len(reviewed),
        "review_passed": len(reviewed) - len(flagged),
        "review_flagged": len(flagged),
        "high_risk_letters": len([r for r in records if r.get("engagement_risk_level") == "high"]),
        "elapsed_seconds": round(elapsed, 1),
        "validation_stats": val_stats,
        "settings": {
            "llm_enabled": not args.no_llm,
            "fix_balances": not args.no_fix_balances,
            "strict_review": not args.loose_review,
        }
    }

    records_json = json.dumps(output_records)
    summary_json = json.dumps(summary)

    # Inject data before the closing </head> tag as inline script
    data_script = (
        f'<script>\n'
        f'window.__PIPELINE_RECORDS = {records_json};\n'
        f'window.__PIPELINE_SUMMARY = {summary_json};\n'
        f'</script>\n'
    )

    # Insert right before </head>
    result_html = template.replace('</head>', data_script + '</head>', 1)

    # Write to ui/index.html — the one file anyone will open
    index_path = ROOT / "ui" / "index.html"
    index_path.write_text(result_html, encoding="utf-8")
    print(f"  UI written to ui/index.html ({len(result_html) // 1024}KB, self-contained)")


if __name__ == "__main__":
    main()
