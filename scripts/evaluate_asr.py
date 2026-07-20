from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from audio_notes.asr.base import Transcriber
from audio_notes.asr.faster_whisper import FasterWhisperTranscriber
from audio_notes.asr.mock import MockTranscriber
from audio_notes.evaluation.aggregation import aggregate_asr_results
from audio_notes.evaluation.asr_evaluator import AsrEvaluator
from audio_notes.evaluation.manifest import load_asr_manifest
from audio_notes.evaluation.reporters import write_asr_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluates an ASR transcriber on an ASR JSONL manifest."
    )
    parser.add_argument(
        "--engine",
        choices=["mock", "faster-whisper"],
        default="mock",
        help="ASR engine to evaluate.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/processed/eval/asr_test_manifest.jsonl"),
        help="Path to the ASR evaluation JSONL manifest.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of records to evaluate; default evaluates all.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for reports; defaults to a timestamped directory.",
    )
    parser.add_argument(
        "--model",
        default="large-v3-turbo",
        help="faster-whisper model name or local model path.",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="faster-whisper device, e.g. cuda or cpu.",
    )
    parser.add_argument(
        "--compute-type",
        default="float16",
        help="CTranslate2 compute type, e.g. float16 or int8.",
    )
    parser.add_argument(
        "--language",
        default="ru",
        help="Source language code; set to an empty string for auto-detect.",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam-search size; must be positive.",
    )
    parser.add_argument(
        "--vad-filter",
        action="store_true",
        help="Enable voice-activity detection in faster-whisper.",
    )
    return parser.parse_args()


def create_transcriber(
    *,
    args: argparse.Namespace,
    records_count: int,
    mock_transcripts: dict[Path, str],
) -> Transcriber:
    if args.engine == "mock":
        return MockTranscriber(mock_transcripts)

    if args.engine == "faster-whisper":
        return FasterWhisperTranscriber(
            model_name=args.model,
            device=args.device,
            compute_type=args.compute_type,
            language=args.language or None,
            beam_size=args.beam_size,
            vad_filter=args.vad_filter,
        )

    raise ValueError(f"Unsupported engine: {args.engine}")


def main() -> None:
    args = parse_arguments()

    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")

    if args.beam_size <= 0:
        raise ValueError("--beam-size must be positive")

    records = load_asr_manifest(args.manifest)
    if args.limit is not None:
        records = records[: args.limit]

    mock_transcripts = {
        record.audio_path: record.reference_text
        for record in records
    }
    transcriber = create_transcriber(
        args=args,
        records_count=len(records),
        mock_transcripts=mock_transcripts,
    )

    evaluator = AsrEvaluator(transcriber=transcriber)
    results = evaluator.evaluate_records(records)
    summary = aggregate_asr_results(results)

    engine_dir_name = args.engine.replace("-", "_")
    output_dir = args.output_dir or (
        Path("artifacts/reports/asr")
        / engine_dir_name
        / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    )

    write_asr_report(
        output_dir=output_dir,
        results=results,
        summary=summary,
    )

    print(f"Engine: {args.engine}")
    print(f"Evaluated records: {summary.n_total}")
    print(f"Successful records: {summary.n_success}")
    print(f"Failed records: {summary.n_failed}")
    print(f"WER: {summary.wer:.4f}")
    print(f"CER: {summary.cer:.4f}")
    print(f"RTF (global): {summary.rtf_global:.4f}")
    print(f"Reports: {output_dir}")


if __name__ == "__main__":
    main()