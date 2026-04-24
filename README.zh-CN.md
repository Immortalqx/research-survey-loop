# research_survey_loop

English version: [README.md](./README.md)

`research_survey_loop` 是一个用于长期、多轮调研流程的 Codex skill 仓库。
它主要面向 Robotics、Embodied AI、计算机视觉、world models、navigation、manipulation 及其相邻方向。

真正可安装的 skill 位于 [research-survey-loop/](./research-survey-loop/)。

## 快速开始

把这个 skill 复制到 `$CODEX_HOME/skills/`：

```bash
cp -R research-survey-loop "$CODEX_HOME/skills/"
```

然后给 Codex 发消息，要求它使用 `$research-survey-loop` 调研某个主题；如果你本地已经有笔记、PDF 或初步结果，也可以一起提供。

```text
Use $research-survey-loop to survey recent work on world models for embodied navigation.
I also have some local notes and PDFs in this workspace. Start round 1.
```

## 工作方式

1. 用户发送调研主题，并可附带本地已有资料。
2. Codex 创建或继续一个持久化的 survey task。
3. Codex 按多个 round 推进。不同 round 可能分别负责检索资料、阅读论文、吸收本地材料、整理分类、扩写综述。
4. 后续用户再告诉 Codex 当前继续哪个 round，或者直接让它继续下一轮。

示例后续消息：

```text
Continue round 2 for the same topic based on current_task.md and round_log.md.
```

## 输出

这个 skill 会在 `survey_tasks/<topic-slug>/` 下维护一个持续演进的流程，并持续更新：

- `task.md`
- `round_log.md`
- `current_task.md`
- `survey.md`

## 仓库结构

- `README.md` 和 `README.zh-CN.md`：仓库说明文档
- `research-survey-loop/`：真正用于安装的 Codex skill
