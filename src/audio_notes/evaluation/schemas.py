from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


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

    audio_duration_seconds: float = Field(ge=0)
    asr_seconds: float = Field(ge=0)
    asr_rtf: float = Field(ge=0)

    wer: float = Field(ge=0)
    cer: float = Field(ge=0)

    substitutions: int = Field(ge=0)
    deletions: int = Field(ge=0)
    insertions: int = Field(ge=0)

    reference_word_count: int = Field(ge=0)
    hypothesis_word_count: int = Field(ge=0)

    character_substitutions: int = Field(ge=0)
    character_deletions: int = Field(ge=0)
    character_insertions: int = Field(ge=0)

    reference_character_count: int = Field(ge=0)
    hypothesis_character_count: int = Field(ge=0)

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


class NoteSegment(BaseModel):
    """One time-aligned reference-transcript segment."""

    segment_id: str = Field(min_length=1)
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_time_range(self) -> "NoteSegment":
        if self.end_seconds <= self.start_seconds:
            raise ValueError(
                "end_seconds must be greater than start_seconds"
            )

        return self


class NotesManifestRecord(BaseModel):
    """One fixed example for transcript-to-notes evaluation."""

    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    split: str = Field(min_length=1)
    audio_path: Path
    reference_text: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    segments: list[NoteSegment] = Field(min_length=1)
    n_segments: int = Field(gt=0)
    duration_seconds: float = Field(gt=0)
    domain: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_segments(self) -> "NotesManifestRecord":
        if self.n_segments != len(self.segments):
            raise ValueError(
                "n_segments must match the number of segments"
            )

        latest_segment_end = max(
            segment.end_seconds
            for segment in self.segments
        )
        if latest_segment_end > self.duration_seconds:
            raise ValueError(
                "segment end time must not exceed duration_seconds"
            )

        return self