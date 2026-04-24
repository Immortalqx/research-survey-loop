---
name: research-survey-loop
description: Long-running survey workflow for robotics, embodied AI, computer vision, world models, navigation, manipulation, 3D scene understanding, and adjacent research. Use when Codex needs to create or continue a multi-round literature review task, maintain stable task documents (`task.md`, `round_log.md`, `current_task.md`, `survey.md`), search Nature/Science plus top CV and robotics venues before arXiv, migrate relevant local PDFs from `papers/` into task-local `sources/`, read PDFs in chunks of at most 10 pages, and incrementally write a Chinese Markdown survey with relative local citations or web links.
allowed-tools: Bash(*), Read, Glob, Grep, WebSearch, WebFetch, Write, Agent, mcp__zotero__*, mcp__obsidian-vault__*
---

# Research Survey Loop

Survey topic: `$ARGUMENTS`

## Overview

Use this skill for long-running survey work with a primary focus on robotics, embodied AI, computer vision, world models, spatial intelligence, navigation, manipulation, and 3D perception.

The workflow can extend to adjacent computer science topics, but the bundled search priorities, venue choices, and writing templates are optimized for robotics and embodied AI communities rather than for all research domains equally.

The default working style is:

1. Create or resume one task directory under `survey_tasks/<topic-slug>/`
2. Keep `task.md` stable unless the user explicitly changes the task itself
3. Append `round_log.md` every round
4. Rewrite `current_task.md` every round so the next unattended run has a precise entry point
5. Grow one long `survey.md` by category paragraphs rather than per-paper cards
6. Move task-absorbed local PDFs out of the root `papers/` pool into the task's own `sources/papers/`

This skill is academic-first. Only include `industry_report/` when the user explicitly wants industry or market material mixed into the survey.

## Directory Contract

Every survey task lives under:

```text
survey_tasks/<topic-slug>/
  task.md
  round_log.md
  current_task.md
  survey.md
  sources/
    papers/
    supplementary/
```

Rules:

- Treat the root `papers/` directory as an unsorted staging pool, not as the long-term citation location.
- Once a local PDF is truly used by a task, move it into that task's `sources/papers/`.
- If another task later needs the same paper, copy it from the first task's `sources/papers/` into the new task instead of pointing back to the old path.
- Use relative local links from `survey.md`, such as `./sources/papers/example.pdf`.
- If a source cannot be downloaded locally, cite the canonical web URL instead.

## Required Resources

Read these bundled files before acting:

- `references/source-priority.md` for the fixed search order and venue priorities
- `references/writing-rules.md` for reading depth, citation format, migration rules, and round-closing discipline

Use these bundled templates and scripts instead of improvising new file layouts:

- `assets/task-template.md`
- `assets/round-log-template.md`
- `assets/current-task-template.md`
- `assets/survey-template.md`
- `scripts/init_task.py`
- `scripts/fetch_sources.py`
- `scripts/extract_pdf_chunk.py`

## Workflow

### 1. Bootstrap or Resume

If the task directory does not exist, run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/research-survey-loop/scripts/init_task.py" "TOPIC" --workspace-root "$PWD"
```

If the task already exists, read in this order before doing any new work:

1. `task.md`
2. `current_task.md`
3. The latest round in `round_log.md`
4. `survey.md`

Do not rewrite `task.md` unless the user explicitly changes the task definition.

### 2. Search Web First

Default search order is fixed:

1. Nature / Science and related journals
2. Top CV venues
3. Top robotics venues
4. arXiv
5. Local `papers/` pool as supplement, de-dup, or migration source

Use `WebSearch` and `WebFetch` for publisher-first searching. Use `scripts/fetch_sources.py` to normalize downloads and imports into the task directory.

Typical commands:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/research-survey-loop/scripts/fetch_sources.py" search "TOPIC" --task-dir "survey_tasks/TOPIC-SLUG" --max-per-source 5
python3 "${CODEX_HOME:-$HOME/.codex}/skills/research-survey-loop/scripts/fetch_sources.py" download --task-dir "survey_tasks/TOPIC-SLUG" --arxiv-id 2402.07556
```

Search rules:

- Prefer official publisher or venue pages over tertiary summaries.
- Prefer formal published versions over arXiv when both exist.
- Keep arXiv as a rapid frontier source and fallback download source.
- When `EXA_API_KEY` is configured, `fetch_sources.py search` can probe priority publisher domains automatically.
- If Exa is unavailable, continue with Semantic Scholar and arXiv rather than blocking.

### 3. Import and Migrate Local Papers

Only migrate local PDFs that the current task actually absorbs.

To move a root-level paper into the task:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/research-survey-loop/scripts/fetch_sources.py" import-local --task-dir "survey_tasks/TOPIC-SLUG" "papers/file.pdf"
```

To reuse a paper from another survey task:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/research-survey-loop/scripts/fetch_sources.py" reuse-task-paper --task-dir "survey_tasks/TOPIC-SLUG" --from-task "survey_tasks/OTHER-TASK" "sources/papers/file.pdf"
```

Migration rules:

- Move from root `papers/` into the task when the paper becomes part of the task's reading queue or survey evidence.
- Record the original and destination paths in `round_log.md`.
- Remove migrated items from the `current_task.md` pending migration list.
- Never keep citing the old root `papers/` path in `survey.md`.

### 4. Read PDFs in Chunks

Never read more than 10 PDF pages at once.

Use:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/research-survey-loop/scripts/extract_pdf_chunk.py" "survey_tasks/TOPIC-SLUG/sources/papers/file.pdf" --start-page 1 --end-page 10 --json
```

Rules:

- Long papers must be read in consecutive windows such as `1-10`, `11-20`, `21-30`.
- Do not write firm conclusions into `survey.md` before understanding:
  - the research problem
  - the core method
  - the claimed contribution
  - the evidence supporting the claim
  - the main limitation
- Use survey papers to build taxonomy and terminology first.
- Use original papers to strengthen category paragraphs and comparisons.

### 5. Write the Survey Incrementally

`survey.md` is one long Markdown document, not a pile of independent paper cards.

Writing rules:

- First round: build rough categories and coarse survey paragraphs.
- Later rounds: deepen one category at a time by integrating newly understood papers into the relevant paragraph.
- If a paper is not yet fully understood, keep it in `current_task.md` or note it in `round_log.md` as pending.
- Preserve terminology consistency across rounds.
- Keep every claim traceable to a relative local path or canonical web link.

### 6. Close the Round

At the end of every round:

1. Append a new round block to `round_log.md`
2. Rewrite `current_task.md`
3. Leave the next round with:
   - explicit search queue
   - explicit reading queue
   - explicit pending migrations
   - explicit next paragraph targets in `survey.md`

Do not finish a round with only a vague note like "continue later."

## Output Shape

The four main files have fixed roles:

- `task.md`: stable task contract
- `round_log.md`: append-only history
- `current_task.md`: editable current execution plan
- `survey.md`: long-form Chinese survey with category paragraphs

Default language is Chinese, while preserving English titles, venues, and technical terms where useful.

## Failure Handling

- If a source cannot be downloaded, keep the best canonical URL and continue.
- If Exa or Semantic Scholar credentials are unavailable, keep working with the remaining sources.
- If a PDF is longer than expected, continue chunked reading rather than skipping it.
- If a paper is relevant but still unclear, mark it as pending instead of writing a fake summary.
- If a task directory already exists, preserve `task.md` by default and only recreate missing files.
