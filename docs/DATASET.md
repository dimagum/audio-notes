# Datasets

## Purpose

- `asr_test`: фиксированный набор коротких записей с эталонными транскриптами
  для оценки ASR через WER/CER.
- `notes_test`: фиксированный набор длинных TEDx-докладов для проверки
  полного pipeline `audio -> transcript -> notes`.
- `notes_candidates.md`: журнал кандидатов для будущего расширения наборов;
  он не изменяет состав `notes_test`.

## Mozilla Common Voice Russian

- Source: https://mozilladatacollective.com/datasets/cmqinj9g500vsnr07qf4hmr3j
- Dataset: Common Voice Scripted Speech, Russian
- Version: 26.0
- Downloaded at: 2026-07-17
- License: CC0
- Local path: `data/external/common_voice_ru/`
- Selected split: `test.tsv`
- Selected samples: 300
- Selection seed: 42
- Manifest: `data/processed/eval/asr_test_manifest.jsonl`
- Selection script: `scripts/build_asr_manifest.py`

## Multilingual TEDx Russian

- Source: https://www.openslr.org/100/
- Dataset: Multilingual TEDx, Russian (`ru-ru`)
- Version: v1.0
- Downloaded at: 2026-07-17
- License: CC BY-NC-ND 4.0
- Local path: `data/external/mtedx_ru/ru-ru/`
- Selected split: `test`
- Selected talks: 9
- Reference transcript: `test.ru`, aligned with `segments`
- Manifest: `data/processed/eval/notes_test_manifest.jsonl`
- Manifest script: `scripts/build_mtedx_notes_manifest.py`

## Dataset Roles

- Common Voice is used only to evaluate ASR quality.
- mTEDx `test` is used only to evaluate the end-to-end pipeline and note quality.
- Neither fixed evaluation manifest is used for model training or prompt selection.
- Candidate recordings are reviewed separately before creating any new dataset.

## Reproducibility

Audio, archives and unpacked datasets are excluded from Git.
Only scripts, manifests and documentation are versioned.

To reproduce the manifests:

```powershell
python scripts/build_asr_manifest.py `
  --cv-dir <COMMON_VOICE_RU_DIR> `
  --split test `
  --limit 300 `
  --seed 42 `
  --output data/processed/eval/asr_test_manifest.jsonl
```

```powershell
python scripts/build_mtedx_notes_manifest.py `
  --dataset-root data/external/mtedx_ru/ru-ru `
  --split test `
  --segments-file data/external/mtedx_ru/ru-ru/data/test/txt/segments `
  --transcript-file data/external/mtedx_ru/ru-ru/data/test/txt/test.ru `
  --output data/processed/eval/notes_test_manifest.jsonl
```