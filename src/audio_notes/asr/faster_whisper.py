from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel


class FasterWhisperTranscriber:
    """ASR transcriber implemented with faster-whisper."""

    def __init__(
        self,
        model_name: str = "large-v3-turbo",
        *,
        device: str = "cuda",
        compute_type: str = "float16",
        language: str = "ru",
        beam_size: int = 5,
        vad_filter: bool = False,
    ) -> None:
        if beam_size <= 0:
            raise ValueError("beam_size must be positive")

        self._language = language
        self._beam_size = beam_size
        self._vad_filter = vad_filter
        self._model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, audio_path: Path) -> str:
        """Returns a complete transcript for one audio file."""
        segments, _ = self._model.transcribe(
            str(audio_path),
            language=self._language,
            task="transcribe",
            beam_size=self._beam_size,
            vad_filter=self._vad_filter,
        )

        return " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )