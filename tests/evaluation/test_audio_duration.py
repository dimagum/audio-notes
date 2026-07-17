from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from audio_notes.evaluation.audio_duration import (
    AudioDurationError,
    get_audio_duration_seconds,
)


def test_get_audio_duration_seconds_returns_ffprobe_duration(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    completed_process = Mock()
    completed_process.stdout = '{"format": {"duration": "12.345678"}}'

    with patch(
        "audio_notes.evaluation.audio_duration.subprocess.run",
        return_value=completed_process,
    ) as run_mock:
        duration = get_audio_duration_seconds(audio_path)

    assert duration == pytest.approx(12.345678)
    run_mock.assert_called_once_with(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(audio_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_get_audio_duration_seconds_raises_for_missing_file(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.mp3"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        get_audio_duration_seconds(missing_path)


def test_get_audio_duration_seconds_raises_when_ffprobe_is_missing(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    with patch(
        "audio_notes.evaluation.audio_duration.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(AudioDurationError, match="was not found"):
            get_audio_duration_seconds(audio_path)


def test_get_audio_duration_seconds_raises_when_ffprobe_fails(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    process_error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["ffprobe"],
        stderr="Invalid data found when processing input",
    )

    with patch(
        "audio_notes.evaluation.audio_duration.subprocess.run",
        side_effect=process_error,
    ):
        with pytest.raises(AudioDurationError, match="ffprobe failed"):
            get_audio_duration_seconds(audio_path)


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        "not json",
        "{}",
        '{"format": {}}',
        '{"format": {"duration": "not-a-number"}}',
        '{"format": {"duration": "0"}}',
        '{"format": {"duration": "-1.0"}}',
    ],
)
def test_get_audio_duration_seconds_raises_for_invalid_duration(
    tmp_path: Path,
    stdout: str,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    completed_process = Mock()
    completed_process.stdout = stdout

    with patch(
        "audio_notes.evaluation.audio_duration.subprocess.run",
        return_value=completed_process,
    ):
        with pytest.raises(AudioDurationError):
            get_audio_duration_seconds(audio_path)