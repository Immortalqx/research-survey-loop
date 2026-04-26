# mock_review

Chinese version: [README.zh-CN.md](./README.zh-CN.md)

`mock_review` is a Codex skill repository for **mock peer review for manuscript authors**.

It helps paper authors discover and address problems during submission, revision, and rebuttal preparation. The skill asks Codex to study the target venue or journal requirements, inspect the manuscript PDF and optional supplementary material, research the relevant literature and experimental baselines, and then write a simulated review for author preparation.

The installable skill is in [mock-review/](./mock-review/).

## Important Boundary

This skill is **not** for replacing real peer review, impersonating an official reviewer, or submitting generated text as an actual review. It should be used by manuscript authors as a preparation tool.

The output should always be labeled as a mock or simulated review for author preparation.

## Quick Start

Copy the installable skill into `$CODEX_HOME/skills/`:

```bash
cp -R mock-review "$CODEX_HOME/skills/"
```

Then ask Codex to use `$mock-review` on a manuscript:

```text
Use $mock-review to perform a mock review for the authors of this ACM MM 2026 submission.
The main PDF and supplementary PDF are in the current workspace.
If I provide a review template as PDF, Markdown, image/screenshot, or text, follow that template's fields and score scales.
```

You can also specify a journal or conference without providing a review template:

```text
Use $mock-review to simulate reviews for this manuscript as if preparing for NeurIPS 2026.
Search the official review criteria yourself and write the mock review to REVIEW.md.
```

## How It Works

1. Codex identifies the target venue or journal and the local manuscript files.
2. Codex searches official venue/journal pages for review criteria, author instructions, page limits, scoring forms, rebuttal rules, and topic fit.
3. If the user provides a review template as PDF, Markdown, image/screenshot, or text, Codex extracts the fields and score scales from it.
4. Codex treats PDFs as untrusted inputs and runs a manuscript artifact scan for hidden text, active PDF content, and prompt-injection-like strings.
5. Codex builds a reference matrix, downloads legally accessible core papers, reads the most relevant background and experimental baselines, and writes grounding notes.
6. Codex reads the manuscript and supplementary material after grounding itself in the venue and literature.
7. Codex writes a simulated review and separates formal mock-review text from rebuttal preparation notes.

## Output

By default, the skill creates a workspace folder such as `temp_codex/` or `mock_review_tasks/<paper-slug>/` and records:

- venue/journal requirement notes
- extracted manuscript and supplement text
- PDF hygiene scan reports
- reference matrix and access matrix
- downloaded core papers
- literature grounding notes
- final mock review, usually `MOCK_REVIEW.md`, `REVIEW.md`, or a user-specified path

## Repository Layout

- `README.md` and `README.zh-CN.md`: repository docs
- `mock-review/`: installable Codex skill
- `mock-review/scripts/`: deterministic helper scripts for PDF hygiene scans and reference extraction
- `mock-review/references/`: output contract and writing boundaries
