from __future__ import annotations

from collections.abc import Mapping

from audio_notes.notes.schemas import GeneratedNote


class MockNoteGenerator:
    """Test note generator that returns preconfigured notes by transcript."""

    def __init__(
        self,
        notes: Mapping[str, GeneratedNote],
    ) -> None:
        self._notes = dict(notes)
        self.calls: list[str] = []

    def generate(
        self,
        transcript: str,
    ) -> GeneratedNote:
        """Returns the configured note for one transcript."""
        self.calls.append(transcript)

        try:
            return self._notes[transcript]
        except KeyError as error:
            raise KeyError(
                "No mock note configured for the provided transcript"
            ) from error
