from __future__ import annotations

from pathlib import Path

from audio_notes.asr.mock import MockTranscriber
from audio_notes.evaluation.asr_evaluator import AsrEvaluator
from audio_notes.evaluation.schemas import AsrManifestRecord


def make_record(
    *,
    record_id: str,
    audio_path: Path,
    reference_text: str,
) -> AsrManifestRecord:
    return AsrManifestRecord(
        id=record_id,
        source="Test dataset",
        split="test",
        audio_path=audio_path,
        reference_text=reference_text,
    )


def test_evaluate_record_returns_metrics_for_successful_asr(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    record = make_record(
        record_id="sample_001",
        audio_path=audio_path,
        reference_text="модель обучается быстро",
    )

    evaluator = AsrEvaluator(
        transcriber=MockTranscriber(
            {audio_path: "модель проверяется быстро"}
        ),
        duration_getter=lambda _: 10.0,
    )

    result = evaluator.evaluate_record(record)

    assert result.id == "sample_001"
    assert result.error is None
    assert result.hypothesis_text == "модель проверяется быстро"
    assert result.audio_duration_seconds == 10.0
    assert result.asr_seconds >= 0.0
    assert result.asr_rtf >= 0.0
    assert result.wer == 1 / 3
    assert result.substitutions == 1
    assert result.reference_word_count == 3
    assert result.hypothesis_word_count == 3


def test_evaluate_record_returns_error_result_when_asr_fails(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    record = make_record(
        record_id="sample_001",
        audio_path=audio_path,
        reference_text="эталонный текст",
    )

    evaluator = AsrEvaluator(
        transcriber=MockTranscriber({}),
        duration_getter=lambda _: 5.0,
    )

    result = evaluator.evaluate_record(record)

    assert result.id == "sample_001"
    assert result.error is not None
    assert "KeyError" in result.error
    assert result.audio_duration_seconds == 5.0
    assert result.hypothesis_text == ""
    assert result.asr_seconds == 0.0
    assert result.wer == 0.0


def test_evaluate_record_returns_error_result_when_duration_fails(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.mp3"
    audio_path.touch()

    record = make_record(
        record_id="sample_001",
        audio_path=audio_path,
        reference_text="эталонный текст",
    )

    def raise_duration_error(_: Path) -> float:
        raise RuntimeError("ffprobe failed")

    evaluator = AsrEvaluator(
        transcriber=MockTranscriber(
            {audio_path: "предсказанный текст"}
        ),
        # duration_getter=lambda _: (_ for _ in ()).throw(
        #     RuntimeError("ffprobe failed")
        # ),
        duration_getter=raise_duration_error,
    )

    result = evaluator.evaluate_record(record)

    assert result.error is not None
    assert "RuntimeError: ffprobe failed" in result.error
    assert result.audio_duration_seconds == 0.0
    assert result.hypothesis_text == ""


def test_evaluate_records_processes_all_records(
    tmp_path: Path,
) -> None:
    first_audio = tmp_path / "first.mp3"
    second_audio = tmp_path / "second.mp3"
    first_audio.touch()
    second_audio.touch()

    records = [
        make_record(
            record_id="first",
            audio_path=first_audio,
            reference_text="первый текст",
        ),
        make_record(
            record_id="second",
            audio_path=second_audio,
            reference_text="второй текст",
        ),
    ]

    transcriber = MockTranscriber(
        {
            first_audio: "первый текст",
            second_audio: "второй текст",
        }
    )
    evaluator = AsrEvaluator(
        transcriber=transcriber,
        duration_getter=lambda _: 3.0,
    )

    results = evaluator.evaluate_records(records)

    assert [result.id for result in results] == ["first", "second"]
    assert all(result.error is None for result in results)
    assert transcriber.calls == [first_audio, second_audio]