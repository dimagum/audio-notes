from __future__ import annotations

import csv
import json
from pathlib import Path

from audio_notes.evaluation.notes_reporters import write_notes_report
from audio_notes.evaluation.schemas import (
    NotesEvaluationSummary,
    NotesSampleResult,
)
from audio_notes.notes.schemas import GeneratedNote


def make_note() -> GeneratedNote:
    return GeneratedNote(
        title="Как технологии меняют образование",
        summary=(
            "Спикер объясняет влияние цифровых инструментов "
            "на доступ к образованию."
        ),
        key_points=[
            "Цифровые инструменты расширяют доступ к обучению.",
            "Преподаватель остаётся наставником.",
        ],
        action_items=[],
        open_questions=[
            "Как сохранить качество обучения при масштабировании?",
        ],
    )


def make_sample_result(
    *,
    record_id: str,
    error: str | None = None,
) -> NotesSampleResult:
    return NotesSampleResult(
        id=record_id,
        source="Test source",
        split="test",
        domain="general",
        reference_text="Полный текст тестового выступления.",
        generated_note=None if error is not None else make_note(),
        generation_seconds=1.25 if error is None else 0.5,
        error=error,
    )


def make_summary() -> NotesEvaluationSummary:
    return NotesEvaluationSummary(
        n_total=2,
        n_success=1,
        n_failed=1,
        generation_seconds_total=1.75,
    )


def test_write_notes_report_creates_all_files(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "reports" / "run_001"

    write_notes_report(
        output_dir=output_dir,
        results=[
            make_sample_result(record_id="success"),
            make_sample_result(
                record_id="failed",
                error="RuntimeError: generation failed",
            ),
        ],
        summary=make_summary(),
    )

    assert (output_dir / "per_sample.jsonl").is_file()
    assert (output_dir / "per_sample.csv").is_file()
    assert (output_dir / "summary.json").is_file()


def test_write_notes_report_writes_jsonl_and_summary(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "run_001"

    write_notes_report(
        output_dir=output_dir,
        results=[make_sample_result(record_id="success")],
        summary=make_summary(),
    )

    jsonl_lines = (
        output_dir / "per_sample.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    summary = json.loads(
        (output_dir / "summary.json").read_text(encoding="utf-8")
    )
    result = json.loads(jsonl_lines[0])

    assert len(jsonl_lines) == 1
    assert result["id"] == "success"
    assert result["generated_note"]["title"] == (
        "Как технологии меняют образование"
    )
    assert result["generated_note"]["key_points"] == [
        "Цифровые инструменты расширяют доступ к обучению.",
        "Преподаватель остаётся наставником.",
    ]
    assert summary["n_total"] == 2
    assert summary["generation_seconds_total"] == 1.75


def test_write_notes_report_writes_flat_csv(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "run_001"

    write_notes_report(
        output_dir=output_dir,
        results=[
            make_sample_result(record_id="success"),
            make_sample_result(
                record_id="failed",
                error="RuntimeError: generation failed",
            ),
        ],
        summary=make_summary(),
    )

    with (output_dir / "per_sample.csv").open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert [row["id"] for row in rows] == ["success", "failed"]
    assert rows[0]["title"] == "Как технологии меняют образование"
    assert json.loads(rows[0]["key_points"]) == [
        "Цифровые инструменты расширяют доступ к обучению.",
        "Преподаватель остаётся наставником.",
    ]
    assert rows[0]["error"] == ""
    assert rows[1]["title"] == ""
    assert rows[1]["key_points"] == "[]"
    assert rows[1]["error"] == "RuntimeError: generation failed"


def test_write_notes_report_overwrites_existing_files(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "run_001"

    write_notes_report(
        output_dir=output_dir,
        results=[make_sample_result(record_id="old")],
        summary=make_summary(),
    )
    write_notes_report(
        output_dir=output_dir,
        results=[make_sample_result(record_id="new")],
        summary=make_summary(),
    )

    lines = (
        output_dir / "per_sample.jsonl"
    ).read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1
    assert json.loads(lines[0])["id"] == "new"