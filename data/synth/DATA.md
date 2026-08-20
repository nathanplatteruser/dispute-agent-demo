# Synthetic Account Ledger

**This file contains entirely synthetic data. No real consumer information
is used anywhere in this dataset.**

## How it was generated

- **Generator:** `data/generate_synthetic.py`
- **Seed:** 42
- **Records:** 3,000
- **Dependencies:** Python 3 standard library only (csv, random, datetime, os)

To regenerate:

```bash
python3 data/generate_synthetic.py
```

The output is deterministic. Running the generator with the same seed
always produces the same file (verified by checksum).

## Schema

| Field                | Type              | Description                                       |
|----------------------|-------------------|---------------------------------------------------|
| account_id           | string            | Format `ACC-XXXXXX`                               |
| consumer_name        | string            | Synthetic name from a pool of ~100 first/last     |
| original_creditor    | string            | Generic bank, medical, telecom, or card company   |
| current_servicer     | string            | Generic collection agency name                    |
| balance_original     | float             | $200 -- $25,000                                   |
| balance_current      | float or string   | See "String balances" defect below                 |
| charge_off_date      | date string       | 2020--2024                                        |
| last_payment_date    | date string or "" | May be empty                                      |
| last_payment_amount  | float or ""       | May be empty                                      |
| state                | string            | Two-letter code (or full name -- see defects)      |
| dispute_type         | string            | One of 7 categories                               |
| validation_requested | boolean           | True/False                                        |
| prior_contacts       | integer           | 0--12                                             |
| contact_log          | string            | Semicolon-delimited dates, or empty               |
| has_contradiction    | boolean           | True if narrative contradicts ledger               |

## Intentional defects (~17.9% of records affected)

The data is deliberately messy. This is the point of the demo: showing
what happens when a pipeline encounters real-world data quality issues.

| Defect                    | Rate | Count | Description                                                                                             |
|---------------------------|------|-------|---------------------------------------------------------------------------------------------------------|
| String balances           | 8.0% |   240 | `balance_current` stored as `"$1,234.56"` or `"1234.56"` instead of a float. Summing concatenates.      |
| Date format inconsistency | 3.0% |    90 | Dates as `MM/DD/YYYY` instead of `YYYY-MM-DD`.                                                         |
| Full state names          | 2.0% |    60 | `"California"` instead of `"CA"`.                                                                       |
| Duplicate account IDs     | 1.0% |    30 | Exact duplicate `account_id` values.                                                                    |
| Null contact logs         | 3.0% |    90 | `contact_log` is empty despite `prior_contacts > 0`.                                                    |
| Narrative contradictions  | 2.0% |    60 | `dispute_type` is `"already_paid"` but `last_payment_date` and `last_payment_amount` are both empty.    |

**String balances are the critical demo moment.** When the pipeline tries
to sum `balance_current` without type-checking, it concatenates strings
instead of adding numbers (e.g., `"$500.00" + "$300.00"` becomes
`"$500.00$300.00"` instead of `800.00`). This is a scripted failure that
the audience will see and fix live.
