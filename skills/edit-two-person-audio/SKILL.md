---
name: edit-two-person-audio
description: Align, merge, clean, render, and verify two separately recorded MP3/M4A voice tracks for a two-person conversation. Use when Codex must remove a shared countdown, synchronize speakers from spoken introduction anchors, remove high-confidence fillers/restarts/adjacent repetitions, normalize loudness, and create a reviewed M4A result.
---

# Edit Two-Person Audio

Create a natural single-track conversation from two independently recorded voices. Treat spoken content—not the countdown—as the synchronization authority.

## Workflow

1. Inspect both sources with `ffprobe`; preserve originals.
2. Convert only the first 30–60 seconds to 16 kHz mono WAV and transcribe with word timestamps.
3. Find semantic anchors. Prefer the end of speaker A's introduction and the beginning of speaker B's introduction, such as `我是小韩` → `我是老苏`.
4. Remove the countdown by trimming both sources before their program content. Never synchronize from countdown timing alone.
5. Calculate speaker B's delay so its first introduction word begins immediately after speaker A's introduction ends. Allow about 50–100 ms pre-roll to avoid clipping consonants.
6. Run `scripts/align_merge.py` to create a lossless FLAC master and a 16 kHz transcription WAV.
7. Transcribe the aligned WAV with full token timestamps.
8. Run `scripts/analyze_transcript.py`, then `scripts/build_edit_filter.py`.
9. Review every proposed cut. Keep intentional emphasis (`非常非常`, `很快很快`, `太难太难`) and sentence particles that carry meaning. Remove only high-confidence fillers, failed restarts, and adjacent duplicate phrases.
10. Render AAC/M4A at 192 kb/s with short crossfades and `loudnorm` targeting -16 LUFS.
11. Decode-test the result, inspect duration/codec/loudness, and retranscribe the first 15–30 seconds. Confirm the countdown is absent and the introduction handoff is continuous.
12. Copy to the requested destination only after QA passes.

## Alignment Formula

Let:

- `a_trim` be speaker A's source trim point.
- `a_anchor_end` be the source time where A's introduction ends.
- `b_trim` be a short pre-roll before speaker B's introduction.
- `b_anchor_start` be the source time where B's introduction begins.

Use:

```text
b_delay = (a_anchor_end - a_trim) - (b_anchor_start - b_trim)
```

Reject negative delay or clipped pre-roll. Generate a one-minute preview whenever anchor confidence is low or the user previously reported misalignment.

## Cleanup Rules

- Remove strict hesitation tokens such as `嗯`, `呃`, `额`, and standalone hesitation `啊` only when timestamps and context show they are disposable.
- Remove the first copy of an adjacent exact repetition; retain the fluent final copy.
- Preserve deliberate rhetorical repetition and emphasis.
- Do not infer profanity removal. Ask for a word list when the user means censorship or muting specific words.
- Add 10–40 ms padding and a roughly 12 ms crossfade around cuts; never hard-splice speech.
- Prefer missing an uncertain filler over deleting meaningful speech.

## Resources

- `scripts/align_merge.py`: build aligned FLAC and transcription WAV masters.
- `scripts/analyze_transcript.py`: detect strict fillers and adjacent repetitions from whisper.cpp JSON.
- `scripts/build_edit_filter.py`: select conservative cuts and generate an FFmpeg filter graph.
- `references/commands.md`: command templates, QA checks, and dependency notes.

