from __future__ import annotations

from dataclasses import dataclass

import jiwer

from audio_notes.evaluation.normalization import normalize_for_asr


@dataclass(frozen=True)
class AsrMetrics:
    wer: float
    cer: float

    substitutions: int
    deletions: int
    insertions: int

    character_substitutions: int
    character_deletions: int
    character_insertions: int

    reference_word_count: int
    hypothesis_word_count: int
    reference_character_count: int
    hypothesis_character_count: int


def calculate_asr_metrics(reference: str, hypothesis: str) -> AsrMetrics:
    """Calculates normalized WER/CER and edit operations for one ASR output."""
    normalized_reference = normalize_for_asr(reference)
    normalized_hypothesis = normalize_for_asr(hypothesis)

    word_output = jiwer.process_words(
        normalized_reference,
        normalized_hypothesis,
    )
    character_output = jiwer.process_characters(
        normalized_reference,
        normalized_hypothesis,
    )

    return AsrMetrics(
        wer=word_output.wer,
        cer=character_output.cer,
        substitutions=word_output.substitutions,
        deletions=word_output.deletions,
        insertions=word_output.insertions,
        reference_word_count=len(normalized_reference.split()),
        hypothesis_word_count=len(normalized_hypothesis.split()),
        character_substitutions=character_output.substitutions,
        character_deletions=character_output.deletions,
        character_insertions=character_output.insertions,
        reference_character_count=len(normalized_reference),
        hypothesis_character_count=len(normalized_hypothesis),
    )