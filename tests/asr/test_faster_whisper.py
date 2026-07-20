from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from audio_notes.asr.faster_whisper import FasterWhisperTranscriber


def test_faster_whisper_transcriber_configures_model() -> None:
    with patch(
        "audio_notes.asr.faster_whisper.WhisperModel"
    ) as model_class:
        FasterWhisperTranscriber(
            model_name="small",
            device="cuda",
            compute_type="float16",
            language="ru",
            beam_size=3,
            vad_filter=True,
        )

    model_class.assert_called_once_with(
        "small",
        device="cuda",
        compute_type="float16",
    )


def test_faster_whisper_transcriber_rejects_invalid_beam_size() -> None:
    with pytest.raises(ValueError, match="beam_size must be positive"):
        FasterWhisperTranscriber(beam_size=0)


def test_faster_whisper_transcriber_joins_non_empty_segments() -> None:
    model = Mock()
    model.transcribe.return_value = (
        [
            SimpleNamespace(text=" Привет, "),
            SimpleNamespace(text=" мир! "),
            SimpleNamespace(text="  "),
        ],
        Mock(),
    )

    with patch(
        "audio_notes.asr.faster_whisper.WhisperModel",
        return_value=model,
    ):
        transcriber = FasterWhisperTranscriber(model_name="small")
        transcript = transcriber.transcribe(Path("sample.mp3"))

    assert transcript == "Привет, мир!"
    model.transcribe.assert_called_once_with(
        "sample.mp3",
        language="ru",
        task="transcribe",
        beam_size=5,
        vad_filter=False,
    )