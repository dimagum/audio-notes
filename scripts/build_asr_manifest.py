from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cv-dir", type=Path, required=True)
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    metadata_path = args.cv_dir / f"{args.split}.tsv"
    clips_dir = args.cv_dir / "clips"

    with metadata_path.open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))

    valid_rows = [
        row
        for row in rows
        if row.get("path")
        and row.get("sentence")
        and (clips_dir / row["path"]).exists()
    ]

    rng = random.Random(args.seed)
    rng.shuffle(valid_rows)
    selected_rows = valid_rows[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as file:
        for index, row in enumerate(selected_rows, start=1):
            record = {
                "id": f"cv_ru_{args.split}_{index:04d}",
                "source": "Mozilla Common Voice Russian",
                "split": args.split,
                "audio_path": str(Path("data/external/common_voice_ru") / args.cv_dir.name / "clips" / row["path"]),
                "reference_text": row["sentence"],
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Selected: {len(selected_rows)} / {len(valid_rows)}")
    print(f"Manifest: {args.output}")


if __name__ == "__main__":
    main()