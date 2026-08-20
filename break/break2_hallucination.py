#!/usr/bin/env python3
"""
BREAK 2: The Hallucination Break

Trigger: Loosen the review gate so it skips date and payment checks.
Symptom: A letter asserts a payment date that doesn't exist in the source.
Fix:     Re-enable strict review and show it catching the same draft.

This demonstrates why the review gate matters — the model will confidently
assert facts it invented.
"""

import sys
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def trigger():
    """Run with a loose review gate to let hallucinations through."""
    from pipeline import intake, validate, classify, draft, review

    print("=" * 60)
    print("  BREAK 2: THE HALLUCINATION BREAK")
    print("  Loosening the review gate...")
    print("=" * 60)

    records = intake.run(max_records=10)
    cleaned, _, _ = validate.run(records)
    classified = classify.run(cleaned, use_llm=False)

    # Draft with LLM (Ollama) to get letters that might hallucinate
    drafted = draft.run(classified, max_drafts=5, use_llm=True)

    # Review with LOOSE gate
    print("\n🔴 REVIEW GATE: LOOSE MODE")
    reviewed = review.run(drafted, strict=False)

    passed = [r for r in reviewed if r.get("review_passed")]
    print(f"\n  With loose gate: {len(passed)} letters passed review")
    print(f"  The gate isn't checking dates or payment assertions.")
    print(f"  If the model invented a payment date, it sailed through.")

    # Now show what strict mode catches
    print("\n" + "─" * 40)
    print("  Now re-reviewing with STRICT gate...")
    for rec in reviewed:
        rec.pop("review_findings", None)
        rec.pop("review_passed", None)
    reviewed_strict = review.run(drafted, strict=True)
    flagged = [r for r in reviewed_strict if not r.get("review_passed")]

    if flagged:
        print(f"\n🚩 Strict gate caught {len(flagged)} letters:")
        for rec in flagged[:3]:
            print(f"\n  Account {rec['account_id']}:")
            for finding in rec.get("review_findings", []):
                print(f"    [{finding['severity']}] {finding['reason']}")
                if finding.get('claim_value'):
                    print(f"    Claim: {finding['claim_value']!r}")
    else:
        print(f"\n  (No hallucinations caught in this sample — model behaved.)")
        print(f"  The point still holds: the gate EXISTS. Without it, you're trusting.")

    print("\n" + "=" * 60)
    print("  TO FIX: python3 run.py  (strict review is ON by default)")
    print("=" * 60)


def fix():
    """Show the strict review gate in action."""
    from pipeline import intake, validate, classify, draft, review

    print("=" * 60)
    print("  FIX 2: STRICT REVIEW GATE")
    print("=" * 60)

    records = intake.run(max_records=10)
    cleaned, _, _ = validate.run(records)
    classified = classify.run(cleaned, use_llm=False)
    drafted = draft.run(classified, max_drafts=5, use_llm=True)

    print("\n✅ REVIEW GATE: STRICT MODE")
    reviewed = review.run(drafted, strict=True)

    passed = [r for r in reviewed if r.get("review_passed")]
    flagged = [r for r in reviewed if not r.get("review_passed")]
    print(f"\n  Passed: {len(passed)}  Flagged: {len(flagged)}")
    print(f"  Every letter checked against its source record.")
    print(f"  Nothing goes out that asserts facts we can't verify.")

    print("\n" + "=" * 60)
    print("  FIX APPLIED. The gate is the compliance layer.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        fix()
    else:
        trigger()
