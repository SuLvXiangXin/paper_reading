# Scaling Helix: a New State of the Art in Humanoid Logistics (2025)

## 基本信息
- 作者: Figure AI 团队（官方页未列出个人作者）
- 机构: Figure AI
- arXiv: 不适用
- 来源类型: 官方技术页/非论文
- 发布日期: 2025-06-07
- 链接: https://www.figure.ai/news/scaling-helix-logistics

## 一句话总结
这是 Helix 物流路线的 scaling follow-up：通过将示教数据从约 10 小时扩到 60 小时，并加入 vision memory、state history、force feedback 和更大 S1 decoder，官方称包裹处理速度提升到约 4.05 秒/件、条码朝向成功率约 95%，但仍属于内部物流评测而非公开 benchmark。

## 问题
第一版物流 Helix 主要处理较规则包裹；更真实的物流场景包含 deformable poly bags、padded envelopes、flat parcels 等薄、软、易变形物体。机器人需要记住已经检查过的包裹面、处理遮挡标签、根据接触调整抓取，并在更频繁 replanning 下保持动作连续。核心问题是：数据扩展和短时记忆/触觉反馈各自如何提升高吞吐 humanoid logistics。

## 方法
- 方法线归属: VLM + 连续 visuomotor policy 的记忆与传感增强；与 VLA 记忆方法、触觉反馈和数据 scaling 组件相关。
- 核心 idea: 在 Helix S1 中加入短时视觉记忆、近期本体状态历史和力反馈，让 policy 从瞬时反应升级为有状态的 package manipulation policy，再用更多高质量示教数据和更大 decoder 释放这些输入的效果。
- 关键技术点:
  - 数据 scaling: 对相同架构/超参数比较约 10、20、40、60 小时 human demonstration trajectories。
  - Vision memory: 将最近视频帧序列的特征组合进 policy，让机器人记住包裹哪些面已检查、标签在哪个角度曾部分可见、输送带区域是否空闲。
  - State history: 将手、躯干、头部等近期本体状态窗口输入 policy，减少固定 action chunk 之间的上下文断裂，使更频繁 replanning 不破坏稳定性。
  - Force feedback: 将 Figure 02 与环境/物体交互产生的力作为状态输入，形成触觉 proxy，用于检测接触、调节抓取力和避免失衡。
  - 模型 scaling: 官方称最终将 transformer decoder head 参数量增加约 50%，在 richer inputs 下进一步降低平均处理时间。
  - Visual conditioning: 用少量人类等待 handoff 的额外示教，使同一 policy 通过视觉上下文学会把包裹递给人，而不需要新程序或 mode switch。

## 实验
- Benchmark: 无公开标准 benchmark；任务是 Figure 内部移动输送带包裹处理，指标为平均秒/件和条码正确朝向扫描成功率。
- 公开视频/内部 claim:
  - 任务范围从 rigid boxes 扩展到 poly bags、padded envelopes、flat envelopes 等，并出现拍平软包以改善条码扫描的示教学习行为。
  - 总体发布 claim：平均处理时间从约 5.0 秒/件降到 4.05 秒/件，速度约提升 20%；条码朝向成功率从约 70% 提升到约 95%。
  - 数据 scaling：约 10 到 60 小时示教使平均处理时间从约 6.84 秒/件降到 4.31 秒/件，条码成功率从 88.2% 升到 94.4%。
  - 模块 ablation：vision memory 消除重复重定向并缩短周期；state history + force feedback 提供时间和触觉上下文，使 first-pass barcode success 约 94%；更大 decoder 后平均 4.05 秒/件且成功率高于 92%。
  - 少量额外 handoff 示教让同一 policy 基于人手伸出这一视觉上下文执行 human-to-robot handover。
- 公开 benchmark:
  - 没有公开数据、模型、episode 数、测试包裹清单或第三方复现。
- 对比基线:
  - 内部 ablation：不同数据量、是否启用 vision memory/state history/force feedback/stereo/更大 decoder；无外部论文方法可复现对比。

## 评价
- 优势: 这页给出了比首个物流页更清楚的生产指标和 ablation 方向，显示短时视觉记忆、本体历史和触觉 proxy 在动态物流任务中是具体瓶颈，而不仅是锦上添花。
- 局限: “new state of the art”是官方口径，没有公开物流 humanoid benchmark 支撑；数据分布、失败定义、重置规则、统计置信度不完整；不能把内部 95% 条码朝向成功率等同于通用 VLA 成功率。
- 对 VLA 领域的贡献: 它把 VLA 记忆问题落到短时工业操作场景，与 MEM 的长短时混合记忆不同，Helix 这里更像低层 S1 的短时视觉状态与本体/触觉闭环，是 production VLA 的关键组件线索。
