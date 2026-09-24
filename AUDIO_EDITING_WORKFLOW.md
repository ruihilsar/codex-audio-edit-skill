# Audio Editing Workflow Principle

This document defines how Codex maintains and uses the reusable two-person
audio-editing skill. Apply this workflow whenever the user says to follow the
"audio editing workflow principle."

## 1. Start from the latest version

1. Confirm that the local Git repository is on `main` and has no uncommitted
   changes.
2. Pull the latest remote version with:

   ```bash
   git pull --ff-only origin main
   ```

3. If the repository is not clean or the pull cannot fast-forward, stop the
   synchronization and report the problem. Do not overwrite local work or
   resolve conflicts by assumption.

## 2. Synchronize the skill copies

- Treat the updated local Git repository as the master copy.
- Synchronize the repository's `skills/edit-two-person-audio/` directory into
  the active working-thread skill directory before editing audio.
- Do not copy recordings, transcripts, temporary work directories, model
  files, or rendered audio results into the skill repository.

## 3. Edit and verify the audio

- Follow `skills/edit-two-person-audio/SKILL.md` and its supporting scripts and
  references.
- Keep timestamps, alignment offsets, filenames, detected-noise locations,
  transcript corrections, and other episode-specific decisions in the current
  job workspace.
- Complete the normal audio quality checks before delivering the result.

## 4. Classify what was learned

After editing, classify each potential change as one of the following:

### Recording-specific exception

A decision that is useful only for the current recordings. Examples include:

- Exact cough, click, thunder, filler, or restart timestamps.
- A track delay or alignment offset chosen for one recording pair.
- Speaker-specific gain or noise-reduction settings for one episode.
- Filenames, dates, transcripts, output names, and edit lists.
- A threshold adjustment supported only by one unusual recording.

Keep these changes outside the reusable skill.

### Reusable improvement

A change that is likely to improve future, previously unseen recordings.
Examples include:

- Fixing a script or alignment bug.
- Improving general introduction-anchor detection.
- Adding a configurable cough, click, keyboard, or thunder-processing option.
- Preventing cleanup logic from cutting meaningful speech.
- Improving rendering, validation, or audio-quality checks.

Prepare these changes in the reusable skill and test them.

### Ambiguous candidate

A change that might be reusable but could unexpectedly affect future audio.
Explain the tradeoff and ask the user before making it permanent.

Use this test when classifying a change:

> Would this change help another unknown pair of recordings without knowing
> their specific speakers, timestamps, filenames, or noises?

- If yes, it is probably reusable.
- If no, it is probably a recording-specific exception.
- If uncertain, treat it as an ambiguous candidate and request a decision.

A reusable capability and its recording-specific configuration may be split.
For example, a general `--alignment-offset` option can be reusable while the
value `0.35` seconds for one episode remains recording-specific.

## 5. Review repository changes

After the audio is complete:

1. Synchronize tested reusable improvements into both local skill copies.
2. Report whether the skill changed.
3. Show the changed files and Git diff.
4. Explain the behavioral effect of each change.
5. Recommend whether each change should become part of the permanent skill.

Do not require a separate discussion for obvious recording-specific
exceptions. Ask the user only when the classification or long-term behavior is
ambiguous.

## 6. Commit and publish only with approval

- Do not commit or push reusable improvements automatically.
- Wait for the user to approve the reviewed diff, unless the user has already
  explicitly requested committing and pushing that specific change.
- After approval, commit the change and push it to remote `main`.
- Confirm that local `main` matches `origin/main`.
- Synchronize the approved repository version back into the working-thread
  skill copy.
