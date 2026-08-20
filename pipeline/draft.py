"""
Stage 4: Draft — generate a compliant dispute-response letter per record.

Each letter is drafted from the source record only. The review gate
(Stage 5) will catch anything that asserts facts not in the record.
"""

import sys
import os
import textwrap
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline.llm import generate, tier_status_line

LETTER_SYSTEM = """\
You are a compliance letter drafter for a debt collection agency.
Write a dispute response letter based ONLY on the facts provided in the record below.

RULES:
1. Only state facts present in the provided record. Do not invent dates, amounts, or events.
2. Be professional and respectful.
3. Reference specific regulatory requirements (FDCPA, state law) where applicable.
4. Acknowledge the consumer's dispute clearly.
5. State what action the agency will take (investigate, provide validation, cease, etc.).
6. Include the consumer's right to further dispute.
7. Keep the letter under 400 words.
8. Do not use threatening language.
9. Address the specific type of dispute raised.

Format the letter with:
- Date line (use the provided letter date)
- Consumer name and address (use the provided values)
- RE: Account reference
- Body paragraphs
- Closing with the provided agency/servicer name
- Format all currency amounts as $X,XXX.XX (e.g. $1,234.56, not 1234.56)
"""


def _build_prompt(record):
    """Build the drafting prompt from a record."""
    account_id = record.get("account_id", "UNKNOWN")
    dispute_type = record.get("classified_type", "general")
    narrative = record.get("narrative", "")[:600]
    balance = _format_currency(record.get("balance_current", "unknown"))
    creditor = record.get("original_creditor", "unknown")
    state = record.get("state", "")
    validation_requested = record.get("validation_requested", "")
    last_payment = record.get("last_payment_date", "")
    charge_off = record.get("charge_off_date", "")
    consumer_name = record.get("consumer_name", "Consumer")
    servicer = record.get("current_servicer", "Account Services Department")
    letter_date = _synthetic_letter_date(record)
    address = _synthetic_address(consumer_name, state)

    prompt = f"""Draft a dispute response letter for this account.

RECORD FACTS (use ONLY these):
- Account ID: {account_id}
- Dispute type: {dispute_type}
- Current balance: {balance}
- Original creditor: {creditor}
- State: {state}
- Charge-off date: {charge_off}
- Last payment date: {last_payment or 'None on file'}
- Validation requested: {validation_requested}

LETTER HEADER (use these exactly):
- Letter date: {letter_date}
- Consumer name: {consumer_name}
- Consumer address: {address}
- Agency name: {servicer}

CONSUMER'S DISPUTE:
{narrative}

Write the response letter now. Format all dollar amounts as $X,XXX.XX.
Remember: only assert facts from the record above."""

    return prompt


def _fill_placeholders(letter, record):
    """Replace any remaining bracket placeholders in LLM output."""
    import re
    consumer_name = record.get("consumer_name", "Consumer")
    state = record.get("state", "TX")
    servicer = record.get("current_servicer", "Account Services Department")
    letter_date = _synthetic_letter_date(record)
    address = _synthetic_address(consumer_name, state)

    # Replace common placeholders the model might leave
    replacements = {
        "[DATE]": letter_date,
        "[CONSUMER ADDRESS]": address,
        "[CONSUMER NAME]": consumer_name,
        "[AGENCY NAME]": servicer,
        "[COMPANY NAME]": servicer,
        "[CREDITOR NAME]": record.get("original_creditor", "the original creditor"),
    }
    for placeholder, value in replacements.items():
        letter = letter.replace(placeholder, value)

    # Also catch case-insensitive and slight variations
    letter = re.sub(r"\[(?:Consumer|Your)\s*(?:Name|Address)\]", consumer_name, letter, flags=re.IGNORECASE)
    letter = re.sub(r"\[(?:Agency|Company|Servicer)\s*(?:Name)?\]", servicer, letter, flags=re.IGNORECASE)
    letter = re.sub(r"\[Date\]", letter_date, letter, flags=re.IGNORECASE)

    return letter


def draft_letter(record, use_llm=True):
    """Generate a draft letter for a single record."""
    if use_llm:
        prompt = _build_prompt(record)
        response, tier = generate(prompt, LETTER_SYSTEM)
        if response:
            record["draft_letter"] = _fill_placeholders(response.strip(), record)
            record["draft_tier"] = tier
            return record

    # Template fallback (or --no-llm mode)
    record["draft_letter"] = _template_letter(record)
    record["draft_tier"] = "template"
    return record


def _format_currency(val):
    """Format a balance value as $X,XXX.XX."""
    try:
        num = float(str(val).replace("$", "").replace(",", ""))
        return f"${num:,.2f}"
    except (ValueError, TypeError):
        return str(val)


