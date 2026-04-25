# Project Go-Big: Internet-Scale Humanoid Pretraining and Direct Human-to-Robot Transfer (2025)

## 基本信息
- 作者: Figure AI 团队（官方页未列出个人作者）
- 机构: Figure AI
- arXiv: 不适用
- 来源类型: 官方技术页/非论文
- 发布日期: 2025-09-18
- 链接: https://www.figure.ai/news/project-go-big

## 一句话总结
Project Go-Big 是 Figure 面向 humanoid 的人类 egocentric 视频预训练计划：借 Brookfield 大规模住宅/办公/物流场景收集人类目标导向行为，并报告 Helix 仅用 100% 人类第一视角视频训练即可 zero-shot 输出机器人 SE(2) 导航控制、执行 speech-to-nav；这是重要数据路线信号，但缺少公开数据规模、模型细节和 benchmark。

## 问题
机器人学习缺少类似 YouTube/Wikipedia 的大规模行为数据源，而逐个机器人遥操作采集昂贵且环境分布窄。Humanoid 与人类在视角和运动结构上更接近，因此 Figure 希望直接利用日常人类第一视角视频学习家庭导航/操作策略。核心问题是：人类 egocentric video 是否能成为 humanoid VLA 的大规模预训练数据，并在没有机器人示教的情况下迁移到真实机器人控制。

## 方法
- 方法线归属: Human Data Pretraining for VLA / egocentric human video；在 Helix 路线中首先展示导航方向的人类视频到机器人迁移。
- 核心 idea: 把人类在真实家庭中的被动第一视角视频作为 goal-directed behavior 数据，训练 Helix 从像素和语言直接输出机器人导航控制，使同一网络同时覆盖 dexterous manipulation 和 speech-conditioned navigation。
- 关键技术点:
  - 数据计划: Figure 宣布 Project Go-Big，借 Brookfield 场景扩大数据采集；官方描述 Brookfield 拥有超过 100,000 个住宅单元、500 million square feet 办公空间和 160 million square feet 物流空间。
  - 数据模态: 官方强调 egocentric human video，记录人在真实环境中如何完成目标；页面没有披露标注格式、动作提取方式或训练规模。
  - 直接 human-to-robot transfer: 官方称 navigation 结果使用 100% 人类第一视角视频训练，没有机器人示教或 robot-specific data/training。
  - 输出动作: 对导航任务，Helix 从图像和自然语言端到端输出低层 SE(2) velocity commands。
  - 统一模型: 同一 Helix network 同时输出高频灵巧操作动作和导航命令，而不是按任务或数据源拆成多个系统。

## 实验
- Benchmark: 无公开标准 benchmark；没有 VLN、真实家庭导航成功率、路径效率或碰撞率等公开协议。
- 公开视频/内部 claim:
  - 官方视频展示在 Brookfield 家庭环境中，从自然语言命令如走到厨房桌、去浇植物等，闭环导航穿过杂乱真实空间。
  - 官方称这是 Helix 首次仅从人类 egocentric video 迁移到 humanoid 机器人导航控制，且不使用机器人示教。
  - 官方称同一模型覆盖 manipulation 与 navigation。
- 公开 benchmark:
  - 未提供数据规模、训练配方、评测集、success rate 或与机器人示教训练 baseline 的数值对比。
- 对比基线:
  - 没有外部 baseline；主要是与传统昂贵机器人示教/手写程序的定性对照。

## 评价
- 优势: 它把 Figure 路线从“机器人遥操作数据训练上半身操作”扩展到“人类第一视角视频预训练导航/家庭行为”，和 EgoScale、Being-H0/H0.5 等人类数据路线形成呼应。
- 局限: 这更像数据战略和早期 demo，而不是完整技术论文；没有说明如何从无动作人类视频监督 SE(2) velocity，也没有公开消融来区分人类视频、语言标注、环境覆盖和模型容量的贡献。
- 对 VLA 领域的贡献: 对 taxonomy 的意义在于提示 humanoid VLA 可能出现一条“互联网规模 egocentric human behavior pretraining -> robot navigation/manipulation transfer”路线；目前证据强度低于有论文/benchmark 的 EgoScale、Being-H0.5。
