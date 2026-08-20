# Run of Show — "Both Sides of the Letter"

60 minutes. Solo. Live build + live break + flip the chair.

---

## Pre-Show Checklist (15 minutes before)

- [ ] Ollama running: `ollama serve` (confirm with `ollama list`)
- [ ] Terminal open, font size 18+, dark background
- [ ] Browser open to `ui/index.html` (pre-loaded with a previous run)
- [ ] Wifi ON initially (for Tier 1 demo option), but pipeline will work without it
- [ ] `cd ~/dispute-demo` (or wherever the repo lives)
- [ ] Run `python3 run.py --records 5 --no-llm` once to warm up — confirm it prints clean output
- [ ] USB sticks with handout/ loaded and ready at the door

---

## 0:00–5:00 — Cold Open: One Dispute That Cost Somebody Real Money

**What's on screen:** Nothing. Black terminal.

**What Nathan says:**

> "Before I write a single line of code, I want to read you something."

Pull up a CFPB narrative — one that's vivid, specific, emotional. Read it aloud, slowly.

```bash
python3 -c "
import csv
with open('data/raw/cfpb_sample_3000.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        n = row.get('Consumer complaint narrative', '')
        if 'identity theft' in n.lower() and len(n) > 300:
            print(n[:800])
            break
"
```

> "That's a real person. That complaint is in a federal database because
> the letter they got back didn't address what they actually said. Today
> we're going to build the thing that catches that."

**Pre-built vs typed live:** The one-liner is typed live. The data file is pre-loaded.

**Recovery if it fails:** Have 3 compelling narratives saved in `break/cold_open_backup.txt` as backup.

---

## 5:00–15:00 — Build the Safe Sandbox

**What's on screen:** Terminal + file browser showing `data/` directory.

**What Nathan does:**

1. Show the CFPB data source (tab to consumerfinance.gov if wifi is on, or describe it)
2. Show the synthetic generator:
   ```bash
   head -5 data/synth/synthetic_ledger.csv
   ```
3. Point out the string balances:
   ```bash
   python3 -c "
   import csv
   with open('data/synth/synthetic_ledger.csv') as f:
       for row in csv.DictReader(f):
           if '$' in str(row.get('balance_current','')):
               print(f\"{row['account_id']}: {row['balance_current']}\")
               break
   "
   ```
4. Show the pre-commit hook:
   ```bash
   cat .git/hooks/pre-commit | head -20
   ```

> "Real narratives, synthetic everything-else. Nothing PII, nothing PCI.
> The mess is deliberate — because your real data is messy too."

**Pre-built vs typed live:** Data is pre-generated. Nathan types the exploration commands live.

---

## 15:00–40:00 — Build the Pipeline Live

**What's on screen:** Terminal. Nathan runs each stage, explains what it does.

### Stage 1: Intake (2 min)
```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from pipeline.intake import run
records = run(max_records=20)
print(f'First record keys: {list(records[0].keys())}')
"
```
> "Twenty records. Real narratives joined to synthetic accounts. This is
> what your intake looks like."

### Stage 2: Validate (3 min)
```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from pipeline.intake import run as intake
from pipeline.validate import run as validate
records = intake(max_records=20)
cleaned, fixes, stats = validate(records)
print(f'Fixes: {stats}')
"
```
> "The validator just coerced string balances to numbers, normalized dates,
> and removed duplicates. Every fix is logged. This is the part most demos
> skip."

### Stage 3: Classify (3 min)
```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from pipeline.intake import run as intake
from pipeline.validate import run as validate
from pipeline.classify import run as classify
records = intake(max_records=20)
cleaned, _, _ = validate(records)
classified = classify(cleaned, use_llm=False)
for r in classified[:5]:
    print(f\"{r['account_id']}: {r['classified_type']} ({r['classification_method']})\")
"
```
> "Keywords first, model second. The classifier isn't magic — it's rules
> where rules work and inference where they don't."

### Stage 4: Draft (5 min)
```bash
python3 run.py --records 10 --max-drafts 3
```
> "Now the model writes. Watch the tier indicator — that tells you whether
> it's using the cloud, the local model, or the cache."

Pause while Ollama generates. Use the ~20-second wait to talk about what's happening.

### Stage 5: Review Gate (5 min)
> "This is the part I care about most."

