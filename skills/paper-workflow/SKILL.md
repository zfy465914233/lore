---
name: paper-workflow
description: "Daily paper discovery workflow: search arXiv + Semantic Scholar, score, deduplicate, and generate a recommendation note. Also handles individual paper searches by topic."
allowed-tools: Bash
---

# Paper Discovery Workflow

Find, score, and recommend academic papers matching the user's research interests.

## Step 1: Choose the search mode

| Mode | When to use |
|------|-------------|
| Daily recommendations | User wants today's paper digest |
| Topic search | User asks about a specific topic |
| Conference search | User asks about papers from a specific venue/year |

## Step 2: Run the search

### Daily recommendations

```
daily_recommend(language="zh", dual_track=true)
```

This runs the full pipeline: arXiv recent papers + conference impact papers + arXiv innovation papers. Returns a daily note and a list of top papers for analysis.

### Topic search

```
search_papers(query="chain of thought reasoning", top_n=10)
```

### Conference search

```
search_conf_papers(venues="NeurIPS,ICML", year=2026, top_n=10)
```

## Step 3: Present results to the user

Show the paper list with:
- Title, authors, arxiv_id
- Recommendation score
- Matched domain and keywords

## Step 4: Deep analysis (if requested)

For papers the user wants to analyze in depth, follow the paper-analysis skill.

## Notes

- Language setting comes from config (`zh` or `en`). Default is Chinese.
- `skip_existing=true` avoids re-analyzing papers already in paper-notes/.
- The dual-track mode gives 2 conference papers (impact-ranked) + 2 arXiv papers (innovation-scored).
