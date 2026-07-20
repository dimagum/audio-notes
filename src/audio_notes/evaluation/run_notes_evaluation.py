from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from audio_notes.evaluation.notes_evaluator import (
    NotesEvaluator,
    summarize_notes_results,
)
from audio_notes.evaluation.notes_reporters import write_notes_report
from audio_notes.evaluation.schemas import NotesManifestRecord
from audio_notes.notes.rule_based import RuleBasedNoteGenerator

_ENGINE_NAME = "rule_based"


def main() -> None:
    """Runs notes evaluation for the configured baseline."""
    args = _parse_args()

    output_dir = run_rule_based_notes_evaluation(
        manifest_path=args.manifest_path,
        output_root=args.output_root,
    )

    print(f"Notes evaluation report written to: {output_dir}")


def run_rule_based_notes_evaluation(
    *,
    manifest_path: Path,
    output_root: Path,
) -> Path:
    """Evaluates the rule-based generator and writes its reports."""
    records = _read_manifest(manifest_path)
    evaluator = NotesEvaluator(
        generator=RuleBasedNoteGenerator(),
    )

    results = evaluator.evaluate_records(records)
    summary = summarize_notes_results(results)
    output_dir = _make_output_dir(output_root)

    write_notes_report(
        output_dir=output_dir,
        results=results,
        summary=summary,
    )

    return output_dir


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the rule-based note generator "
            "on a notes JSONL manifest."
        ),
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path(
            "data/processed/eval/notes_test_manifest.jsonl"
        ),
        help="Path to a JSONL notes manifest.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("artifacts/reports/notes"),
        help="Directory where evaluation reports are stored.",
    )

    return parser.parse_args()


def _read_manifest(
    manifest_path: Path,
) -> list[NotesManifestRecord]:
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Notes manifest does not exist: {manifest_path}"
        )

    records = [
        NotesManifestRecord.model_validate_json(line)
        for line in manifest_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    if not records:
        raise ValueError("Notes manifest must contain records")

    return records


def _make_output_dir(
    output_root: Path,
) -> Path:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    return output_root / _ENGINE_NAME / timestamp


if __name__ == "__main__":
    main()