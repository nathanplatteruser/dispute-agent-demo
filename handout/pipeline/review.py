"""
Stage 5: Review — the ethical center of the pipeline.

HOW THIS WORKS (for non-developers):
-------------------------------------
This is the most important stage. It acts as a fact-checker between the
AI-drafted letter and the source record.

The AI might write "Your payment of $500 was received on March 15th"
but if the source record has no payment on file, that is a hallucination
— the AI invented a fact. This stage catches that.

What it checks:

  - DOLLAR AMOUNTS: Every dollar figure in the letter must match a number
    in the source record (balance, payment amount, etc.).

  - DATES: Every date in the letter must appear somewhere in the record.

  - PAYMENT CLAIMS: If the letter says "you paid," the record must show
    a payment history.

  - OUTCOME PROMISES: Statements like "this will be removed from your
    credit report" are always flagged because the agency cannot promise
    that unilaterally.

  - TONE: Aggressive language ("you clearly owe," "your failure to pay")
    is flagged as a compliance risk.

Each finding is marked as "warning" or "critical." A letter with any
critical finding fails the review and should not be sent.

This gate can be loosened for the demo to show what happens when you
turn it off — the hallucination break scenario.
"""

import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline.llm import generate


def _extract_claims(letter):
    """Extract factual claims from a letter (dates, amounts, names, actions)."""
    claims = []

    # Dates mentioned in the letter
    date_patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b",
    ]
    for pattern in date_patterns:
        for match in re.finditer(pattern, letter, re.IGNORECASE):
            claims.append({"type": "date", "value": match.group(), "position": match.start()})

    # Dollar amounts
    for match in re.finditer(r"\$[\d,]+\.?\d*", letter):
        claims.append({"type": "amount", "value": match.group(), "position": match.start()})

    # Payment assertions
    payment_phrases = [
        r"payment\s+(?:of\s+)?\$[\d,]+\.?\d*\s+(?:was\s+)?(?:made|received|processed|recorded)",
        r"you\s+paid\s+\$[\d,]+",
        r"paid\s+(?:on|in)\s+\w+",
        r"payment\s+date\s*(?:of|:)\s*\S+",
    ]
    for pattern in payment_phrases:
        for match in re.finditer(pattern, letter, re.IGNORECASE):
            claims.append({"type": "payment_assertion", "value": match.group(), "position": match.start()})

    # Specific outcome promises
    outcome_phrases = [
        r"(?:will|shall)\s+(?:be\s+)?(?:removed|deleted)\s+from\s+(?:your\s+)?credit",
        r"(?:will|shall)\s+(?:be\s+)?(?:forgiven|waived|cancelled)",
        r"balance.*(?:reduced|adjusted)\s+to\s+\$[\d,]+",
        r"(?:we|the\s+agency)\s+(?:will|shall)\s+(?:not|never)\s+(?:sue|litigate|pursue\s+legal)",
    ]
    for pattern in outcome_phrases:
        for match in re.finditer(pattern, letter, re.IGNORECASE):
            claims.append({"type": "outcome_promise", "value": match.group(), "position": match.start()})

    return claims


