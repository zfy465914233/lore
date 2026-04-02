# Phase 1: Answer Synthesis Layer — Changelog

Date: 2026-04-02

## What Changed

### New: `scripts/synthesize_answer.py`

The system's largest gap was that it could collect and package evidence but never actually generate an answer. This module closes that gap by calling an LLM to produce structured answers from the rendered prompt bundle.

**Key design decisions:**

1. **OpenAI-compatible API** — uses `urllib` (no new dependencies) to call any OpenAI-compatible chat completions endpoint. Configuration via environment variables:
   - `LLM_API_URL` (default: `https://api.openai.com/v1`)
   - `LLM_API_KEY`
   - `LLM_MODEL` (default: `gpt-4o-mini`)

2. **Structured answer contract** — the LLM is instructed to output JSON with:
   - `answer`: concise direct answer
   - `supporting_claims`: grounded claims with evidence_ids and confidence levels
   - `inferences`: reasoning beyond direct evidence
   - `uncertainty`: what we're not sure about
   - `missing_evidence`: what would help but isn't available
   - `suggested_next_steps`: follow-up actions

3. **Robust parsing** — handles fenced JSON (```json), JSON with preamble text, and plain-text fallbacks when the LLM doesn't produce valid JSON.

4. **Dry-run mode** — `--dry-run` flag emits the API request payload without calling the LLM, useful for prompt debugging.

### New: `tests/test_synthesize_answer.py`

4 test cases covering dry-run mode, stdin input, model override, and file output.

## Updated Data Flow

```
query → orchestrate_research → route + evidence pack
  → build_answer_context → structured context
    → render_answer_bundle → prompt bundle
      → synthesize_answer → structured answer (NEW)
        → distill_knowledge → draft card
          → promote_draft → knowledge base
```

## Next Step (Phase 2)

End-to-end integration: wire the full pipeline from query to final answer, build a basic eval framework to measure answer quality.
