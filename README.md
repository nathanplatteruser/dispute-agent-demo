# Dispute Response Demo (Prototype)

A local, air-gapped-capable prototype that ingests fictional debt-collection dispute
documents, classifies them, checks factual claims against mock reference data, and
drafts a response for **mandatory human review**. Built for a live conference demo
session (~40-45 minutes) at Brainstorm 2026.

## What this is

- A hands-on prototype showing one narrow workflow: identify factually incorrect
  items in a dispute and draft a response for human sign-off.
- Runs entirely on synthetic, de-identified data (~20 documents for the live run,
  a larger pre-run batch for the "Return on Time" comparison).
- Designed to run air-gapped / fully local, with tiered failover (see
  `docs/facilitator-runbook.md`).

## What this is NOT

- **Not production-ready automation.** This is a training prototype.
- **Not legal advice.**
- **Not approved for real consumer data**, ever, under any circumstance.
- **Not a substitute** for compliance, security, privacy, data-storage, legal, or
  operational review before any real deployment.

See `docs/compliance-disclaimer.md` for the full statement, read it before you run
anything, and definitely before you share this repo further.

## Quick start

1. Read `docs/compliance-disclaimer.md`
2. Follow `setup/install.md` (or the OS-specific guide: `setup/windows.md` /
   `setup/mac.md`).
   **New to command lines / setting up a machine from scratch?**
   Use `setup/beginner-windows.md` instead, no experience assumed, every
   step spelled out. Assumes a standard Windows machine.
3. Run `scripts/preflight_check.py` to confirm your machine is ready
4. Follow `docs/participant-handout.md` to run the live demo

## Repo layout

```text
dispute-agent-demo/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── setup/
│   ├── install.md
│   ├── windows.md
│   ├── mac.md
│   └── troubleshooting.md
├── data/
│   ├── sample_disputes/
│   ├── mock_reference_data/
│   └── README.md
├── prompts/
│   ├── 01_define-workflow.md
│   ├── 02_classify-dispute.md
│   ├── 03_check-factual-claims.md
│   ├── 04_draft-human-review-response.md
│   └── 05_operationalize-and-risk-review.md
├── src/
│   └── (your application code goes here, see src/README.md)
├── outputs/
│   ├── example_response_drafts/
│   ├── example_review_report.csv
│   └── example_summary.pdf
├── docs/
│   ├── facilitator-runbook.md
│   ├── participant-handout.md
│   ├── compliance-disclaimer.md
│   └── demo-script.md
├── scripts/
│   └── preflight_check.py
└── assets/
    └── screenshots/
```

## Status

Prototype under active development. Last structured for Brainstorm 2026
(Sept 9-11, Denver). Maintained by Nathan Platter.
