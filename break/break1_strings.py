#!/usr/bin/env python3
"""
BREAK 1: The String Break

Trigger: Run the pipeline with balance validation disabled.
Symptom: A letter quotes a concatenated nonsense balance ("$1,234.56$2,345.67")
         because string balances were added instead of summed.
Fix:     Re-run with balance validation enabled (default).

This is the "what is a string?" moment. Nathan uses it to test whether
an AI consultant actually understands their own pipeline.
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def trigger():
    """Run the pipeline with string balances left unfixed."""
    from pipeline import intake, validate, classify, draft, review

    print("=" * 60)
    print("  BREAK 1: THE STRING BREAK")
    print("  Running pipeline WITHOUT balance type coercion...")
    print("=" * 60)

    # Load enough records to guarantee we hit string balances (~4% rate)
    records = intake.run(max_records=100)

    # KEY: fix_balances=False leaves string balances as-is
    cleaned, fix_log, stats = validate.run(records, fix_balances=False)

    # Show the damage
    print("\n🔴 DAMAGE REPORT:")
    string_balances = []
    for rec in cleaned:
        bal = rec.get("balance_current", "")
        if isinstance(bal, str) and ("$" in bal or "," in bal):
            string_balances.append(rec)

    if string_balances:
        print(f"  {len(string_balances)} records have string balances")
        # Demonstrate concatenation
        print("\n  What happens when you 'add' these:")
        total = ""
        for rec in string_balances[:3]:
            bal = rec["balance_current"]
            total = total + str(bal)  # String concatenation!
            print(f"    {rec['account_id']}: balance = {bal!r}")
        print(f"\n  'Total': {total!r}")
        print(f"  That's not math. That's two strings glued together.")
    else:
        print("  (No string balances in this sample — try --records 50)")

    # Draft a letter with the broken balance
    classified = classify.run(cleaned, use_llm=False)
    if string_balances:
        broken_rec = string_balances[0]
        draft.draft_letter(broken_rec, use_llm=False)
        print(f"\n  Letter for {broken_rec['account_id']} references balance: {broken_rec['balance_current']!r}")
        print(f"  That letter would go out with a nonsense number.")

    print("\n" + "=" * 60)
    print("  TO FIX: python3 run.py  (balance fix is ON by default)")
    print("=" * 60)


def fix():
    """Show the fixed version."""
    from pipeline import intake, validate

    print("=" * 60)
    print("  FIX 1: BALANCE TYPE COERCION")
    print("  Running pipeline WITH balance validation (default)...")
    print("=" * 60)

    records = intake.run(max_records=10)
    cleaned, fix_log, stats = validate.run(records, fix_balances=True)

    balance_fixes = [f for f in fix_log if "string_balance" in f.get("issue", "")]
    print(f"\n✅ {stats['balances_fixed']} balances coerced from strings to numbers")
    for fix in balance_fixes[:3]:
        print(f"    {fix['account_id']}: {fix['issue']} → {fix['action']}")

    # Now add them properly
    total = sum(float(rec.get("balance_current", 0)) for rec in cleaned[:3])
    print(f"\n  Actual total of first 3: ${total:,.2f}")
    print(f"  That's math.")

    print("\n" + "=" * 60)
    print("  FIX APPLIED. Pipeline catches type issues at intake.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        fix()
    else:
        trigger()
