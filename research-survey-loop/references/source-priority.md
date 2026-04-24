# Source Priority

Use this file to keep the retrieval order stable across rounds.

## Default Search Ladder

1. Nature / Science and related journals
2. Top computer vision venues
3. Top robotics venues
4. arXiv
5. Local `papers/` pool for migration, de-duplication, and gap filling

Treat this as the default order unless the user explicitly overrides it.

## Nature / Science First

Prioritize publisher pages and journal landing pages before tertiary summaries.

Recommended domains:

- `nature.com`
- `science.org`

Typical query anchors:

- `"TOPIC" site:nature.com`
- `"TOPIC" site:science.org`
- `"TOPIC" Nature`
- `"TOPIC" Science`

## Top CV Venues

Default priority list:

- `CVPR`
- `ICCV`
- `ECCV`
- `TPAMI`
- `IJCV`

Recommended domains:

- `openaccess.thecvf.com`
- `ieeexplore.ieee.org`
- `springer.com`

Typical query anchors:

- `"TOPIC" site:openaccess.thecvf.com`
- `"TOPIC" CVPR`
- `"TOPIC" ICCV`
- `"TOPIC" TPAMI`

## Top Robotics Venues

Default priority list:

- `Science Robotics`
- `IJRR`
- `TRO`
- `RA-L`
- `RSS`
- `ICRA`
- `CoRL`
- `IROS`

Recommended domains:

- `science.org`
- `journals.sagepub.com`
- `ieeexplore.ieee.org`
- `roboticsconference.org`
- `proceedings.mlr.press`

Typical query anchors:

- `"TOPIC" "Science Robotics"`
- `"TOPIC" IJRR`
- `"TOPIC" site:roboticsconference.org`
- `"TOPIC" ICRA`
- `"TOPIC" CoRL`

## arXiv Layer

Use arXiv to widen coverage, surface the newest ideas, and fetch accessible PDFs fast.

Rules:

- Prefer the published version when both arXiv and a formal venue page exist.
- Keep the arXiv PDF link when it is the most accessible downloadable source.
- Use arXiv results to backfill gaps left by closed publisher pages.

## Local Paper Pool

Use the root `papers/` directory as an unsorted local reservoir.

Rules:

- Do not cite root `papers/` paths in `survey.md`.
- Only move papers that the current task truly absorbs.
- After migration, cite the task-local `./sources/papers/...` path only.

## Source Selection Heuristics

Prefer papers that help with at least one of these goals:

- define the problem clearly
- establish a taxonomy
- provide a benchmark or evaluation protocol
- introduce a reusable method family
- expose an important limitation or failure mode
- represent the newest strong trend that the survey should not miss
