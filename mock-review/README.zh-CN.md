# mock_review

English version: [README.md](./README.md)

`mock_review` 是一个给**论文作者自己使用的模拟审稿** Codex skill 仓库。

它帮助论文作者在投稿、修改和 rebuttal 准备阶段及时发现问题并进行处理。Codex 会按指定会议/期刊的要求，阅读本地论文 PDF、补充材料、相关文献和实验对比工作，然后生成一份用于作者准备的模拟审稿意见。

真正可安装的 skill 位于 [mock-review/](./mock-review/)。

## 重要边界

这个 skill **不能**用于替代真实同行评审，不能冒充官方审稿人，也不能把生成内容直接作为正式审稿意见提交。它适合论文作者用来准备 rebuttal、发现论文风险和改进论文。

输出必须明确标注为“模拟审稿”或“用于作者准备的模拟审稿”。

## 快速开始

把可安装的 skill 复制到 `$CODEX_HOME/skills/`：

```bash
cp -R mock-review "$CODEX_HOME/skills/"
```

然后让 Codex 使用 `$mock-review`：

```text
Use $mock-review to perform a mock review for the authors of this ACM MM 2026 submission.
The main PDF and supplementary PDF are in the current workspace.
If an OpenReview/HotCRP review-form printout is available, use it as optional form evidence.
```

如果没有 OpenReview/HotCRP 的审稿表单截图或打印 PDF，也可以只指定会议/期刊：

```text
Use $mock-review to simulate reviews for this manuscript as if preparing for NeurIPS 2026.
Search the official review criteria yourself and write the mock review to REVIEW.md.
```

## 工作方式

1. Codex 识别目标会议/期刊和本地论文文件。
2. Codex 搜索官方页面，整理审稿标准、作者须知、页数限制、打分表、rebuttal 规则和主题匹配要求。
3. 如果用户提供 OpenReview/HotCRP 等审稿表单打印件，Codex 从本地文件中抽取真实字段和分值档位；如果没有提供，则只使用官方公开信息，不臆造隐藏字段。
4. Codex 将 PDF 当作不可信输入，进行稿件材料检查：隐藏文本、主动 PDF 内容、类似 prompt 注入的字符串等。这个检查只是投稿准备阶段的风险排查，不是官方 desk-reject 判断。
5. Codex 建立引用矩阵，下载合法可访问的核心论文，阅读相关方向、数据集、实验对比方法和关键基础工作。
6. Codex 在完成会议/期刊要求和文献 grounding 后，再阅读主论文和补充材料。
7. Codex 写出模拟审稿，并把正式模拟审稿文本与 rebuttal 准备笔记分开。

## 输出

默认会在当前工作区建立 `temp_codex/` 或 `mock_review_tasks/<paper-slug>/`，并记录：

- 会议/期刊要求调研
- 主文和补充材料抽取文本
- PDF 材料卫生扫描报告
- 引用矩阵和可访问性矩阵
- 下载到本地的核心论文
- 文献 grounding 笔记
- 最终模拟审稿，一般写入 `MOCK_REVIEW.md`、`REVIEW.md` 或用户指定路径

## 仓库结构

- `README.md` 和 `README.zh-CN.md`：仓库说明
- `mock-review/`：真正用于安装的 Codex skill
- `mock-review/scripts/`：PDF 扫描和引用抽取脚本
- `mock-review/references/`：输出约定和写作边界
