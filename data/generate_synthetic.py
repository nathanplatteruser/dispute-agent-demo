#!/usr/bin/env python3
"""
Synthetic Account Ledger Generator
===================================
Generates a reproducible, deliberately messy synthetic ledger for the
brainstorm 2026 collections demo.

Seed: 42
Records: 3000
Defect rate: ~15%

ALL DATA IS SYNTHETIC. No real consumer information is used anywhere.

Defect types injected:
  1. String balances (~8%) — balance_current stored as "$1,234.56" or
     "1234.56" instead of a float. This is the scripted demo moment:
     summing these concatenates strings instead of adding numbers.
  2. Date format inconsistency (~3%) — "MM/DD/YYYY" instead of
     "YYYY-MM-DD".
  3. State code inconsistency (~2%) — full state name instead of
     two-letter code.
  4. Duplicate account IDs (~1%) — exact duplicate rows.
  5. Null contact history (~3%) — contact_log is null despite
     prior_contacts > 0.
  6. Narrative contradiction (~2%) — has_contradiction flag set true;
     dispute_type is "already_paid" but ledger shows no payment.

Usage:
    python data/generate_synthetic.py
"""

import csv
import random
import os
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SEED = 42
NUM_RECORDS = 3000
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synth")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "synthetic_ledger.csv")

# ---------------------------------------------------------------------------
# Name pools (synthetic — no real people)
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Aiden", "Amara", "Blake", "Brianna", "Caleb", "Carmen", "Daniel",
    "Destiny", "Elijah", "Elena", "Finn", "Gabriella", "Hassan", "Harper",
    "Isaac", "Ivy", "Jalen", "Jasmine", "Kai", "Kayla", "Leo", "Lucia",
    "Marcus", "Maya", "Nolan", "Nina", "Omar", "Olivia", "Patrick", "Priya",
    "Quinn", "Rosa", "Samuel", "Sofia", "Terrence", "Tanya", "Ulises",
    "Uma", "Victor", "Valerie", "Wesley", "Wendy", "Xavier", "Yara",
    "Zachary", "Zoe", "Andre", "Bianca", "Carlos", "Dana", "Emilio",
    "Fiona", "Grant", "Holly", "Ivan", "Julia", "Kendall", "Lena",
    "Miles", "Natasha", "Oscar", "Paige", "Rafael", "Selena", "Travis",
    "Ursula", "Vince", "Willa", "Xander", "Yolanda", "Abel", "Brenda",
    "Clay", "Dina", "Evan", "Felicia", "Garrett", "Heidi", "Irene",
    "Jerome", "Kendra", "Lance", "Marta", "Neil", "Opal", "Preston",
    "Rhonda", "Shane", "Tina", "Vernon", "Wallace", "Ximena", "Yvonne",
    "Zane", "Alicia", "Byron", "Celeste", "Darren", "Estelle",
]

LAST_NAMES = [
    "Adams", "Banks", "Chen", "Davis", "Edwards", "Foster", "Garcia",
    "Harris", "Ibrahim", "Jackson", "Kim", "Lopez", "Mitchell", "Nguyen",
    "O'Brien", "Patel", "Quinn", "Ramirez", "Smith", "Torres", "Underwood",
    "Vasquez", "Williams", "Xu", "Young", "Zhang", "Alvarez", "Brown",
    "Clark", "Diaz", "Evans", "Franklin", "Gonzalez", "Henderson", "Ingram",
    "Johnson", "King", "Lee", "Moore", "Nelson", "Ortiz", "Phillips",
    "Reed", "Sanchez", "Thomas", "Upton", "Valdez", "Walker", "Yang",
    "Zimmerman", "Abbott", "Bell", "Carter", "Daniels", "Ellis", "Ford",
    "Graham", "Hall", "Irving", "Jensen", "Knox", "Lambert", "Marshall",
    "Nash", "Owen", "Price", "Reeves", "Shaw", "Tucker", "Uribe",
    "Vega", "Ward", "Yates", "Zavala", "Arnold", "Burke", "Cole",
    "Duncan", "Fitzgerald", "Grant", "Hayes", "Jacobs", "Klein",
    "Lawrence", "Mendoza", "Norris", "Pace", "Reese", "Stone", "Tran",
    "Voss", "Webb", "York", "Zeller", "Barker", "Chambers", "Drake",
    "Farrell", "Gibson", "Hunt", "James", "Keller",
]

# ---------------------------------------------------------------------------
# Generic creditor / servicer names (no real company names)
# ---------------------------------------------------------------------------

