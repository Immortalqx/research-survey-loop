# 任务文档：{{TOPIC}}

## 任务定义

- 主题：{{TOPIC}}
- 任务标识：{{TOPIC_SLUG}}
- 创建时间：{{CREATED_AT}}
- 工作区根目录：{{WORKSPACE_ROOT}}
- 任务目录：{{TASK_DIR}}

## 核心目标

- 产出一份可长期追加的中文 Markdown 综述：`./survey.md`
- 调研范围默认聚焦具身智能、计算机视觉、机器人及其交叉方向
- 优先从网络检索高质量正式来源，再补充 arXiv 与本地论文池

## 固定约束

- `task.md` 默认保持稳定，除非用户明确要求修改任务本身
- `round_log.md` 只追加，不回改历史
- `current_task.md` 每轮结束后重写
- `survey.md` 只做分类段落式追加，不生成“每篇论文一张卡片”
- 所有本地引用必须使用相对路径
- 无法下载的来源使用网络链接
- 单次 PDF 阅读不得超过 10 页

## 优先来源

- Nature / Science 及相关子刊
- CVPR / ICCV / ECCV / TPAMI / IJCV
- Science Robotics / IJRR / TRO / RA-L / RSS / ICRA / CoRL / IROS
- arXiv
- 当前工作区根目录 `papers/` 中与任务直接相关的本地 PDF

## 纳入标准

- 论文必须与主题直接相关，或对分类地图、术语统一、方法比较有明确价值
- 写入 `survey.md` 前必须明确理解研究问题、核心方法、主要贡献、关键局限
- 本地 `papers/` 中被任务吸收的论文必须迁移到 `./sources/papers/`

## 排除项

- 与主题明显无关的论文
- 只看标题或局部摘要却未读懂就写成确定结论的内容
- 继续引用根目录 `papers/` 作为综述中的 canonical path
- 未经用户明确要求时，将 `industry_report/` 混入学术主综述

## 输出要求

- 主综述文件：`./survey.md`
- 轮次记录：`./round_log.md`
- 当前任务：`./current_task.md`
- 论文与补充材料：`./sources/`

## 初始分类建议

- 先建立粗粒度分类，再逐步细化
- 示例：综述与领域全景 / world models / spatial memory / 3D scene representation / navigation / manipulation / benchmarks / evaluation

## 质量标准

- 结论可追溯到本地 PDF 或网络链接
- 术语前后一致
- 每轮都有明确的下一轮入口
- 分类结构逐步变清晰，而不是越写越散
