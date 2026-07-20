# Notes Evaluation Rubric

## Purpose

This rubric evaluates generated notes for Russian long-form talks.

Each sample receives scores from 1 to 5 for four dimensions.
Use the source `reference_text` as the only factual reference.

## Scoring dimensions

### Factuality

Does the note accurately reflect the reference text?

- 5 — All claims are supported by the source; no material distortions
- 4 — One minor imprecision, but the main meaning is correct
- 3 — Some questionable phrasing or a minor unsupported claim
- 2 — A material error or several unsupported claims
- 1 — Mostly incorrect, fabricated, or unrelated to the source

### Coverage

Does the note capture the central ideas of the whole talk?

- 5 — Covers the main thesis and all major themes
- 4 — Captures the main thesis and most major themes
- 3 — Captures the main thesis but misses important material
- 2 — Covers only a narrow part of the talk
- 1 — Misses the talk's central content

### Structure

Is the note clear and easy to scan?

- 5 — Clear title, concise summary, well-separated key points
- 4 — Clear overall structure with minor issues
- 3 — Understandable but repetitive or uneven
- 2 — Difficult to scan or poorly organized
- 1 — Unstructured or unusable

### Usefulness

Would the note help someone who did not watch the talk?

- 5 — Gives an actionable, self-contained understanding
- 4 — Useful overview with small gaps
- 3 — Partly useful but requires the source for context
- 2 — Limited practical value
- 1 — Not useful

## Procedure

1. Select all records when the set has 10 or fewer talks; otherwise sample at least 10 records.
2. Read the source `reference_text`.
3. Read `generated_note`.
4. Assign one score from 1 to 5 for each dimension.
5. Write one short comment identifying the most important strength or failure.
6. Record results in a CSV file.

## CSV format

```csv
id,engine,factuality,coverage,structure,usefulness,comment
talk_001,rule_based,5,2,3,2,"Extractive text is accurate but only covers the introduction."
```

## Baseline expectations

The rule-based baseline should score highly on factuality because it copies source sentences.
Its coverage will often be low because it selects only the first three sentences.