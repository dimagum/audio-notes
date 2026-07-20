from __future__ import annotations

import pytest

from audio_notes.notes.mock import MockNoteGenerator
from audio_notes.notes.schemas import GeneratedNote


def make_note(
    *,
    title: str = "Краткая заметка",
) -> GeneratedNote:
    return GeneratedNote(
        title=title,
        summary="Спикер объяснил ключевую идею выступления.",
        key_points=[
            "Первый ключевой тезис.",
            "Второй ключевой тезис.",
        ],
    )


def test_mock_note_generator_returns_configured_note() -> None:
    transcript = "Текст первого выступления."
    expected_note = make_note(title="Первое выступление")
    generator = MockNoteGenerator(
        {
            transcript: expected_note,
        }
    )

    note = generator.generate(transcript)

    assert note == expected_note
    assert generator.calls == [transcript]


def test_mock_note_generator_tracks_multiple_calls() -> None:
    first_transcript = "Первый текст."
    second_transcript = "Второй текст."
    generator = MockNoteGenerator(
        {
            first_transcript: make_note(title="Первый доклад"),
            second_transcript: make_note(title="Второй доклад"),
        }
    )

    first_note = generator.generate(first_transcript)
    second_note = generator.generate(second_transcript)

    assert first_note.title == "Первый доклад"
    assert second_note.title == "Второй доклад"
    assert generator.calls == [
        first_transcript,
        second_transcript,
    ]


def test_mock_note_generator_rejects_unconfigured_transcript() -> None:
    generator = MockNoteGenerator({})
    transcript = "Текст без настроенного результата."

    with pytest.raises(
        KeyError,
        match="No mock note configured",
    ):
        generator.generate(transcript)

    assert generator.calls == [transcript]