from __future__ import annotations

import json
from pathlib import Path

import pytest

from audio_notes.evaluation.manifest import (
    ManifestValidationError,
    load_asr_manifest,
)


def write_manifest(path: Path, records: list[dict]) -> None:
    lines = [
        json.dumps(record, ensure_ascii=False)
        for record in records
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def make_valid_record(audio_path: Path, record_id: str = "sample_001") -> dict:
    return {
        "id": record_id,
        "source": "Test source",
        "split": "test",
        "audio_path": str(audio_path),
        "reference_text": "тестовая фраза",
    }


def test_load_asr_manifest_returns_valid_records(tmp_path: Path) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    manifest_path = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest_path,
        [
            make_valid_record(audio_path, "sample_001"),
            make_valid_record(audio_path, "sample_002"),
        ],
    )

    records = load_asr_manifest(manifest_path)

    assert [record.id for record in records] == [
        "sample_001",
        "sample_002",
    ]


def test_load_asr_manifest_ignores_empty_lines(tmp_path: Path) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    manifest_path = tmp_path / "manifest.jsonl"
    valid_line = json.dumps(
        make_valid_record(audio_path),
        ensure_ascii=False,
    )
    manifest_path.write_text(
        f"\n{valid_line}\n\n",
        encoding="utf-8",
    )

    records = load_asr_manifest(manifest_path)

    assert len(records) == 1


def test_load_asr_manifest_rejects_missing_manifest(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_asr_manifest(manifest_path)


def test_load_asr_manifest_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    manifest_path.write_text("{invalid json}", encoding="utf-8")

    with pytest.raises(
        ManifestValidationError,
        match="line 1",
    ):
        load_asr_manifest(manifest_path)


def test_load_asr_manifest_rejects_invalid_schema(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    manifest_path.write_text(
        json.dumps({"id": "sample_001"}),
        encoding="utf-8",
    )

    with pytest.raises(
        ManifestValidationError,
        match="line 1",
    ):
        load_asr_manifest(manifest_path)


def test_load_asr_manifest_rejects_duplicate_ids(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    manifest_path = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest_path,
        [
            make_valid_record(audio_path, "duplicate"),
            make_valid_record(audio_path, "duplicate"),
        ],
    )

    with pytest.raises(
        ManifestValidationError,
        match="Duplicate record id 'duplicate'",
    ):
        load_asr_manifest(manifest_path)


def test_load_asr_manifest_rejects_missing_audio(
    tmp_path: Path,
) -> None:
    missing_audio_path = tmp_path / "missing.mp3"

    manifest_path = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest_path,
        [make_valid_record(missing_audio_path)],
    )

    with pytest.raises(
        ManifestValidationError,
        match="Audio file does not exist",
    ):
        load_asr_manifest(manifest_path)


def test_load_asr_manifest_rejects_empty_manifest(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    manifest_path.write_text("\n  \n", encoding="utf-8")

    with pytest.raises(
        ManifestValidationError,
        match="contains no non-empty records",
    ):
        load_asr_manifest(manifest_path)