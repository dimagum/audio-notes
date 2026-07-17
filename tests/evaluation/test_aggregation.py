from __future__ import annotations

import pytest

from audio_notes.evaluation.aggregation import (
    aggregate_asr_results,
    percentile,
)
from audio_notes.evaluation.schemas import AsrSampleResult


def make_result(
    *,
    record_id: str,
    audio_duration_seconds: float = 10.0,
    asr_seconds: float = 1.0,
    wer: float = 0.0,
    cer: float = 0.0,
    substitutions: int = 0,
    deletions: int = 0,
    insertions: int = 0,
    character_substitutions: int = 0,
    character_deletions: int = 0,
    character_insertions: int = 0,
    reference_word_count: int = 10,
    hypothesis_word_count: int = 10,
    reference_character_count: int = 50,
    hypothesis_character_count: int = 50,
    error: str | None = None,
) -> AsrSampleResult:
    return AsrSampleResult(
        id=record_id,
        audio_path=f"{record_id}.mp3",
        reference_text="эталон",
        hypothesis_text="гипотеза",
        audio_duration_seconds=audio_duration_seconds,
        asr_seconds=asr_seconds,
        asr_rtf=asr_seconds / audio_duration_seconds,
        wer=wer,
        cer=cer,
        substitutions=substitutions,
        deletions=deletions,
        insertions=insertions,
        character_substitutions=character_substitutions,
        character_deletions=character_deletions,
        character_insertions=character_insertions,
        reference_word_count=reference_word_count,
        hypothesis_word_count=hypothesis_word_count,
        reference_character_count=reference_character_count,
        hypothesis_character_count=hypothesis_character_count,
        error=error,
    )


def test_aggregate_asr_results_uses_corpus_level_metrics() -> None:
    results = [
        make_result(
            record_id="short",
            reference_word_count=1,
            substitutions=1,
            reference_character_count=4,
            character_substitutions=4,
            audio_duration_seconds=2.0,
            asr_seconds=0.2,
        ),
        make_result(
            record_id="long",
            reference_word_count=9,
            substitutions=0,
            reference_character_count=36,
            character_substitutions=0,
            audio_duration_seconds=18.0,
            asr_seconds=1.8,
        ),
    ]

    summary = aggregate_asr_results(results)

    assert summary.wer == pytest.approx(0.1)
    assert summary.cer == pytest.approx(0.1)
    assert summary.rtf_global == pytest.approx(0.1)
    assert summary.rtf_median == pytest.approx(0.1)
    assert summary.rtf_p95 == pytest.approx(0.1)


def test_aggregate_asr_results_ignores_failed_samples() -> None:
    results = [
        make_result(
            record_id="success",
            reference_word_count=10,
            substitutions=1,
            reference_character_count=50,
            character_substitutions=5,
            audio_duration_seconds=10.0,
            asr_seconds=1.0,
        ),
        make_result(
            record_id="failed",
            error="ffprobe failed",
            audio_duration_seconds=20.0,
            asr_seconds=2.0,
        ),
    ]

    summary = aggregate_asr_results(results)

    assert summary.n_total == 2
    assert summary.n_success == 1
    assert summary.n_failed == 1
    assert summary.wer == pytest.approx(0.1)
    assert summary.cer == pytest.approx(0.1)
    assert summary.audio_seconds_total == pytest.approx(10.0)
    assert summary.asr_seconds_total == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("values", "percent", "expected"),
    [
        ([1.0], 95, 1.0),
        ([1.0, 2.0, 3.0], 50, 2.0),
        ([1.0, 2.0, 3.0, 4.0], 95, 3.85),
    ],
)
def test_percentile(
    values: list[float],
    percent: float,
    expected: float,
) -> None:
    assert percentile(values, percent) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("values", "percent"),
    [
        ([], 95),
        ([1.0], -0.1),
        ([1.0], 100.1),
    ],
)
def test_percentile_rejects_invalid_arguments(
    values: list[float],
    percent: float,
) -> None:
    with pytest.raises(ValueError):
        percentile(values, percent)


def test_aggregate_asr_results_rejects_empty_results() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        aggregate_asr_results([])


def test_aggregate_asr_results_rejects_all_failed_results() -> None:
    results = [make_result(record_id="failed", error="ASR error")]

    with pytest.raises(ValueError, match="at least one result"):
        aggregate_asr_results(results)