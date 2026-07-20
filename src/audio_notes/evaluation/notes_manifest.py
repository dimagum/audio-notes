from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from audio_notes.evaluation.schemas import NotesManifestRecord


class NotesManifestValidationError(ValueError):
    """Raised when a notes evaluation manifest is invalid."""


def load_notes_manifest(
    manifest_path: Path,
) -> list[NotesManifestRecord]:
    """Loads and validates records from a notes JSONL manifest."""
    if not manifest_path.is_file():
        raise NotesManifestValidationError(
            f"Manifest file does not exist: {manifest_path}"
        )

    records: list[NotesManifestRecord] = []

    with manifest_path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped_line = line.strip()

            if not stripped_line:
                raise NotesManifestValidationError(
                    f"Manifest contains an empty line: {line_number}"
                )

            try:
                payload = json.loads(stripped_line)
            except json.JSONDecodeError as error:
                raise NotesManifestValidationError(
                    f"Invalid JSON at line {line_number}"
                ) from error

            try:
                record = NotesManifestRecord.model_validate(payload)
            except ValidationError as error:
                raise NotesManifestValidationError(
                    f"Invalid record at line {line_number}: {error}"
                ) from error

            records.append(record)

    if not records:
        raise NotesManifestValidationError(
            "Manifest must contain at least one record"
        )

    return records