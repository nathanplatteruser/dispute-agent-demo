# Both Sides of the Letter

### Session Run of Show

**Brainstorm 2026 · Denver · September 9 to 11**

Ralph Hall, moderator · Nathan Platter · Olga Mironova · Aryeh Derman

---

## What this document is

This is the working run of show for our sandbox session, published before the session rather than after it.

Every number in here came out of a real run on a laptop with the wifi off. Nothing is projected, modeled, or rounded in our favor. If a figure looks surprising, the code that produced it is in this repository and you can run it yourself.

We are publishing this for three reasons.

First, so attendees can follow along without taking notes, and can read it again later on their own time.

Second, so the four of us are working from the same document rather than four different mental models.

Third, because the argument of this session is that AI systems should show their work. It would be strange to make that argument from behind a curtain.

---

## The thesis

Your compliance process works. You pass your audits. Your letters clear review.

And somewhere in your book right now are accounts sitting at zero recovery, not because anyone broke a rule, but because the letter you sent was **correct and useless at the same time**.

Compliant and effective are two different measurements. They are audited by two different people. Most operations instrument one of them.

This session builds a system that measures both, live, offline, on a laptop.

---

## The verified numbers

Pooled across four runs, 1,640 drafted letters, all offline on a local model. September 1 to 2, 2026.

| Metric | Value |
| :--- | :--- |
| Letters drafted | 1,640 |
| Flagged by the review gate | 126, about 1 in 13 |
| Recovered after remediation | 123, or 97.6 percent |
| Refused outright | 3, roughly 1 in 550 |
| Scored high engagement risk | 14.1 percent |
| Balances arriving as text, not numbers | 2 per record, every record |
| Records classified with zero model calls | 1,500 of 1,500 |
| Time to read and classify one dispute | 46 milliseconds |
| Time to draft one letter | 15.6 seconds |

### Per run, in case you want to check the spread

| Run | Drafted | Flagged | Recovered | Refused |
| :--- | ---: | ---: | ---: | ---: |
| 100 records, 40 drafts | 40 | 5 | 5 | 0 |
| 1,500 records, 300 drafts (A) | 300 | 26 | 25 | 1 |
| 1,500 records, 300 drafts (B) | 300 | 20 | 19 | 1 |
| 1,500 records, 1,000 drafts | 1,000 | 75 | 74 | 1 |

The flag rate held between 6.7 and 12.5 percent across every run. That consistency is the finding. The exact number is not the point.

---

## The four levels

The session walks four approaches to the same problem. Each one solves the previous level's failure and introduces its own.

Volume assumptions come from a practicing ARM attorney: 500 to 1,000 dispute letters per month, 10 to 15 minutes each by hand, handled by processing staff at 20 to 25 dollars per hour. Figures below assume 1,000 per month.

### Level 1. The Uploader

Pastes the dispute into a chat assistant, copies the letter, mails it. Thirty seconds each, and the output looks professional.

**Where it breaks.** Nothing compares the letter to the account record.

In our demonstration record, the consumer writes that they were offered a discount to settle a one thousand dollar bill. The ledger says the balance is 20,370 dollars and 53 cents. The model wrote one thousand dollars into the response, because the consumer wrote one thousand dollars into the complaint.

The model was not hallucinating from nothing. It was agreeing with the consumer. That is a harder failure to catch, because the number came from somewhere real.

**What it costs.** Roughly 77 letters a month state amounts or dates that appear nowhere in the account record. You find out from a complaint, a regulatory inquiry, or opposing counsel.

**Why you cannot stay here.** The failure is invisible. A wrong letter looks exactly like a right one.

### Level 2. The Prompt Engineer

Writes better prompts. Adds examples. Builds a custom assistant. Instructs the model to use only facts from the record.

**Where it breaks.** We do this. Our prompt says, in capital letters, to use only the record facts, and repeats the instruction at the end. It is in this repository and you can read it.

It still fails in about one letter out of thirteen.

**Why you cannot stay here.** You cannot prompt your way out of this, because the model does not know when it is wrong. And better letters are harder to audit, not easier. The wrong ones now look more convincing.

### Level 3. The Checker

Builds a verification layer. Every dollar amount, every date, every payment assertion is extracted from the draft and checked against the source record. Anything unsupported is blocked.

This is real engineering and it works. Of 1,640 letters, 126 were caught. Zero fabrications reached the mail.

**Where it breaks.** The checker tells you where the problems are. It does not fix a single one.

