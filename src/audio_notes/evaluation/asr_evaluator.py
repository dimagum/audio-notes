from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from audio_notes.asr.base import Transcriber
from audio_notes.evaluation.asr_metrics import calculate_asr_metrics
from audio_notes.evaluation.audio_duration import get_audio_duration_seconds
from audio_notes.evaluation.schemas import (
    AsrManifestRecord,
    AsrSampleResult,
)
from audio_notes.evaluation.timing import measure_inference


class AsrEvaluator:
    """Evaluates one ASR transcriber on manifest records."""

    def __init__(
        self,
        transcriber: Transcriber,
        duration_getter: Callable[[Path], float] = get_audio_duration_seconds,
    ) -> None:
        self._transcriber = transcriber
        self._duration_getter = duration_getter

    def evaluate_record(
        self,
        record: AsrManifestRecord,
    ) -> AsrSampleResult:
        """Runs ASR, calculates metrics, and returns a result for one record."""
        audio_duration_seconds = 0.0

        try:
            audio_duration_seconds = self._duration_getter(record.audio_path)

            hypothesis_text, timing = measure_inference(
                self._transcriber.transcribe,
                record.audio_path,
                audio_duration_seconds=audio_duration_seconds,
            )

            metrics = calculate_asr_metrics(
                reference=record.reference_text,
                hypothesis=hypothesis_text,
            )

            return AsrSampleResult(
                id=record.id,
                audio_path=record.audio_path,
                reference_text=record.reference_text,
                hypothesis_text=hypothesis_text,
                audio_duration_seconds=audio_duration_seconds,
                asr_seconds=timing.elapsed_seconds,
                asr_rtf=timing.rtf,
                wer=metrics.wer,
                cer=metrics.cer,
                substitutions=metrics.substitutions,
                deletions=metrics.deletions,
                insertions=metrics.insertions,
                character_substitutions=metrics.character_substitutions,
                character_deletions=metrics.character_deletions,
                character_insertions=metrics.character_insertions,
                reference_word_count=metrics.reference_word_count,
                hypothesis_word_count=metrics.hypothesis_word_count,
                reference_character_count=metrics.reference_character_count,
                hypothesis_character_count=metrics.hypothesis_character_count,
                error=None,
            )
        except Exception as error:
            return self._build_failed_result(
                record=record,
                audio_duration_seconds=audio_duration_seconds,
                error=error,
            )

    def evaluate_records(
        self,
        records: list[AsrManifestRecord],
    ) -> list[AsrSampleResult]:
        """Evaluates all records without stopping after an individual failure."""
        return [
            self.evaluate_record(record)
            for record in records
        ]

    @staticmethod
    def _build_failed_result(
        *,
        record: AsrManifestRecord,
        audio_duration_seconds: float,
        error: Exception,
    ) -> AsrSampleResult:
        return AsrSampleResult(
            id=record.id,
            audio_path=record.audio_path,
            reference_text=record.reference_text,
            hypothesis_text="",
            audio_duration_seconds=audio_duration_seconds,
            asr_seconds=0.0,
            asr_rtf=0.0,
            wer=0.0,
            cer=0.0,
            substitutions=0,
            deletions=0,
            insertions=0,
            character_substitutions=0,
            character_deletions=0,
            character_insertions=0,
            reference_word_count=0,
            hypothesis_word_count=0,
            reference_character_count=0,
            hypothesis_character_count=0,
            error=f"{type(error).__name__}: {error}",
        )