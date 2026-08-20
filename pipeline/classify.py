"""
Stage 3: Classify — route each dispute into a category.

Categories:
  identity_theft, not_mine, already_paid, wrong_amount,
  validation_request, statute_of_limitations, hardship

Uses keyword matching first, then LLM for ambiguous cases.
"""

import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline.llm import generate

CATEGORIES = [
    "identity_theft",
    "not_mine",
    "already_paid",
    "wrong_amount",
    "validation_request",
    "statute_of_limitations",
    "hardship",
]

# Keyword patterns for fast local classification (no LLM needed)
KEYWORD_RULES = {
    "identity_theft": [
        r"identity\s*theft", r"someone\s*(else\s*)?opened", r"not\s*my\s*account",
        r"stolen\s*identity", r"fraud(ulent)?", r"someone\s*used\s*my",
        r"police\s*report", r"ftc.*report", r"id\s*theft",
    ],
    "not_mine": [
        r"not\s*my\s*debt", r"don.t\s*owe", r"never\s*had.*account",
        r"do\s*not\s*recognize", r"not\s*mine", r"wrong\s*person",
        r"never\s*(opened|applied|signed)",
    ],
    "already_paid": [
        r"already\s*paid", r"paid\s*(this\s*)?(in\s*)?full", r"proof\s*of\s*payment",
        r"have\s*(the\s*)?receipt", r"payment\s*was\s*made", r"cleared\s*this",
        r"zero\s*balance",
    ],
    "wrong_amount": [
        r"wrong\s*amount", r"incorrect\s*balance", r"amount\s*is\s*(wrong|incorrect)",
        r"owe\s*less", r"more\s*than.*original", r"overcharg", r"fees.*incorrect",
        r"interest.*wrong",
    ],
    "validation_request": [
        r"validat(e|ion)", r"verify\s*(the\s*)?debt", r"provide\s*documentation",
        r"proof.*owe", r"original\s*contract", r"signed\s*agreement",
        r"fdcpa", r"30\s*day", r"written\s*(notice|request)",
    ],
    "statute_of_limitations": [
        r"statute\s*of\s*limitation", r"too\s*old", r"expired",
        r"years?\s*old", r"time.?barred", r"can.t\s*(legally\s*)?sue",
        r"past\s*the\s*(legal\s*)?deadline",
    ],
    "hardship": [
        r"hardship", r"can.?t\s*afford", r"financial\s*difficult",
        r"lost\s*(my\s*)?job", r"medical\s*(emergency|bills?)",
        r"disab(led|ility)", r"payment\s*plan", r"work\s*with\s*me",
        r"struggling", r"fixed\s*income",
    ],
}


def _classify_by_keywords(narrative):
    """
    Fast local classification by keyword matching.
    Returns (category, confidence) or (None, 0) if ambiguous.
    """
    narrative_lower = narrative.lower()
    scores = {}

    for category, patterns in KEYWORD_RULES.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, narrative_lower)
            score += len(matches)
        if score > 0:
            scores[category] = score

    if not scores:
        return None, 0.0

    best = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = scores[best] / total if total > 0 else 0

    # Only confident if clearly dominant
    if confidence >= 0.6 and scores[best] >= 2:
        return best, confidence

    return None, 0.0


def _classify_by_llm(narrative, account_id=""):
    """Use LLM for ambiguous cases."""
    system = (
        "You are a dispute classifier for a debt collection compliance system. "
        "Classify the consumer's dispute into exactly one category. "
        "Respond with ONLY the category name, nothing else."
    )
    prompt = (
        f"Classify this consumer dispute into one of these categories:\n"
        f"- identity_theft (someone else opened the account)\n"
        f"- not_mine (consumer says the debt is not theirs)\n"
        f"- already_paid (consumer says they already paid)\n"
        f"- wrong_amount (consumer disputes the balance)\n"
        f"- validation_request (consumer wants debt validation/proof)\n"
        f"- statute_of_limitations (debt is too old to collect)\n"
        f"- hardship (consumer can't pay, wants arrangement)\n\n"
        f"Consumer's dispute:\n{narrative[:500]}\n\n"
        f"Category:"
    )

    response, tier = generate(prompt, system)
    if response:
        response = response.strip().lower().replace(" ", "_")
        # Find best match
        for cat in CATEGORIES:
            if cat in response:
                return cat, tier
    return "validation_request", tier  # safe default


def classify_record(record, use_llm=True):
    """Classify a single record. Returns the record with classification added."""
    narrative = record.get("narrative", "")
    dispute_type_from_ledger = record.get("dispute_type", "")

    # First try keywords
    category, confidence = _classify_by_keywords(narrative)

    if category:
        record["classified_type"] = category
        record["classification_method"] = "keywords"
        record["classification_confidence"] = round(confidence, 2)
        return record

    # If ledger already has a dispute type, use it
    if dispute_type_from_ledger in CATEGORIES:
        record["classified_type"] = dispute_type_from_ledger
        record["classification_method"] = "ledger"
        record["classification_confidence"] = 0.5
        return record

    # Fall back to LLM
    if use_llm:
        category, tier = _classify_by_llm(narrative, record.get("account_id", ""))
        record["classified_type"] = category
        record["classification_method"] = f"llm_{tier}"
        record["classification_confidence"] = 0.7
    else:
        record["classified_type"] = dispute_type_from_ledger or "validation_request"
        record["classification_method"] = "default"
        record["classification_confidence"] = 0.3

    return record


def run(records, use_llm=True):
    """Execute the classification stage."""
    print("\n🏷️  STAGE 3: CLASSIFY")
    print("─" * 50)

    method_counts = {"keywords": 0, "ledger": 0, "llm": 0, "default": 0}
    category_counts = {cat: 0 for cat in CATEGORIES}

    for i, rec in enumerate(records):
        classify_record(rec, use_llm=use_llm)

        method = rec["classification_method"]
        if method.startswith("llm"):
            method_counts["llm"] += 1
        else:
            method_counts[method] = method_counts.get(method, 0) + 1

        cat = rec["classified_type"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        if (i + 1) % 100 == 0:
            print(f"  Classified {i + 1}/{len(records)}...")

    print(f"  Classification complete: {len(records)} records")
    print(f"  Methods: keywords={method_counts['keywords']}, "
          f"ledger={method_counts['ledger']}, "
          f"llm={method_counts['llm']}, "
          f"default={method_counts['default']}")
    print(f"  Categories:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"    {cat}: {count}")

    return records
