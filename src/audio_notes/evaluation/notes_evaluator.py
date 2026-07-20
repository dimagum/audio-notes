from __future__ import annotations

from time import perf_counter

from audio_notes.evaluation.schemas import (
    NotesEvaluationSummary,
    NotesManifestRecord,
    NotesSampleResult,
)
from audio_notes.notes.base import NoteGenerator


class NotesEvaluator:
    """Runs a note generator for notes-manifest records."""

    def __init__(
        self,
        generator: NoteGenerator,
    ) -> None:
        self._generator = generator

    def evaluate_record(
        self,
        record: NotesManifestRecord,
    ) -> NotesSampleResult:
        """Generates one note and captures a per-record failure."""
        started_at = perf_counter()

        try:
            generated_note = self._generator.generate(
                record.reference_text
            )
            generation_seconds = perf_counter() - started_at

            return NotesSampleResult(
                id=record.id,
                source=record.source,
                split=record.split,
                domain=record.domain,
                reference_text=record.reference_text,
                generated_note=generated_note,
                generation_seconds=generation_seconds,
                error=None,
            )
        except Exception as error:
            generation_seconds = perf_counter() - started_at

            return NotesSampleResult(
                id=record.id,
                source=record.source,
                split=record.split,
                domain=record.domain,
                reference_text=record.reference_text,
                generated_note=None,
                generation_seconds=generation_seconds,
                error=f"{type(error).__name__}: {error}",
            )

    def evaluate_records(
        self,
        records: list[NotesManifestRecord],
    ) -> list[NotesSampleResult]:
        """Evaluates all records without stopping after a failure."""
        return [
            self.evaluate_record(record)
            for record in records
        ]


def summarize_notes_results(
    results: list[NotesSampleResult],
) -> NotesEvaluationSummary:
    """Summarizes the completion and latency of a notes run."""
    if not results:
        raise ValueError("results must not be empty")

    n_total = len(results)
    n_success = sum(
        result.error is None
        for result in results
    )

    return NotesEvaluationSummary(
        n_total=n_total,
        n_success=n_success,
        n_failed=n_total - n_success,
        generation_seconds_total=sum(
            result.generation_seconds
            for result in results
        ),
    )