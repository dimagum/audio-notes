from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from audio_notes.evaluation.schemas import AsrManifestRecord


class ManifestValidationError(ValueError):
    """Raised when an ASR evaluation manifest is invalid."""


def load_asr_manifest(manifest_path: Path) -> list[AsrManifestRecord]:
    """Loads and validates an ASR JSONL manifest."""
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Manifest file does not exist: {manifest_path}"
        )

    records: list[AsrManifestRecord] = []
    seen_ids: set[str] = set()

    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        try:
            record = AsrManifestRecord.model_validate_json(line)
        except ValidationError as error:
            raise ManifestValidationError(
                f"Invalid manifest record at line {line_number}: {error}"
            ) from error

        if record.id in seen_ids:
            raise ManifestValidationError(
                f"Duplicate record id '{record.id}' at line {line_number}."
            )

        if not record.audio_path.is_file():
            raise ManifestValidationError(
                f"Audio file does not exist for record '{record.id}': "
                f"{record.audio_path}"
            )

        seen_ids.add(record.id)
        records.append(record)

    if not records:
        raise ManifestValidationError(
            f"Manifest contains no non-empty records: {manifest_path}"
        )

    return records