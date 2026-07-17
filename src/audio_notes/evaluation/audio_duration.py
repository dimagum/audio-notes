from __future__ import annotations

import json
import subprocess
from pathlib import Path


class AudioDurationError(RuntimeError):
    """Raised when audio duration cannot be extracted."""


def get_audio_duration_seconds(
    audio_path: Path,
    *,
    ffprobe_binary: str = "ffprobe",
) -> float:
    """Returns media duration in seconds using ffprobe."""
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file does not exist: {audio_path}")

    command = [
        ffprobe_binary,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(audio_path),
    ]

    try:
        completed_process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise AudioDurationError(
            f"'{ffprobe_binary}' was not found. "
            "Install FFmpeg and add its bin directory to PATH."
        ) from error
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip()
        raise AudioDurationError(
            f"ffprobe failed for '{audio_path}': {stderr}"
        ) from error

    try:
        payload = json.loads(completed_process.stdout)
        duration = float(payload["format"]["duration"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise AudioDurationError(
            f"ffprobe returned no valid duration for '{audio_path}'."
        ) from error

    if duration <= 0:
        raise AudioDurationError(
            f"Audio duration must be positive, got {duration} for '{audio_path}'."
        )

    return duration