from __future__ import annotations

import json
from pathlib import Path

import pytest

from audio_notes.evaluation.run_notes_evaluation import (
    run_rule_based_notes_evaluation,
)


def write_manifest(
    manifest_path: Path,
) -> None:
    records = [
        {
            "id": "talk_001",
            "source": "Test source",
            "split": "test",
            "audio_path": "data/audio/talk_001.flac",
            "reference_text": (
                "Первое предложение выступления. "
                "Второе предложение выступления. "
                "Третье предложение выступления."
            ),
            "segments": [
                {
                    "segment_id": "talk_001_0000",
                    "start_seconds": 0.0,
                    "end_seconds": 3.0,
                    "text": (
                        "Первое предложение выступления. "
                        "Второе предложение выступления. "
                        "Третье предложение выступления."
                    ),
                }
            ],
            "n_segments": 1,
            "duration_seconds": 3.0,
            "domain": "general",
        },
        {
            "id": "talk_002",
            "source": "Test source",
            "split": "test",
            "audio_path": "data/audio/talk_002.flac",
            "reference_text": (
                "Другое первое предложение. "
                "Другое второе предложение."
            ),
            "segments": [
                {
                    "segment_id": "talk_002_0000",
                    "start_seconds": 0.0,
                    "end_seconds": 2.0,
                    "text": (
                        "Другое первое предложение. "
                        "Другое второе предложение."
                    ),
                }
            ],
            "n_segments": 1,
            "duration_seconds": 2.0,
            "domain": "general",
        },
    ]

    manifest_path.write_text(
        "".join(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


def test_run_rule_based_notes_evaluation_writes_reports(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes_manifest.jsonl"
    output_root = tmp_path / "reports"
    write_manifest(manifest_path)

    output_dir = run_rule_based_notes_evaluation(
        manifest_path=manifest_path,
        output_root=output_root,
    )

    assert output_dir.parent.name == "rule_based"
    assert (output_dir / "per_sample.jsonl").is_file()
    assert (output_dir / "per_sample.csv").is_file()
    assert (output_dir / "summary.json").is_file()

    summary = json.loads(
        (output_dir / "summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["n_total"] == 2
    assert summary["n_success"] == 2
    assert summary["n_failed"] == 0


def test_run_rule_based_notes_evaluation_writes_notes(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes_manifest.jsonl"
    write_manifest(manifest_path)

    output_dir = run_rule_based_notes_evaluation(
        manifest_path=manifest_path,
        output_root=tmp_path / "reports",
    )

    lines = (
        output_dir / "per_sample.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    first_result = json.loads(lines[0])

    assert len(lines) == 2
    assert first_result["id"] == "talk_001"
    assert "error" not in first_result
    assert first_result["generated_note"]["title"] == (
        "Первое предложение выступления"
    )


def test_run_rule_based_notes_evaluation_rejects_missing_manifest(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Notes manifest does not exist",
    ):
        run_rule_based_notes_evaluation(
            manifest_path=tmp_path / "missing.jsonl",
            output_root=tmp_path / "reports",
        )


def test_run_rule_based_notes_evaluation_rejects_empty_manifest(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "empty.jsonl"
    manifest_path.write_text("", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Notes manifest must contain records",
    ):
        run_rule_based_notes_evaluation(
            manifest_path=manifest_path,
            output_root=tmp_path / "reports",
        )