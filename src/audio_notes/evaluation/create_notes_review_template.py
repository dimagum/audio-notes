from __future__ import annotations

import argparse
import csv
from pathlib import Path

from audio_notes.evaluation.run_notes_evaluation import (
    _read_manifest,
)

_FIELDNAMES = [
    "id",
    "engine",
    "factuality",
    "coverage",
    "structure",
    "usefulness",
    "comment",
]


def main() -> None:
    """Creates a blank manual-review CSV for a notes manifest."""
    args = _parse_args()

    create_notes_review_template(
        manifest_path=args.manifest_path,
        output_path=args.output_path,
        engine=args.engine,
    )

    print(f"Notes review template written to: {args.output_path}")


def create_notes_review_template(
    *,
    manifest_path: Path,
    output_path: Path,
    engine: str,
) -> None:
    """Writes one blank manual-review row for each manifest record."""
    if not engine.strip():
        raise ValueError("engine must not be empty")

    records = _read_manifest(manifest_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=_FIELDNAMES,
        )
        writer.writeheader()

        for record in records:
            writer.writerow(
                {
                    "id": record.id,
                    "engine": engine,
                    "factuality": "",
                    "coverage": "",
                    "structure": "",
                    "usefulness": "",
                    "comment": "",
                }
            )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a blank CSV template for manual "
            "notes evaluation."
        ),
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path(
            "data/processed/eval/notes_test_manifest.jsonl"
        ),
        help="Path to a JSONL notes manifest.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path(
            "artifacts/reviews/notes/"
            "rule_based_manual_review.csv"
        ),
        help="Path to the output CSV review template.",
    )
    parser.add_argument(
        "--engine",
        default="rule_based",
        help="Generator name recorded in every CSV row.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()