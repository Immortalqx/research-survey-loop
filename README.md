# research_survey_loop

Chinese version: [README.zh-CN.md](./README.zh-CN.md)

`research_survey_loop` is a Codex skill repository for long-running, multi-round survey workflows.
It is mainly tuned for Robotics, Embodied AI, computer vision, world models, navigation, manipulation, and nearby topics.

The installable skill is in [research-survey-loop/](./research-survey-loop/).

## Quick Start

Copy the skill into `$CODEX_HOME/skills/`:

```bash
cp -R research-survey-loop "$CODEX_HOME/skills/"
```

Then ask Codex to use `$research-survey-loop` for a topic and include any local notes, PDFs, or early findings if available.

```text
Use $research-survey-loop to survey recent work on world models for embodied navigation.
I also have some local notes and PDFs in this workspace. Start round 1.
```

## How It Works

1. The user sends a prompt with a survey topic and optional local materials.
2. Codex creates or resumes a persistent survey task.
3. Codex works round by round. Different rounds may search sources, read papers, absorb local materials, refine categories, and expand the survey.
4. The user later tells Codex which round to continue, or asks it to continue the next round.

Example follow-up:

```text
Continue round 2 for the same topic based on current_task.md and round_log.md.
```

## Output

The skill maintains a persistent workflow under `survey_tasks/<topic-slug>/` and updates:

- `task.md`
- `round_log.md`
- `current_task.md`
- `survey.md`

## Repository Layout

- `README.md` and `README.zh-CN.md`: repository docs
- `research-survey-loop/`: the installable Codex skill
