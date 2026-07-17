from __future__ import annotations

import re

from jiwer import cer, wer


def normalize_text(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def calculate_asr_metrics(reference: str, hypothesis: str) -> dict[str, float]:
    reference = normalize_text(reference)
    hypothesis = normalize_text(hypothesis)

    return {
        "wer": wer(reference, hypothesis),
        "cer": cer(reference, hypothesis),
    }