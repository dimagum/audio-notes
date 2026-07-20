from __future__ import annotations

import re

from audio_notes.notes.schemas import GeneratedNote

_SENTENCE_SPLIT_PATTERN = re.compile(
    r"(?<=[.!?])\s+",
)


class RuleBasedNoteGenerator:
    """Extractive baseline generator for short Russian transcripts."""

    def generate(
        self,
        transcript: str,
    ) -> GeneratedNote:
        """Builds a deterministic note from source sentences."""
        sentences = _split_sentences(transcript)

        return GeneratedNote(
            title=_make_title(sentences),
            summary=_make_summary(sentences),
            key_points=_make_key_points(sentences),
            action_items=[],
            open_questions=[],
        )


def _split_sentences(
    transcript: str,
) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in _SENTENCE_SPLIT_PATTERN.split(
            transcript.strip()
        )
        if sentence.strip()
    ]

    if not sentences:
        raise ValueError("transcript must contain text")

    return sentences


def _make_title(
    sentences: list[str],
) -> str:
    first_sentence = sentences[0].rstrip(".!?")

    if len(first_sentence) <= 80:
        return first_sentence

    return first_sentence[:77].rstrip() + "..."


def _make_summary(
    sentences: list[str],
) -> str:
    return " ".join(sentences[:2])


def _make_key_points(
    sentences: list[str],
) -> list[str]:
    return sentences[:3]