Open `output/records.json` or the UI to show review findings.

```bash
python3 -c "
import json
with open('output/records.json') as f:
    records = json.load(f)
for r in records:
    if r.get('review_findings'):
        print(f\"Account {r['account_id']}:\")
        for f in r['review_findings']:
            print(f\"  [{f['severity']}] {f['reason']}\")
"
```

> "The gate checks every claim in the letter against the source record.
> If the model says 'you paid on March 15th' and there's no payment on
> March 15th in the record, the gate catches it. This is the compliance
> layer."

### Stage 6: Consumer View (5 min)

Open `ui/index.html` in browser. Click through records.

> "Now I'm going to read this letter the way the person who gets it
> reads it."

Click to the Consumer Impact tab. Show the intent-vs-impact comparison.

> "The agency intended to say 'we're investigating.' The consumer heard
> 'they might sue me.' That's not a compliance failure. That letter
> probably passes every compliance check you have. But the consumer
> threw it away."

**Pre-built vs typed live:** Pipeline code is pre-written. Nathan runs it live. UI is pre-built.

**Recovery if a stage fails:** Run `python3 run.py --no-llm` for instant results with templates.

---

## 40:00–55:00 — Break It, Fix It, Flip the Chair

### Break 1: The String Break (4 min)

```bash
python3 break/break1_strings.py
```

> "See that? The balance is a string. When you add strings, you get
> concatenation. '$462' plus '$121' equals '$462$121'. That letter
> just went out quoting a number that doesn't exist."

```bash
python3 break/break1_strings.py fix
```

> "One line of type coercion at intake. That's it. The model didn't fail —
> the data layer did."

### Break 2: The Hallucination Break (4 min)

```bash
python3 break/break2_hallucination.py
```

> "I just turned off half the review gate. Watch what the model does."

Wait for output. Point to any hallucinated dates/payments.

```bash
python3 break/break2_hallucination.py fix
```

> "Same letter, same model. But now the gate catches it. The model
> isn't the compliance layer. The gate is."

### Break 3: The Wrong-Consumer Break (3 min)

```bash
python3 break/break3_wrong_consumer.py
```

> "Consumer says 'this isn't my account.' The letter responds with a
> payment plan. Raise your hand if you've seen this in your own shop."

(Pause for hands.)

```bash
python3 break/break3_wrong_consumer.py fix
```

> "Route the dispute, then respond to it. In that order."

### Flip the Chair: Read the Letter as the Consumer (4 min)

Open the UI. Select a high-risk letter. Read it aloud, slowly, as if Nathan received it in the mail.

> "I'm going to read this the way you'd read it if it showed up in your
> mailbox on a Tuesday."

Read the letter. Then read the consumer impact annotations.

> "Technically compliant. Probably passes your QA. And the person who
> got this threw it away, because the first paragraph scared them into
> thinking they had no options. Your recovery rate just went to zero on
> this account. Not because the AI failed. Because compliant and
> effective are different measurements."

---

## 55:00–60:00 — What They Run Monday

**What's on screen:** Slide or terminal showing three actions.

> "On the USB stick at the door, there's everything I just built. It runs
> on your laptop. No signup, no email, no tracking. It's yours."

The three Monday actions (from WHAT-TO-DO-MONDAY.md):

1. **Run one dispute through your current pipeline and read the output
   as the consumer.** Not as compliance. As the person who got the letter.
2. **Check whether your pipeline enforces types at intake.** If your
   balances can arrive as strings, your math is wrong and you don't know it.
3. **Ask your vendor what happens when the review gate is off.** If they
   don't have a review gate, ask what happens when the model invents a
   payment date.

> "Thank you. The handout is at the door. I'll be here if you want to
> talk."

---

## Contingency Plans

| Problem | Recovery |
|---------|----------|
| Ollama crashes | `python3 run.py --no-llm` (template mode, instant) |
| Wifi dies during API demo | "And that's exactly what happens at a conference." Show Tier 2 picking up. |
| Pipeline throws unexpected error | Show the error, diagnose it live. "This is real. Let me fix it." |
| Running long | Cut Break 3, go straight to flip-the-chair |
| Running short | Expand the consumer-view walkthrough, take questions during |
| Projector/display issues | Everything runs in terminal. Font size 18+. |
