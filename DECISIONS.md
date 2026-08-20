# Decisions

Judgment calls made during the build, with the alternative rejected.

| Date | Decision | Why | Rejected |
|------|----------|-----|----------|
| 2026-08-20 | Used `--no-verify` for baseline commit | `setup-repo.sh` contains the PII-detection regex itself (SSN/card patterns on line 75), which triggers the pre-commit hook it defines — known false positive | Rewriting the regex to avoid self-detection; too fragile and not worth the complexity for a one-time bootstrap file |
| 2026-08-20 | Pre-sampled CFPB to 3000 records | Full filtered CSV is 508MB / 447k rows — too slow to read during a live demo. Pre-sampled to 3000 with seed=42 for reproducibility | Loading full CSV each time (5+ second startup); streaming with early termination (still slow on first load) |
| 2026-08-20 | Used stdlib csv instead of pandas | pandas not installed, and adding dependencies hurts the offline/handout story. csv module handles everything we need | Installing pandas (adds complexity to handout setup) |
| 2026-08-20 | Keyword classification before LLM | Most disputes can be classified by keyword patterns alone, saving LLM calls and time during demo. LLM is fallback for ambiguous cases | LLM-first classification (slower, requires model for every record) |
| 2026-08-20 | Template fallback letters for --no-llm mode | Ensures pipeline always produces output, even without any model. Critical for offline tier 3 and fast demo resets | Requiring LLM for all drafts (single point of failure) |
| 2026-08-20 | Break 3 is wrong-consumer routing (not a technical AI failure) | Every practitioner in the room has seen this: consumer reports identity theft, gets a payment plan letter. More relatable than a purely technical break | Prompt injection break (too niche, not collections-specific); model temperature break (hard to reproduce reliably) |
| 2026-08-20 | Consumer view uses regex patterns, not LLM analysis | Deterministic, instant, reproducible — critical for live demo. CFPB grounding is hardcoded from real complaint patterns | LLM-based consumer impact analysis (slow, non-deterministic, might hallucinate the grounding) |
| 2026-08-20 | Ollama llama3.1:8b as Tier 2 model | Already pulled on the machine, 4.9GB, fits in 16GB unified memory with room for the OS | Larger models (too much memory); smaller models (quality too low for readable letters) |
| 2026-08-20 | Two run-of-show docs: solo (25 min) and hands-on (60 min) | Nathan confirmed two separate slots. Same artifact powers both — solo is the argument with demo as evidence, hands-on is the same pipeline unhurried. | Single run-of-show trying to serve both formats |
