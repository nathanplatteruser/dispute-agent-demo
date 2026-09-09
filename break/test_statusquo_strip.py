#!/usr/bin/env python3
"""Check the live refuse page still has the locked facts and a labeled status-quo / ROI strip."""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "DEMO-OUTPUT.html")


def fail(msg):
    print(f"  FAIL  {msg}")
    return False


def ok(msg):
    print(f"  ok    {msg}")
    return True


def load():
    with open(LIVE, encoding="utf-8") as f:
        return f.read()


def summary(html):
    m = re.search(r"window\.__PIPELINE_SUMMARY\s*=\s*(\{.*?\});", html)
    if not m:
        return None
    return json.loads(m.group(1))


def const_int(html, key):
    m = re.search(rf"{key}:(\d+(?:\.\d+)?)", html)
    return float(m.group(1)) if m else None


def test_locked_facts(html, s):
    passed = True
    if "ACC-600149" not in html:
        passed = fail("ACC-600149 missing")
    else:
        ok("ACC-600149 still in the file")
    if "20370.53" not in html and "20,370.53" not in html:
        passed = fail("ledger $20,370.53 missing")
    else:
        ok("ledger $20,370.53 still present")
    if "$1,000" not in html and "1000" not in html:
        passed = fail("hero $1,000 missing")
    else:
        ok("hero $1,000 still present")
    if s.get("total_records") != 1500:
        passed = fail(f"total_records is {s.get('total_records')}, expected 1500")
    else:
        ok("total_records 1500")
    if s.get("drafted") != 300:
        passed = fail(f"drafted is {s.get('drafted')}, expected 300")
    else:
        ok("drafted 300")
    elapsed = s.get("elapsed_seconds")
    if elapsed is None:
        passed = fail("elapsed_seconds missing")
    elif not (4600 <= float(elapsed) <= 4700):
        passed = fail(f"elapsed_seconds {elapsed} is not the locked ~4660 run")
    else:
        ok(f"elapsed_seconds {elapsed} from SUMMARY")
    return passed