At 1,000 disputes a month, that is roughly 77 letters flagged for factual defects and another 141 flagged for high engagement risk. Call it 218 letters a month landing in somebody's queue.

You did not remove the work. You relocated it, and you added a queue that did not exist before.

**Why you cannot stay here.** A gate that only says no is a smoke alarm. It tells you where the fire is. It does not go get water.

### Level 4. Fix, then refuse

Every blocked letter goes back to the model along with its own report card. Not an instruction to try again, but a specific correction:

> You wrote one thousand dollars. That amount does not appear in the account record. The balance is 20,370 dollars and 53 cents. Draft it again.

The gate then re-runs on the new draft, twice if necessary.

**Result across 1,640 letters.** 126 blocked, 123 recovered, 3 refused.

Refused means refused. Not sent, not quietly patched. Escalated to a human with a written record of what was wrong, how many attempts were made, and why the system stopped.

**What it costs.** At 1,000 disputes a month, roughly two letters need human judgment, plus a spot check of what passed. Four hours instead of two hundred.

---

## The comparison

At 1,000 dispute letters per month.

| Approach | Monthly labor | Letters mailed with fabricated facts | Letters needing a human |
| :--- | :--- | ---: | ---: |
| By hand | 167 to 250 hours | approx. 0 | 1,000 |
| Chat assistant, unchecked | minimal | approx. 67 | 0 |
| Checked but not corrected | approx. 23 hours | approx. 0 | approx. 227 |
| Fix, then refuse | machine cost only | approx. 0 | approx. 3 |

Machine cost is electricity. Under two cents for a thousand letters. The pipeline runs locally with no API spend and no accounts.

---

## What this is not

The pitch is not headcount reduction. At 1,000 disputes a month an agency is spending roughly a person and a half on this workflow, and telling that agency to fire someone is both a depressing argument and a weak one.

The argument is capacity. Dispute volume currently caps how much business an agency can take on, because a larger client means hiring before you can serve them. Remove that ceiling and it is the same team handling more work. Depending on what share of the team's day disputes actually occupy, the realistic headroom is 30 to 65 percent more volume without adding staff.

---

## What we still cannot do

Three limitations, stated plainly, because a session about honest AI should be honest about its own tooling.

**Nothing here checks whether the answer answers the question.** The gate verifies that claims are true. It has no view on whether the letter is responsive to the dispute the consumer actually raised. A consumer can write that an account is not theirs and receive a validation timeline in response. Every fact correct, entirely unresponsive, gate satisfied.

**The engagement risk scorer is phrase matching, not comprehension.** It flags "pursuant to" as jargon because that phrase is on a list. It is a lookup table. Calling it anything more would be the same overselling this session argues against.

**Records are not stable across runs.** A different draw produces different flags. We present from a locked file and we say so.

---

## Session flow

Twenty-five minutes, four levels, three demonstrations.

| Time | Segment |
| :--- | :--- |
| 0:00 | The thesis. Compliant and effective are different measurements. |
| 2:00 | Level 1. The Uploader. Read the consumer's own words. |
| 5:00 | Level 2. The Prompt Engineer. Live run, and the data layer problem. |
| 8:00 | Level 3. The Checker. Both measurements on screen. |
| 12:00 | The letters the gate will not pass. |
| 15:00 | Remediation. The report card goes back to the model. |
| 18:00 | The letter the system refuses to send. |
| 20:00 | Why the refused letter is the most readable one in the batch. |
| 22:00 | What to run on Monday. |

---

## What to run on Monday

**Read one of your own letters as the consumer.** Not as compliance. As the person who opened it on a Tuesday and has fourteen other things going on.

**Check whether your intake enforces types.** If a balance can arrive as text rather than a number, your arithmetic is silently wrong and nothing in your stack will tell you.

**Ask your vendor what happens when the review gate is off.** If there is no review gate, ask what happens when the model invents a payment date.

---

## Running this yourself

Everything is in this repository. No signup, no account, no email capture.

Start with **00-START-HERE-Setup-Guide.docx** if you have not used a command line before. It is written for Windows, Mac and Linux, one command per step, no assumed knowledge.

Requirements are a laptop, Python 3.10 or newer, and Ollama, which is free. There are no other dependencies. The pipeline uses only Python's standard library, and the model runs locally, so nothing you type leaves your machine.

---

*All work runs on public CFPB complaint narratives joined to a synthetic account ledger. No personally identifiable information, no client data. Letters are drafted for review and never dispatched.*
