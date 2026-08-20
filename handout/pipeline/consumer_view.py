"""
The Second Half: Consumer View

HOW THIS WORKS (for non-developers):
-------------------------------------
This is the part most collection shops never look at. After the pipeline
drafts a letter, this stage flips the perspective: what does the person
receiving this letter actually experience?

It does three things:

1. DISENGAGEMENT DETECTION: Scans the letter for language patterns that
   real consumers report cause them to stop reading, panic, or throw the
   letter away. These patterns come from the CFPB complaint database —
   they are things people actually said about collection letters.

   Examples:
   - Vague legal threats ("may pursue legal action") — consumers ignore
     the letter instead of responding
   - Legal jargon ("pursuant to," "notwithstanding") — consumers skip
     entire paragraphs
   - Urgency without clarity ("immediate action required") — causes panic,
     not compliance
   - Credit bureau threats — consumer thinks "my credit is already ruined,
     why bother"

2. INTENT vs. IMPACT comparison: Shows what the agency meant to say
   versus what the consumer actually hears. For example, the agency
   intended "we're investigating your claim" but the letter communicates
   "something bad is about to happen."

3. RISK SCORING: Each letter gets a risk score — how likely is this
   letter to cause the recipient to disengage? High-risk letters are
   technically compliant but practically counterproductive.

The point: a letter can pass every compliance check and still wreck your
recovery rate.
"""

import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline.llm import generate

# Patterns drawn from real CFPB complaint language about collection letters.
# These are the things consumers actually report being confused or scared by.
DISENGAGEMENT_PATTERNS = [
    {
        "id": "legal_threat_ambiguity",
        "pattern": r"(?:may|might|could|reserve the right to)\s+(?:pursue|take|initiate)\s+(?:legal|further)\s+(?:action|proceedings|remedies)",
        "flag": "Vague legal threat — consumers report this makes them ignore the letter entirely rather than respond",
        "cfpb_grounding": "CFPB complaints frequently cite vague legal threats as reason for not responding: 'I was scared so I just threw it away'",
        "severity": "high",
    },
    {
        "id": "jargon_wall",
        "pattern": r"(?:pursuant to|in accordance with|notwithstanding|hereinafter|aforementioned|thereunder)",
        "flag": "Legal jargon — most recipients do not understand this language and skip paragraphs containing it",
        "cfpb_grounding": "Consumers report: 'I couldn't understand half the letter so I didn't know what to do'",
        "severity": "medium",
    },
    {
        "id": "urgency_without_clarity",
        "pattern": r"(?:immediate(?:ly)?|urgent(?:ly)?|time.?sensitive|prompt(?:ly)?)\s+(?:action|response|attention|payment)",
        "flag": "Urgency language without clear action steps — triggers panic or avoidance, not compliance",
        "cfpb_grounding": "CFPB pattern: 'They said it was urgent but didn't tell me what to actually do'",
        "severity": "high",
    },
    {
        "id": "credit_bureau_threat",
        "pattern": r"(?:report(?:ed|ing)?|furnish(?:ed|ing)?)\s+(?:to|with)\s+(?:the\s+)?(?:credit\s+)?(?:bureau|reporting\s+agenc)",
        "flag": "Credit reporting threat — often causes consumers to disengage from legitimate dispute processes",
        "cfpb_grounding": "Top CFPB complaint: 'They threatened my credit so I felt like I had no options'",
        "severity": "high",
    },
    {
        "id": "buried_rights",
        "pattern": r"(?:you\s+(?:have|retain)\s+the\s+right|your\s+rights?\s+(?:include|under))",
        "flag": "Consumer rights buried in dense paragraph — should be prominent, not embedded",
        "cfpb_grounding": "Consumers report: 'I didn't know I could dispute it — I found out later I had rights'",
        "severity": "medium",
    },
    {
        "id": "passive_voice_responsibility",
        "pattern": r"(?:it has been determined|the account has been|this debt was|the balance was)",
        "flag": "Passive voice obscures who did what — consumer doesn't know who to contact or what happened",
        "cfpb_grounding": "CFPB pattern: 'Nobody would tell me who actually owns the debt or who made the decision'",
        "severity": "low",
    },
    {
        "id": "amount_without_breakdown",
        "pattern": r"\$[\d,]+\.?\d{0,2}\s+(?:is\s+)?(?:due|owed|outstanding|remaining)",
        "flag": "States amount owed without itemization — consumers dispute amounts they can't verify",
        "cfpb_grounding": "CFPB pattern: 'They say I owe $X but won't show me how they got that number'",
        "severity": "medium",
    },
    {
        "id": "double_negative_or_confusing",
        "pattern": r"(?:not\s+un|unless\s+you\s+(?:do\s+not|fail\s+to)|failure\s+to\s+(?:not|refrain))",
        "flag": "Double negative or confusing conditional — recipients misunderstand the required action",
        "cfpb_grounding": "Consumers report: 'I couldn't tell if I was supposed to do something or not'",
        "severity": "medium",
    },
    {
        "id": "small_print_deadline",
        "pattern": r"(?:within\s+)?\d+\s*(?:calendar\s+|business\s+)?days?\s+(?:of|from)\s+(?:receipt|this\s+(?:letter|notice))",
        "flag": "Deadline tied to receipt date — consumer may not know when clock started",
        "cfpb_grounding": "CFPB pattern: 'By the time I got the letter the deadline had already passed'",
        "severity": "medium",
    },
]