def test_strip(html, s):
    passed = True
    for needle, label in [
        ('id="statusquo"', "statusquo mount"),
        ("STATUS_QUO", "STATUS_QUO const"),
        ("rateHour:40", "$40 rate in one place"),
        ("pilotMonth:499", "Pilot $499"),
        ("jokeElectricity:0.25", "joke electricity"),
        ("Olga Mironova", "Olga cited by name"),
        ("not a wage study", "rate labeled illustrative"),
        ("not a kill claim", "soft filter, not a kill claim"),
        ("joke electricity", "electricity called a joke"),
        ("Firm $1,299 is not on this strip", "Firm kept off the strip"),
        ("never dispatched", "letters never dispatched"),
        ("Not legal advice", "not legal advice"),
        ("Adjusted ROI", "adjusted ROI leads"),
        ("Hours a gate can actually take", "gate hours chip"),
        ("If the gate replaced every minute", "unadjusted ceiling labeled"),
        ("Unadjusted ceiling", "ceiling chip"),
        ("one third of her 30", "research one-third credit"),
        ("Half of her 7", "draft half credit"),
        ("Intake, review, and close stay human", "still-human line"),
        ("We do not haircut again", "no lunch double-discount"),
        ("researchCredit:1/3", "research share in one place"),
        ("draftCredit:1/2", "draft share in one place"),
        ("complianceCleanMin:2", "compliance first-pass minutes"),
    ]:
        if needle not in html:
            passed = fail(f"missing {label}")
        else:
            ok(label)

    if "1,499" in html or "$1499" in html:
        passed = fail("found $1,499")
    else:
        ok("no $1,499")
    if re.search(r"\bDell\b", html):
        passed = fail("Dell appears in the live file")
    else:
        ok("no Dell")

    # New user-facing block should not use em dashes.
    block = html[html.find("const STATUS_QUO"): html.find("const FILTERS")]
    if "—" in block:
        passed = fail("em dash in new status-quo copy")
    else:
        ok("no em dash in new copy")

    n = s["drafted"]
    read = (n * (3 + 20), n * (5 + 30))
    draft = (n * 5, n * 7)
    review = (n * 4, n * 4)
    counsel = (n * 3, n * 6)
    close = (n * 3, n * 5)
    total = (n * 38, n * 57)
    if total != (read[0] + draft[0] + review[0] + counsel[0] + close[0],
                 read[1] + draft[1] + review[1] + counsel[1] + close[1]):
        passed = fail("Olga stage minutes do not sum to 38-57")
    else:
        ok("Olga stages sum to 38-57 min / dispute")

    labor = (total[1] / 60) * 40
    cost = 499 + 0.25
    roi = labor / cost
    if labor != 11400:
        passed = fail(f"unadjusted labor {labor}, expected 11400")
    else:
        ok("unadjusted labor $11,400")
    if round(roi, 1) != 22.8:
        passed = fail(f"unadjusted ROI {roi:.3f}, expected ~22.8")
    else:
        ok(f"unadjusted ceiling {roi:.2f} -> 22.8x")

    high_risk = s.get("high_risk_letters") or 0
    flagged = s.get("review_flagged") or 0
    refused = 1  # locked refuse on this run; review_flagged is that letter
    refuse_like = max(refused, flagged)
    clean = n - high_risk - refuse_like
    if clean != 251:
        passed = fail(f"clean compliance subset {clean}, expected 251")
    else:
        ok("clean subset 251 (300 minus 48 high-risk minus 1 refused)")

    research_credit = n * 30 * (1 / 3)
    draft_credit = n * 7 * 0.5
    compliance_credit = clean * 2
    gate_min = research_credit + draft_credit + compliance_credit
    adj_labor = (gate_min / 60) * 40
    adj_roi = adj_labor / cost
    if research_credit != 3000 or draft_credit != 1050:
        passed = fail(f"credits research {research_credit} draft {draft_credit}")
    else:
        ok("research 50 hr (10 of 30) and draft 17 hr 30 min (3.5 of 7)")
    if gate_min != 4552:
        passed = fail(f"gate minutes {gate_min}, expected 4552")
    else:
        ok("gate can take 75 hr 52 min")
    if round(adj_roi, 1) != 6.1:
        passed = fail(f"adjusted ROI {adj_roi:.3f}, expected ~6.1")
    else:
        ok(f"adjusted lead ROI {adj_roi:.2f} -> 6.1x")
    if not (4 <= adj_roi <= 8):
        passed = fail(f"adjusted ROI {adj_roi:.2f} outside 4x-8x")
    else:
        ok("adjusted ROI inside 4x-8x; shares not tightened")

    adj_pos = html.find("Adjusted ROI")
    ceil_pos = html.find("Unadjusted ceiling")
    if adj_pos < 0 or ceil_pos < 0 or adj_pos > ceil_pos:
        passed = fail("adjusted ROI does not appear before the unadjusted ceiling")
    else:
        ok("adjusted ROI is the lead figure")

    elapsed_min = round(s["elapsed_seconds"] / 60)
    if elapsed_min != 78:
        passed = fail(f"elapsed rounds to {elapsed_min} min, expected 78")
    else:
        ok("SUMMARY elapsed formats as 1 hr 18 min")

    if const_int(html, "rateHour") != 40:
        passed = fail("rateHour is not 40")
    return passed


def main():
    print("status-quo / ROI strip")
    if not os.path.exists(LIVE):
        print("  FAIL  DEMO-OUTPUT.html missing")
        return 1
    html = load()
    s = summary(html)
    if not s:
        print("  FAIL  SUMMARY missing")
        return 1
    results = [test_locked_facts(html, s), test_strip(html, s)]
    print("PASS" if all(results) else "FAIL")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
