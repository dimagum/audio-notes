from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class GeneratedNote(BaseModel):
    """Structured note generated from one transcript."""

    title: str = Field(min_length=1, max_length=160)
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(min_length=1, max_length=10)
    action_items: list[str] = Field(default_factory=list, max_length=10)
    open_questions: list[str] = Field(default_factory=list, max_length=10)

    @field_validator(
        "title",
        "summary",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: str,
    ) -> str:
        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("text must not be blank")

        return stripped_value

    @field_validator(
        "key_points",
        "action_items",
        "open_questions",
    )
    @classmethod
    def strip_list_items(
        cls,
        values: list[str],
    ) -> list[str]:
        stripped_values = [
            value.strip()
            for value in values
        ]

        if any(not value for value in stripped_values):
            raise ValueError("list items must not be blank")

        return stripped_values