# Command Templates

## Dependencies

- FFmpeg: `ffmpeg`, `ffprobe`
- whisper.cpp: `whisper-cli` and a multilingual GGML model
- Python 3 standard library only
- Shell utilities: `cp`, `ls`, optionally `jq`

## Inspect

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_name,sample_rate,channels -of json input.m4a
```

## Opening transcription

```bash
ffmpeg -y -i input.m4a -t 40 -ar 16000 -ac 1 opening.wav
whisper-cli -ng -m models/ggml-small.bin -f opening.wav -l zh -ojf -osrt -of opening
```

## Build aligned masters

```bash
python3 scripts/align_merge.py me.m4a him.mp3 \
  --a-trim 7.800 --b-trim 11.450 --b-delay 5.024 \
  --a-gain 1.0 --b-gain 1.0 \
  --master aligned.flac --transcription-wav aligned-16k.wav
```

## Full transcription and cleanup plan

```bash
whisper-cli -ng -m models/ggml-small.bin -f aligned-16k.wav -l zh \
  -t 8 -bs 1 -bo 1 -nf -ojf -osrt -of merged
python3 scripts/analyze_transcript.py merged.json candidates.json
python3 scripts/build_edit_filter.py candidates.json --duration 1485.75 \
  --plan edits.json --filter render-filter.txt
```

Review `edits.json` before rendering.

## Render

```bash
ffmpeg -y -i aligned.flac -filter_complex_script render-filter.txt \
  -map '[out]' -c:a aac -b:a 192k -movflags +faststart result.m4a
```

## QA

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate:stream=codec_name,sample_rate,channels -of json result.m4a
ffmpeg -v error -i result.m4a -f null -
ffmpeg -i result.m4a -af volumedetect -f null -
ffmpeg -y -i result.m4a -t 20 -ar 16000 -ac 1 result-start.wav
whisper-cli -ng -m models/ggml-small.bin -f result-start.wav -l zh -otxt -of result-start
```

Confirm the opening transcript contains the intended introduction sequence and no countdown.
