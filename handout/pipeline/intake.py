"""
Stage 1: Intake — load CFPB narratives and synthetic ledger, join them.

HOW THIS WORKS (for non-developers):
-------------------------------------
This is the starting point of the pipeline. It does three things:

1. Loads real consumer complaint narratives from the CFPB public database.
   These are stories people submitted about their experiences with debt
   collectors. All personal information has already been removed by the CFPB.

2. Loads the synthetic account ledger — a spreadsheet of fake account data
   we generated for this demo (balances, dates, creditor names, etc.).
   None of this is real consumer data.

3. Joins them together: each synthetic account gets paired with a real
   complaint narrative, so the pipeline has both structured data (numbers,
   dates) and unstructured data (the consumer's own words) to work with.

If the CFPB data file isn't available (e.g., you're running this offline
from a USB stick), it falls back to built-in synthetic narratives so the
demo still works.
"""

import csv
import os
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
SYNTH_DIR = DATA_DIR / "synth"


def load_cfpb_narratives(max_records=3000):
    """Load filtered CFPB debt-collection complaints with narratives."""
    # Prefer the pre-sampled file (fast) over the full file (slow)
    sample_path = RAW_DIR / "cfpb_sample_3000.csv"
    path = sample_path if sample_path.exists() else RAW_DIR / "cfpb_debt_collection.csv"

    if not path.exists():
        print("  ⚠ CFPB data not found at data/raw/")
        print("  → Using synthetic narratives as fallback")
        return _generate_fallback_narratives(max_records)

    records = []
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            narrative = row.get("Consumer complaint narrative", "").strip()
            if narrative and len(narrative) > 50:
                records.append({
                    "complaint_id": row.get("Complaint ID", ""),
                    "date_received": row.get("Date received", ""),
                    "product": row.get("Product", ""),
                    "sub_product": row.get("Sub-product", ""),
                    "issue": row.get("Issue", ""),
                    "sub_issue": row.get("Sub-issue", ""),
                    "narrative": narrative,
                    "company": row.get("Company", ""),
                    "state": row.get("State", ""),
                    "submitted_via": row.get("Submitted via", ""),
                    "company_response": row.get("Company response to consumer", ""),
                })
            if len(records) >= max_records:
                break

    print(f"  Loaded {len(records)} CFPB narratives with complaints")
    return records


def _generate_fallback_narratives(count):
    """Synthetic narratives for when CFPB data isn't available."""
    rng = random.Random(42)
    templates = [
        "I received a call from a collection agency about a debt of ${amount} that I do not recognize. "
        "I have never had an account with {creditor}. I asked for validation and they could not provide it. "
        "This is causing me significant stress and affecting my credit score.",

        "A debt collector contacted me about a medical bill from {creditor}. I already paid this bill in full "
        "on {date}. I have the receipt. They continue to call me multiple times a day and have threatened "
        "to report this to the credit bureaus even though I provided proof of payment.",

        "I am disputing a debt of ${amount} from {creditor}. The amount is wrong — my original balance was "
        "${orig_amount} and I made payments totaling ${paid}. The collector is claiming I owe more than "
        "the original debt, which does not seem right.",

        "I sent a written request for debt validation to the collection agency over 45 days ago. They have "
        "not responded with any documentation but continue to call me. Under the FDCPA they should have "
        "ceased collection activity until they validated the debt.",

        "The statute of limitations on this debt from {creditor} has expired. It is over {years} years old. "
        "The collector is threatening to sue me even though they cannot legally do so. I feel harassed "
        "and intimidated by their tactics.",

        "I am a victim of identity theft. Someone opened an account with {creditor} using my information. "
        "I have filed a police report and an FTC identity theft report. The collection agency refuses to "
        "remove this from my credit report despite the documentation I have provided.",

        "I am going through a financial hardship due to a medical emergency. I contacted {creditor} to "
        "discuss a payment plan but the collector was rude and refused to work with me. They said I had "
        "to pay the full ${amount} immediately or they would garnish my wages.",
    ]
    creditors = [
        "Westlake Medical Center", "Pacific Credit Union", "Metro Wireless",
        "Lakeside Hospital", "Sunrise Financial", "Valley Auto Lending",
        "Community Health Partners", "First National Lending", "Harbor Utilities"
    ]
    records = []
    for i in range(count):
        t = rng.choice(templates)
        narrative = t.format(
            amount=f"{rng.randint(200, 15000):,}",
            creditor=rng.choice(creditors),
            date=f"{rng.randint(1,12):02d}/{rng.randint(1,28):02d}/{rng.randint(2022,2025)}",
            orig_amount=f"{rng.randint(200, 10000):,}",
            paid=f"{rng.randint(100, 5000):,}",
            years=rng.randint(4, 12),
        )
        records.append({
            "complaint_id": f"SYNTH-{i+1:06d}",
            "date_received": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "product": "Debt collection",
            "sub_product": rng.choice(["Medical debt", "Credit card debt", "Auto debt", "Other debt"]),
            "issue": rng.choice(["Attempts to collect debt not owed", "Written notification about debt",
                                 "Took or threatened to take negative or legal action", "False statements or representation"]),
            "sub_issue": "",
            "narrative": narrative,
            "company": "Synthetic Agency",
            "state": rng.choice(["CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI"]),
            "submitted_via": "Web",
            "company_response": "Closed with explanation",
        })
    print(f"  Generated {len(records)} synthetic fallback narratives")
    return records


def load_synthetic_ledger():
    """Load the synthetic account ledger."""
    path = SYNTH_DIR / "synthetic_ledger.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Synthetic ledger not found at {path}. "
            f"Run: python3 data/generate_synthetic.py"
        )

    records = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))

    print(f"  Loaded {len(records)} synthetic ledger records")
    return records


def join_data(narratives, ledger, max_records=500):
    """
    Join CFPB narratives with synthetic ledger records.
    Assigns real narratives to synthetic accounts for the demo.
    """
    rng = random.Random(42)

    # Shuffle narratives so we get variety
    narr_pool = list(narratives)
    rng.shuffle(narr_pool)

    joined = []
    for i, ledger_rec in enumerate(ledger[:max_records]):
        narr = narr_pool[i % len(narr_pool)]
        combined = {**ledger_rec}
        combined["narrative"] = narr["narrative"]
        combined["complaint_id"] = narr["complaint_id"]
        combined["cfpb_product"] = narr.get("product", "")
        combined["cfpb_issue"] = narr.get("issue", "")
        combined["cfpb_sub_issue"] = narr.get("sub_issue", "")
        combined["cfpb_company_response"] = narr.get("company_response", "")
        joined.append(combined)

    print(f"  Joined {len(joined)} records (narratives + ledger)")
    return joined


def run(max_records=500):
    """Execute the intake stage."""
    print("\n📥 STAGE 1: INTAKE")
    print("─" * 50)

    narratives = load_cfpb_narratives(max_records=max_records * 2)
    ledger = load_synthetic_ledger()
    joined = join_data(narratives, ledger, max_records=max_records)

    return joined
