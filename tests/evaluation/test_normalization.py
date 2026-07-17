import pytest

from audio_notes.evaluation.normalization import normalize_for_asr


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        ("Привет, мир!", "привет мир"),
        ("  Модель   обучается\nбыстро.\t", "модель обучается быстро"),
        ("Ёлка и ёжик", "елка и ежик"),
        ("PyTorch 2.7 + CUDA 12.8", "pytorch 2 7 cuda 12 8"),
        ("Kubernetes/MLflow: готовы?", "kubernetes mlflow готовы"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_normalize_for_asr(raw_text: str, expected: str) -> None:
    assert normalize_for_asr(raw_text) == expected