ORIGINAL_CREDITORS = [
    # Banks (generic)
    "First National Bank", "Pacific Coast Bank", "Heartland Savings Bank",
    "Meridian Federal Credit Union", "Summit Trust Bank",
    "Cornerstone Community Bank", "Frontier State Bank",
    # Credit card issuers (generic)
    "Platinum Card Services", "Liberty Credit Corp", "Horizon Card Co",
    "Premier Financial Group",
    # Medical
    "Clearview Medical Center", "Sunrise Health Partners",
    "Valley Regional Hospital", "Metro Physicians Group",
    # Telecom
    "National Wireless Co", "Citylink Communications",
    "TruConnect Services",
    # Utilities / misc
    "Greenfield Energy", "Lakeshore Utilities", "Apex Auto Finance",
]

CURRENT_SERVICERS = [
    "Allied Recovery Services", "National Credit Solutions",
    "Pinnacle Asset Management", "Redstone Collections Group",
    "Vanguard Debt Services", "Crestview Financial Recovery",
    "Keystone Account Solutions", "Bridgeport Recovery Inc",
    "Continental Receivables Corp", "Trident Portfolio Services",
]

# ---------------------------------------------------------------------------
# US states
# ---------------------------------------------------------------------------

STATE_CODES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

STATE_FULL_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

