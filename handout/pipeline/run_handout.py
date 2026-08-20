#!/usr/bin/env python3
"""
Handout Pipeline Runner

Runs the dispute-response pipeline in template mode (no AI model needed).
This is the self-contained version for conference attendees.

Usage:
    python3 pipeline/run_handout.py
"""

import json
import os
import sys
import time
from pathlib import Path

# Set up paths
HANDOUT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HANDOUT_ROOT))

from pipeline import intake, validate, classify, draft, review, consumer_view


def main():
    output_dir = HANDOUT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)

    start = time.time()

    print("=" * 55)
    print("  DISPUTE RESPONSE PIPELINE — Handout Edition")
    print("  Running in template mode (no AI model needed)")
    print("=" * 55)

    # Stage 1: Intake
    records = intake.run(max_records=20)

    # Stage 2: Validate
    records, fix_log, stats = validate.run(records)

    # Stage 3: Classify
    records = classify.run(records, use_llm=False)

    # Stage 4: Draft (template only — no LLM required)
    records = draft.run(records, max_drafts=20, use_llm=False)

    # Stage 5: Review
    records = review.run(records)

    # Stage 6: Consumer View
    records = consumer_view.run(records)

    elapsed = time.time() - start

    # Save results
    with open(output_dir / "records.json", "w") as f:
        json.dump(records, f, indent=2)
    with open(output_dir / "summary.json", "w") as f:
        json.dump({
            "total_records": len(records),
            "drafted": len([r for r in records if r.get("draft_letter")]),
            "review_passed": len([r for r in records if r.get("review_passed")]),
            "review_flagged": len([r for r in records if not r.get("review_passed", True)]),
            "elapsed_seconds": round(elapsed, 1),
        }, f, indent=2)

    print(f"\n{'=' * 55}")
    print(f"  DONE in {elapsed:.1f}s")
    print(f"  Results saved to output/")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
