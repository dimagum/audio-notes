from __future__ import annotations

from audio_notes.evaluation.notes_evaluator import (
    NotesEvaluator,
    summarize_notes_results,
)
from audio_notes.evaluation.schemas import (
    NotesManifestRecord,
    NotesSampleResult,
)
from audio_notes.notes.mock import MockNoteGenerator
from audio_notes.notes.schemas import GeneratedNote


def make_record(
    *,
    record_id: str,
    transcript: str,
) -> NotesManifestRecord:
    return NotesManifestRecord(
        id=record_id,
        source="Test source",
        split="test",
        audio_path=f"data/audio/{record_id}.flac",
        reference_text=transcript,
        segments=[
            {
                "segment_id": f"{record_id}_0000",
                "start_seconds": 0.0,
                "end_seconds": 2.0,
                "text": transcript,
            }
        ],
        n_segments=1,
        duration_seconds=2.0,
        domain="general",
    )


def make_note(
    *,
    title: str = "Тестовая заметка",
) -> GeneratedNote:
    return GeneratedNote(
        title=title,
        summary="Краткое содержание выступления.",
        key_points=["Первый ключевой тезис."],
    )


def test_evaluate_record_returns_generated_note() -> None:
    record = make_record(
        record_id="record_001",
        transcript="Первый текст.",
    )
    expected_note = make_note(title="Первый доклад")
    generator = MockNoteGenerator(
        {
            record.reference_text: expected_note,
        }
    )
    evaluator = NotesEvaluator(generator=generator)

    result = evaluator.evaluate_record(record)

    assert result.id == "record_001"
    assert result.error is None
    assert result.generated_note == expected_note
    assert result.generation_seconds >= 0.0
    assert generator.calls == ["Первый текст."]


def test_evaluate_record_returns_error_result_when_generation_fails() -> None:
    record = make_record(
        record_id="record_001",
        transcript="Текст без настройки.",
    )
    evaluator = NotesEvaluator(generator=MockNoteGenerator({}))

    result = evaluator.evaluate_record(record)

    assert result.id == "record_001"
    assert result.generated_note is None
    assert result.error is not None
    assert "KeyError" in result.error
    assert result.generation_seconds >= 0.0


def test_evaluate_records_processes_all_records() -> None:
    first_record = make_record(
        record_id="first",
        transcript="Первый текст.",
    )
    second_record = make_record(
        record_id="second",
        transcript="Второй текст.",
    )
    generator = MockNoteGenerator(
        {
            first_record.reference_text: make_note(
                title="Первый доклад"
            ),
            second_record.reference_text: make_note(
                title="Второй доклад"
            ),
        }
    )
    evaluator = NotesEvaluator(generator=generator)

    results = evaluator.evaluate_records(
        [first_record, second_record]
    )

    assert [result.id for result in results] == ["first", "second"]
    assert all(result.error is None for result in results)
    assert generator.calls == [
        "Первый текст.",
        "Второй текст.",
    ]


def test_summarize_notes_results_counts_successes_and_failures() -> None:
    results = [
        NotesSampleResult(
            id="success",
            source="Test source",
            split="test",
            domain="general",
            reference_text="Текст.",
            generated_note=make_note(),
            generation_seconds=1.5,
            error=None,
        ),
        NotesSampleResult(
            id="failed",
            source="Test source",
            split="test",
            domain="general",
            reference_text="Другой текст.",
            generated_note=None,
            generation_seconds=0.5,
            error="RuntimeError: generation failed",
        ),
    ]

    summary = summarize_notes_results(results)

    assert summary.n_total == 2
    assert summary.n_success == 1
    assert summary.n_failed == 1
    assert summary.generation_seconds_total == 2.0