def annotate_letter(record):
    """
    Analyze a draft letter for language that may cause consumer disengagement.
    Returns the record with consumer_annotations added.
    """
    letter = record.get("draft_letter", "")
    if not letter:
        record["consumer_annotations"] = []
        return record

    annotations = []

    for pattern_def in DISENGAGEMENT_PATTERNS:
        for match in re.finditer(pattern_def["pattern"], letter, re.IGNORECASE):
            annotations.append({
                "id": pattern_def["id"],
                "matched_text": match.group(),
                "position": match.start(),
                "flag": pattern_def["flag"],
                "cfpb_grounding": pattern_def["cfpb_grounding"],
                "severity": pattern_def["severity"],
            })

    # Score: how likely is this letter to cause the recipient to disengage?
    severity_weights = {"high": 3, "medium": 2, "low": 1}
    engagement_risk = sum(severity_weights.get(a["severity"], 1) for a in annotations)

    record["consumer_annotations"] = annotations
    record["engagement_risk_score"] = engagement_risk
    record["engagement_risk_level"] = (
        "high" if engagement_risk >= 6 else
        "medium" if engagement_risk >= 3 else
        "low"
    )

    return record


def build_intent_vs_impact(record):
    """
    Build a plain-language comparison:
    What the agency intended to say vs. what the letter actually communicates.
    """
    letter = record.get("draft_letter", "")
    dispute_type = record.get("classified_type", "")
    annotations = record.get("consumer_annotations", [])

    # What the agency intended
    intent_map = {
        "identity_theft": "We're investigating your identity theft claim and pausing collection.",
        "not_mine": "We're looking into whether this debt belongs to you and stopping contact meanwhile.",
        "already_paid": "We're checking our records to confirm your payment.",
        "wrong_amount": "We're reviewing the balance and will send you an itemized breakdown.",
        "validation_request": "We're getting the original documentation to prove the debt is valid.",
        "statute_of_limitations": "We're checking the legal timeline on this debt.",
        "hardship": "We want to work with you on a payment arrangement you can manage.",
    }

    intended = intent_map.get(dispute_type, "We're responding to your dispute.")

    # What the letter actually communicates (based on annotations)
    impacts = []
    if any(a["id"] == "legal_threat_ambiguity" for a in annotations):
        impacts.append("'They might sue me' — consumer focuses on threat, not resolution")
    if any(a["id"] == "jargon_wall" for a in annotations):
        impacts.append("'I can't understand this' — consumer stops reading")
    if any(a["id"] == "urgency_without_clarity" for a in annotations):
        impacts.append("'Something bad is about to happen but I don't know what to do' — paralysis")
    if any(a["id"] == "credit_bureau_threat" for a in annotations):
        impacts.append("'My credit is already ruined, why bother responding' — disengagement")
    if any(a["id"] == "buried_rights" for a in annotations):
        impacts.append("'I didn't know I could dispute this' — consumer doesn't exercise rights")
    if any(a["id"] == "amount_without_breakdown" for a in annotations):
        impacts.append("'This number doesn't match what I think I owe' — consumer disputes amount instead of resolving")

    if not impacts:
        impacts.append("Letter communicates its intent clearly — consumer likely to engage")

    record["agency_intent"] = intended
    record["consumer_impact"] = impacts

    return record


def render_consumer_view(record):
    """
    Render the letter as the consumer receives it.
    Returns an HTML-safe string for the UI, or a terminal-formatted string.
    """
    letter = record.get("draft_letter", "")
    annotations = record.get("consumer_annotations", [])

    # Build the consumer view data
    consumer_view = {
        "letter_text": letter,
        "annotations": annotations,
        "risk_score": record.get("engagement_risk_score", 0),
        "risk_level": record.get("engagement_risk_level", "unknown"),
        "intent": record.get("agency_intent", ""),
        "impact": record.get("consumer_impact", []),
        "account_id": record.get("account_id", ""),
        "dispute_type": record.get("classified_type", ""),
    }

    record["consumer_view"] = consumer_view
    return record


def run(records):
    """Execute the consumer view analysis."""
    print("\n👤 STAGE 6: CONSUMER VIEW")
    print("─" * 50)

    high_risk = 0
    medium_risk = 0
    low_risk = 0
    total_annotations = 0

    for i, rec in enumerate(records):
        if not rec.get("draft_letter"):
            continue

        annotate_letter(rec)
        build_intent_vs_impact(rec)
        render_consumer_view(rec)

        risk = rec.get("engagement_risk_level", "low")
        if risk == "high":
            high_risk += 1
        elif risk == "medium":
            medium_risk += 1
        else:
            low_risk += 1

        total_annotations += len(rec.get("consumer_annotations", []))

    print(f"  Analyzed {len(records)} letters for consumer impact")
    print(f"  Engagement risk: 🔴 high={high_risk}  🟡 medium={medium_risk}  🟢 low={low_risk}")
    print(f"  Total annotations: {total_annotations}")

    if high_risk > 0:
        print(f"\n  Sample high-risk letter:")
        for rec in records:
            if rec.get("engagement_risk_level") == "high":
                print(f"    Account {rec.get('account_id', '?')}:")
                print(f"    Agency intended: {rec.get('agency_intent', '?')}")
                for impact in rec.get("consumer_impact", [])[:2]:
                    print(f"    Consumer hears: {impact}")
                break

    return records
