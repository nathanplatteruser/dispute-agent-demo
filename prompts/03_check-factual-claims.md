# Prompt 3: Check Factual Accuracy

For each classified dispute (excluding anything already flagged for
escalation), compare the consumer's factual claims against the mock account
reference data provided in data/mock_reference_data/.

Flag only disputes where a claim is factually incorrect against the reference
data, for example, a disputed payment date, amount, or account status that
doesn't match the mock record.

Do not draft a response yet. Output: document ID, the specific claim checked,
the reference data used, and a match / mismatch result.
