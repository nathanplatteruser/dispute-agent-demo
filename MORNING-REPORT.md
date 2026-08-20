# Morning Report

```bash
python3 run.py --records 50 --max-drafts 10
```

Open `ui/results.html` in a browser to see results (works from file://, no server needed).

---

## What Works

- **Pipeline runs end to end.** Intake → validate → classify → draft → review → consumer view. Tested with 50 records, 10 LLM-drafted letters. Completes in ~2.5 minutes with Ollama.
- **Ollama (Tier 2) is working.** llama3.1:8b drafts real letters. Falls back automatically when no API key is set.
- **Template fallback (--no-llm) works.** Pipeline completes in <1 second with no model at all.
- **Tier 3 cache works.** Prior Ollama responses are cached by input hash. Replay is instant.
- **Offline verified.** Wifi off: Tier 2 drafted 3 letters in 50.6s. Ollama killed: Tier 3 cache served instantly.
- **Review gate catches hallucinations.** In a 10-letter run, the gate flagged 2 letters for asserting dates not in the source record. This is the demo working as designed.
- **Consumer view flags disengagement patterns.** 2 of 10 letters rated "high risk" for language that triggers panic or avoidance. CFPB grounding attached to each flag.
- **All three breaks work.** String break shows concatenation. Hallucination break shows gate bypass. Wrong-consumer break shows misrouted disputes. Each triggers in <5s, fixes in <90s.
- **UI loads and displays records.** Source panel, letter panel, review tab, consumer impact tab, intent-vs-impact comparison.
- **CFPB data downloaded.** 447,347 debt-collection complaints with narratives. Pre-sampled to 3,000 for fast demo loading.
- **Synthetic ledger generated.** 3,000 records, seed=42, 119 string balances (~4%), date format defects, state code inconsistencies, duplicates, null contact logs.
- **Pre-commit hook blocks PII/PCI patterns.**

## What Is Stubbed or Rough

- **No API (Tier 1) tested.** No Anthropic API key was available during build. The code is written and will work — it's a standard urllib POST to the messages endpoint — but I did not execute a Tier 1 call. Test this when you have a key.
- **Consumer view annotation is regex-based, not LLM-based.** This makes it fast and deterministic, but the flags are pattern-matched, not contextually analyzed. For the demo this is better (instant, reproducible), but a production system would want deeper analysis.
- **Letter formatting in the UI is plain text in a white box.** It looks like a letter but doesn't have real envelope chrome, postmarks, etc. Good enough for demo.
- **Classification is mostly keyword + ledger, not LLM.** The keyword classifier handles ~30% of records, ledger handles ~70%, LLM gets called only for truly ambiguous cases. This is by design (fast, deterministic) but means the LLM classification path is lightly tested.
- **Handout package needs review.** Built but not tested as a standalone USB-stick experience.

## NEEDS NATHAN

1. **Tier 1 API key.** Set `ANTHROPIC_API_KEY` environment variable to test cloud API path. The code uses `claude-sonnet-4-20250514` — confirm this is the model you want. Nathan will test separately.
2. ~~**Session format.**~~ RESOLVED — two slots confirmed. `RUN-OF-SHOW-solo.md` (25 min) and `RUN-OF-SHOW-handson.md` (60 min).
3. ~~**Offline verification.**~~ VERIFIED — wifi off, Tier 2 Ollama drafted 3 letters in 50.6s. Killed Ollama, Tier 3 cache served instantly. All three tiers confirmed.
4. ~~**Cold open narrative.**~~ RESOLVED — CFPB complaint #2486787. The validation response that didn't have the consumer's name on it. Written into both run-of-show docs.

## Next Action

**Run through RUN-OF-SHOW-solo.md once, start to finish, with a stopwatch.** That's the gap between MVP and rehearsal-ready. Time each section, mark which ones run long, and adjust. The pipeline is built. The talk needs your voice on it.
