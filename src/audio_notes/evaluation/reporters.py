from __future__ import annotations

import csv
import json
from pathlib import Path

from audio_notes.evaluation.schemas import (
    AsrEvaluationSummary,
    AsrSampleResult,
)

_PER_SAMPLE_JSONL_FILENAME = "per_sample.jsonl"
_PER_SAMPLE_CSV_FILENAME = "per_sample.csv"
_SUMMARY_JSON_FILENAME = "summary.json"


def _serialize_sample_result(
    result: AsrSampleResult,
) -> dict[str, object]:
    payload = result.model_dump(mode="python")
    payload["audio_path"] = result.audio_path.as_posix()

    return payload


def write_asr_report(
    *,
    output_dir: Path,
    results: list[AsrSampleResult],
    summary: AsrEvaluationSummary,
) -> None:
    """Writes per-sample ASR results and an aggregate summary."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_per_sample_jsonl(
        output_path=output_dir / _PER_SAMPLE_JSONL_FILENAME,
        results=results,
    )
    _write_per_sample_csv(
        output_path=output_dir / _PER_SAMPLE_CSV_FILENAME,
        results=results,
    )
    _write_summary_json(
        output_path=output_dir / _SUMMARY_JSON_FILENAME,
        summary=summary,
    )


def _write_per_sample_jsonl(
    *,
    output_path: Path,
    results: list[AsrSampleResult],
) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        for result in results:
            payload = _serialize_sample_result(result)
            file.write(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                )
            )
            file.write("\n")


def _write_per_sample_csv(
    *,
    output_path: Path,
    results: list[AsrSampleResult],
) -> None:
    fieldnames = list(AsrSampleResult.model_fields)

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="raise",
        )
        writer.writeheader()

        for result in results:
            writer.writerow(_serialize_sample_result(result))


def _write_summary_json(
    *,
    output_path: Path,
    summary: AsrEvaluationSummary,
) -> None:
    output_path.write_text(
        summary.model_dump_json(
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )