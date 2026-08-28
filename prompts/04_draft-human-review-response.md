# Prompt 4: Draft a Response for Human Review

For each document flagged as a factual mismatch in Prompt 3, draft a response
letter that:

1. States the factual correction, citing the specific reference data used
2. Uses plain, non-technical language appropriate for a consumer
3. Is explicitly labeled "DRAFT, PENDING HUMAN REVIEW" at the top
4. Includes an evidence summary block separate from the letter body, listing
   exactly what data supported the draft

Output: one draft file per document in outputs/example_response_drafts/,
plus a row in the review report (outputs/example_review_report.csv)
recording classification, evidence used, flag status, and
draft/human-review status.
