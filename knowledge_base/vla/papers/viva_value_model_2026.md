# ViVa: A Video-Generative Value Model for Robot Reinforcement Learning (2026)

## 基本信息
- 作者: Jindi Lv, Hao Li, Jie Li, Yifei Nie, Fankun Kong, Yang Wang, Xiaofeng Wang, Zheng Zhu, Chaojun Ni, Qiuping Deng, Hengtao Li, Jiancheng Lv, Guan Huang
- 机构: GigaAI, Sichuan University, Tsinghua University
- arXiv: 2604.08168
- 项目: https://viva-value-model.github.io/

## 一句话总结
ViVa 把预训练视频生成模型改造成价值函数：输入当前多视角图像和 proprioception，联合预测未来 proprioception 与当前 state value；接入 RECAP 后，Box Assembly 真机成功率从 RECAP(VLM) 的 58% 提到 73%，吞吐从 11 提到 14 tasks/hour。

## 问题
RECAP/ACP 类 RL 后训练依赖 value model 估计 advantage，但 VLM-based value function 主要看静态图像语义，容易把时间推进误判为任务进度，不能可靠识别中途错误、柔性物状态变化或长时序动态。

## 方法
- 方法线归属: VLA RL 后训练 / 视频生成价值模型 / Reward-Value Learning
- 核心 idea: 价值估计本质是预测未来是否会成功，因此应使用具备时空动态先验的视频生成模型，而不是静态 VLM 分类器。
- 关键技术点:
  - 基于 Wan2.2 video DiT，通过 latent injection 在不改核心架构的情况下加入 proprioception 和 scalar value latent frame。
  - clean conditioning frames 包含 blank/proprio/multi-view images；target frames 是 future proprioception 和 value。
  - value 监督来自 episode success 构造的 normalized return，成功轨迹随进度增长，失败轨迹与成功区间分离。
  - 联合预测 future proprioception + value；消融显示只预测 value 更快但准确性和异常敏感性下降。
  - RECAP 中直接替换 VLM-based value，policy 训练流程保持一致。

## 实验
- Benchmark: shirt folding、box packaging and assembly、toilet paper organization 的 value 质性分析；box assembly 真机 RECAP 对比；pants folding OOD value generalization。
- 主要结果: Box Assembly 真机 π0.5 42%、GigaBrain-0 53%、RECAP(VLM) 58%、RECAP(ViVa) 73%；ViVa 吞吐 14 tasks/hour；训练 4 GPU·days、推理 0.18s/frame，比 VLM value 的 6 GPU·days、0.32s/frame 更省。
- 对比基线: π0.5、GigaBrain-0、RECAP with VLM value、video-based value-only variant、ViVa without future proprioception。

## 评价
- 优势: 把视频模型用于 value estimation 而非 policy/world rollout，定位清晰；能在错误发生时 value 下跌，在关键阶段 value 上升，对 deformable/assembly 任务比静态 VLM 更可信。
- 局限: 真机定量只集中在 box assembly，其他任务主要为价值曲线质性分析；仍依赖 RECAP 长 rollout 周期，未证明大规模多任务 RL 闭环效率。
- 对 VLA 领域的贡献: 为 VLA RL 后训练补上"视频先验价值函数"组件，可与 RAMP 的 state+value world model、Evo-RL 的 ACP、RLT 的 critic 表征形成价值信号设计谱系。
