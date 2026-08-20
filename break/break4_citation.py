#!/usr/bin/env python3
"""
BREAK 4: The Invented Law

Trigger: Inject a letter with a fabricated statutory citation.
Symptom: The letter cites "15 U.S.C. § 1692z" — a section that
         does not exist — and the review gate catches it.
Fix:     The citation validator is already on by default. This
         break shows what happens WITHOUT it.

Every attorney and compliance officer in this room knows what a
wrong citation does. It's not just sloppy — it's a liability.
"""

import sys
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


FAKE_LETTER = """\
August 15, 2026

Jordan Mitchell
3891 Maple Avenue
Arlington, TX 76010

RE: Account ACC-DEMO-001

Dear Jordan Mitchell,

We are writing in response to your dispute regarding the above-referenced
account. We have received your correspondence and are taking the following
steps.

Pursuant to 15 U.S.C. § 1692g, you have the right to request validation
of this debt within 30 days of receiving this notice. We are providing
the required disclosures under this section.

Additionally, under 15 U.S.C. § 1692z, we are required to provide you
with a full accounting of all fees and interest applied to your account
since the original charge-off date. This section mandates transparency
in post-charge-off balance calculations.

Furthermore, in accordance with 15 U.S.C. § 1692e(11), we are required
to disclose that this communication is from a debt collector and that
any information obtained will be used for that purpose.

Your current balance is $4,827.33. The original creditor was Summit Trust
Bank. If you wish to dispute this amount, please contact us within 30
days at the address above.

We also note your rights under 15 U.S.C. § 1681m(a) to receive notice
of any adverse action taken based on information in your consumer report.

Sincerely,

Redstone Collections Group
Compliance Department
"""


def trigger():
    """Show the citation validator catching a fabricated law."""
    from pipeline.review import review_letter, _extract_claims, _check_citation, VALID_CITATIONS

    print("=" * 60)
    print("  BREAK 4: THE INVENTED LAW")
    print("  Feeding a letter with a fabricated citation...")
    print("=" * 60)

    # Show what citations are in the letter
    claims = _extract_claims(FAKE_LETTER)
    cite_claims = [c for c in claims if c["type"] == "citation"]

    print(f"\n  Citations found in the letter:")
    for c in cite_claims:
        is_valid, reason = _check_citation(c, FAKE_LETTER)
        status = "✅" if is_valid else "🔴 FABRICATED"
        print(f"    {c['value']}: {status}")
        if is_valid:
            print(f"      {reason}")
        else:
            print(f"      {reason}")

    # Now run the full review
    record = {
        "account_id": "ACC-DEMO-001",
        "draft_letter": FAKE_LETTER,
        "balance_current": 4827.33,
        "balance_original": 6200.00,
        "charge_off_date": "2023-09-15",
        "last_payment_date": "2023-08-01",
        "last_payment_amount": "150.00",
        "original_creditor": "Summit Trust Bank",
        "consumer_name": "Jordan Mitchell",
        "state": "TX",
    }

    reviewed = review_letter(record, strict=True)

    print(f"\n  Review gate result: {'PASSED' if reviewed['review_passed'] else 'FLAGGED'}")
    for f in reviewed.get("review_findings", []):
        if f["claim_type"] == "citation":
            print(f"\n  🔴 CRITICAL: {f['reason']}")
            print(f"     The model cited a law that doesn't exist.")
            print(f"     15 U.S.C. § 1692z is not a real section.")
            print(f"     The FDCPA ends at § 1692p.")

    print(f"\n  For comparison, here are the real FDCPA sections:")
    fdcpa = {k: v for k, v in VALID_CITATIONS.items() if v.startswith("FDCPA") and len(k) <= 5}
    for section, desc in sorted(fdcpa.items()):
        print(f"    § {section}: {desc.split(' — ')[1]}")

    print("\n" + "=" * 60)
    print("  The model will eventually hallucinate a citation.")
    print("  The validator catches it before it goes out.")
    print("=" * 60)


def fix():
    """Show the validator catching citations correctly."""
    from pipeline.review import VALID_CITATIONS

    print("=" * 60)
    print("  FIX 4: CITATION VALIDATOR")
    print("=" * 60)

    print(f"\n  The review gate checks every statutory citation")
    print(f"  against a hardcoded allowlist of {len(VALID_CITATIONS)} real sections.")
    print(f"  If it's not on the list, or cited for the wrong purpose,")
    print(f"  it gets flagged as CRITICAL before the letter goes out.")

    print(f"\n✅ Valid citations in the allowlist:")
    shown = 0
    for section, desc in sorted(VALID_CITATIONS.items()):
        if len(section) <= 5 and shown < 10:
            print(f"    § {section}: {desc}")
            shown += 1

    print(f"\n  Total: {len(VALID_CITATIONS)} sections")
    print(f"  This is the gate's job: not trust, verify.")

    print("\n" + "=" * 60)
    print("  FIX APPLIED. Citation validator is on by default.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        fix()
    else:
        trigger()
