from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class TimingResult:
    """Execution time and real-time factor for one audio sample."""

    elapsed_seconds: float
    audio_duration_seconds: float
    rtf: float


def calculate_rtf(
    elapsed_seconds: float,
    audio_duration_seconds: float,
) -> float:
    """Calculates the real-time factor for an ASR inference."""
    if elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be non-negative")

    if audio_duration_seconds <= 0:
        raise ValueError("audio_duration_seconds must be positive")

    return elapsed_seconds / audio_duration_seconds


def measure_inference(
    function: Callable[..., T],
    *args: object,
    audio_duration_seconds: float,
    **kwargs: object,
) -> tuple[T, TimingResult]:
    """Runs an inference function and measures only its execution time."""
    started_at = perf_counter()
    result = function(*args, **kwargs)
    elapsed_seconds = perf_counter() - started_at

    timing = TimingResult(
        elapsed_seconds=elapsed_seconds,
        audio_duration_seconds=audio_duration_seconds,
        rtf=calculate_rtf(
            elapsed_seconds=elapsed_seconds,
            audio_duration_seconds=audio_duration_seconds,
        ),
    )

    return result, timing