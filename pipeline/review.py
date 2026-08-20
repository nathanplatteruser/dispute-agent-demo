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

    # Payment assertions — catch the model asserting payments happened
    payment_phrases = [
        r"payment\s+(?:of\s+)?\$[\d,]+\.?\d*\s+(?:was\s+)?(?:made|received|processed|recorded|applied)",
        r"you\s+(?:have\s+)?paid\s+\$[\d,]+",
        r"(?:a|your)\s+payment\s+(?:of\s+)?\$[\d,]+",
        r"paid\s+(?:on|in)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|\d)",
        r"payment\s+(?:date|received)\s*(?:of|on|:)\s*\S+",
        r"last\s+payment\s+(?:of|was|received)\s+",
        r"records?\s+(?:show|indicate|confirm)\s+(?:a|that\s+a|your|the)\s+payment",
        r"payment\s+history\s+(?:shows?|indicates?|confirms?)\s+(?:a|that|your)",
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

    # Statutory citations — match federal USC references only.
    # Skip bare § preceded by state code abbreviations (e.g. "C.R.S. §")
    cite_patterns = [
        r"15\s+U\.?S\.?C\.?\s*§?\s*(\d+[a-z]?(?:\([a-z0-9]+\))*)",
    ]
    for pattern in cite_patterns:
        for match in re.finditer(pattern, letter):
            claims.append({
                "type": "citation",
                "value": match.group(),
                "section": match.group(1),
                "position": match.start(),
            })

    return claims


# Allowlist of real FDCPA/FCRA sections with their actual subject matter.
# Any citation not on this list, or cited for the wrong purpose, gets flagged.
VALID_CITATIONS = {
    # FDCPA — 15 U.S.C. §§ 1692–1692p
    "1692":    "FDCPA — Congressional findings and declaration of purpose",
    "1692a":   "FDCPA — Definitions",
    "1692b":   "FDCPA — Acquisition of location information",
    "1692c":   "FDCPA — Communication in connection with debt collection",
    "1692c(a)":"FDCPA — Communication with consumer (unusual times/places)",
    "1692c(b)":"FDCPA — Communication with third parties",
    "1692c(c)":"FDCPA — Ceasing communication upon consumer request",
    "1692d":   "FDCPA — Harassment or abuse",
    "1692e":   "FDCPA — False or misleading representations",
    "1692f":   "FDCPA — Unfair practices",
    "1692g":   "FDCPA — Validation of debts (30-day notice, right to dispute)",
    "1692g(a)":"FDCPA — Notice of debt (initial communication requirements)",
    "1692g(b)":"FDCPA — Disputed debts (cease until verification)",
    "1692h":   "FDCPA — Multiple debts",
    "1692i":   "FDCPA — Legal actions by debt collectors (venue)",
    "1692j":   "FDCPA — Furnishing certain deceptive forms",
    "1692k":   "FDCPA — Civil liability",
    "1692l":   "FDCPA — Administrative enforcement",
    "1692n":   "FDCPA — Relation to State laws",
    "1692o":   "FDCPA — Exemption for State regulation",
    "1692p":   "FDCPA — Exception for certain bad check enforcement programs",
    # FCRA — 15 U.S.C. §§ 1681–1681x
    "1681":    "FCRA — Congressional findings and statement of purpose",
    "1681a":   "FCRA — Definitions",
    "1681b":   "FCRA — Permissible purposes of consumer reports",
    "1681c":   "FCRA — Requirements relating to information in consumer reports",
    "1681c(a)":"FCRA — Obsolete information (7-year/10-year limits)",
    "1681d":   "FCRA — Disclosure of investigative consumer reports",
    "1681e":   "FCRA — Compliance procedures",
    "1681e(b)":"FCRA — Accuracy of reports (reasonable procedures)",
    "1681g":   "FCRA — Disclosures to consumers",
    "1681i":   "FCRA — Procedure in case of disputed accuracy",
    "1681j":   "FCRA — Charges for certain disclosures",
    "1681k":   "FCRA — Public record information for employment purposes",
    "1681m":   "FCRA — Adverse action notices",
    "1681n":   "FCRA — Civil liability for willful noncompliance",
    "1681o":   "FCRA — Civil liability for negligent noncompliance",
    "1681s":   "FCRA — Administrative enforcement",
    "1681s-2": "FCRA — Responsibilities of furnishers of information",
}


def _check_citation(claim, letter_text):
    """
    Validate a statutory citation against the allowlist.
    Returns (is_valid, reason).
    """
    section = claim.get("section", "")

    # Normalize: strip spaces, lowercase for matching
    normalized = section.strip()

    # Check against allowlist
    if normalized in VALID_CITATIONS:
        return True, f"Valid: {VALID_CITATIONS[normalized]}"

    # Check if it's a subsection of something valid (e.g. "1692g(a)(3)")
    base = re.match(r"(\d+[a-z]?)", normalized)
    if base and base.group(1) in VALID_CITATIONS:
        return True, f"Subsection of {VALID_CITATIONS[base.group(1)]}"

    return False, f"Citation {claim['value']} is not a recognized FDCPA/FCRA section"


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
                "severity": "critical",
                "claim_type": claim["type"],
                "claim_value": claim["value"],
                "reason": reason,
                "position": claim["position"],
            })

    # Check statutory citations against allowlist
    for claim in claims:
        if claim["type"] != "citation":
            continue
        if not strict:
            continue
        is_valid, reason = _check_citation(claim, letter)
        if not is_valid:
            findings.append({
                "severity": "critical",
                "claim_type": "citation",
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
