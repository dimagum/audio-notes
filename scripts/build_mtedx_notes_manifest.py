from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--split", choices=["train", "valid", "test"], default="test")
    parser.add_argument("--segments-file", type=Path, required=True)
    parser.add_argument("--transcript-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def read_segments(path: Path) -> list[tuple[str, str, float, float]]:
    segments = []

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        parts = line.split()

        if len(parts) != 4:
            raise ValueError(
                f"{path}, line {line_number}: expected 4 fields, got {len(parts)}"
            )

        segment_id, talk_id, start, end = parts
        segments.append((segment_id, talk_id, float(start), float(end)))

    return segments


def read_transcripts(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def resolve_audio_path(wav_dir: Path, talk_id: str) -> Path:
    candidates = [
        wav_dir / f"{talk_id}.flac",
        wav_dir / f"{talk_id}.wav",
        wav_dir / f"{talk_id}.mp3",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    matches = list(wav_dir.glob(f"{talk_id}.*"))
    if len(matches) == 1:
        return matches[0]

    raise FileNotFoundError(
        f"Audio for talk_id='{talk_id}' was not found in {wav_dir}"
    )


def main() -> None:
    args = parse_args()

    split_dir = args.dataset_root / "data" / args.split
    wav_dir = split_dir / "wav"

    segments = read_segments(args.segments_file)
    transcripts = read_transcripts(args.transcript_file)

    if len(segments) != len(transcripts):
        raise ValueError(
            f"Line count mismatch: segments={len(segments)}, "
            f"transcripts={len(transcripts)}. "
            "These files must be parallel line-by-line."
        )

    talks: dict[str, list[dict]] = defaultdict(list)

    for (segment_id, talk_id, start, end), text in zip(
        segments,
        transcripts,
        strict=True,
    ):
        talks[talk_id].append(
            {
                "segment_id": segment_id,
                "start_seconds": start,
                "end_seconds": end,
                "text": text,
            }
        )

    records = []

    for talk_id, talk_segments in sorted(talks.items()):
        talk_segments.sort(key=lambda item: item["start_seconds"])

        audio_path = resolve_audio_path(wav_dir, talk_id)
        duration_seconds = max(
            segment["end_seconds"] for segment in talk_segments
        )

        record = {
            "id": f"mtedx_ru_{talk_id}",
            "source": "Multilingual TEDx / OpenSLR 100",
            "split": args.split,
            "audio_path": str(audio_path).replace("\\", "/"),
            "reference_text": " ".join(
                segment["text"] for segment in talk_segments
            ),
            "segments": talk_segments,
            "n_segments": len(talk_segments),
            "duration_seconds": round(duration_seconds, 3),
            "domain": "general",
        }
        records.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Split: {args.split}")
    print(f"Segments: {len(segments)}")
    print(f"Talks: {len(records)}")
    print(f"Manifest: {args.output}")


if __name__ == "__main__":
    main()