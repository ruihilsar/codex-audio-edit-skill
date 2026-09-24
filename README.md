# Codex Two-Person Audio Editing Skill

A reusable Codex skill for aligning and editing two independently
recorded conversation tracks.

## Features

- Removes recording countdowns
- Aligns using “我是小韩” → “我是老苏”
- Removes clear fillers, failed restarts, and adjacent repetitions
- Softens clicks and keyboard noise
- Reviews cough candidates
- Normalizes loudness
- Produces a verified M4A result

## Dependencies

- FFmpeg
- whisper.cpp
- Python 3

## Installation

Copy or link `skills/edit-two-person-audio` into:

`~/.codex/skills/edit-two-person-audio`
