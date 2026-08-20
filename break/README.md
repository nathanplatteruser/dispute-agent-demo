# Break-and-Fix Kit

Three scripted failures for the live demo. Each breaks in under 10 seconds
and is fixable in under 90.

---

## Break 1: The String Break

**What it proves:** Your pipeline can produce mathematically wrong letters
if it doesn't enforce types at intake.

**Trigger:**
```bash
python3 break/break1_strings.py
```

**What appears on screen:** Balances load as strings. When "added," they
concatenate: `"$1,234.56" + "$2,345.67"` becomes `"$1,234.56$2,345.67"`.
A letter goes out quoting a nonsense balance.

**What Nathan says:** "This is the 'what is a string' test. If your AI
vendor can't tell you what this does to your portfolio math, they don't
understand their own pipeline. The model didn't fail here — the data
layer did."

**Fix:**
```bash
python3 break/break1_strings.py fix
```
Or just:
```bash
python3 run.py
```
(Balance coercion is on by default.)

**Recovery time:** ~5 seconds.

---

## Break 2: The Hallucination Break

**What it proves:** Without a review gate, the model will confidently
assert facts it invented — payment dates that don't exist, amounts
that don't match.

**Trigger:**
```bash
python3 break/break2_hallucination.py
```

**What appears on screen:** The review gate runs in loose mode, skipping
date and payment checks. Then it re-runs in strict mode and catches
what it missed.

**What Nathan says:** "The model just made up a payment date. It's not
lying — it's doing what language models do. It's completing the pattern.
The gate is what catches it. Without the gate, this letter goes out, a
consumer gets told they paid on a date they didn't, and that's a
compliance finding."

**Fix:**
```bash
python3 break/break2_hallucination.py fix
```
Or:
```bash
python3 run.py
```
(Strict review is on by default.)

**Recovery time:** ~45 seconds (includes Ollama inference).

---

## Break 3: The Wrong-Consumer Break

**What it proves:** When the dispute routing is wrong, a consumer who
reports identity theft gets a payment plan letter. Every practitioner
in the room has seen this in their own shop.

**Trigger:**
```bash
python3 break/break3_wrong_consumer.py
```

**What appears on screen:** Dispute types get scrambled. An identity
theft complaint gets routed as a wrong-amount dispute. The response
letter talks about verifying the balance when the consumer is saying
"this isn't me at all."

**What Nathan says:** "This is the complaint that fills the CFPB
database. 'I told them it wasn't my account and they sent me a payment
plan.' Your AI didn't fail the compliance check — it passed. It used
the right template, the right tone, the right disclosures. And it
completely ignored what the person said. That's not a model problem.
That's a routing problem."

**Fix:**
```bash
python3 break/break3_wrong_consumer.py fix
```
Or:
```bash
python3 run.py
```
(Correct routing is the default.)

**Recovery time:** ~5 seconds.
