from __future__ import annotations

from statistics import median

from audio_notes.evaluation.schemas import (
    AsrEvaluationSummary,
    AsrSampleResult,
)


def percentile(values: list[float], percent: float) -> float:
    """Returns a linearly interpolated percentile for non-empty values."""
    if not values:
        raise ValueError("values must not be empty")

    if not 0 <= percent <= 100:
        raise ValueError("percent must be in range [0, 100]")

    sorted_values = sorted(values)

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (len(sorted_values) - 1) * percent / 100
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = position - lower_index

    return (
        sorted_values[lower_index]
        + (sorted_values[upper_index] - sorted_values[lower_index]) * fraction
    )


def aggregate_asr_results(
    results: list[AsrSampleResult],
) -> AsrEvaluationSummary:
    """Aggregates successful ASR sample results into corpus-level metrics."""
    if not results:
        raise ValueError("results must not be empty")

    successful_results = [
        result
        for result in results
        if result.error is None
    ]

    if not successful_results:
        raise ValueError("at least one result must be successful")

    n_total = len(results)
    n_success = len(successful_results)

    word_errors = sum(
        result.substitutions + result.deletions + result.insertions
        for result in successful_results
    )
    reference_words = sum(
        result.reference_word_count
        for result in successful_results
    )

    character_errors = sum(
        result.character_substitutions
        + result.character_deletions
        + result.character_insertions
        for result in successful_results
    )
    reference_characters = sum(
        result.reference_character_count
        for result in successful_results
    )

    total_audio_seconds = sum(
        result.audio_duration_seconds
        for result in successful_results
    )
    total_asr_seconds = sum(
        result.asr_seconds
        for result in successful_results
    )
    rtfs = [result.asr_rtf for result in successful_results]

    wer = word_errors / reference_words if reference_words else 0.0
    cer = character_errors / reference_characters if reference_characters else 0.0

    return AsrEvaluationSummary(
        n_total=n_total,
        n_success=n_success,
        n_failed=n_total - n_success,
        wer=wer,
        cer=cer,
        audio_seconds_total=total_audio_seconds,
        asr_seconds_total=total_asr_seconds,
        rtf_global=total_asr_seconds / total_audio_seconds,
        rtf_median=median(rtfs),
        rtf_p95=percentile(rtfs, 95),
    )