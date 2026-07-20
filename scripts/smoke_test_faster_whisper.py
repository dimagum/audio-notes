from __future__ import annotations

from pathlib import Path

from audio_notes.asr.faster_whisper import FasterWhisperTranscriber
from audio_notes.evaluation.manifest import load_asr_manifest


def main() -> None:
    records = load_asr_manifest(
        Path("data/processed/eval/asr_test_manifest.jsonl")
    )
    record = records[0]

    print(f"Audio: {record.audio_path}")
    print(f"Reference: {record.reference_text}")

    transcriber = FasterWhisperTranscriber(
        model_name="large-v3-turbo",
        device="cuda",
        compute_type="float16",
        language="ru",
        beam_size=5,
        vad_filter=False,
    )
    hypothesis = transcriber.transcribe(record.audio_path)

    print(f"Hypothesis: {hypothesis}")


if __name__ == "__main__":
    main()