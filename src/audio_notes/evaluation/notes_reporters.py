from __future__ import annotations

import csv
import json
from pathlib import Path

from audio_notes.evaluation.schemas import (
    NotesEvaluationSummary,
    NotesSampleResult,
)

_PER_SAMPLE_JSONL_FILENAME = "per_sample.jsonl"
_PER_SAMPLE_CSV_FILENAME = "per_sample.csv"
_SUMMARY_JSON_FILENAME = "summary.json"

_CSV_FIELDNAMES = [
    "id",
    "source",
    "split",
    "domain",
    "reference_text",
    "title",
    "summary",
    "key_points",
    "action_items",
    "open_questions",
    "generation_seconds",
    "error",
]


def write_notes_report(
    *,
    output_dir: Path,
    results: list[NotesSampleResult],
    summary: NotesEvaluationSummary,
) -> None:
    """Writes per-sample notes results and aggregate summary."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_per_sample_jsonl(
        output_path=output_dir / _PER_SAMPLE_JSONL_FILENAME,
        results=results,
    )
    _write_per_sample_csv(
        output_path=output_dir / _PER_SAMPLE_CSV_FILENAME,
        results=results,
    )
    _write_summary_json(
        output_path=output_dir / _SUMMARY_JSON_FILENAME,
        summary=summary,
    )


def _write_per_sample_jsonl(
    *,
    output_path: Path,
    results: list[NotesSampleResult],
) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        for result in results:
            file.write(
                result.model_dump_json(
                    exclude_none=True,
                )
            )
            file.write("\n")


def _write_per_sample_csv(
    *,
    output_path: Path,
    results: list[NotesSampleResult],
) -> None:
    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=_CSV_FIELDNAMES,
            extrasaction="raise",
        )
        writer.writeheader()

        for result in results:
            writer.writerow(_serialize_result_for_csv(result))


def _serialize_result_for_csv(
    result: NotesSampleResult,
) -> dict[str, object]:
    row: dict[str, object] = {
        "id": result.id,
        "source": result.source,
        "split": result.split,
        "domain": result.domain,
        "reference_text": result.reference_text,
        "title": "",
        "summary": "",
        "key_points": "[]",
        "action_items": "[]",
        "open_questions": "[]",
        "generation_seconds": result.generation_seconds,
        "error": result.error or "",
    }

    if result.generated_note is not None:
        note = result.generated_note
        row.update(
            {
                "title": note.title,
                "summary": note.summary,
                "key_points": json.dumps(
                    note.key_points,
                    ensure_ascii=False,
                ),
                "action_items": json.dumps(
                    note.action_items,
                    ensure_ascii=False,
                ),
                "open_questions": json.dumps(
                    note.open_questions,
                    ensure_ascii=False,
                ),
            }
        )

    return row


def _write_summary_json(
    *,
    output_path: Path,
    summary: NotesEvaluationSummary,
) -> None:
    output_path.write_text(
        summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )