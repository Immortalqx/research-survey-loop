# Writing Rules

Use this file to keep the survey disciplined across many rounds.

## Core Discipline

- Write the survey in Chinese by default.
- Keep English paper titles, venue names, and technical terms when they improve precision.
- Grow one long `survey.md` by category paragraphs.
- Do not switch to a per-paper card database unless the user explicitly asks for that format.

## Reading Depth

Before writing a paper into `survey.md`, understand:

1. what problem the paper studies
2. what the main contribution actually is
3. how the method works at a useful level of detail
4. what evidence supports the claim
5. what the main limitation or caveat is

If any of these remain unclear, keep the paper in `current_task.md` or mark it as pending in `round_log.md`.

## PDF Chunk Rule

- Never read more than 10 PDF pages at once.
- Read long papers in consecutive windows such as `1-10`, `11-20`, `21-30`.
- Use early windows to establish the problem, method, and claim.
- Use later windows to verify experiments, ablations, assumptions, and limitations.

## Citation Rule

- Local sources must use relative links.
- If a source cannot be downloaded, use the canonical web link.
- Do not leave uncited factual claims in `survey.md`.
- When both published and arXiv versions exist, prefer citing the formal version first.

## Survey Growth Rule

The document does not need to be complete in one round.

Preferred rhythm:

1. first round: rough classification and broad scan
2. middle rounds: deepen category by category
3. later rounds: refine comparisons, terminology, and evidence quality

Each round should add one of the following:

- a better classification
- a deeper category paragraph
- a stronger comparison across papers
- a clarified limitation or open question

## Migration Rule

- Treat root `papers/` as a staging pool only.
- Move a local PDF into the task directory as soon as the task truly absorbs it.
- Record every move in `round_log.md`.
- Remove moved files from the pending migration list in `current_task.md`.
- After moving, cite only the task-local relative path.

## Round Closing Rule

Every round must end with:

- one appended round entry in `round_log.md`
- one rewritten `current_task.md`
- one clear statement of the next paragraph or category to improve

Avoid empty endings like "continue next time." Leave the next run with concrete queues and explicit page windows.

## Honesty Rule

- Do not pretend to understand a paper after only reading the title or abstract.
- Do not write uncertain claims as settled conclusions.
- Do not skip limitations when they matter for comparing methods.
- Do not silently mix academic papers and industry reports unless the user asked for that blend.