def _template_letter(record):
    """Fallback template letter when no LLM is available."""
    account_id = record.get("account_id", "UNKNOWN")
    dispute_type = record.get("classified_type", "general")
    balance = _format_currency(record.get("balance_current", "unknown"))
    creditor = record.get("original_creditor", "unknown")

    type_responses = {
        "identity_theft": (
            "We take allegations of identity theft very seriously. Upon receipt of your "
            "dispute, we are placing a hold on all collection activity for account {account_id} "
            "pending our investigation. Please provide any supporting documentation such as "
            "a police report or FTC Identity Theft Report to assist in our review."
        ),
        "not_mine": (
            "We acknowledge your dispute that the debt associated with account {account_id} "
            "does not belong to you. We are initiating an investigation and will provide "
            "validation documentation within 30 days. Collection activity on this account "
            "is suspended during our review."
        ),
        "already_paid": (
            "We acknowledge your claim that the balance on account {account_id} has been "
            "paid. We are reviewing our records and contacting the original creditor, "
            "{creditor}, to verify payment status. If you have proof of payment, please "
            "forward it to expedite our review."
        ),
        "wrong_amount": (
            "We acknowledge your dispute regarding the balance of {balance} on account "
            "{account_id}. We are reviewing the account history with the original creditor, "
            "{creditor}, to verify the correct amount owed. We will provide an itemized "
            "statement within 30 days."
        ),
        "validation_request": (
            "We are in receipt of your request for debt validation on account {account_id}. "
            "As required under the Fair Debt Collection Practices Act, we are ceasing all "
            "collection activity until we provide you with verification of the debt, "
            "including documentation from the original creditor, {creditor}."
        ),
        "statute_of_limitations": (
            "We acknowledge your dispute regarding account {account_id}. We are reviewing "
            "the applicable statute of limitations for your state of residence. No legal "
            "action will be taken on this account while this review is pending."
        ),
        "hardship": (
            "We acknowledge the financial hardship you described regarding account "
            "{account_id}. We would like to work with you to find a resolution. Please "
            "contact us to discuss available options, which may include a modified payment "
            "plan or settlement arrangement."
        ),
    }

    body = type_responses.get(dispute_type, type_responses["validation_request"])
    body = body.format(
        account_id=account_id,
        balance=balance,
        creditor=creditor,
    )

    consumer_name = record.get("consumer_name", "Consumer")
    state = record.get("state", "TX")
    servicer = record.get("current_servicer", "Account Services Department")
    letter_date = _synthetic_letter_date(record)
    address = _synthetic_address(consumer_name, state)

    letter = textwrap.dedent(f"""\
    {letter_date}

    {address}

    RE: Account {account_id}

    Dear {consumer_name},

    Thank you for contacting us regarding your account. We have received and
    logged your dispute.

    {body}

    You have the right to dispute this debt again at any time. If you have
    questions about your rights under the Fair Debt Collection Practices Act,
    you may contact the Consumer Financial Protection Bureau at
    consumerfinance.gov or (855) 411-2372.

    Sincerely,

    {servicer}
    Compliance Department
    """)

    return letter


def _synthetic_letter_date(record):
    """Generate a plausible letter date from the record."""
    import hashlib
    # Deterministic but plausible: hash the account ID to pick a recent date
    seed = int(hashlib.md5(record.get("account_id", "").encode()).hexdigest()[:8], 16)
    day = (seed % 28) + 1
    month = (seed // 28 % 12) + 1
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return f"{months[month - 1]} {day}, 2026"


# Synthetic street names and cities by state — just enough to look real on a projector
_STREETS = [
    "142 Oakwood Drive", "3891 Maple Avenue", "507 Cedar Lane",
    "2240 Birch Street", "1018 Elm Court", "765 Willow Road",
    "4422 Pine Bluff Way", "330 Spruce Circle", "1987 Aspen Trail",
]
_CITIES_BY_STATE = {
    "TX": "Arlington, TX 76010", "CA": "Riverside, CA 92501",
    "FL": "Lakeland, FL 33801", "NY": "Rochester, NY 14604",
    "IL": "Naperville, IL 60540", "PA": "Allentown, PA 18101",
    "OH": "Dayton, OH 45402", "GA": "Savannah, GA 31401",
    "NC": "Durham, NC 27701", "MI": "Lansing, MI 48933",
    "NJ": "Edison, NJ 08817", "VA": "Richmond, VA 23219",
    "MO": "Springfield, MO 65801", "AZ": "Mesa, AZ 85201",
    "CO": "Aurora, CO 80012", "WA": "Tacoma, WA 98402",
}


def _synthetic_address(consumer_name, state):
    """Generate a plausible synthetic mailing address."""
    import hashlib
    seed = int(hashlib.md5(consumer_name.encode()).hexdigest()[:8], 16)
    street = _STREETS[seed % len(_STREETS)]
    city_line = _CITIES_BY_STATE.get(state, f"Springfield, {state} 62701")
    return f"{consumer_name}\n{street}\n{city_line}"


def run(records, max_drafts=None, use_llm=True):
    """Execute the drafting stage."""
    print("\n✍️  STAGE 4: DRAFT")
    print("─" * 50)

    to_draft = records[:max_drafts] if max_drafts else records
    tier_counts = {}

    for i, rec in enumerate(to_draft):
        draft_letter(rec, use_llm=use_llm)
        tier = rec.get("draft_tier", "unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        if (i + 1) % 10 == 0 or (i + 1) == len(to_draft):
            print(f"  Drafted {i + 1}/{len(to_draft)} letters  [{tier_status_line()}]")

    print(f"  Drafting complete: {len(to_draft)} letters")
    print(f"  Tiers used: {tier_counts}")

    return records
