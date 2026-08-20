#!/usr/bin/env python3
"""
Review Gate Regression Test

Asserts that known-bad letters get flagged. If any of these pass,
the gate is broken.

Usage:
    python3 break/test_review_gate.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pipeline.review import review_letter, _extract_claims


def make_record(**overrides):
    """Base record with no payment history."""
    rec = {
        "account_id": "TEST-001",
        "balance_current": 5000.00,
        "balance_original": 7500.00,
        "charge_off_date": "2023-06-15",
        "last_payment_date": "",
        "last_payment_amount": "",
        "original_creditor": "Test Bank",
        "consumer_name": "Test Consumer",
        "state": "TX",
    }
    rec.update(overrides)
    return rec


# --- Test letters with known fabrications ---

LETTER_FABRICATED_DATE = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

We acknowledge your dispute regarding the above account. Our records
show the original charge-off date was June 15, 2023.

We also note that a payment of $500.00 was received on March 12, 2024,
which has been applied to your account.

Sincerely,
Test Agency
"""

LETTER_FABRICATED_AMOUNT = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

We acknowledge your dispute. The current balance on your account is
$33,660.66. We will provide an itemized statement.

Sincerely,
Test Agency
"""

LETTER_FABRICATED_CITATION = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

Pursuant to 15 U.S.C. § 1692z, we are required to provide you with
a full accounting of all fees applied to your account.

Sincerely,
Test Agency
"""

LETTER_PAYMENT_NO_HISTORY = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

We acknowledge your dispute. Our records show that your last payment
of $250.00 was received on January 5, 2024. This payment has been
applied to your balance.

Sincerely,
Test Agency
"""

LETTER_CLEAN = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

We acknowledge your dispute regarding the above account. We are
reviewing the matter and will respond within 30 days.

Your current balance is $5,000.00.

Sincerely,
Test Agency
"""


def test_fabricated_date():
    """Letter asserts March 12, 2024 — not in record."""
    rec = make_record(draft_letter=LETTER_FABRICATED_DATE)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    date_findings = [f for f in findings if f["claim_type"] == "date"]
    passed = rec["review_passed"]

    if date_findings and not passed:
        print(f"  PASS: fabricated date flagged — {date_findings[0]['claim_value']!r}")
        return True
    else:
        print(f"  FAIL: fabricated date NOT caught")
        print(f"    findings={findings}")
        print(f"    review_passed={passed}")
        return False


def test_fabricated_amount():
    """Letter asserts $33,660.66 — not in record (record has $5000/$7500)."""
    rec = make_record(draft_letter=LETTER_FABRICATED_AMOUNT)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    amt_findings = [f for f in findings if f["claim_type"] == "amount"]
    passed = rec["review_passed"]

    if amt_findings and not passed:
        print(f"  PASS: fabricated amount flagged — {amt_findings[0]['claim_value']!r} (critical)")
        return True
    else:
        print(f"  FAIL: fabricated amount NOT caught or not critical")
        print(f"    findings={findings}")
        return False


def test_fabricated_citation():
    """Letter cites § 1692z — does not exist."""
    rec = make_record(draft_letter=LETTER_FABRICATED_CITATION)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    cite_findings = [f for f in findings if f["claim_type"] == "citation"]
    passed = rec["review_passed"]

    if cite_findings and not passed:
        print(f"  PASS: fabricated citation flagged — {cite_findings[0]['claim_value']!r}")
        return True
    else:
        print(f"  FAIL: fabricated citation NOT caught")
        print(f"    findings={findings}")
        return False


def test_payment_no_history():
    """Letter asserts payment when record has no payment history."""
    rec = make_record(draft_letter=LETTER_PAYMENT_NO_HISTORY)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    pay_findings = [f for f in findings if f["claim_type"] in ("payment_assertion", "date")]
    passed = rec["review_passed"]

    if pay_findings and not passed:
        types = [f["claim_type"] for f in pay_findings]
        print(f"  PASS: payment assertion flagged — types={types}")
        return True
    else:
        print(f"  FAIL: payment assertion NOT caught")
        print(f"    findings={findings}")
        return False


def test_clean_letter_passes():
    """A clean letter with only real facts should pass."""
    rec = make_record(draft_letter=LETTER_CLEAN)
    review_letter(rec, strict=True)
    passed = rec["review_passed"]
    findings = rec["review_findings"]

    if passed:
        print(f"  PASS: clean letter passed review")
        return True
    else:
        print(f"  FAIL: clean letter was incorrectly flagged")
        print(f"    findings={findings}")
        return False


if __name__ == "__main__":
    print("=" * 55)
    print("  REVIEW GATE REGRESSION TEST")
    print("=" * 55)

    tests = [
        ("Fabricated date", test_fabricated_date),
        ("Fabricated amount (critical)", test_fabricated_amount),
        ("Fabricated citation", test_fabricated_citation),
        ("Payment with no history", test_payment_no_history),
        ("Clean letter passes", test_clean_letter_passes),
    ]

    results = {}
    for name, fn in tests:
        print(f"\n── {name} ──")
        results[name] = fn()

    print("\n" + "=" * 55)
    print("  RESULTS")
    print("=" * 55)
    all_pass = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n  Review gate catches all known fabrication types.")
    else:
        print("\n  REGRESSION DETECTED. Fix the gate before rehearsal.")

    sys.exit(0 if all_pass else 1)
