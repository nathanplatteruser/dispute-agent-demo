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


# --- Regression-specific letters for the false-positive bugs ---

LETTER_ENGLISH_DATE_MATCHES_RECORD = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

We acknowledge your dispute. The charge-off date for this account was
June 15, 2023. We are reviewing the matter.

Your current balance is $5,000.00.

Sincerely,
Test Agency
"""

LETTER_HEADER_DATE_ONLY = """\
March 17, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

We acknowledge your dispute and are reviewing the matter. We will
respond within 30 days.

Your current balance is $5,000.00.

Sincerely,
Test Agency
"""

LETTER_TWO_FABRICATED_AMOUNTS = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

Our records indicate the current balance is $33,660.66. A fee of
$1,299.00 was applied to the account.

Sincerely,
Test Agency
"""

LETTER_TWO_DATES_ONE_BAD = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

The charge-off date was June 15, 2023. We note a payment was received
on November 3, 2024, which has been applied.

Sincerely,
Test Agency
"""


def test_english_date_must_not_flag():
    """'June 15, 2023' matches record '2023-06-15' — must NOT flag."""
    rec = make_record(draft_letter=LETTER_ENGLISH_DATE_MATCHES_RECORD)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    date_findings = [f for f in findings if f["claim_type"] == "date"]

    if len(date_findings) == 0 and rec["review_passed"]:
        print(f"  PASS: 'June 15, 2023' correctly matched record '2023-06-15', 0 date findings")
        return True
    else:
        print(f"  FAIL: date was incorrectly flagged")
        print(f"    date_findings={date_findings}")
        return False


def test_header_date_must_not_flag():
    """Letter date 'March 17, 2026' in header must NOT flag."""
    rec = make_record(draft_letter=LETTER_HEADER_DATE_ONLY)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    date_findings = [f for f in findings if f["claim_type"] == "date"]

    if len(date_findings) == 0 and rec["review_passed"]:
        print(f"  PASS: header date not flagged, 0 date findings")
        return True
    else:
        print(f"  FAIL: header date was incorrectly flagged")
        print(f"    date_findings={date_findings}")
        return False


def test_fabricated_amount_is_critical():
    """$33,660.66 not in record — must flag as critical, not warning."""
    rec = make_record(draft_letter=LETTER_TWO_FABRICATED_AMOUNTS)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    amt_findings = [f for f in findings if f["claim_type"] == "amount"]
    critical_amts = [f for f in amt_findings if f["severity"] == "critical"]

    if len(critical_amts) == 2 and not rec["review_passed"]:
        print(f"  PASS: 2 fabricated amounts flagged as critical")
        return True
    else:
        print(f"  FAIL: expected 2 critical amount findings, got {len(critical_amts)}")
        print(f"    all amount findings: {[(f['severity'], f['claim_value']) for f in amt_findings]}")
        print(f"    review_passed={rec['review_passed']}")
        return False


def test_fabricated_date_is_critical():
    """Nov 3, 2024 not in record — must flag as critical."""
    rec = make_record(draft_letter=LETTER_TWO_DATES_ONE_BAD)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]
    date_findings = [f for f in findings if f["claim_type"] == "date"]
    critical_dates = [f for f in date_findings if f["severity"] == "critical"]

    # June 15, 2023 should match. November 3, 2024 should not.
    if len(critical_dates) == 1 and critical_dates[0]["claim_value"] == "November 3, 2024" and not rec["review_passed"]:
        print(f"  PASS: 1 fabricated date flagged as critical ('November 3, 2024'), record date passed")
        return True
    else:
        print(f"  FAIL: expected exactly 1 critical date finding for 'November 3, 2024'")
        print(f"    date_findings={[(f['severity'], f['claim_value']) for f in date_findings]}")
        print(f"    review_passed={rec['review_passed']}")
        return False


def test_finding_counts_exact():
    """Assert exact finding counts on a letter with known issues."""
    # Letter with: 1 fabricated date, 1 fabricated amount, 1 valid date, 1 valid amount
    letter = """\
August 1, 2026

Test Consumer
123 Main St
Arlington, TX 76010

RE: Account TEST-001

Dear Test Consumer,

The charge-off date was June 15, 2023. Your current balance is $5,000.00.

We also note a payment of $999.99 was received on April 4, 2025.

Sincerely,
Test Agency
"""
    rec = make_record(draft_letter=letter)
    review_letter(rec, strict=True)
    findings = rec["review_findings"]

    # Expected: April 4, 2025 = fabricated date (critical)
    #           $999.99 = fabricated amount (critical)
    #           payment assertion (critical)
    #           June 15, 2023 = matches record (no finding)
    #           $5,000.00 = matches record (no finding)
    critical = [f for f in findings if f["severity"] == "critical"]
    date_crits = [f for f in critical if f["claim_type"] == "date"]
    amt_crits = [f for f in critical if f["claim_type"] == "amount"]
    pay_crits = [f for f in critical if f["claim_type"] == "payment_assertion"]

    ok = True
    if len(date_crits) != 1:
        print(f"  FAIL: expected 1 critical date, got {len(date_crits)}: {[(f['claim_value']) for f in date_crits]}")
        ok = False
    if len(amt_crits) != 1:
        print(f"  FAIL: expected 1 critical amount, got {len(amt_crits)}: {[(f['claim_value']) for f in amt_crits]}")
        ok = False
    if not rec["review_passed"] == False:
        print(f"  FAIL: review_passed should be False")
        ok = False
    if ok:
        total = len(critical)
        print(f"  PASS: {total} critical findings (1 date, 1 amount, {len(pay_crits)} payment), review_passed=False")
    return ok


if __name__ == "__main__":
    print("=" * 55)
    print("  REVIEW GATE REGRESSION TEST")
    print("=" * 55)

    tests = [
        # Original tests
        ("Fabricated date flagged", test_fabricated_date),
        ("Fabricated amount flagged", test_fabricated_amount),
        ("Fabricated citation flagged", test_fabricated_citation),
        ("Payment with no history flagged", test_payment_no_history),
        ("Clean letter passes", test_clean_letter_passes),
        # New regression tests for the specific bugs
        ("English date matching record must NOT flag", test_english_date_must_not_flag),
        ("Header date must NOT flag", test_header_date_must_not_flag),
        ("Fabricated amounts must be CRITICAL", test_fabricated_amount_is_critical),
        ("Fabricated date must be CRITICAL", test_fabricated_date_is_critical),
        ("Exact finding counts on mixed letter", test_finding_counts_exact),
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

    print(f"\n  {sum(results.values())}/{len(results)} passed")

    if all_pass:
        print("  Review gate catches all known fabrication types")
        print("  and does not false-positive on valid data.")
    else:
        print("  REGRESSION DETECTED. Fix the gate before rehearsal.")

    sys.exit(0 if all_pass else 1)
