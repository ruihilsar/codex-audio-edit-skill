#!/usr/bin/env python3
"""Align and merge two recordings with FFmpeg; requires no third-party Python packages."""

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("speaker_a", type=Path)
    parser.add_argument("speaker_b", type=Path)
    parser.add_argument("--a-trim", type=float, required=True)
    parser.add_argument("--b-trim", type=float, required=True)
    parser.add_argument("--b-delay", type=float, required=True, help="Seconds after output start")
    parser.add_argument("--a-gain", type=float, default=1.0, help="Linear gain for speaker A")
    parser.add_argument("--b-gain", type=float, default=1.0, help="Linear gain for speaker B")
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--transcription-wav", type=Path, required=True)
    args = parser.parse_args()

    if args.b_delay < 0:
        raise SystemExit("--b-delay must be non-negative")
    if args.a_gain <= 0 or args.b_gain <= 0:
        raise SystemExit("speaker gains must be positive")
    args.master.parent.mkdir(parents=True, exist_ok=True)
    args.transcription_wav.parent.mkdir(parents=True, exist_ok=True)
    delay_ms = round(args.b_delay * 1000)
    graph = (
        f"[0:a]atrim=start={args.a_trim:.3f},asetpts=PTS-STARTPTS,volume={args.a_gain:.4f}[a];"
        f"[1:a]aformat=channel_layouts=mono,atrim=start={args.b_trim:.3f},"
        f"asetpts=PTS-STARTPTS,adelay={delay_ms}:all=1,volume={args.b_gain:.4f}[b];"
        "[a][b]amix=inputs=2:duration=longest:weights='0.5 0.5':normalize=0,"
        "highpass=f=70,lowpass=f=14000,alimiter=limit=0.95,asplit=2[master][tx];"
        "[tx]aresample=16000[tx16]"
    )
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(args.speaker_a), "-i", str(args.speaker_b),
        "-filter_complex", graph,
        "-map", "[master]", "-ar", "48000", "-ac", "1", "-c:a", "flac", str(args.master),
        "-map", "[tx16]", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        str(args.transcription_wav),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
