# Phase 5: Knowledge Schema + Governance — Changelog

Date: 2026-04-02

## What Changed

### New: `scripts/knowledge_lifecycle.py`

Core knowledge governance module:

**Schema validation**
- Required fields: id, title, type, topic, confidence, updated_at
- Optional fields: tags, source_refs, origin, aliases, domain, review_status, last_reviewed_at, freshness_expectation, supersedes, conflicts_with, question_types, prerequisites
- Validates card types (definition, theorem, method, derivation, comparison, decision)
- Validates confidence levels and origins

**Lifecycle management**
- States: draft → reviewed → trusted → stale → deprecated
- Explicit transition rules (e.g., trusted can only go to stale or deprecated)
- Deprecated is a terminal state
- `transition_card()` validates and applies state changes

**Duplicate detection**
- Exact ID match detection
- Identical signature detection (topic + type + title)
- Title similarity via word overlap with configurable threshold

**Card scanning**
- `scan_knowledge_dir()` reads all card metadata from the knowledge tree

### New: `scripts/knowledge_governance.py`

CLI tool for knowledge governance operations:
```
python knowledge_governance.py validate     # validate all cards
python knowledge_governance.py duplicates   # find duplicates
python knowledge_governance.py scan         # scan and report
python knowledge_governance.py transition   # change lifecycle state
python knowledge_governance.py transitions  # show valid transitions
```

### Updated: All knowledge cards now have `review_status`

- Seed cards (markov_chain): `review_status: trusted`
- Domain seed cards (lp, qpe, quantization): `review_status: reviewed`
- Web research cards (xband-qpe): `review_status: draft`

### New: `tests/test_knowledge_lifecycle.py`

12 tests covering:
- Card validation (valid, missing fields, invalid type)
- Lifecycle transitions (valid, invalid, terminal state)
- Duplicate detection (identical ID, no duplicates)
- Governance CLI (scan, validate, duplicates, transitions)

## Summary: All 5 Phases Complete

| Phase | Status | Tests |
|---|---|---|
| Phase 1: Answer synthesis | Done | 4 |
| Phase 2: E2E pipeline + eval | Done | 6 |
| Phase 3: Retrieval upgrade | Done | 9 |
| Phase 4: Agent control loop | Done | 8 |
| Phase 5: Knowledge governance | Done | 12 |
| **Existing tests preserved** | **Done** | **22** |
| **Total** | | **61** |

Zero new external dependencies added across all phases.
