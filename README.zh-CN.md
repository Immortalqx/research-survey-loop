# my_codex_skills

[English](./README.md) | 中文

这是我个人维护的 Codex Skills 集合，用来沉淀可复用的科研工作流。

每个顶层 skill 文件夹都会保留自己的 README 文档，并在内部包含真正可安装的 `SKILL.md` 目录。

## Skills

| Skill | 中文简介 | 典型用途 | 可安装目录 |
| --- | --- | --- | --- |
| [`mock-review`](./mock-review/) | 给论文作者使用的模拟审稿工具；按指定会议或期刊调研官方要求，检查稿件 PDF 材料风险，调研相关文献和实验对比，并生成用于准备 rebuttal、发现论文风险和改进论文的模拟审稿意见。 | 投稿前风险排查、rebuttal 准备、论文修改前的 reviewer-style critique。 | [`mock-review/mock-review`](./mock-review/mock-review/) |
| [`research-survey-loop`](./research-survey-loop/) | 长周期文献综述工作流；创建或继续综述任务，维护 `task.md`、`round_log.md`、`current_task.md` 和 `survey.md`，按来源优先级搜索论文，迁移本地 PDF，并逐轮扩展中文综述。 | 机器人、具身智能、计算机视觉、世界模型、导航、操作、3D 感知等方向的持续文献调研。 | [`research-survey-loop/research-survey-loop`](./research-survey-loop/research-survey-loop/) |

## 安装

把真正可安装的 skill 目录复制到 Codex skills 目录即可。

```powershell
# 安装 mock-review
Copy-Item -Recurse -Force .\mock-review\mock-review "$env:USERPROFILE\.codex\skills\mock-review"

# 安装 research-survey-loop
Copy-Item -Recurse -Force .\research-survey-loop\research-survey-loop "$env:USERPROFILE\.codex\skills\research-survey-loop"
```

如果你设置了 `CODEX_HOME`，也可以复制到 `$env:CODEX_HOME\skills\`。

## 说明

- 这些 skills 是个人科研工作流沉淀，不代表任何会议、期刊或机构的官方流程。
- 使用 `mock-review` 生成的内容应明确标注为 simulated/mock review，不能替代真实同行评审，也不能冒充官方审稿意见。
- 文献下载和调研应优先使用官方开放页面、arXiv、OpenReview、作者主页等合法可访问来源。
- 每个 skill 的具体说明请阅读对应 skill 文件夹内的 README 文档。
