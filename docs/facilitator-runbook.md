# Facilitator Runbook: 40-45 Minute Session

## Roles

- **Nathan**, drives the technical demo, explains architecture
- **Olga**, explains queue management, operational scaling, workflow decisions
- **Aryeh / Ralph**, ask audience-level governance and business questions,
  keep the session on track, translate technical concepts for nontechnical
  attendees

## Timing

| Time | Segment |
|---|---|
| 0-5 min | Set expectations, show the workflow end to end at a glance |
| 5-10 min | Explain the fictional dataset and the human-review boundary |
| 10-25 min | Run the 20-document live demo |
| 25-35 min | Review outputs, flags, and drafted responses |
| 35-40 min | Show the pre-run 26,000-document result and "Return on Time" comparison |
| 40-45 min | Explain deployment risks, controls, and next steps |

## Failover plan

Run the tiered failover check before going live:

1. **Tier 1, cloud model** (primary path)
2. **Tier 2, local model (Ollama, llama3.1:8b)**, fallback if venue Wi-Fi drops
3. **Tier 3, cached responses**, fallback if Tier 2 also fails, so the demo
   never dead-airs in front of a room

Test all three tiers before the session, not during it.

## Value story to show at the 35-40 min mark

One slide/page covering:

- Number of documents processed
- Time required for the workflow
- Estimated manual effort for the same batch
- Estimated manual error/rework cost
- Approximate cost to run the demo
- A visible statement that these figures are illustrative and will vary by
  organization

Format: "20 documents live, 26,000 documents pre-run", the cooking-show
comparison.

## Before the session

- Run the full demo from a fresh clone, on your own machine
- Have Ralph run it on his Windows / 16 GB RAM machine
- Have Aryeh run the instructions with no technical assistance
- Have Olga validate the mock workflow against realistic dispute-queue handling
- Record every point someone gets stuck, and fix the instructions before the
  live session
