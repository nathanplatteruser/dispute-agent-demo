# Run of Show — Solo Presentation (25 minutes)

**Argument:** Your AI can pass every compliance check and still wreck
your recovery rate, because compliant and effective are different
measurements.

**Structure:** 10 minutes of idea, 10 minutes of live proof, 5 minutes
of what the room does Monday.

---

## Pre-Show Checklist (15 minutes before)

- [ ] Ollama running: `ollama serve`
- [ ] Terminal open, font size 18+, dark background
- [ ] `cd` to the repo root
- [ ] Pre-run: `python3 run.py --records 50 --max-drafts 10` (output already saved)
- [ ] Browser open to `ui/index.html` (self-contained, works from file://)
- [ ] Verify a high-risk letter is visible (click through sidebar, find a red dot)
- [ ] USB sticks at the door

---

## 0:00–2:00 — Cold Open: The Spreadsheet

**Screen:** Black terminal. Nothing.

No slides, no intro, no "hi I'm Nathan." Just the story.

> "A consumer gets a collection notice. He doesn't recognize the debt.
> So he does what you'd want him to do — he calls the agency and asks
> for validation.
>
> They send him a document. It's an Excel spreadsheet. It has a list
> of names on it, and a list of balances. His name is not on the list.
>
> He calls back. He says, 'my name isn't on this.' They send him the
> same spreadsheet again.
>
> He sends a certified letter requesting formal debt validation. They
> call him a few more times. Eventually they send him a one-page letter
> that says he owes a balance and should pay it. No contract. No
> account agreement. No proof the debt is his.
>
> That response was legal. It checked every box. And it communicated
> nothing. The consumer still doesn't know whether the debt is real.
> He can't verify it. He can't pay it with confidence. He can't dispute
> it with evidence. So he does nothing. And that account sits at zero
> recovery — not because the agency broke a rule, but because compliance
> and communication are different things."

Pause.

> "That's a real complaint in the CFPB database. Today I'm going to
> show you why your AI pipeline has the same problem."

**Recovery:** This is spoken, not read from screen. Nothing to fail.

---

## 2:00–10:00 — The Idea (No Code Yet)

**Screen:** Can stay black, or show the CFPB complaint database landing
page if wifi is up. This section is Nathan talking, not typing.

### The two measurements (2 min)

> "Every vendor in this room will tell you their AI is compliant. I
> believe them. The question nobody is asking is: does the letter work?
>
> Compliant means it won't get you sued. Effective means the consumer
> reads it, understands it, and responds. Those are different
> measurements, and most shops only track the first one."

### What the data shows (3 min)

> "The CFPB publishes every complaint with a narrative. There are over
> 400,000 from debt collection alone. I read a few thousand of them.
> Here's what consumers actually say about the letters they get:"

Rattle off patterns from memory (these are real CFPB patterns):

- "I didn't understand the letter so I threw it away."
- "They threatened to sue me so I stopped answering the phone."
- "I didn't know I could dispute it."
- "They sent me a payment plan when I told them it wasn't my account."
- "By the time I got the letter the deadline had already passed."

> "These are not compliance failures. These are effectiveness failures.
> The letter passed QA. The consumer threw it away. Your recovery rate
> on that account just went to zero."

### The gap in the pipeline (3 min)

> "Here's what a typical AI pipeline looks like: intake, classify,
> draft, send. Maybe there's a compliance check. What's missing is the
> other half — what does this letter look like when someone opens it on
> a Tuesday after work?
>
> I built a tool that shows both sides. Let me show you."

---

## 10:00–20:00 — Live Proof

**Screen:** Terminal + browser. Nathan runs commands, shows results.

### Show the pipeline (2 min)

```bash
python3 run.py --records 10 --no-llm
```

> "That just ran 10 records through the full pipeline in under a second.
> Template letters — no model needed. Let me show you what it did."

Point at the terminal output: intake, validate, classify, draft, review,
consumer view. Each stage reported what it found.

### Break 1: The String Break (3 min)

```bash
python3 break/break1_strings.py
```

> "See that? '$462' plus '$121' equals '$462$121'. That's not math.
> That's two strings glued together. A letter just went out with a
> balance that doesn't exist.
>
> This is the 'what is a string' test. If your AI vendor can't tell you
> what this does to your portfolio math, they don't understand their own
> pipeline."

```bash
python3 break/break1_strings.py fix
```

> "One line of type coercion. Fixed."

### Show a real LLM letter + review gate (3 min)

Open the browser to `ui/index.html`. Click a record that has an
LLM-drafted letter with review findings.

> "This letter was written by a local model running on this laptop.
> It looks good. Professional tone, right disclosures, correct format.
>
> Now look at the review gate."

Click the Review Gate tab.

> "The model said 'your payment of $X was received on June 18th.' There
> is no payment on June 18th in the source record. The model made it up.
> It's not lying — it's completing the pattern. That's what language
> models do. The gate caught it. Without the gate, that letter goes out."

### Flip the chair: read it as the consumer (4 min)

Click the Consumer Impact tab. Read the annotations.

> "Now I'm going to read this letter the way the person who gets it
> reads it."

Read the letter aloud, slowly. Then:

> "The agency intended to say: 'We're investigating your claim.'
>
> The consumer heard: 'They might sue me, and my credit is already
> ruined, so why bother responding.'
>
> That letter is compliant. It would pass your QA. And the person who
> got it put it in a drawer. Your recovery rate on this account is zero.
> Not because the AI failed. Because compliant and effective are
> different measurements."

---

## 20:00–25:00 — What They Do Monday

**Screen:** Three bullet points (terminal `cat` or just say them).

> "Three things you can do Monday. No software to buy."

**1. Pull 50 of your own letters and read them as the consumer.**
Not as compliance. As the person who opened the envelope. For each one:
does it tell the consumer what to do next, in plain language, in the
first two paragraphs?

**2. Check whether your pipeline enforces types at intake.**
If your balances can arrive as strings, your math is wrong and you
don't know it.

**3. Ask your vendor what happens when the review gate is off.**
If they don't have a review gate, ask what happens when the model
invents a payment date.

> "On the USB stick at the door, there's everything I just showed you.
> It runs on your laptop. No signup, no email, no tracking. It's yours.
>
> Thank you."

---

## Contingency Plans

| Problem | Recovery | Time cost |
|---------|----------|-----------|
| Ollama slow/crashes | `--no-llm` for template letters, show pre-generated LLM output in browser | 0s |
| Break script doesn't hit string balances | Pre-loaded output shows the effect; talk through it | 15s |
| Browser won't open | Show `output/records.json` in terminal with `python3 -c "import json; ..."` | 10s |
| Running long | Cut Break 1, go straight to browser + consumer view | Saves 3 min |
| Running short | Expand consumer view reading, show a second letter, take questions | Fills 3 min |
| Projector fails | Everything is terminal. Can deliver the talk with voice + terminal alone | 0s |

---

## Timing Targets

| Beat | Clock | Duration |
|------|-------|----------|
| Cold open (narrative) | 0:00 | 2 min |
| The two measurements | 2:00 | 2 min |
| CFPB patterns | 4:00 | 3 min |
| The gap in the pipeline | 7:00 | 3 min |
| Show pipeline run | 10:00 | 2 min |
| String break + fix | 12:00 | 3 min |
| LLM letter + review gate | 15:00 | 3 min |
| Flip the chair (consumer view) | 18:00 | 4 min |
| Monday actions + close | 22:00 | 3 min |
| **Total** | | **25 min** |
