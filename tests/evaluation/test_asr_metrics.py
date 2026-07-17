import pytest

from audio_notes.evaluation.asr_metrics import calculate_asr_metrics


@pytest.mark.parametrize(
    ("reference", "hypothesis", "expected"),
    [
        pytest.param(
            "Модель обучается быстро.",
            "модель обучается быстро",
            {
                "wer": 0.0,
                "cer": 0.0,
                "substitutions": 0,
                "deletions": 0,
                "insertions": 0,
                "reference_word_count": 3,
                "hypothesis_word_count": 3,
            },
            id="equal-after-normalization",
        ),
        pytest.param(
            "модель обучается быстро",
            "модель проверяется быстро",
            {
                "wer": 1 / 3,
                "substitutions": 1,
                "deletions": 0,
                "insertions": 0,
            },
            id="one-substitution",
        ),
        pytest.param(
            "модель обучается очень быстро",
            "модель обучается быстро",
            {
                "wer": 1 / 4,
                "substitutions": 0,
                "deletions": 1,
                "insertions": 0,
            },
            id="one-deletion",
        ),
        pytest.param(
            "модель обучается быстро",
            "модель очень обучается быстро",
            {
                "wer": 1 / 3,
                "substitutions": 0,
                "deletions": 0,
                "insertions": 1,
            },
            id="one-insertion",
        ),
        pytest.param(
            "",
            "",
            {
                "wer": 0.0,
                "cer": 0.0,
                "substitutions": 0,
                "deletions": 0,
                "insertions": 0,
                "reference_word_count": 0,
                "hypothesis_word_count": 0,
            },
            id="both-empty",
        ),
        pytest.param(
            "",
            "лишний текст",
            {
                "wer": 2.0,
                "cer": float(len("лишний текст")),
                "substitutions": 0,
                "deletions": 0,
                "insertions": 2,
                "reference_word_count": 0,
                "hypothesis_word_count": 2,
            },
            id="hallucination-on-silence",
        ),
    ],
)
def test_calculate_asr_metrics(
    reference: str,
    hypothesis: str,
    expected: dict[str, int | float],
) -> None:
    result = calculate_asr_metrics(reference, hypothesis)

    for field_name, expected_value in expected.items():
        assert getattr(result, field_name) == pytest.approx(expected_value)