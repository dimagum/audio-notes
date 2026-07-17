from __future__ import annotations

import re

_PUNCTUATION_PATTERN = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WHITESPACE_PATTERN = re.compile(r"\s+", flags=re.UNICODE)


def normalize_for_asr(text: str) -> str:
    """Normalizes text before WER/CER calculation.

    The function applies only meaning-preserving transformations:
    lowercasing, 'ё' -> 'е', punctuation removal, and whitespace cleanup.
    """
    normalized = text.lower()
    normalized = normalized.replace("ё", "е")
    normalized = _PUNCTUATION_PATTERN.sub(" ", normalized)
    normalized = _WHITESPACE_PATTERN.sub(" ", normalized)

    return normalized.strip()