"""
Stage 5: Review — the ethical center of the talk.

Inspects each draft letter and flags anything that asserts a fact
not present in the source record. Makes its work visible on screen.

This gate can be loosened (for the hallucination break demo) or
tightened. The default is strict.
"""

import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline.llm import generate


def _extract_claims(letter):
    """Extract factual claims from a letter (dates, amounts, names, actions)."""
    claims = []

    # Dates mentioned in the letter body (skip the header date line).
    # The first date in a letter is typically the letter date, not a
    # factual claim about the consumer's account.
    date_patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b",
    ]
    # Find where the letter body starts (after "Dear" or "RE:")
    body_start = 0
    for marker in ["Dear ", "RE:", "Re:"]:
        pos = letter.find(marker)
        if pos > 0:
            body_start = pos
            break

    for pattern in date_patterns:
        for match in re.finditer(pattern, letter, re.IGNORECASE):
            if match.start() < body_start:
                continue  # Skip header dates (letter date, address block)
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


MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def _normalize_date_for_comparison(date_str):
    """
    Normalize a date string to (year, month, day) tuple for comparison.
    Handles: "2024-06-18", "06/18/2024", "June 18, 2024", "June 18 2024".
    Returns None if unparseable.
    """
    s = date_str.strip().rstrip(".")

    # YYYY-MM-DD
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # MM/DD/YYYY
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return (int(m.group(3)), int(m.group(1)), int(m.group(2)))

    # Month DD, YYYY or Month DD YYYY
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})$", s)
    if m:
        month_name = m.group(1).lower()
        if month_name in MONTH_NAMES:
            return (int(m.group(3)), MONTH_NAMES[month_name], int(m.group(2)))

    return None


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
        # Check if this date appears anywhere in the record.
        # The model may write "June 18, 2024" while the record has "2024-06-18",
        # so normalize both sides before comparing.
        claim_normalized = _normalize_date_for_comparison(claim_value)
        for field in ["charge_off_date", "last_payment_date", "date_received"]:
            rec_val = str(record.get(field, "")).strip()
            if not rec_val:
                continue
            rec_normalized = _normalize_date_for_comparison(rec_val)
            if claim_normalized and rec_normalized and claim_normalized == rec_normalized:
                return True, f"Matches {field}"
            # Also try substring match for partial dates
            if claim_value in rec_val or rec_val in claim_value:
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
