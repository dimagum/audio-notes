from __future__ import annotations

import pytest

from audio_notes.notes.rule_based import RuleBasedNoteGenerator


def test_rule_based_generator_creates_extractive_note() -> None:
    transcript = (
        "Искусственный интеллект меняет образование. "
        "Он помогает подбирать задания под уровень ученика. "
        "Преподаватель при этом остаётся наставником. "
        "Школам важно защищать данные учащихся."
    )
    generator = RuleBasedNoteGenerator()

    note = generator.generate(transcript)

    assert note.title == "Искусственный интеллект меняет образование"
    assert note.summary == (
        "Искусственный интеллект меняет образование. "
        "Он помогает подбирать задания под уровень ученика."
    )
    assert note.key_points == [
        "Искусственный интеллект меняет образование.",
        "Он помогает подбирать задания под уровень ученика.",
        "Преподаватель при этом остаётся наставником.",
    ]
    assert note.action_items == []
    assert note.open_questions == []


def test_rule_based_generator_truncates_long_title() -> None:
    first_sentence = (
        "Это очень длинное первое предложение, которое специально "
        "превышает установленный лимит символов для заголовка заметки."
    )
    generator = RuleBasedNoteGenerator()

    note = generator.generate(
        f"{first_sentence} Второе предложение."
    )

    assert note.title == first_sentence[:77].rstrip() + "..."


def test_rule_based_generator_handles_one_sentence() -> None:
    generator = RuleBasedNoteGenerator()

    note = generator.generate("Единственное предложение.")

    assert note.title == "Единственное предложение"
    assert note.summary == "Единственное предложение."
    assert note.key_points == ["Единственное предложение."]


def test_rule_based_generator_handles_line_breaks() -> None:
    generator = RuleBasedNoteGenerator()

    note = generator.generate(
        "Первое предложение.\nВторое предложение!\nТретье?"
    )

    assert note.summary == (
        "Первое предложение. Второе предложение!"
    )
    assert note.key_points == [
        "Первое предложение.",
        "Второе предложение!",
        "Третье?",
    ]


@pytest.mark.parametrize(
    "transcript",
    [
        "",
        "   ",
        "\n\t",
    ],
)
def test_rule_based_generator_rejects_empty_transcript(
    transcript: str,
) -> None:
    generator = RuleBasedNoteGenerator()

    with pytest.raises(
        ValueError,
        match="transcript must contain text",
    ):
        generator.generate(transcript)