---
name: paper-analysis
description: "Deep analysis of a single paper: download PDF, extract figures, generate structured 20+ section note, fill LLM placeholders."
allowed-tools: Bash
---

# Paper Analysis Skill

Generate a comprehensive analysis note for a single paper.

## Step 1: Download the paper

```
download_paper(paper_id="2510.24701", title="Paper Title", domain="LLM")
```

This caches the PDF locally under `paper-notes/<title>/`.

## Step 2: Extract figures

```
extract_paper_images(paper_id="2510.24701")
```

Auto-detects the local PDF. Images go to `paper-notes/<title>/images/`.

## Step 3: Generate the analysis note

```
analyze_paper(paper_json='{"title": "...", "authors": [...], "arxiv_id": "..."}', language="zh")
```

Returns:
- `note_path`: path to the generated markdown note
- `quality_check`: whether the note has unfilled placeholders
- `pdf_text`: full text extracted from the PDF (if available)
- `instructions`: if placeholders exist, instructions to fill them

## Step 4: Fill placeholders

The generated note contains `<!-- LLM: describe method -->` style placeholders. When `instructions` is non-null, you MUST fill all placeholders using the `pdf_text` field:

### Filling rules

1. Read the note at `note_path`.
2. For each `<!-- LLM: ... -->` placeholder, replace it with substantive content drawn from `pdf_text`.
3. Be specific: cite numbers, dataset names, architecture details, formula descriptions.
4. Do NOT leave any placeholder unfilled.
5. Write the complete filled note back using the Write tool.

### Section guide

| Section | What to write |
|---------|---------------|
| Core information | One-sentence contribution, key result, paper type |
| Abstract translation | Translate or paraphrase the abstract with domain context |
| Research background | What problem existed, why it matters |
| Research questions | List the explicit or implicit questions the paper addresses |
| Method overview | Architecture, algorithm, pipeline — with specifics |
| Experimental results | Datasets, metrics, comparisons, ablation findings |
| Deep analysis | Strengths, weaknesses, assumptions, limitations |
| Comparison with related work | Position vs. prior art |
| Technical roadmap | Where this fits in the broader research trajectory |
| Future work | Open questions the paper raises |
| Comprehensive evaluation | Your own 1-5 rating with justification |
| My notes | Leave empty for user to fill |

## Step 5: Convert to knowledge card (optional)

```
paper_to_card(paper_json='...', note_path='/path/to/note.md')
```

## Step 6: Link keywords (optional)

```
link_paper_keywords()
```

Scans all notes and auto-creates `[[wiki-links]]` for technical terms.
