"""
Stage 2: Validate — type coercion, dedupe, normalization, defect detection.

HOW THIS WORKS (for non-developers):
-------------------------------------
Real-world data is messy. This stage cleans it up before anything else
touches it. Here is what it fixes:

- STRING BALANCES: Some balances come in as text like "$1,234.56" instead
  of the number 1234.56. If you try to add text together, you get nonsense
  ("$500$300" instead of 800). This stage strips the dollar signs and
  commas and converts everything to proper numbers.

- DATE FORMATS: Some dates arrive as "03/15/2023" instead of "2023-03-15".
  This stage normalizes them all to the same format so comparisons work.

- STATE CODES: Some records say "California" instead of "CA". This stage
  converts full names to two-letter codes.

- DUPLICATES: Some account IDs appear more than once. This stage removes
  the duplicate rows.

- MISSING DATA: If a record says "5 prior contacts" but has no contact
  log, that inconsistency gets flagged.

Every fix is logged so you can see exactly what changed. Nothing is hidden.
"""

import re
from datetime import datetime

# US state code mapping for normalization
STATE_CODES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}


def _parse_balance(val):
    """
    Parse a balance value that might be a string with currency formatting.
    Returns (float_value, was_fixed: bool, original_string).

    This is where the string-balance defect gets caught (or not, if validation
    is disabled for the break demo).
    """
    if isinstance(val, (int, float)):
        return float(val), False, str(val)

    original = str(val)
    cleaned = original.strip()

    if not cleaned:
        return 0.0, True, original

    # Remove currency symbols and commas
    cleaned = cleaned.replace("$", "").replace(",", "").strip()

    try:
        return float(cleaned), True, original
    except ValueError:
        return 0.0, True, original


def _normalize_date(val):
    """
    Normalize date strings to YYYY-MM-DD format.
    Returns (normalized_string, was_fixed: bool).
    """
    if not val or val.strip() == "" or val.strip().lower() == "null":
        return "", False

    val = val.strip()

    # Already in correct format?
    if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        return val, False

    # Try MM/DD/YYYY
    try:
        dt = datetime.strptime(val, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d"), True
    except ValueError:
        pass

    # Try M/D/YYYY
    try:
        dt = datetime.strptime(val, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d"), True
    except ValueError:
        pass

    # Try DD-MM-YYYY
    try:
        dt = datetime.strptime(val, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d"), True
    except ValueError:
        pass

    return val, False


def _normalize_state(val):
    """Normalize state to two-letter code."""
    if not val:
        return "", False

    val = val.strip()

    # Already a two-letter code?
    if len(val) == 2 and val.isalpha():
        return val.upper(), val != val.upper()

    # Full state name?
    lookup = val.lower()
    if lookup in STATE_CODES:
        return STATE_CODES[lookup], True

    return val, False


def validate_records(records, fix_balances=True):
    """
    Validate and clean records. Returns (cleaned_records, fix_log).

    fix_balances: if False, string balances pass through uncorrected.
    This is the knob the break-and-fix demo turns.
    """
    fix_log = []
    seen_ids = set()
    cleaned = []
    dupes_removed = 0
    balances_fixed = 0
    dates_fixed = 0
    states_fixed = 0
    nulls_flagged = 0

    for rec in records:
        account_id = rec.get("account_id", "")

        # Dedupe
        if account_id in seen_ids:
            dupes_removed += 1
            fix_log.append({
                "account_id": account_id,
                "field": "account_id",
                "issue": "duplicate",
                "action": "removed"
            })
            continue
        seen_ids.add(account_id)

        cleaned_rec = dict(rec)

        # Balance coercion
        for field in ["balance_current", "balance_original"]:
            val = rec.get(field, 0)
            parsed, was_fixed, original = _parse_balance(val)

            if fix_balances:
                cleaned_rec[field] = parsed
                if was_fixed:
                    balances_fixed += 1
                    fix_log.append({
                        "account_id": account_id,
                        "field": field,
                        "issue": f"string_balance: '{original}'",
                        "action": f"coerced to {parsed}"
                    })
            else:
                # Leave as-is for break demo — this is where concatenation happens
                cleaned_rec[field] = val

        # Date normalization
        for field in ["charge_off_date", "last_payment_date"]:
            val = rec.get(field, "")
            normalized, was_fixed = _normalize_date(val)
            cleaned_rec[field] = normalized
            if was_fixed:
                dates_fixed += 1
                fix_log.append({
                    "account_id": account_id,
                    "field": field,
                    "issue": f"date_format: '{val}'",
                    "action": f"normalized to {normalized}"
                })

        # State normalization
        state = rec.get("state", "")
        normalized_state, was_fixed = _normalize_state(state)
        cleaned_rec["state"] = normalized_state
        if was_fixed:
            states_fixed += 1
            fix_log.append({
                "account_id": account_id,
                "field": "state",
                "issue": f"state_format: '{state}'",
                "action": f"normalized to {normalized_state}"
            })

        # Null consistency check
        prior_contacts = rec.get("prior_contacts", "0")
        contact_log = rec.get("contact_log", "")
        try:
            n_contacts = int(prior_contacts)
        except (ValueError, TypeError):
            n_contacts = 0

        if n_contacts > 0 and (not contact_log or contact_log.strip() in ("", "null", "[]")):
            nulls_flagged += 1
            fix_log.append({
                "account_id": account_id,
                "field": "contact_log",
                "issue": f"null_contact_log with {n_contacts} prior contacts",
                "action": "flagged — data inconsistency"
            })

        cleaned.append(cleaned_rec)

    return cleaned, fix_log, {
        "input_count": len(records),
        "output_count": len(cleaned),
        "duplicates_removed": dupes_removed,
        "balances_fixed": balances_fixed,
        "dates_fixed": dates_fixed,
        "states_fixed": states_fixed,
        "nulls_flagged": nulls_flagged,
    }


def run(records, fix_balances=True):
    """Execute the validation stage."""
    print("\n🔍 STAGE 2: VALIDATE")
    print("─" * 50)

    cleaned, fix_log, stats = validate_records(records, fix_balances=fix_balances)

    print(f"  Records in:  {stats['input_count']}")
    print(f"  Records out: {stats['output_count']}")
    print(f"  Fixes applied:")
    print(f"    Duplicates removed:  {stats['duplicates_removed']}")
    print(f"    Balances coerced:    {stats['balances_fixed']}")
    print(f"    Dates normalized:    {stats['dates_fixed']}")
    print(f"    States normalized:   {stats['states_fixed']}")
    print(f"    Null inconsistencies: {stats['nulls_flagged']}")

    return cleaned, fix_log, stats
