# Prompt 2: Classify the Incoming Disputes

For each document in the mock dataset, assign one category:

- Debt-verification dispute
- Payment / balance dispute
- Liability dispute
- Fee-related dispute
- Escalation required (do not attempt to classify further, flag and stop)

Also flag any document that is incomplete or ambiguous, missing account
reference, unclear claim, or contradictory information, as
"needs clarification" rather than forcing it into one of the categories above.

Output: a table of document ID, category, and one-line justification.
