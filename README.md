# Dispute Response Demo (Prototype)

A local, air-gapped-capable prototype that ingests fictional debt-collection dispute documents, classifies them, checks factual claims against a mock ledger, and drafts a response for **mandatory human review**. Built for a live session at Brainstorm 2026.

## What this is

- A hands-on prototype showing one narrow workflow: find factually unsupported claims in a drafted dispute response, and stage the letter for human sign-off.
- Runs entirely on public CFPB narratives joined to a synthetic ledger. No PII, no client data.
- Runs fully offline on a local model, with tiered failover (cloud API, then local Ollama, then a response cache).

## What this is NOT

- **Not production-ready automation.** This is a training prototype.
- **Not legal advice.**
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

Timing: about 18 seconds per letter on an M1 Mac. On Windows without Metal, expect 30 to 60 seconds per letter. That is normal.

## Flags

- `--records N` how many records to ingest
- `--max-drafts N` how many letters to actually draft
- `--no-llm` instant template letters, for smoke tests
- `--no-fix-balances` the string-concatenation break demo
- `--loose-review` the hallucination break demo

## Repo layout

```text
dispute-agent-demo/
├── run.py                    # the pipeline, start here
├── CLAUDE.md
├── DECISIONS.md
├── RUN-OF-SHOW-solo.md       # 25-min session
├── RUN-OF-SHOW-handson.md    # 60-min session
├── pipeline/                 # intake, validate, classify, draft, review, consumer
├── offline/                  # tiered LLM fallback and response cache
├── data/synth/               # synthetic ledger
├── break/                    # the three break demos
├── handout/                  # attendee takeaway package
└── ui/                       # index-100-DEMO.html is the pre-run 100-record output
```

## Status

Prototype under active development. Built for Brainstorm 2026 (Sept 9-11, Denver). Maintained by Nathan Platter.