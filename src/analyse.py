import argparse
import hashlib
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from format import format_session
from prompt import ANALYSIS_PROMPT
from schema import SessionAnalysis

load_dotenv()

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


def _hash_video(video_path: Path) -> str:
    h = hashlib.sha256()
    with video_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _wait_for_active(client: genai.Client, file_handle):
    while file_handle.state.name == "PROCESSING":
        time.sleep(2)
        file_handle = client.files.get(name=file_handle.name)
    if file_handle.state.name != "ACTIVE":
        raise RuntimeError(
            f"Gemini file processing ended in state {file_handle.state.name}"
        )
    return file_handle


def analyse_video(video_path: Path, model: str = "gemini-2.5-pro") -> SessionAnalysis:
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Copy .env.example to .env in the project root and add your key."
        )

    digest = _hash_video(video_path)
    cache_path = CACHE_DIR / f"{digest}.json"
    if cache_path.exists():
        return SessionAnalysis.model_validate_json(cache_path.read_text())

    client = genai.Client(api_key=api_key)
    uploaded = client.files.upload(file=str(video_path))
    uploaded = _wait_for_active(client, uploaded)

    response = client.models.generate_content(
        model=model,
        contents=[uploaded, ANALYSIS_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SessionAnalysis,
            temperature=0.3,
        ),
    )

    raw = response.text
    try:
        result = SessionAnalysis.model_validate_json(raw)
    except ValidationError as e:
        raise ValueError(
            "Gemini response did not match SessionAnalysis schema.\n"
            f"Validation error: {e}\n"
            f"Raw response:\n{raw}"
        ) from e

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(result.model_dump_json(indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse a basketball video with Gemini.")
    parser.add_argument("video", type=Path, help="Path to the video file.")
    parser.add_argument("--json", action="store_true", help="Print raw JSON instead of the formatted summary.")
    args = parser.parse_args()

    analysis = analyse_video(args.video)

    if args.json:
        print(analysis.model_dump_json(indent=2))
    else:
        print(format_session(analysis))
