from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class AsrManifestRecord(BaseModel):
    """One input record from an ASR evaluation manifest."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    split: str = Field(min_length=1)
    audio_path: Path
    reference_text: str


class AsrSampleResult(BaseModel):
    """ASR output, quality metrics, and inference timing for one audio file."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    audio_path: Path
    reference_text: str
    hypothesis_text: str

    audio_duration_seconds: float = Field(gt=0)
    asr_seconds: float = Field(ge=0)
    asr_rtf: float = Field(ge=0)

    wer: float = Field(ge=0)
    cer: float = Field(ge=0)

    substitutions: int = Field(ge=0)
    deletions: int = Field(ge=0)
    insertions: int = Field(ge=0)

    reference_word_count: int = Field(ge=0)
    hypothesis_word_count: int = Field(ge=0)

    error: str | None = None


class AsrEvaluationSummary(BaseModel):
    """Aggregate metrics for one ASR evaluation run."""

    model_config = ConfigDict(extra="forbid")

    n_total: int = Field(ge=0)
    n_success: int = Field(ge=0)
    n_failed: int = Field(ge=0)

    wer: float = Field(ge=0)
    cer: float = Field(ge=0)

    audio_seconds_total: float = Field(ge=0)
    asr_seconds_total: float = Field(ge=0)
    rtf_global: float = Field(ge=0)
    rtf_median: float = Field(ge=0)
    rtf_p95: float = Field(ge=0)