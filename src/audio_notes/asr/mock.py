from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path


class MockTranscriber:
    """Test transcriber that returns preconfigured transcripts by audio path."""

    def __init__(
        self,
        transcripts: Mapping[Path, str],
    ) -> None:
        self._transcripts = dict(transcripts)
        self.calls: list[Path] = []

    def transcribe(self, audio_path: Path) -> str:
        self.calls.append(audio_path)

        try:
            return self._transcripts[audio_path]
        except KeyError as error:
            raise KeyError(
                f"No mock transcript configured for: {audio_path}"
            ) from error