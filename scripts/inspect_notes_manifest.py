from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import mean

from audio_notes.evaluation.notes_manifest import load_notes_manifest


def main() -> None:
    manifest_path = Path(
        "data/processed/eval/notes_test_manifest.jsonl"
    )
    records = load_notes_manifest(manifest_path)

    domains = Counter(record.domain for record in records)
    durations = [record.duration_seconds for record in records]
    transcript_words = [
        len(record.reference_text.split())
        for record in records
    ]
    # summary_words = [
    #     len(record.summary.split())
    #     for record in records
    # ]

    print(f"Records: {len(records)}")
    print(f"Domains: {dict(sorted(domains.items()))}")
    print(
        "Duration seconds: "
        f"min={min(durations):.1f}, "
        f"mean={mean(durations):.1f}, "
        f"max={max(durations):.1f}"
    )
    print(
        "Transcript words: "
        f"min={min(transcript_words)}, "
        f"mean={mean(transcript_words):.1f}, "
        f"max={max(transcript_words)}"
    )
    # print(
    #     "Reference-summary words: "
    #     f"min={min(summary_words)}, "
    #     f"mean={mean(summary_words):.1f}, "
    #     f"max={max(summary_words)}"
    # )

    first = records[0]
    print()
    print(f"First ID: {first.id}")
    print(f"First domain: {first.domain}")
    print(f"First duration: {first.duration_seconds:.1f} seconds")
    print("First reference excerpt:")
    print(first.reference_text[:500])
    # print()
    # print("First reference summary:")
    # print(first.summary)


if __name__ == "__main__":
    main()