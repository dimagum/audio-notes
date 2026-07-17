# audio-notes

Локальный сервис для преобразования аудиозаписей в структурированные заметки.

## Возможности

- Распознавание русской и английской речи
- Генерация кратких и подробных заметок
- Извлечение ключевых тезисов, решений, вопросов и задач
- Отдельные режимы `general` и `it`
- LoRA-адаптеры для личного стиля заметок

## Pipeline

`audio -> preprocessing -> ASR -> transcript -> LLM summarization -> notes.md + notes.json`

## Быстрый старт

```bash
git clone https://github.com/dimagum/audio-notes.git
cd audio-to-notes

uv sync
uv run python scripts/check_gpu.py

uv run python -m audio_notes.cli process \
  --input data/raw/example.m4a \
  --mode standard \
  --domain general
```

Результаты появятся в `data/processed/`.

## Формат результата

- `transcript.json` — транскрипт с временными метками
- `notes.json` — структурированная заметка
- `notes.md` — заметка в Markdown

## Обучение

Подготовить датасет:

```bash
uv run python scripts/build_dataset.py \
  --input data/processed/datasets/raw_pairs.jsonl \
  --output data/processed/datasets/general_sft.jsonl
```

Запустить QLoRA:

```bash
bash scripts/train_general.sh
```

## Оценка

```bash
uv run python -m audio_notes.training.evaluate \
  --predictions eval/results/predictions.jsonl \
  --references eval/references/test.jsonl
```

## Приватность

Аудио и модели обрабатываются локально. Не добавляйте в датасеты записи, содержащие персональные, конфиденциальные или NDA-данные.