def _check_claim_against_record(claim, record):
    """
    Check if a claim in the letter is supported by the source record.
    Returns (is_supported, reason).
    """
    claim_type = claim["type"]
    claim_value = claim["value"]

    if claim_type == "amount":
        # Strip $ and commas for comparison
        claim_amount = claim_value.replace("$", "").replace(",", "")
        try:
            claim_float = float(claim_amount)
        except ValueError:
            return False, f"Unparseable amount: {claim_value}"

        # Check against known amounts in the record
        for field in ["balance_current", "balance_original", "last_payment_amount"]:
            rec_val = record.get(field, "")
            try:
                rec_float = float(str(rec_val).replace("$", "").replace(",", ""))
                if abs(rec_float - claim_float) < 0.01:
                    return True, f"Matches {field}"
            except (ValueError, TypeError):
                continue

        return False, f"Amount {claim_value} not found in source record"

    if claim_type == "date":
        # Check if this date appears anywhere in the record
        for field in ["charge_off_date", "last_payment_date", "date_received"]:
            rec_val = str(record.get(field, ""))
            if rec_val and (claim_value in rec_val or rec_val in claim_value):
                return True, f"Matches {field}"
        return False, f"Date {claim_value} not found in source record"

    if claim_type == "payment_assertion":
        # Payment assertions need evidence in the record
        last_payment = record.get("last_payment_date", "")
        last_amount = record.get("last_payment_amount", "")
        if last_payment or last_amount:
            return True, "Payment history exists in record"
        return False, "Letter asserts payment but no payment history in source record"

    if claim_type == "outcome_promise":
        # Outcome promises are always flagged — the agency can't unilaterally promise these
        return False, f"Outcome promise requires authorization: '{claim_value}'"

    return True, "Unknown claim type — passed"


def review_letter(record, strict=True):
    """
    Review a single letter against its source record.

    strict=True: flag all unsupported claims (default, correct behavior)
    strict=False: skip some checks (used for hallucination break demo)

    Returns the record with review findings added.
    """
    letter = record.get("draft_letter", "")
    if not letter:
        record["review_findings"] = [{"severity": "error", "message": "No draft letter to review"}]
        record["review_passed"] = False
        return record

    claims = _extract_claims(letter)
    findings = []

    for claim in claims:
        if not strict and claim["type"] in ("date", "payment_assertion"):
            continue  # Skip these checks in loose mode (hallucination break)

        is_supported, reason = _check_claim_against_record(claim, record)

        if not is_supported:
            findings.append({
                "severity": "warning" if claim["type"] == "amount" else "critical",
                "claim_type": claim["type"],
                "claim_value": claim["value"],
                "reason": reason,
                "position": claim["position"],
            })

    # Check for asserting things about the consumer's intent
    intent_phrases = [
        r"you\s+(?:clearly|obviously|evidently)\s+(?:owe|are\s+responsible)",
        r"your\s+(?:failure|refusal)\s+to\s+pay",
        r"you\s+(?:must|are\s+required\s+to)\s+pay\s+immediately",
    ]
    for pattern in intent_phrases:
        for match in re.finditer(pattern, letter, re.IGNORECASE):
            findings.append({
                "severity": "critical",
                "claim_type": "tone",
                "claim_value": match.group(),
                "reason": "Aggressive or presumptive language about consumer intent",
                "position": match.start(),
            })

    record["review_findings"] = findings
    record["review_passed"] = len([f for f in findings if f["severity"] == "critical"]) == 0
    record["review_warnings"] = len([f for f in findings if f["severity"] == "warning"])
    record["review_critical"] = len([f for f in findings if f["severity"] == "critical"])

    return record


def run(records, strict=True):
    """Execute the review stage."""
    print("\n🛡️  STAGE 5: REVIEW GATE")
    print("─" * 50)

    passed = 0
    flagged = 0
    total_findings = 0

    for i, rec in enumerate(records):
        if not rec.get("draft_letter"):
            continue

        review_letter(rec, strict=strict)

        if rec.get("review_passed"):
            passed += 1
        else:
            flagged += 1

        total_findings += len(rec.get("review_findings", []))

        if (i + 1) % 50 == 0:
            print(f"  Reviewed {i + 1}/{len(records)}...")

    print(f"  Review complete: {len(records)} letters examined")
    print(f"  ✅ Passed: {passed}")
    print(f"  🚩 Flagged: {flagged}")
    print(f"  Total findings: {total_findings}")

    if flagged > 0:
        print(f"\n  Sample findings from flagged letters:")
        shown = 0
        for rec in records:
            if rec.get("review_findings") and shown < 3:
                print(f"    Account {rec.get('account_id', '?')}:")
                for finding in rec["review_findings"][:2]:
                    print(f"      [{finding['severity']}] {finding['reason']}")
                shown += 1

    return records
