# Datasets

## Purpose

- `asr_test`: фиксированный набор для WER/CER.
- `notes_test`: фиксированный набор длинных аудиозаписей для оценки pipeline
  и качества структурированных заметок.

## Mozilla Common Voice Russian

- Source: https://mozilladatacollective.com/datasets/cmqinj9g500vsnr07qf4hmr3j
- Dataset: Common Voice Scripted Speech, Russian
- Version: 26.0
- Downloaded at: YYYY-MM-DD
- License: CC0
- Local path: `data/external/common_voice_ru/`
- Selected split: `test.tsv`
- Selected samples: 300
- Selection seed: 42
- Manifest: `data/processed/eval/asr_test_manifest.jsonl`

## Multilingual TEDx Russian

- Source: https://www.openslr.org/100/
- Dataset: Multilingual TEDx, Russian
- Downloaded at: YYYY-MM-DD
- Local path: `data/external/mtedx_ru/`
- License: Check the archive README and the OpenSLR page before redistribution.
- Selected talks: 10–20
- Manifest: `data/processed/eval/notes_test_manifest.jsonl`

## Reproducibility

Audio, archives and unpacked datasets are excluded from Git.
Only scripts, manifests and this documentation are versioned.