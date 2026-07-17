from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    extensions = Counter(
        path.suffix.lower()
        for path in args.root.rglob("*")
        if path.is_file()
    )

    print("File extensions:")
    for suffix, count in extensions.most_common():
        print(f"{suffix or '<no extension>'}: {count}")

    print("\nCandidate metadata files:")
    for path in args.root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".tsv", ".csv", ".json", ".jsonl"}:
            print(path)


if __name__ == "__main__":
    main()