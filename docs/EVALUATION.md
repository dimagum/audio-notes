# ASR Evaluation

## Protocol

- Dataset: `asr_test_manifest.jsonl`
- Normalization: lowercase, `ё -> е`, punctuation removal, whitespace normalization
- Metrics: corpus-level WER/CER, global RTF, median RTF, p95 RTF
- Failed samples: excluded from WER/CER/RTF, counted in `n_failed`

## Baseline Runs

| Date | Engine | Model | Device | Compute | Language | Beam | Samples | WER | CER | RTF | Report |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| 2026-07-20 | faster-whisper | large-v3-turbo | CUDA | float16 | ru | 5 | 5 | 0.1034 | 0.0150 | 0.0459 | `artifacts/reports/asr/faster_whisper/2026-07-20_185826/` |
| 2026-07-20 | faster-whisper | large-v3-turbo | CUDA | float16 | ru | 5 | 50 | 0.0688 | 0.0192 | 0.0359 | `artifacts/reports/asr/faster_whisper/2026-07-20_190051/` |
| 2026-07-20 | faster-whisper | large-v3-turbo | CUDA | float16 | ru | 5 | 300 | 0.0597 | 0.0145 | 0.0324 | `artifacts/reports/asr/faster_whisper/2026-07-20_190647/` |

## Baseline Configuration

- Engine: `faster-whisper`
- Model: `large-v3-turbo`
- Device: `cuda`
- Compute type: `float16`
- Language: `ru`
- Task: `transcribe`
- Beam size: `5`
- VAD filter: `false`
- Dataset: fixed `asr_test_manifest.jsonl`, 300 Common Voice Russian test samples

## Error Analysis: large-v3-turbo

Reviewed 15 samples with the highest per-sample WER.

Observed error categories:
- Phonetic substitutions in short utterances and rare words/proper names.
- Word-boundary changes: merged and split tokens.
- Equivalent number representation: words versus digits.
- Morphological substitutions.
- Errors in rare words and inflected forms.

Decision:
- Keep the current strict normalization as the primary reproducible benchmark.
- Do not normalize numbers, abbreviations, or split/merged words in v1.
- Evaluate domain-specific technical terminology separately before fine-tuning.