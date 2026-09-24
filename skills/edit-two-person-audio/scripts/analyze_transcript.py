#!/usr/bin/env python3
"""Find conservative filler and adjacent-repeat candidates in whisper.cpp full JSON."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

PUNCT = re.compile(r"[\s，。！？、,.!?；;：:…—\-（）()\[\]【】‘’“”\"']+")
STRICT_FILLERS = {"嗯", "嗯嗯", "呃", "呃呃", "额", "額", "啊", "哦", "um", "uh", "umm", "uhh", "erm"}
ONE_TOKEN_REPEAT_OK = {"对", "對", "是", "不", "我", "你", "这", "這", "那", "就是", "这个", "這個", "那个", "那個"}


def norm(text: str) -> str:
    return PUNCT.sub("", text).lower()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.transcript.read_text())
    tokens = []
    for segment in data["transcription"]:
        for token in segment["tokens"]:
            cleaned = norm(token["text"])
            if cleaned and not token["text"].startswith("[_"):
                tokens.append({
                    "text": token["text"].strip(), "norm": cleaned,
                    "start_ms": token["offsets"]["from"], "end_ms": token["offsets"]["to"],
                    "confidence": token.get("p", 0.0),
                })

    candidates = []
    for index, token in enumerate(tokens):
        if token["norm"] in STRICT_FILLERS and token["end_ms"] - token["start_ms"] <= 1800:
            candidates.append({"kind": "filler", "token_start": index, "token_end": index + 1, **token})

    covered = set()
    for index in range(len(tokens)):
        if index in covered:
            continue
        for length in range(4, 0, -1):
            if index + 2 * length > len(tokens):
                continue
            left = tokens[index:index + length]
            right = tokens[index + length:index + 2 * length]
            if [x["norm"] for x in left] != [x["norm"] for x in right]:
                continue
            if right[0]["start_ms"] - left[-1]["end_ms"] > 900:
                continue
            phrase = "".join(x["norm"] for x in left)
            if length == 1 and len(phrase) == 1 and phrase not in ONE_TOKEN_REPEAT_OK:
                continue
            candidates.append({
                "kind": "repeat", "text": "".join(x["text"] for x in left),
                "start_ms": left[0]["start_ms"], "end_ms": left[-1]["end_ms"],
                "confidence": min(x["confidence"] for x in left),
                "token_start": index, "token_end": index + length,
            })
            covered.update(range(index, index + length))
            break

    candidates.sort(key=lambda x: (x["start_ms"], x["end_ms"]))
    for item in candidates:
        start, end = item["token_start"], item["token_end"]
        item["context"] = "".join(x["text"] for x in tokens[max(0, start - 8):min(len(tokens), end + 8)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
    print("tokens", len(tokens), "candidates", dict(Counter(x["kind"] for x in candidates)))


if __name__ == "__main__":
    main()

