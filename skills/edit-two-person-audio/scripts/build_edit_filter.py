#!/usr/bin/env python3
"""Select safe cuts and write an FFmpeg filter graph with short speech crossfades."""

import argparse
import json
import re
from pathlib import Path

PUNCT = re.compile(r"[\s，。！？、,.!?；;：:…—\-（）()\[\]【】‘’“”\"']+")
INTENTIONAL = {"非常", "特别", "特別", "慢慢", "很快", "太难", "太難", "最最"}


def norm(text: str) -> str:
    return PUNCT.sub("", text).lower()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--filter", type=Path, required=True)
    args = parser.parse_args()

    selected = []
    for item in json.loads(args.candidates.read_text()):
        duration = item["end_ms"] - item["start_ms"]
        if duration < 80 or item.get("confidence", 0) < 0.45 or norm(item["text"]) in INTENTIONAL:
            continue
        start = max(0, (item["start_ms"] - 15) / 1000)
        end = (item["end_ms"] + 20) / 1000
        selected.append({"start": start, "end": end, "kind": item["kind"], "text": item["text"], "context": item["context"]})

    selected.sort(key=lambda x: (x["start"], x["end"]))
    merged = []
    for item in selected:
        if merged and item["start"] <= merged[-1]["end"] + 0.035:
            merged[-1]["end"] = max(merged[-1]["end"], item["end"])
            merged[-1]["text"] += "/" + item["text"]
        else:
            merged.append(item)

    args.plan.parent.mkdir(parents=True, exist_ok=True)
    args.filter.parent.mkdir(parents=True, exist_ok=True)
    args.plan.write_text(json.dumps(merged, ensure_ascii=False, indent=2))
    keep, cursor = [], 0.0
    for item in merged:
        if item["start"] > cursor:
            keep.append((cursor, item["start"]))
        cursor = max(cursor, item["end"])
    if cursor < args.duration:
        keep.append((cursor, args.duration))

    lines = [f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[s{i}]" for i, (a, b) in enumerate(keep)]
    tail = "[s0]"
    for index in range(1, len(keep)):
        lines.append(f"{tail}[s{index}]acrossfade=d=0.012:c1=tri:c2=tri[x{index}]")
        tail = f"[x{index}]"
    lines.append(f"{tail}loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
    args.filter.write_text(";\n".join(lines) + "\n")
    print("selected", len(merged), "removed_seconds", round(sum(x["end"] - x["start"] for x in merged), 3))


if __name__ == "__main__":
    main()

