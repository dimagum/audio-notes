from __future__ import annotations

from unittest.mock import patch

import pytest

from audio_notes.evaluation.timing import calculate_rtf, measure_inference


@pytest.mark.parametrize(
    ("elapsed_seconds", "audio_duration_seconds", "expected_rtf"),
    [
        (1.0, 10.0, 0.1),
        (10.0, 10.0, 1.0),
        (0.0, 10.0, 0.0),
        (2.5, 5.0, 0.5),
    ],
)
def test_calculate_rtf(
    elapsed_seconds: float,
    audio_duration_seconds: float,
    expected_rtf: float,
) -> None:
    assert calculate_rtf(
        elapsed_seconds=elapsed_seconds,
        audio_duration_seconds=audio_duration_seconds,
    ) == pytest.approx(expected_rtf)


@pytest.mark.parametrize(
    ("elapsed_seconds", "audio_duration_seconds"),
    [
        (-0.1, 10.0),
        (1.0, 0.0),
        (1.0, -1.0),
    ],
)
def test_calculate_rtf_rejects_invalid_values(
    elapsed_seconds: float,
    audio_duration_seconds: float,
) -> None:
    with pytest.raises(ValueError):
        calculate_rtf(elapsed_seconds, audio_duration_seconds)


def test_measure_inference_returns_function_result_and_timing() -> None:
    with patch(
        "audio_notes.evaluation.timing.perf_counter",
        side_effect=[100.0, 100.25],
    ):
        result, timing = measure_inference(
            lambda value: value.upper(),
            "hello",
            audio_duration_seconds=5.0,
        )

    assert result == "HELLO"
    assert timing.elapsed_seconds == pytest.approx(0.25)
    assert timing.audio_duration_seconds == pytest.approx(5.0)
    assert timing.rtf == pytest.approx(0.05)


def test_measure_inference_propagates_function_error() -> None:
    def raise_error() -> None:
        raise RuntimeError("ASR failed")

    with pytest.raises(RuntimeError, match="ASR failed"):
        measure_inference(
            raise_error,
            audio_duration_seconds=1.0,
        )