from __future__ import annotations

from pathlib import Path

import pytest

from audio_notes.asr.mock import MockTranscriber


def test_mock_transcriber_returns_configured_transcript() -> None:
    audio_path = Path("data/audio/sample.mp3")
    transcriber = MockTranscriber(
        {
            audio_path: "модель успешно распознала аудио",
        }
    )

    transcript = transcriber.transcribe(audio_path)

    assert transcript == "модель успешно распознала аудио"
    assert transcriber.calls == [audio_path]


def test_mock_transcriber_tracks_multiple_calls() -> None:
    first_path = Path("data/audio/first.mp3")
    second_path = Path("data/audio/second.mp3")

    transcriber = MockTranscriber(
        {
            first_path: "первый текст",
            second_path: "второй текст",
        }
    )

    assert transcriber.transcribe(first_path) == "первый текст"
    assert transcriber.transcribe(second_path) == "второй текст"
    assert transcriber.calls == [first_path, second_path]


def test_mock_transcriber_rejects_unconfigured_path() -> None:
    transcriber = MockTranscriber({})
    audio_path = Path("data/audio/missing.mp3")

    with pytest.raises(KeyError, match="No mock transcript configured"):
        transcriber.transcribe(audio_path)