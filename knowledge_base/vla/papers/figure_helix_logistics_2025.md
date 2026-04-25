# Helix Accelerating Real-World Logistics (2025)

## 基本信息
- 作者: Figure AI 团队（官方页未列出个人作者）
- 机构: Figure AI
- arXiv: 不适用
- 来源类型: 官方技术页/非论文
- 发布日期: 2025-02-26
- 链接: https://www.figure.ai/news/helix-logistics

## 一句话总结
该发布把 Helix 应用到物流包裹分拣/重定向，重点升级 System 1 的视觉和部署组件：隐式 stereo、多尺度视觉、learned visual proprioception 自校准、数据筛选和 action chunk 重采样的 Sport Mode；官方内部指标显示 stereo、数据质量和推理加速显著提升吞吐，但没有公开 benchmark。

## 问题
物流包裹处理要求机器人在移动输送带上抓取、翻转和重定向包裹，让面单朝向可扫描方向。包裹形状、重量、刚性和标签位置变化大，且场景持续动态流动，仿真难以完整覆盖。核心问题是：如何让 Helix 的低层 visuomotor policy 在真实工业任务中同时做到速度、深度感知、跨机器人迁移和在线纠错。

## 方法
- 方法线归属: VLM + 连续 visuomotor policy 的工业部署增强；更偏 System 1 视觉/本体校准/数据策略组件，而不是新的 VLA benchmark 论文。
- 核心 idea: 针对包裹分拣这个高吞吐任务，把 Helix S1 从单目低层策略升级为带 stereo、多尺度特征和视觉自校准的高频 action chunk policy，并用数据筛选和 test-time chunk resampling 提升速度。
- 关键技术点:
  - Implicit stereo vision: S1 使用 stereo vision backbone 和 multiscale feature extraction，将双目特征先融合再 token 化，保持输入 cross-attention transformer 的视觉 token 数不增加。
  - Multi-scale visual representation: 同时保留细粒度物体边缘/标签信息和场景级上下文，用于更稳定的抓取与重定向。
  - Learned visual proprioception: 从 onboard 视觉估计末端 6D pose，用在线自校准缓解不同机器人传感器标定、关节响应差异导致的 observation/action shift。
  - 数据筛选: 剔除慢、miss、操作员失败的示教；保留由于环境随机性引发的纠错行为，并和遥操作员统一操作策略。
  - Sport Mode: S1 输出 200Hz action chunk；测试时将长度为 T 的 chunk 线性重采样为更短轨迹并仍以 200Hz 执行，从而不改训练过程即可加速。

## 实验
- Benchmark: 无公开标准 benchmark；评测是 Figure 内部物流场景的 normalized effective throughput `T_eff`，以示教者轨迹速度为参照。
- 公开视频/内部 claim:
  - 官方称 8 小时高质量示教即可得到灵巧、灵活的物流策略。
  - 加入 multiscale + stereo 后，stereo 模型相对非 stereo baseline 吞吐提升约 60%，并能泛化到训练未见的 flat envelopes。
  - curated 高质量数据相比更多但质量较低的数据，在少约 1/3 数据量的情况下吞吐高约 40%。
  - Sport Mode 在最高约 50% test-time speedup 前仍有效，50% 加速时 `T_eff > 1`，即超过示教轨迹的有效吞吐。
  - learned calibration 支持单机器人数据训练的 policy 迁移到多台机器人，并保持相近操作表现。
- 公开 benchmark:
  - 未公开数据、模型、episode 数、置信区间或外部复现实验。
- 对比基线:
  - 内部 ablation：单目/非 multiscale/stereo、数据质量配置、不同 Sport Mode 加速比例；没有与 π0、OpenVLA 等外部 VLA 的可复现对比。

## 评价
- 优势: 这页对 production-like VLA 很有价值，强调了 stereo 几何、视觉自校准、示教质量和 action chunk 时间重采样这些工程组件，而不是只讨论 backbone scaling。
- 局限: 指标是内部物流吞吐，任务分布和统计细节不足；“faster-than-demonstrator”依赖 `T_eff` 定义，不能直接和学术 benchmark 成功率互换；没有给出 S1 架构、数据和训练细节到可复现程度。
- 对 VLA 领域的贡献: 它补充了 Helix 路线的工业化细节：高频 action chunk policy 在真实动态场景里需要 3D 感知、自校准和数据质量控制，和现有 VLA taxonomy 中的视觉编码器、动作 chunk、数据策略组件相关。
