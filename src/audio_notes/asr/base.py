from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Transcriber(Protocol):
    """Interface for a component that produces text from one audio file."""

    def transcribe(self, audio_path: Path) -> str:
        """Returns a transcript for one audio file."""
        ...