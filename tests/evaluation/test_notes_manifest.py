from __future__ import annotations

import json
from pathlib import Path

import pytest

from audio_notes.evaluation.notes_manifest import (
    NotesManifestValidationError,
    load_notes_manifest,
)


def make_record() -> dict[str, object]:
    return {
        "id": "record_001",
        "source": "Test source",
        "split": "test",
        "audio_path": "data/audio/record_001.flac",
        "reference_text": "Исходный текст выступления.",
        # "summary": "Краткая заметка по выступлению.",
        "segments": [
            {
                "segment_id": "record_001_0000",
                "start_seconds": 0.0,
                "end_seconds": 4.0,
                "text": "Исходный текст выступления.",
            }
        ],
        "n_segments": 1,
        "duration_seconds": 4.0,
        "domain": "general",
    }


def write_jsonl(
    path: Path,
    records: list[dict[str, object]],
) -> None:
    path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


def test_load_notes_manifest_returns_valid_records(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes.jsonl"
    write_jsonl(manifest_path, [make_record()])

    records = load_notes_manifest(manifest_path)

    assert len(records) == 1
    assert records[0].id == "record_001"
    # assert records[0].summary == "Краткая заметка по выступлению."
    assert records[0].reference_text == "Исходный текст выступления."
    assert records[0].segments[0].segment_id == "record_001_0000"


def test_load_notes_manifest_rejects_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        NotesManifestValidationError,
        match="does not exist",
    ):
        load_notes_manifest(tmp_path / "missing.jsonl")


def test_load_notes_manifest_rejects_empty_file(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes.jsonl"
    manifest_path.write_text("", encoding="utf-8")

    with pytest.raises(
        NotesManifestValidationError,
        match="at least one record",
    ):
        load_notes_manifest(manifest_path)


def test_load_notes_manifest_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes.jsonl"
    manifest_path.write_text("{invalid json}\n", encoding="utf-8")

    with pytest.raises(
        NotesManifestValidationError,
        match="Invalid JSON at line 1",
    ):
        load_notes_manifest(manifest_path)


def test_load_notes_manifest_rejects_invalid_record(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes.jsonl"
    record = make_record()
    record["summary"] = ""
    record["reference_text"] = ""
    write_jsonl(manifest_path, [record])

    with pytest.raises(
        NotesManifestValidationError,
        match="Invalid record at line 1",
    ):
        load_notes_manifest(manifest_path)


def test_load_notes_manifest_rejects_empty_line(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes.jsonl"
    manifest_path.write_text(
        json.dumps(make_record(), ensure_ascii=False) + "\n\n",
        encoding="utf-8",
    )

    with pytest.raises(
        NotesManifestValidationError,
        match="empty line: 2",
    ):
        load_notes_manifest(manifest_path)