# Phase 2: End-to-End Pipeline + Evaluation — Changelog

Date: 2026-04-02

## What Changed

### New: `scripts/run_pipeline.py`

End-to-end pipeline that wires together all stages:

```
query → build_answer_context → render_answer_bundle → synthesize_answer → final answer
```

Features:
- `--dry-run` flag stops before LLM call, useful for debugging
- `--keep-intermediate` includes answer context and prompt bundle in output
- Auto-builds index if missing
- Pipes JSON between stages via subprocess stdin/stdout

### New: `scripts/run_eval.py`

Evaluation runner with a benchmark query set covering:
- **Definition** (3 cases): Markov chain, LP duality, QAT
- **Derivation** (2 cases): Stationary distribution, QPE error bound
- **Freshness** (1 case): SOTA quantization
- **Comparison** (1 case): Markov chains vs other processes

Metrics reported:
- Route accuracy (did the system classify the query correctly?)
- Retrieval hit rate (did the right evidence IDs appear in citations?)
- Min citations met rate (are there enough citations?)
- Answer present rate (was an answer generated?)
- Per-category breakdown

Usage:
```
python run_eval.py --dry-run              # quick eval without LLM
python run_eval.py --category definition   # subset
python run_eval.py --output report.json    # save report
```

### New: `tests/test_pipeline_and_eval.py`

6 test cases covering pipeline dry-run (local-led, web-led, keep-intermediate) and eval runner (all, single category, category breakdown).

## Evaluation Baseline (dry-run)

| Metric | Value |
|---|---|
| Total cases | 7 |
| Route accuracy | 100% |
| Retrieval hit rate | 100% |
| Categories covered | 4 (definition, derivation, freshness, comparison) |

## Next Step (Phase 3)

Upgrade retrieval from TF-IDF to hybrid (BM25 + Embedding + Rerank), then measure improvement via eval runner.
