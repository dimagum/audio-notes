from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from audio_notes.evaluation.schemas import (
    AsrEvaluationSummary,
    AsrManifestRecord,
    AsrSampleResult,
)


def test_asr_manifest_record_accepts_valid_data() -> None:
    record = AsrManifestRecord.model_validate(
        {
            "id": "cv_ru_test_0001",
            "source": "Mozilla Common Voice Russian",
            "split": "test",
            "audio_path": "data/external/common_voice_ru/clips/sample.mp3",
            "reference_text": "модель должна быть воспроизводимой",
        }
    )

    assert record.id == "cv_ru_test_0001"
    assert record.audio_path == Path(
        "data/external/common_voice_ru/clips/sample.mp3"
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "id": "",
            "source": "Common Voice",
            "split": "test",
            "audio_path": "sample.mp3",
            "reference_text": "текст",
        },
        {
            "id": "sample_001",
            "source": "",
            "split": "test",
            "audio_path": "sample.mp3",
            "reference_text": "текст",
        },
        {
            "id": "sample_001",
            "source": "Common Voice",
            "split": "",
            "audio_path": "sample.mp3",
            "reference_text": "текст",
        },
        {
            "id": "sample_001",
            "source": "Common Voice",
            "split": "test",
            "audio_path": "sample.mp3",
            "reference_text": "текст",
            "unexpected_field": "not allowed",
        },
    ],
)
def test_asr_manifest_record_rejects_invalid_data(
    payload: dict[str, str],
) -> None:
    with pytest.raises(ValidationError):
        AsrManifestRecord.model_validate(payload)


def test_asr_sample_result_accepts_valid_data() -> None:
    result = AsrSampleResult.model_validate(
        {
            "id": "cv_ru_test_0001",
            "audio_path": "sample.mp3",
            "reference_text": "модель обучается быстро",
            "hypothesis_text": "модель обучается быстро",
            "audio_duration_seconds": 3.5,
            "asr_seconds": 0.4,
            "asr_rtf": 0.114,
            "wer": 0.0,
            "cer": 0.0,
            "substitutions": 0,
            "deletions": 0,
            "insertions": 0,
            "character_substitutions": 0,
            "character_deletions": 0,
            "character_insertions": 0,
            "reference_word_count": 3,
            "hypothesis_word_count": 3,
            "reference_character_count": 23,
            "hypothesis_character_count": 23,
            "error": None,
        }
    )

    assert result.wer == 0.0
    assert result.error is None


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("audio_duration_seconds", -0.1),
        ("asr_seconds", -0.1),
        ("asr_rtf", -0.1),
        ("wer", -0.1),
        ("cer", -0.1),
        ("substitutions", -1),
        ("deletions", -1),
        ("insertions", -1),
        ("reference_word_count", -1),
        ("hypothesis_word_count", -1),
        ("character_substitutions", -1),
        ("character_deletions", -1),
        ("character_insertions", -1),
        ("reference_character_count", -1),
        ("hypothesis_character_count", -1),
    ],
)
def test_asr_sample_result_rejects_invalid_metrics(
    field_name: str,
    invalid_value: float | int,
) -> None:
    payload = {
        "id": "sample_001",
        "audio_path": "sample.mp3",
        "reference_text": "эталон",
        "hypothesis_text": "предсказание",
        "audio_duration_seconds": 1.0,
        "asr_seconds": 0.1,
        "asr_rtf": 0.1,
        "wer": 0.0,
        "cer": 0.0,
        "substitutions": 0,
        "deletions": 0,
        "insertions": 0,
        "reference_word_count": 1,
        "hypothesis_word_count": 1,
        "character_substitutions": 0,
        "character_deletions": 0,
        "character_insertions": 0,
        "reference_character_count": 10,
        "hypothesis_character_count": 10,
        "error": None,
    }
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        AsrSampleResult.model_validate(payload)


def test_asr_evaluation_summary_accepts_valid_data() -> None:
    summary = AsrEvaluationSummary.model_validate(
        {
            "n_total": 300,
            "n_success": 299,
            "n_failed": 1,
            "wer": 0.093,
            "cer": 0.025,
            "audio_seconds_total": 1560.0,
            "asr_seconds_total": 84.0,
            "rtf_global": 0.054,
            "rtf_median": 0.051,
            "rtf_p95": 0.089,
        }
    )

    assert summary.n_total == 300
    assert summary.rtf_global == pytest.approx(0.054)