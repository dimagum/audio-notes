from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from audio_notes.asr.mock import MockTranscriber
from audio_notes.evaluation.aggregation import aggregate_asr_results
from audio_notes.evaluation.asr_evaluator import AsrEvaluator
from audio_notes.evaluation.manifest import load_asr_manifest
from audio_notes.evaluation.reporters import write_asr_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Runs a dry-run ASR evaluation with a mock transcriber."
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
        default=5,
        help="Maximum number of manifest records to evaluate.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory for reports. "
            "Defaults to artifacts/reports/asr/mock/<timestamp>."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit must be positive")

    records = load_asr_manifest(args.manifest)[: args.limit]

    transcripts = {
        record.audio_path: record.reference_text
        for record in records
    }
    transcriber = MockTranscriber(transcripts)
    evaluator = AsrEvaluator(transcriber=transcriber)

    results = evaluator.evaluate_records(records)
    summary = aggregate_asr_results(results)

    output_dir = args.output_dir or (
        Path("artifacts/reports/asr/mock")
        / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    )
    write_asr_report(
        output_dir=output_dir,
        results=results,
        summary=summary,
    )

    print(f"Evaluated records: {summary.n_total}")
    print(f"Successful records: {summary.n_success}")
    print(f"Failed records: {summary.n_failed}")
    print(f"WER: {summary.wer:.4f}")
    print(f"CER: {summary.cer:.4f}")
    print(f"RTF (global): {summary.rtf_global:.4f}")
    print(f"Reports: {output_dir}")


if __name__ == "__main__":
    main()