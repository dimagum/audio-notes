from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from audio_notes.evaluation.create_notes_review_template import (
    create_notes_review_template,
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
            "reference_text": "Первый текст.",
            "segments": [
                {
                    "segment_id": "talk_001_0000",
                    "start_seconds": 0.0,
                    "end_seconds": 1.0,
                    "text": "Первый текст.",
                }
            ],
            "n_segments": 1,
            "duration_seconds": 1.0,
            "domain": "general",
        },
        {
            "id": "talk_002",
            "source": "Test source",
            "split": "test",
            "audio_path": "data/audio/talk_002.flac",
            "reference_text": "Второй текст.",
            "segments": [
                {
                    "segment_id": "talk_002_0000",
                    "start_seconds": 0.0,
                    "end_seconds": 1.0,
                    "text": "Второй текст.",
                }
            ],
            "n_segments": 1,
            "duration_seconds": 1.0,
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


def read_rows(
    output_path: Path,
) -> list[dict[str, str]]:
    with output_path.open(
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def test_create_notes_review_template_writes_one_row_per_record(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes_manifest.jsonl"
    output_path = tmp_path / "reviews" / "review.csv"
    write_manifest(manifest_path)

    create_notes_review_template(
        manifest_path=manifest_path,
        output_path=output_path,
        engine="rule_based",
    )

    rows = read_rows(output_path)

    assert output_path.is_file()
    assert [row["id"] for row in rows] == [
        "talk_001",
        "talk_002",
    ]
    assert [row["engine"] for row in rows] == [
        "rule_based",
        "rule_based",
    ]


def test_create_notes_review_template_leaves_scores_empty(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes_manifest.jsonl"
    output_path = tmp_path / "review.csv"
    write_manifest(manifest_path)

    create_notes_review_template(
        manifest_path=manifest_path,
        output_path=output_path,
        engine="rule_based",
    )

    first_row = read_rows(output_path)[0]

    assert first_row["factuality"] == ""
    assert first_row["coverage"] == ""
    assert first_row["structure"] == ""
    assert first_row["usefulness"] == ""
    assert first_row["comment"] == ""


def test_create_notes_review_template_overwrites_old_file(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes_manifest.jsonl"
    output_path = tmp_path / "review.csv"
    write_manifest(manifest_path)

    output_path.write_text(
        "outdated,data\n",
        encoding="utf-8",
    )

    create_notes_review_template(
        manifest_path=manifest_path,
        output_path=output_path,
        engine="rule_based",
    )

    rows = read_rows(output_path)

    assert len(rows) == 2
    assert rows[0]["id"] == "talk_001"


def test_create_notes_review_template_rejects_empty_engine(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "notes_manifest.jsonl"
    write_manifest(manifest_path)

    with pytest.raises(
        ValueError,
        match="engine must not be empty",
    ):
        create_notes_review_template(
            manifest_path=manifest_path,
            output_path=tmp_path / "review.csv",
            engine="  ",
        )