# my_codex_skills

English | [中文](./README.zh-CN.md)

This repository collects my personal Codex skills for reusable research workflows.

Each top-level skill folder keeps its own README files and contains an installable skill directory with `SKILL.md`.

## Skills

| Skill | Summary | Typical Use | Installable Directory |
| --- | --- | --- | --- |
| [`mock-review`](./mock-review/) | Mock peer-review workflow for manuscript authors. It researches venue or journal requirements, inspects manuscript PDFs, studies related literature and experimental baselines, and writes a simulated review for rebuttal preparation and paper improvement. | Pre-submission risk check, rebuttal preparation, reviewer-style critique before revising a manuscript. | [`mock-review/mock-review`](./mock-review/mock-review/) |
| [`research-survey-loop`](./research-survey-loop/) | Long-running literature survey workflow. It creates or resumes survey tasks, maintains stable task documents, searches prioritized sources, migrates local PDFs, reads papers in chunks, and incrementally writes a Chinese survey. | Sustained literature surveys for robotics, embodied AI, computer vision, world models, navigation, manipulation, 3D perception, and adjacent topics. | [`research-survey-loop/research-survey-loop`](./research-survey-loop/research-survey-loop/) |

## Install

Copy the installable skill directory into your Codex skills directory.

```powershell
# Install mock-review
Copy-Item -Recurse -Force .\mock-review\mock-review "$env:USERPROFILE\.codex\skills\mock-review"

# Install research-survey-loop
Copy-Item -Recurse -Force .\research-survey-loop\research-survey-loop "$env:USERPROFILE\.codex\skills\research-survey-loop"
```

If `CODEX_HOME` is configured, copy the folders into `$env:CODEX_HOME\skills\` instead.

## Notes

- These skills encode personal research workflows and do not represent official processes of any venue, journal, or institution.
- Outputs from `mock-review` should be clearly labeled as simulated/mock reviews. They must not replace real peer review or impersonate official reviewer reports.
- Literature retrieval should prioritize legally accessible sources such as official open-access pages, arXiv, OpenReview, and author pages.
- For details about a specific skill, read the README files inside that skill folder.
