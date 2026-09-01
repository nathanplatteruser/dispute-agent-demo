"""Stage 7: Remediate. Feed gate findings back as constraints, re-draft, re-check."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import draft as draft_stage
from pipeline import review as review_stage
from pipeline import consumer_view as consumer_stage

T = {
 "amount": "You wrote the amount {c}. That amount does not appear anywhere in the account record. Do not use it. State only amounts listed in the source record.",
 "date": "You wrote the date {c}. That date does not appear anywhere in the account record. Do not use it. State only dates listed in the source record.",
 "payment_assertion": "You wrote \"{c}\". The account record shows no payment history. Do not assert, imply, or reference any payment.",
 "outcome_promise": "You wrote \"{c}\". Do not promise any outcome. Describe what will be investigated, not what the result will be.",
 "citation": "You cited {c}. That is not a recognized FDCPA or FCRA section. Cite only sections you are certain of, or omit it.",
 "tone": "You wrote \"{c}\". Remove presumptive or aggressive language about what the consumer owes or intends.",
}

def build_constraint_block(record):
    f_list = record.get("review_findings") or []
    if not f_list:
        return ""
    lines, seen = [], set()
    for f in f_list:
        t = T.get(f.get("claim_type", ""))
        txt = t.format(c=f.get("claim_value", "")) if t else "A prior draft was rejected for this reason: %s. Do not repeat it." % f.get("reason", "")
        if txt in seen:
            continue
        seen.add(txt)
        lines.append("  - " + txt)
    if not lines:
        return ""
    return ("\n\nMANDATORY CORRECTIONS. A previous draft of this letter was rejected by compliance review. "
            "Each item below is a specific defect found in that draft. Your new draft must not repeat any of them:\n"
            + "\n".join(lines)
            + "\n\nWrite the corrected letter. State only what the account record supports. "
              "If you cannot make a claim the record supports, leave it out.")

def remediate_record(record, use_llm=True):
    if "original_draft_letter" not in record:
        record["original_draft_letter"] = record.get("draft_letter", "")
        record["original_review_findings"] = list(record.get("review_findings") or [])
        record["original_review_passed"] = record.get("review_passed", False)
    c = build_constraint_block(record)
    if not c:
        return record
    record["remediation_notes"] = c
    try:
        draft_stage.draft_letter(record, use_llm=use_llm)
    except Exception as e:
        record["remediation_error"] = str(e)
        record["remediation_notes"] = None
        return record
    record["remediation_notes"] = None
    review_stage.review_letter(record, strict=True)
    record["remediation_passes"] = record.get("remediation_passes", 0) + 1
    return record

def run(records, max_passes=2, use_llm=True, strict=True):
    print("\n\U0001F527 STAGE 7: REMEDIATION")
    print("-" * 50)
    drafted = [r for r in records if r.get("draft_letter")]
    flagged = [r for r in drafted if not r.get("review_passed", True)]
    before_f = len(flagged)
    before_n = sum(len(r.get("review_findings") or []) for r in drafted)
    if not flagged:
        print("  Nothing to remediate. Every drafted letter passed the gate.")
        return records, {"before_flagged": 0, "after_flagged": 0, "recovered": 0, "refused": 0}
    print("  Letters the gate refused to pass: %d" % before_f)
    print("  Total findings to correct:        %d" % before_n)
    print("  Max passes per letter:            %d\n" % max_passes)
    working = list(flagged)
    for attempt in range(1, max_passes + 1):
        if not working:
            break
        print("  Pass %d: re-drafting %d letters with their findings attached..." % (attempt, len(working)))
        for i, rec in enumerate(working):
            remediate_record(rec, use_llm=use_llm)
            if (i + 1) % 5 == 0 or (i + 1) == len(working):
                print("    %d/%d" % (i + 1, len(working)))
        still = [r for r in working if not r.get("review_passed", True)]
        print("  Pass %d result: %d recovered, %d still failing\n" % (attempt, len(working) - len(still), len(still)))
        working = still
    for rec in working:
        rec["remediation_refused"] = True
    for rec in flagged:
        if not rec.get("remediation_refused"):
            rec["remediation_recovered"] = True
    consumer_stage.run(records)
    after_f = len([r for r in drafted if not r.get("review_passed", True)])
    after_n = sum(len(r.get("review_findings") or []) for r in drafted)
    print("  " + "-" * 48)
    print("  BEFORE:    %d letters blocked, %d findings" % (before_f, before_n))
    print("  AFTER:     %d letters blocked, %d findings" % (after_f, after_n))
    print("  RECOVERED: %d letters now pass the gate" % (before_f - after_f))
    print("  REFUSED:   %d letters could not be fixed and will not be sent" % len(working))
    print("  " + "-" * 48)
    if working:
        print("\n  Refused accounts (partner review required):")
        for rec in working[:5]:
            print("    %s" % rec.get("account_id", "?"))
            for f in (rec.get("review_findings") or [])[:2]:
                print("      %s" % f.get("reason", ""))
    return records, {"before_flagged": before_f, "after_flagged": after_f,
                     "recovered": before_f - after_f, "refused": len(working),
                     "before_findings": before_n, "after_findings": after_n}
