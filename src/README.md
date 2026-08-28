# src/: Application Code

Your existing application code (the air-gapped ingestion, classification,
factual-check, and drafting pipeline currently in `~/git repos/brainstorm-demo`)
goes here.

## Migration checklist

1. Copy your working code from the local repo into this folder, preserving
   its internal structure where reasonable.
2. Confirm the Tier 1 (cloud) / Tier 2 (Ollama llama3.1:8b) / Tier 3 (cached)
   failover logic still points to the right config after the move.
3. Update any hardcoded local file paths to relative paths within this repo.
4. Confirm your existing regression tests still pass from the new location.
5. Add a one-line run command here (e.g. `python src/main.py`) so
   `docs/participant-handout.md` and `setup/install.md` can reference it
   exactly.