DISPUTE_TYPES = [
    "identity_theft", "not_mine", "already_paid", "wrong_amount",
    "validation_request", "statute_of_limitations", "hardship",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_date(rng, start_year, end_year):
    """Return a random date between Jan 1 of start_year and Dec 31 of end_year."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, delta))


def format_date_iso(d):
    """Standard ISO format."""
    return d.strftime("%Y-%m-%d")


def format_date_us(d):
    """US slash format — used as a defect."""
    return d.strftime("%m/%d/%Y")


def generate_contact_log(rng, charge_off, prior_contacts):
    """Generate a list of contact dates after charge-off."""
    if prior_contacts == 0:
        return []
    dates = []
    for _ in range(prior_contacts):
        offset = rng.randint(30, 800)
        contact_date = charge_off + timedelta(days=offset)
        # Cap at a reasonable date
        if contact_date > datetime(2025, 6, 30):
            contact_date = datetime(2025, 6, 30) - timedelta(days=rng.randint(1, 90))
        dates.append(contact_date)
    dates.sort()
    return dates


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_ledger():
    rng = random.Random(SEED)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = [
        "account_id", "consumer_name", "original_creditor",
        "current_servicer", "balance_original", "balance_current",
        "charge_off_date", "last_payment_date", "last_payment_amount",
        "state", "dispute_type", "validation_requested", "prior_contacts",
        "contact_log", "has_contradiction",
    ]

    records = []
    used_ids = set()

    # Counters for defect reporting
    defects = {
        "string_balance": 0,
        "date_format": 0,
        "state_full_name": 0,
        "duplicate_id": 0,
        "null_contact_log": 0,
        "narrative_contradiction": 0,
    }

    # Pre-select which record indices get which defect.
    # We assign defects by drawing from the full index range so they
    # can overlap (a record can have more than one defect).
    all_indices = list(range(NUM_RECORDS))

    defect_string_bal = set(rng.sample(all_indices, int(NUM_RECORDS * 0.08)))
    defect_date_fmt = set(rng.sample(all_indices, int(NUM_RECORDS * 0.03)))
    defect_state = set(rng.sample(all_indices, int(NUM_RECORDS * 0.02)))
    defect_null_log = set(rng.sample(all_indices, int(NUM_RECORDS * 0.03)))
    defect_contradiction = set(rng.sample(all_indices, int(NUM_RECORDS * 0.02)))

    # Duplicates: pick ~1% of indices; each will be duplicated once.
    defect_dup_indices = set(rng.sample(all_indices, int(NUM_RECORDS * 0.01)))

    for i in range(NUM_RECORDS):
        # --- Account ID ---
        acc_num = rng.randint(100000, 999999)
        account_id = f"ACC-{acc_num:06d}"
        # Allow duplicates only for the defect set; otherwise regenerate.
        if i not in defect_dup_indices:
            while account_id in used_ids:
                acc_num = rng.randint(100000, 999999)
                account_id = f"ACC-{acc_num:06d}"
        used_ids.add(account_id)

        # --- Consumer name ---
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        consumer_name = f"{first} {last}"

        # --- Creditor / servicer ---
        original_creditor = rng.choice(ORIGINAL_CREDITORS)
        current_servicer = rng.choice(CURRENT_SERVICERS)

        # --- Balances ---
        balance_original = round(rng.uniform(200.0, 25000.0), 2)
        # Current balance is between 0 and original (payments, fees, etc.)
        balance_current_float = round(rng.uniform(0.0, balance_original), 2)

        # --- Dates ---
        charge_off = random_date(rng, 2020, 2024)
        charge_off_str = format_date_iso(charge_off)

        # Last payment: 70% chance there was one
        if rng.random() < 0.70:
            lp_date = random_date(rng, charge_off.year, min(charge_off.year + 2, 2025))
            last_payment_date_str = format_date_iso(lp_date)
            last_payment_amount = round(rng.uniform(10.0, min(500.0, balance_original)), 2)
        else:
            last_payment_date_str = ""
            last_payment_amount = ""
            lp_date = None

        # --- State ---
        state = rng.choice(STATE_CODES)

        # --- Dispute ---
        dispute_type = rng.choice(DISPUTE_TYPES)
        validation_requested = rng.random() < 0.35

        # --- Contact history ---
        prior_contacts = rng.randint(0, 12)
        contact_dates = generate_contact_log(rng, charge_off, prior_contacts)
        contact_log_str = ";".join(format_date_iso(d) for d in contact_dates) if contact_dates else ""

        # --- Contradiction flag ---
        has_contradiction = False

        # ---------------------------------------------------------------
        # Defect injection
        # ---------------------------------------------------------------

        # 1. String balances (~8%)
        if i in defect_string_bal:
            if rng.random() < 0.5:
                balance_current_val = f"${balance_current_float:,.2f}"
            else:
                balance_current_val = f"{balance_current_float:.2f}"
            defects["string_balance"] += 1
        else:
            balance_current_val = balance_current_float

        # 2. Date format inconsistency (~3%)
        if i in defect_date_fmt:
            charge_off_str = format_date_us(charge_off)
            if lp_date:
                last_payment_date_str = format_date_us(lp_date)
            defects["date_format"] += 1

        # 3. State code inconsistency (~2%)
        if i in defect_state:
            state = STATE_FULL_NAMES[state]
            defects["state_full_name"] += 1

        # 4. Duplicate ID — already handled above in ID generation.
        if i in defect_dup_indices:
            defects["duplicate_id"] += 1

        # 5. Null contact log despite prior_contacts > 0 (~3%)
        if i in defect_null_log and prior_contacts > 0:
            contact_log_str = ""
            defects["null_contact_log"] += 1
        elif i in defect_null_log and prior_contacts == 0:
            # Force prior_contacts > 0 so the defect is meaningful
            prior_contacts = rng.randint(1, 5)
            contact_log_str = ""
            defects["null_contact_log"] += 1

        # 6. Narrative contradiction (~2%)
        if i in defect_contradiction:
            dispute_type = "already_paid"
            last_payment_date_str = ""
            last_payment_amount = ""
            has_contradiction = True
            defects["narrative_contradiction"] += 1

        # ---------------------------------------------------------------
        # Build row
        # ---------------------------------------------------------------
        row = {
            "account_id": account_id,
            "consumer_name": consumer_name,
            "original_creditor": original_creditor,
            "current_servicer": current_servicer,
            "balance_original": balance_original,
            "balance_current": balance_current_val,
            "charge_off_date": charge_off_str,
            "last_payment_date": last_payment_date_str,
            "last_payment_amount": last_payment_amount,
            "state": state,
            "dispute_type": dispute_type,
            "validation_requested": validation_requested,
            "prior_contacts": prior_contacts,
            "contact_log": contact_log_str,
            "has_contradiction": has_contradiction,
        }
        records.append(row)

    # Write CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Report
    total_defect_instances = sum(defects.values())
    records_with_any_defect = len(
        defect_string_bal | defect_date_fmt | defect_state
        | defect_dup_indices | defect_null_log | defect_contradiction
    )

    print(f"Generated {len(records)} records -> {OUTPUT_FILE}")
    print(f"\nDefect summary ({records_with_any_defect} records affected, "
          f"{records_with_any_defect / NUM_RECORDS * 100:.1f}% of total):")
    print(f"  String balances:         {defects['string_balance']:>4}  ({defects['string_balance']/NUM_RECORDS*100:.1f}%)")
    print(f"  Date format issues:      {defects['date_format']:>4}  ({defects['date_format']/NUM_RECORDS*100:.1f}%)")
    print(f"  Full state names:        {defects['state_full_name']:>4}  ({defects['state_full_name']/NUM_RECORDS*100:.1f}%)")
    print(f"  Duplicate IDs:           {defects['duplicate_id']:>4}  ({defects['duplicate_id']/NUM_RECORDS*100:.1f}%)")
    print(f"  Null contact logs:       {defects['null_contact_log']:>4}  ({defects['null_contact_log']/NUM_RECORDS*100:.1f}%)")
    print(f"  Narrative contradictions:{defects['narrative_contradiction']:>4}  ({defects['narrative_contradiction']/NUM_RECORDS*100:.1f}%)")
    print(f"  Total defect instances:  {total_defect_instances:>4}")


if __name__ == "__main__":
    generate_ledger()
