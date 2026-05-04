# Basketball Shot Review

A pipeline that takes a recorded basketball clip, asks Gemini what happened
on each shot, and renders an annotated video with running make/miss counters
and per-shot coaching feedback.

## Pipeline

1. **capture** — a clip lands in `capture/` (recorded by the iOS app in
   `Basketball/`, or dropped in manually).
2. **analyse** — `src/analyse.py` uploads the clip to Gemini and gets back
   structured shot data (timestamp, made/missed, shot type, feedback).
   Responses are cached in `cache/` keyed by video hash so re-renders are
   free.
3. **render** — `src/render.py` walks the video frame by frame with OpenCV,
   overlays counters and feedback driven by the Gemini output, and writes a
   silent mp4 to `output/`.
4. **mux audio** — ffmpeg copies the original audio track onto the rendered
   mp4 as the final step (OpenCV can't write audio).

## Layout

```
src/        pipeline code (schema, prompt, analyse, render)
capture/    input clips (gitignored)
cache/      Gemini response cache by video hash (gitignored)
output/     rendered mp4s (gitignored)
reference/  Farza's original gemini-bball code, read-only, gitignored
Basketball/ iOS capture app (separate; see SETUP.md)
```

## Setup

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GEMINI_API_KEY
```

Also requires `ffmpeg` on PATH for the audio mux step.

For the iOS capture app, see [SETUP.md](SETUP.md).
