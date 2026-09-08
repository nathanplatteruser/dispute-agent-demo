# CLAUDE.md — Collections Demo ("Both Sides of the Letter")

Read this before doing anything in this repo.

## What this is

A live conference demo for **brainstorm**, September 9-11, 2026, Denver.
An AI conference for the third-party collections and accounts-receivable
industry. About 290 attendees. Creditor-side names in the room include
Ally Bank, U.S. Bank, Arvest, Prosper. AI people from AWS, Equifax,
Resurgent, InDebted, TrueML.

Nathan has two slots:

1. **A lightning / solo presentation.** The argument: your AI can pass every
   compliance check and still wreck your recovery rate, because compliant
   and effective are different measurements. Title in the dark. Hold
   $1,000 vs $20,370.53. Two tests. Olga's 57 minutes. Monday checklist.
   "I implement this." No GitHub navigation. No pricing on stage.
2. **Thursday morning sandbox** with Ralph Hall, Olga Mironova, and Aryeh
   Derman. The room builds along on Ollama. Personal laptop. Synthetic
   data. Company security policy first.

**One artifact powers both.** Never build two things. The solo talk is the
argument with the demo as evidence. The hands-on is the same pipeline,
unhurried, with the audience following.

This is Mike Gibb's conference. Nathan is an honored guest. The sandbox
track is sponsored by Clark Hill. Thank them. Do not compete with Jurgen's
Doc or Rob Graf Rath's synthetic CRM. Help desk is a Genius bar
(Wednesday afternoon and Thursday all day). Help first. Calendly after
they ask. Do not pitch during someone else's session.

## HARD CONSTRAINTS — do not violate, ever

1. **No real consumer data.** No PII, no PCI, no account numbers, real
   names, addresses, phone numbers, SSNs, card numbers. Not in the repo,
   not in a fixture, not in a comment, not in a test, not in a commit
   message.
2. **Nothing employer-related.** No internal architectures, customer
   material, product names, internal tooling patterns, or proprietary
   approaches from Nathan's day job. Public sources and original work only.
   Unsure? Leave it out and log it in `DECISIONS.md`.
3. **No lead capture in the handout.** No email gate, no signup, no
   analytics, no tracking, nothing that phones home. Nathan promised the
   room this on the record.
4. **Everything runs offline.** Conference wifi will fail. This is a
   promise made to the organizer, not a nice-to-have.
5. **Original code only.** Do not copy code, prose, or letter templates
   verbatim from any source.
6. **Company security policy first.** Do not tell attendees to override
   IT. Personal laptop. If they cannot install, they watch.
7. **Ollama for this session.** Anything LLM, Tesseract, Python-under-the-hood,
   and WSL belong to Rob and Dan. Do not mix those install steps into
   START-HERE.
8. **No pricing on lightning, sandbox, or help-desk screens.** Pilot,
   Firm, and Letter Risk Audit live after they ask. Never say $1,499.
   Never quote fines or ROI. Never claim CFPB-approved.
9. **Cite Olga.** Minutes are hers. Do not invent a 12-minute average.
10. **No em dashes** in attendee-facing copy.

## Data

**Primary:** CFPB Consumer Complaint Database. Public domain, US federal
government work. Narratives published with consumer consent after CFPB
removes sensitive information. Filter to debt-collection products.

- Bulk: `https://files.consumerfinance.gov/ccdb/complaints.csv.zip`
- Codebook: `https://cfpb.github.io/api/ccdb/fields.html`

**Derived:** synthetic account ledger. Seeded, reproducible, and
deliberately messy — roughly 15% of records carry realistic defects
(dates as strings, currency with symbols, inconsistent state codes,
duplicate IDs, narratives that contradict the ledger). The mess is the
demo. Balances stored as strings in a portion of the data on purpose, so
the pipeline visibly concatenates instead of adding.

Raw downloads live in `data/raw/` and are **git-ignored**. Never commit
them.

## Architecture

```
pipeline/     intake -> validate -> classify -> draft -> review
ui/           local web view, no build step, opens from file
break/        three scripted failures, each with trigger + fix
offline/      tier 1 API, tier 2 local Ollama, tier 3 cached
handout/      self-contained attendee package
talk/         the 25-minute presentation
data/raw/     git-ignored
data/synth/   generated, committed, small
```

The **review gate** is the ethical center of the talk. It inspects each
draft and flags anything asserting a fact not present in the source
record. Make its work visible on screen.

The **consumer view** is the half most likely to be under-built. After the
pipeline drafts a letter, render it the way the recipient actually receives
it, and annotate language that is technically compliant but likely to make
someone disengage, panic, or ignore it. Ground those flags in patterns
visible in the CFPB narratives themselves.

## Working agreements

- Commit after every working phase, real messages, so any point is
  recoverable.
- Log judgment calls in `DECISIONS.md` with the alternative you rejected.
- Do not claim something works that you did not execute. If you didn't run
  it, say you didn't run it.
- Stuck more than 20 minutes? Ship a working stub, log it, move on.
- Offline tiers are verified by turning the network off and running it.
  Not by reading the code.
- Attendee-facing docs follow `CONFERENCE-COC.md`.

## Machine

MacBook M1, 16GB unified memory. Local model is `llama3.1:8b` via Ollama.
Build within that envelope.

## Timeline

- **Aug 24** — pipeline runs end to end, breaks trigger and recover,
  offline verified with the network actually off
- **Aug 31** — 25-minute talk written
- **Sept 1-7** — three timed rehearsals, one with wifi off
- **Sept 8** — Mike Gibb sandbox briefing locked the guest rules
- **Sept 9-11** — Denver
