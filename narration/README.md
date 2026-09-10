# Narration — "The Letter That Refused to Send"

An audio-first telling of this session, written so a listener who cannot see a screen loses nothing.
Two hosts. Every number is spelled out in words. The four levels are carried by one running analogy
(taking your car to a shop) so the structure survives without a diagram.

## Files

| File | What it is |
|---|---|
| `SCRIPT.md` | Full 12-minute script with production notes and the four TLDR soundbites |
| `RECORDING-SCRIPT.txt` | Same script, stage directions stripped, ready for voice actors |
| `tts-segments.json` | The 12 prompts used to generate the 7-minute audio cut, with voice assignments |
| `stitch-npr-audio.py` | Downloads the 12 rendered clips and joins them into one MP3 |

## The 7-minute cut

Generated 2026-09-10 with Artlist text-to-speech. Twelve alternating segments:

- **DANA** — *Path* (female, adult, American)
- **RAY** — *Gravity* (male, middle-aged, American)

Run `python3 stitch-npr-audio.py` to rebuild `the-letter-that-refused-to-send.mp3` from the rendered clips.
To re-voice, feed each entry in `tts-segments.json` to any TTS engine in order and concatenate.

## The four soundbites

1. It didn't lie. It agreed. And a wrong letter looks exactly like a right one.
2. Better prompts make the wrong letters more convincing, not rarer.
3. A smoke alarm doesn't carry water. You didn't remove the work — you relocated it.
4. Refused means refused.

## Accuracy note

`SESSION-RUN-OF-SHOW.md` gives two figures for monthly unsupported letters at Level 1 (77 in the Level 1
narrative, 67 in the comparison table). The narration says "somewhere around seventy," which is true either
way. Reconcile the source before any version claims a precise number.

*All content runs on public CFPB complaint narratives plus a synthetic ledger. No real identity appears
anywhere. Letters are drafted for review, never dispatched.*
