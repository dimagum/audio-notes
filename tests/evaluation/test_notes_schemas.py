from __future__ import annotations

import pytest
from pydantic import ValidationError

from audio_notes.evaluation.schemas import (
    NoteSegment,
    NotesManifestRecord,
)


def make_segment() -> dict[str, object]:
    return {
        "segment_id": "record_001_0000",
        "start_seconds": 0.0,
        "end_seconds": 4.5,
        "text": "Первый фрагмент выступления.",
    }


def make_payload() -> dict[str, object]:
    return {
        "id": "record_001",
        "source": "Test source",
        "split": "test",
        "audio_path": "data/audio/record_001.flac",
        "reference_text": (
            "Первый фрагмент выступления. "
            "Второй фрагмент выступления."
        ),
        "summary": (
            "Спикер представил основную тему "
            "и обозначил дальнейший контекст."
        ),
        "segments": [
            make_segment(),
        ],
        "n_segments": 1,
        "duration_seconds": 5.0,
        "domain": "general",
    }


def test_note_segment_accepts_valid_data() -> None:
    segment = NoteSegment.model_validate(make_segment())

    assert segment.segment_id == "record_001_0000"
    assert segment.start_seconds == 0.0
    assert segment.end_seconds == 4.5


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("segment_id", ""),
        ("start_seconds", -0.1),
        ("end_seconds", 0),
        ("text", ""),
    ],
)
def test_note_segment_rejects_invalid_fields(
    field_name: str,
    invalid_value: str | float,
) -> None:
    payload = make_segment()
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        NoteSegment.model_validate(payload)


def test_note_segment_rejects_invalid_time_range() -> None:
    payload = make_segment()
    payload["start_seconds"] = 4.5
    payload["end_seconds"] = 4.5

    with pytest.raises(
        ValidationError,
        match="end_seconds must be greater",
    ):
        NoteSegment.model_validate(payload)


def test_notes_manifest_record_accepts_valid_data() -> None:
    record = NotesManifestRecord.model_validate(make_payload())

    assert record.id == "record_001"
    assert record.n_segments == 1
    assert record.summary.startswith("Спикер")


def test_notes_manifest_record_rejects_wrong_segment_count() -> None:
    payload = make_payload()
    payload["n_segments"] = 2

    with pytest.raises(
        ValidationError,
        match="n_segments must match",
    ):
        NotesManifestRecord.model_validate(payload)


def test_notes_manifest_record_rejects_segment_beyond_duration() -> None:
    payload = make_payload()
    payload["duration_seconds"] = 4.0

    with pytest.raises(
        ValidationError,
        match="must not exceed duration_seconds",
    ):
        NotesManifestRecord.model_validate(payload)