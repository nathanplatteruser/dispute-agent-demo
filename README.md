# SettleUp Collections

**The Level-4 dispute-letter gate.** Draft. Check vs ledger. One Remediate. Loud **Refuse**. Human owns Send. We sit beside your recovery stack. We do not replace dialer, payments, or CMS.

Not legal advice. Not CFPB-approved. Synthetic demo only.

## Loud Refuse

Lead with the letter that almost left and did not. Default demo: claim asserted $1,000 × 3 vs ledger $20,370.53. Still wrong after one remediation. **REFUSED**, inspectable reason, operator escalation.

Verified fixture spine: 300 drafted · 20 blocked · 19 remediations · 1 refuse.

## Audience links (send these, not the GitHub profile)

- Public offering landing: https://nathanplatteruser.github.io/dispute-agent-demo/
- Live refused-letter demo, nothing to install: https://nathanplatteruser.github.io/dispute-agent-demo/DEMO-OUTPUT.html
- This repository (default branch `demo/both-sides`, also aliased as `master`): https://github.com/nathanplatteruser/dispute-agent-demo
- Setup guide: [00-START-HERE-Setup-Guide.docx](00-START-HERE-Setup-Guide.docx)
- Session run of show: [SESSION-RUN-OF-SHOW.md](SESSION-RUN-OF-SHOW.md)
- Attendee handout: [handout/START-HERE.md](handout/START-HERE.md)
- Booth flash page (optional aisle follow-up): https://nathanplatteruser.github.io/settleup-booth-kit/

**brAInstorm 2026 session:** Taming the Dispute Queue
Thursday, September 10, 8:30am · Ralph Hall, Ari Derman, Olga Mironova, Nathan Platter

Working title inside this repo: Both Sides of the Letter. A local, air-gapped-capable prototype that ingests fictional debt-collection dispute documents, classifies them, checks factual claims against a mock ledger, and drafts a response for **mandatory human review**.

## What you get

| Pillar | SettleUp promise |
|---|---|
| Controls in the workflow | Gate fires at draft time, not in annual theater |
| Fits your stack | Bolt onto CMS / agency desk; CSV / SFTP / assisted import path |
| Diligence-grade trust | Claim → ledger → attempts → refuse trail; Admin / Contributor / Compliance |
| Live in weeks | Start on fixtures, then your book; expand when earned |

## Capacity with a gate

Capacity means **more accurate dispute volume with a hard stop when the ledger disagrees**, not headcount cuts. Refuse protects the creditor brand and the agency relationship. Never pitch SettleUp as a layoff tool or an FTE-replace.

Olga Mironova minutes are cited on the demo page. Working range about 38 to 57 minutes per dispute. Do not cite a single 12-minute average.

## Beside your stack

Complementary to recovery platforms that own contact, placement, scoring, and digital engage. SettleUp owns **letter content risk** before Send. We are not a dialer, not a payments portal, not a CMS rip-replace.

## Book a walkthrough

https://calendly.com/nathanplatter

No public price sheet. No checkout. Calendly only.

## Out forever

Unsupervised auto-send · dialer / Reg F contact engine · payments portal · CMS rip-replace · claiming we are Equabli · SOC 2 badge without evidence.

## What this is

- A hands-on prototype showing one narrow workflow: find factually unsupported claims in a drafted dispute response, and stage the letter for human sign-off.
- Runs entirely on public CFPB narratives joined to a synthetic ledger. No PII, no client data.
- Runs fully offline on a local model, with tiered failover. No accounts, no API keys, nothing leaves your machine.

## What this is NOT

- **Not production-ready automation.** This is a training prototype.
- **Not legal advice.**
- **Not CFPB-approved.**
- **Not approved for real consumer data**, ever, under any circumstance.
- **Not a substitute** for compliance, security, privacy, data-storage, legal, or operational review before any real deployment.

Letters are drafted for review, never dispatched.

## Quick start

1. Install Ollama: https://ollama.com/download
2. Pull the model (4.9GB):
   `ollama pull llama3.1:8b`
3. Set up Python (3.10+):
   `python -m venv venv`
   `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Run it:
   `python run.py --records 10 --max-drafts 3`
5. Open `ui/index.html` in a browser. Self-contained, no server needed.

No requirements.txt: everything is Python standard library plus Ollama on localhost:11434.

Timing: about 15.6 seconds per letter on an M1 Mac. On Windows without Metal, expect 30 to 60 seconds per letter. That is normal.

## Flags

- `--records N` how many records to ingest
- `--max-drafts N` how many letters to actually draft
- `--no-llm` instant template letters, for smoke tests
- `--no-fix-balances` the string-concatenation break demo
- `--loose-review` the hallucination break demo
- `--remediate` re-draft flagged letters with their own findings attached as constraints, then re-check

## Repo layout

```text
dispute-agent-demo/
├── index.html                # public offering landing (GitHub Pages)
├── run.py                    # the pipeline, start here
├── CLAUDE.md
├── DECISIONS.md
├── SESSION-RUN-OF-SHOW.md    # full session breakdown
├── 00-START-HERE-Setup-Guide.docx
├── pipeline/                 # intake, validate, classify, draft, review, consumer
├── offline/                  # tiered LLM fallback and response cache
├── data/synth/               # synthetic ledger
├── break/                    # the three break demos
├── handout/                  # attendee takeaway package
└── ui/                       # index-100-DEMO.html is the pre-run 100-record output
```

## Status

Prototype under active development. Built for Brainstorm 2026 (Sept 9-11, Denver). Maintained by Nathan Platter.
