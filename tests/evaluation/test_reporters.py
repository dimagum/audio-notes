from __future__ import annotations

import csv
import json
from pathlib import Path

from audio_notes.evaluation.reporters import write_asr_report
from audio_notes.evaluation.schemas import (
    AsrEvaluationSummary,
    AsrSampleResult,
)


def make_sample_result(
    *,
    record_id: str,
    error: str | None = None,
) -> AsrSampleResult:
    return AsrSampleResult(
        id=record_id,
        audio_path=Path(f"audio/{record_id}.mp3"),
        reference_text="эталонный текст",
        hypothesis_text="распознанный текст" if error is None else "",
        audio_duration_seconds=10.0,
        asr_seconds=1.0 if error is None else 0.0,
        asr_rtf=0.1 if error is None else 0.0,
        wer=0.2 if error is None else 0.0,
        cer=0.1 if error is None else 0.0,
        substitutions=1 if error is None else 0,
        deletions=0,
        insertions=1 if error is None else 0,
        character_substitutions=2 if error is None else 0,
        character_deletions=0,
        character_insertions=1 if error is None else 0,
        reference_word_count=2 if error is None else 0,
        hypothesis_word_count=2 if error is None else 0,
        reference_character_count=15 if error is None else 0,
        hypothesis_character_count=16 if error is None else 0,
        error=error,
    )


def make_summary() -> AsrEvaluationSummary:
    return AsrEvaluationSummary(
        n_total=2,
        n_success=1,
        n_failed=1,
        wer=0.2,
        cer=0.1,
        audio_seconds_total=10.0,
        asr_seconds_total=1.0,
        rtf_global=0.1,
        rtf_median=0.1,
        rtf_p95=0.1,
    )


def test_write_asr_report_creates_all_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports" / "run_001"

    write_asr_report(
        output_dir=output_dir,
        results=[
            make_sample_result(record_id="sample_001"),
            make_sample_result(
                record_id="sample_002",
                error="RuntimeError: ASR failed",
            ),
        ],
        summary=make_summary(),
    )

    assert (output_dir / "per_sample.jsonl").is_file()
    assert (output_dir / "per_sample.csv").is_file()
    assert (output_dir / "summary.json").is_file()


def test_write_asr_report_writes_valid_jsonl_and_summary(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "run_001"

    write_asr_report(
        output_dir=output_dir,
        results=[make_sample_result(record_id="sample_001")],
        summary=make_summary(),
    )

    jsonl_lines = (
        output_dir / "per_sample.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    summary = json.loads(
        (output_dir / "summary.json").read_text(encoding="utf-8")
    )

    assert len(jsonl_lines) == 1
    assert json.loads(jsonl_lines[0])["id"] == "sample_001"
    assert json.loads(jsonl_lines[0])["audio_path"] == "audio/sample_001.mp3"

    assert summary["n_total"] == 2
    assert summary["wer"] == 0.2


def test_write_asr_report_writes_csv_with_all_results(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "run_001"

    write_asr_report(
        output_dir=output_dir,
        results=[
            make_sample_result(record_id="sample_001"),
            make_sample_result(
                record_id="sample_002",
                error="RuntimeError: ASR failed",
            ),
        ],
        summary=make_summary(),
    )

    with (output_dir / "per_sample.csv").open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert [row["id"] for row in rows] == [
        "sample_001",
        "sample_002",
    ]
    assert rows[0]["audio_path"] == "audio/sample_001.mp3"
    assert rows[0]["wer"] == "0.2"
    assert rows[1]["error"] == "RuntimeError: ASR failed"


def test_write_asr_report_overwrites_existing_files(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "run_001"

    write_asr_report(
        output_dir=output_dir,
        results=[make_sample_result(record_id="old")],
        summary=make_summary(),
    )
    write_asr_report(
        output_dir=output_dir,
        results=[make_sample_result(record_id="new")],
        summary=make_summary(),
    )

    rows = (
        output_dir / "per_sample.jsonl"
    ).read_text(encoding="utf-8").splitlines()

    assert len(rows) == 1
    assert json.loads(rows[0])["id"] == "new"