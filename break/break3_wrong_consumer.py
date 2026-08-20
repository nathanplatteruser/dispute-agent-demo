#!/usr/bin/env python3
"""
BREAK 3: The Wrong-Consumer Break (Collections-Specific)

Trigger: Corrupt the account-to-narrative mapping so a response letter
         addresses the wrong dispute. Consumer says "identity theft" but
         the letter responds to "wrong amount."
Symptom: The letter talks about verifying the balance when the consumer
         is saying "this isn't me at all."
Fix:     Re-run with intake integrity checks that catch mismatches.

Every practitioner in this room has seen this. A consumer calls about
identity theft and gets a form letter about payment plans. It destroys
trust, triggers complaints, and the CFPB narrative data is full of it.
"""

import sys
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def trigger():
    """Scramble the narrative-to-record mapping."""
    from pipeline import intake, validate, classify, draft, review, consumer_view

    print("=" * 60)
    print("  BREAK 3: THE WRONG-CONSUMER BREAK")
    print("  Scrambling dispute type vs. response mapping...")
    print("=" * 60)

    records = intake.run(max_records=20)
    cleaned, _, _ = validate.run(records)

    # BREAK: Swap classified types so responses don't match narratives
    rng = random.Random(99)
    original_types = [(r["account_id"], r.get("dispute_type", "")) for r in cleaned]

    # Force mismatches: identity_theft gets wrong_amount response, etc.
    swap_map = {
        "identity_theft": "wrong_amount",
        "wrong_amount": "already_paid",
        "already_paid": "hardship",
        "hardship": "validation_request",
        "validation_request": "identity_theft",
        "not_mine": "wrong_amount",
        "statute_of_limitations": "already_paid",
    }

    mismatched = 0
    for rec in cleaned:
        original = rec.get("dispute_type", "validation_request")
        swapped = swap_map.get(original, original)
        if swapped != original:
            rec["classified_type"] = swapped
            rec["classification_method"] = "CORRUPTED"
            mismatched += 1
        else:
            rec["classified_type"] = original
            rec["classification_method"] = "keywords"

    print(f"\n🔴 Scrambled {mismatched} dispute-to-response mappings")

    # Draft letters with wrong types
    drafted = draft.run(cleaned, max_drafts=5, use_llm=False)

    # Show the damage
    print("\n🔴 DAMAGE EXAMPLES:")
    for rec in drafted[:3]:
        if rec.get("draft_letter"):
            orig_type = rec.get("dispute_type", "?")
            resp_type = rec.get("classified_type", "?")
            print(f"\n  Account {rec['account_id']}:")
            print(f"    Consumer's dispute: {orig_type}")
            print(f"    Letter responds to: {resp_type}")
            if orig_type != resp_type:
                print(f"    ❌ MISMATCH — consumer says '{orig_type}', letter addresses '{resp_type}'")

    # Run consumer view to show impact
    consumer_view.run(drafted)

    print("\n  This is what consumers report to the CFPB:")
    print("  'I told them it wasn't my account and they sent me a payment plan.'")
    print("  'They completely ignored what I said in my dispute.'")

    print("\n" + "=" * 60)
    print("  TO FIX: python3 run.py  (correct mapping is default)")
    print("=" * 60)


def fix():
    """Show correct dispute routing."""
    from pipeline import intake, validate, classify, draft, review

    print("=" * 60)
    print("  FIX 3: CORRECT DISPUTE ROUTING")
    print("=" * 60)

    records = intake.run(max_records=10)
    cleaned, _, _ = validate.run(records)
    classified = classify.run(cleaned, use_llm=False)

    print("\n✅ CORRECT MAPPING:")
    for rec in classified[:5]:
        print(f"  {rec['account_id']}: dispute={rec.get('dispute_type', '?')} → classified={rec.get('classified_type', '?')} ({rec.get('classification_method', '?')})")

    drafted = draft.run(classified, max_drafts=5, use_llm=False)

    matches = sum(1 for r in drafted if r.get("classified_type") == r.get("dispute_type") and r.get("draft_letter"))
    print(f"\n  {matches} of {len([r for r in drafted if r.get('draft_letter')])} letters match their dispute type")
    print(f"  Each consumer gets a response to what they actually said.")

    print("\n" + "=" * 60)
    print("  FIX APPLIED. Route the dispute, then respond to it.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        fix()
    else:
        trigger()
