# GigaBrain-0.5M*: a VLA That Learns From World Model-Based Reinforcement Learning (2026)

## 基本信息
- 作者: GigaBrain Team (Boyuan Wang, Bohan Li, Chaojun Ni, Guan Huang, Guosheng Zhao, Hao Li, Jie Li, Jindi Lv, Xiaofeng Wang, Zheng Zhu 等)
- 机构: GigaAI
- arXiv: 2602.12099
- 项目: https://gigabrain05m.github.io/

## 一句话总结
GigaBrain-0.5M* 在 10K+ 小时预训练的 GigaBrain-0.5 上引入 RAMP，用世界模型预测未来状态和值作为策略条件，形成 HIL rollout → world model/policy 持续训练的闭环；相比 RECAP 只输入二值 advantage，RAMP 在 Box Packing 和 Espresso Preparation 等真机任务上约 +30pp，并在 RoboChallenge 以 51.67% 平均 SR 排名第一。

## 问题
流式 VLA 只看当前观测生成 action chunk，长时序任务缺少 future anticipation；RECAP/ACP 一类 advantage-conditioned 方法把 RL 信号压成稀疏标签，信息量不足，难以指导复杂多步物理规划。

## 方法
- 方法线归属: VLA RL 后训练 / World Model-conditioned Policy / RAMP
- 核心 idea: 将 advantage-conditioned policy 扩展为 world-model-conditioned policy，策略不仅看到改进标签，还看到世界模型预测的未来 latent state 和 value。
- 关键技术点:
  - 基座 GigaBrain-0.5 继承 GigaBrain-0 的 PaliGemma2 + flow action expert + Embodied CoT，预训练数据超过 10K 小时（约 6K 小时生成数据 + 4K 小时真机数据）。
  - RAMP 四阶段: world model 预训练、带 WM 条件的 policy 训练、HIL rollout 数据收集、rollout 数据持续训练。
  - 世界模型基于 Wan2.2，联合预测未来视觉状态、proprio 和 value；value 用 episode success 推导的 sparse return。
  - 理论上把 RECAP 写成忽略未来 latent 的退化特例；RAMP 通过 zfuture 降低动作条件熵。
  - 训练时对 future latent 和 advantage indicator 做 stochastic attention masking，支持推理时绕过 WM 的高频模式。

## 实验
- Benchmark: 8 个 GigaAI 内部真机任务、RoboChallenge 30 标准任务、RAMP value prediction 和真机 RL 对比。
- 主要结果: GigaBrain-0.5 在 Juice Preparation 达 100%，Box Packing/Espresso Preparation 分别比 π0.5 高 10%/20%；RoboChallenge 中间模型 GigaBrain-0.1 平均 SR 51.67%，高于 π0.5 的 42.67%；WM state+value 预测 MAE 0.0621、Kendall 0.8018，优于 VLM value；RAMP 在三项困难任务上接近满分，Box Packing/Espresso Preparation 较 RECAP 约 +30pp。
- 对比基线: π0、π0.5、GigaBrain-0、GigaBrain-0.5+AWR、GigaBrain-0.5+RECAP、VLM-based value、value-only WM。

## 评价
- 优势: 相比 Hi-ORS 的 outcome filtering、RLT 的轻量 actor-critic、Evo-RL/RECAP 的 advantage label，RAMP 把未来状态作为稠密条件，特别适合长时序和多任务迁移。
- 局限: 评测主要来自内部真机和项目页视频，细粒度公开复现不足；world model 条件增加训练复杂度，推理时若开启标准模式也会引入额外延迟。
- 对 VLA 领域的贡献: 将 "world model + VLA" 与 "RL post-training" 合并成闭环自改进路线，是 GigaBrain 系列从数据增强走向 model-based RL 的关键节点。
