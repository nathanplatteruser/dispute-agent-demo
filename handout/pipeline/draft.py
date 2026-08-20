"""
Stage 4: Draft — generate a compliant dispute-response letter per record.

HOW THIS WORKS (for non-developers):
-------------------------------------
This is where the pipeline writes a response letter for each dispute.
It has two modes:

  1. LLM MODE: Sends the account data and the consumer's complaint to an
     AI model and asks it to draft a professional, compliant letter. The
     AI is given strict rules: only state facts from the record, be
     respectful, reference the FDCPA, acknowledge the dispute, and explain
     what happens next.

  2. TEMPLATE MODE: If no AI model is available (offline, no API key),
     it uses pre-written template letters customized with account details.
     These are simpler but still compliant.

The key constraint: the AI can only use facts from the source record.
It cannot invent dates, amounts, or events. Stage 5 (Review) will catch
it if it does.
"""

import sys
import os
import textwrap
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline.llm import generate, tier_status_line

# ─────────────────────────────────────────────────────────────────────────────
# This is the system prompt given to the AI when drafting letters.
# It defines the rules the AI must follow. You can read the full text in
# prompts.txt in this handout folder.
# ─────────────────────────────────────────────────────────────────────────────
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
- Date line
- Consumer name and address placeholder [CONSUMER ADDRESS]
- RE: Account reference
- Body paragraphs
- Closing with agency name placeholder [AGENCY NAME]
"""


def _build_prompt(record):
    """Build the drafting prompt from a record."""
    account_id = record.get("account_id", "UNKNOWN")
    dispute_type = record.get("classified_type", "general")
    narrative = record.get("narrative", "")[:600]
    balance = record.get("balance_current", "unknown")
    creditor = record.get("original_creditor", "unknown")
    state = record.get("state", "")
    validation_requested = record.get("validation_requested", "")
    last_payment = record.get("last_payment_date", "")
    charge_off = record.get("charge_off_date", "")

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

CONSUMER'S DISPUTE:
{narrative}

Write the response letter now. Remember: only assert facts from the record above."""

    return prompt


def draft_letter(record, use_llm=True):
    """Generate a draft letter for a single record."""
    if use_llm:
        prompt = _build_prompt(record)
        response, tier = generate(prompt, LETTER_SYSTEM)
        if response:
            record["draft_letter"] = response.strip()
            record["draft_tier"] = tier
            return record

    # Template fallback (or --no-llm mode)
    record["draft_letter"] = _template_letter(record)
    record["draft_tier"] = "template"
    return record


def _template_letter(record):
    """Fallback template letter when no LLM is available."""
    account_id = record.get("account_id", "UNKNOWN")
    dispute_type = record.get("classified_type", "general")
    balance = record.get("balance_current", "unknown")
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

    letter = textwrap.dedent(f"""\
    [DATE]

    [CONSUMER ADDRESS]

    RE: Account {account_id}

    Dear Consumer,

    Thank you for contacting us regarding your account. We have received and
    logged your dispute.

    {body}

    You have the right to dispute this debt again at any time. If you have
    questions about your rights under the Fair Debt Collection Practices Act,
    you may contact the Consumer Financial Protection Bureau at
    consumerfinance.gov or (855) 411-2372.

    Sincerely,

    [AGENCY NAME]
    Compliance Department
    """)

    return letter


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
