# Start Here

Dispute Response Pipeline — "Both Sides of the Letter"
brainstorm 2026, Denver

This folder contains the working code from the session. Everything runs
on your own machine. Nothing phones home, nothing tracks you, nothing
requires an account.

---

## What is in this folder

```
handout/
  START-HERE.md .............. You are here
  WHAT-TO-DO-MONDAY.md ...... Three things you can do this week
  prompts.txt ................ Every AI prompt used in the pipeline

  pipeline/ .................. The six-stage processing code
    intake.py ................ Stage 1: Load complaint narratives + account data
    validate.py .............. Stage 2: Fix data quality issues (dates, balances, dupes)
    classify.py .............. Stage 3: Categorize each dispute (identity theft, hardship, etc.)
    draft.py ................. Stage 4: Draft a compliant response letter
    review.py ................ Stage 5: Fact-check the letter against the source record
    consumer_view.py ......... Stage 6: Analyze the letter from the recipient's perspective

  data/
    generate_synthetic.py .... Generates the fake account ledger (3,000 records)
    sample_ledger.csv ........ A small sample so you can see the format

  sample-output/ ............. Pre-generated results you can look at right now
    summary.json ............. Pipeline run statistics
    records.json ............. Full processed records with letters and annotations
    fix_log.json ............. Every data fix the pipeline made, with before/after
```

---

## Five-minute path (no install needed)

If you only have five minutes, skip the code entirely and read these two
files. They are plain text and JSON — any text editor will open them.

1. Open **prompts.txt**. Read the letter-drafting system prompt (Prompt 1).
   This is the set of rules the AI follows when writing response letters.
   Notice rule #1: "Only state facts present in the provided record."
   That single constraint is what the review gate enforces.

2. Open **sample-output/records.json**. Search for "consumer_annotations"
   in any record. These are the places where the letter is technically
   compliant but likely to make the recipient stop reading, panic, or
   ignore the letter. Each annotation includes the actual CFPB complaint
   language it is grounded in.

3. In the same file, look at "agency_intent" vs "consumer_impact" for
   any record. That gap — between what the agency meant to say and what
   the consumer hears — is the core argument of the session.

That is the whole idea. Everything else is machinery.

---

## Thirty-minute path (run it yourself)

You will need Python installed. Nothing else.

### Step 1: Check if Python is already installed

**Mac:** Open Terminal (Applications > Utilities > Terminal) and type:

    python3 --version

If you see something like `Python 3.10.4`, you are good. Skip to Step 3.

**Windows:** Open Command Prompt (search "cmd" in Start) and type:

    python --version

If you see a version number (3.8 or higher), you are good. Skip to Step 3.

### Step 2: Install Python (if needed)

**Mac:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Open the downloaded file and follow the installer
4. When done, close and reopen Terminal, then try `python3 --version` again

**Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. **Important:** On the first installer screen, check the box that says
   "Add Python to PATH" before clicking Install
4. When done, close and reopen Command Prompt, then try `python --version`

### Step 3: Get the full project files

This handout folder is a reference copy. To run the pipeline, you need
the full project. If you received a USB drive at the session, the full
project is in the root folder of the drive. Copy the entire folder to
your computer.

### Step 4: Generate the synthetic data

Open a terminal, navigate to the project folder, and run:

**Mac:**

    cd /path/to/the/project
    python3 data/generate_synthetic.py

**Windows:**

    cd C:\path\to\the\project
    python data/generate_synthetic.py

This creates 3,000 synthetic account records. It takes about one second.
No internet needed. All data is fake.

### Step 5: Run the pipeline

**Mac:**

    python3 run.py --records 10 --no-llm

**Windows:**

    python run.py --records 10 --no-llm

The `--no-llm` flag skips AI calls and uses template letters instead.
This means you do not need an API key or a local AI model to see the
pipeline work. It will run in under a second.

The `--records 10` flag processes just 10 records so it finishes fast.

### Step 6: Look at the results

The pipeline creates files in the `output/` folder:

- **summary.json** — How many records processed, how many letters passed
  review, how many got flagged
- **records.json** — Every record with its draft letter, review findings,
  and consumer-view annotations
- **fix_log.json** — Every data quality fix, showing what was wrong and
  what it was changed to

Open these in any text editor or JSON viewer.

### Going further (optional)

If you want to see AI-generated letters instead of templates, you have
two options:

**Option A — Local AI model (free, no internet):**
1. Install Ollama from https://ollama.com
2. Run: `ollama pull llama3.1:8b` (downloads about 4.7 GB, one time)
3. Run: `python3 run.py --records 10` (without `--no-llm`)

**Option B — Cloud API (requires account):**
1. Get an API key from https://console.anthropic.com
2. Set it: `export ANTHROPIC_API_KEY=your-key-here` (Mac) or
   `set ANTHROPIC_API_KEY=your-key-here` (Windows)
3. Run: `python3 run.py --records 10`

---

## Where to find help

- **Python installation:** https://www.python.org/about/gettingstarted/
- **Ollama (local AI):** https://ollama.com
- **CFPB complaint database (the public data source):** https://www.consumerfinance.gov/data-research/consumer-complaints/
- **FDCPA text:** https://www.ftc.gov/legal-library/browse/statutes/fair-debt-collection-practices-act

---

## About the data

All account data in this project is synthetic — generated by a script
with a fixed random seed. No real consumer information is used anywhere.

The complaint narratives come from the CFPB Consumer Complaint Database,
a public dataset published by the US federal government. Before
publishing, the CFPB removes all personal information and only publishes
narratives that consumers have consented to share.

The synthetic data is deliberately messy (about 15% of records have
problems like string balances, inconsistent date formats, or missing
fields). That mess is intentional — it demonstrates what happens when
a pipeline encounters real-world data quality issues.
