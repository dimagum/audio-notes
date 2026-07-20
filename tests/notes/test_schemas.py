from __future__ import annotations

import pytest
from pydantic import ValidationError

from audio_notes.notes.schemas import GeneratedNote


def make_payload() -> dict[str, object]:
    return {
        "title": "Как технологии меняют образование",
        "summary": (
            "Спикер объясняет, как цифровые инструменты "
            "меняют доступ к образованию и роль преподавателя."
        ),
        "key_points": [
            "Цифровые инструменты расширяют доступ к обучению.",
            "Преподаватель сохраняет роль наставника.",
        ],
        "action_items": [],
        "open_questions": [],
    }


def test_generated_note_accepts_valid_data() -> None:
    note = GeneratedNote.model_validate(make_payload())

    assert note.title == "Как технологии меняют образование"
    assert len(note.key_points) == 2
    assert note.action_items == []
    assert note.open_questions == []


def test_generated_note_strips_text_values() -> None:
    payload = make_payload()
    payload["title"] = "  Заголовок  "
    payload["key_points"] = [
        "  Первый тезис  ",
        " Второй тезис ",
    ]

    note = GeneratedNote.model_validate(payload)

    assert note.title == "Заголовок"
    assert note.key_points == [
        "Первый тезис",
        "Второй тезис",
    ]


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("title", ""),
        ("title", "   "),
        ("summary", ""),
        ("summary", "   "),
        ("key_points", []),
        ("key_points", [""]),
        ("key_points", ["  "]),
        ("action_items", [""]),
        ("open_questions", ["   "]),
    ],
)
def test_generated_note_rejects_invalid_data(
    field_name: str,
    invalid_value: str | list[str],
) -> None:
    payload = make_payload()
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        GeneratedNote.model_validate(payload)


def test_generated_note_rejects_too_many_key_points() -> None:
    payload = make_payload()
    payload["key_points"] = [
        f"Тезис {index}"
        for index in range(11)
    ]

    with pytest.raises(ValidationError):
        GeneratedNote.model_validate(payload)