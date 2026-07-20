from __future__ import annotations

from typing import Protocol

from audio_notes.notes.schemas import GeneratedNote


class NoteGenerator(Protocol):
    """Generates one structured note from a transcript."""

    def generate(
        self,
        transcript: str,
    ) -> GeneratedNote:
        """Returns a structured note for a non-empty transcript."""
        ...