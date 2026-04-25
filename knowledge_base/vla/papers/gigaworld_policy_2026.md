# GigaWorld-Policy: An Efficient Action-Centered World-Action Model (2026)

## 基本信息
- 作者: GigaWorld Team (Angen Ye, Boyuan Wang, Chaojun Ni, Guan Huang, Guosheng Zhao, Hao Li, Hengtao Li, Xiaofeng Wang, Zheng Zhu 等)
- 机构: GigaAI
- arXiv: 2603.17240
- 项目/代码: https://gigaai-research.github.io/GigaWorld-Policy/ / https://github.com/open-gigaai/giga-world-policy

## 一句话总结
GigaWorld-Policy 是 action-centered WAM：训练时用未来视觉动态提供稠密监督，推理时可关闭未来视频生成只解码动作；在 RoboTwin 2.0 上达到 0.86 simulation SR、A100 延迟 360ms，真实 PiPER 4 任务平均 0.83 SR，比 Motus 快 9x 且高 7pp。

## 问题
Cosmos Policy、DreamZero、Motus 等 WAM 通过视频/动作联合建模获得时空先验，但推理时常需要生成未来视频，带来高延迟和视频预测误差累积；传统 VLA 虽快，却缺乏稠密未来动态监督。

## 方法
- 方法线归属: World Model + VLA → 流派B 视频+动作联合建模 / Action-centered WAM
- 核心 idea: 让未来视频预测成为训练期正则和可选推理分支，而不是动作输出的必经路径，从而兼顾 WAM 的动态先验和 VLA 的低延迟。
- 关键技术点:
  - Wan2.2 5B DiT 初始化，动作 chunk 长度 48，未来观测 stride Δ=12。
  - 因果序列建模: action tokens 只 attend 当前 observation/state，future visual tokens 用 action-conditioned dynamics 预测，避免未来信息泄漏。
  - post-training 中 action loss 权重 5、video loss 权重 1，强调控制同时保留视觉一致性监督。
  - action-only decoding path 在推理时禁用 future video decoding，降低显存和延迟。
  - 预训练从通用视频模型 → embodied robot-centric 数据（真实机器人 + egocentric human video）→ target robot trajectories。

## 实验
- Benchmark: RoboTwin 2.0 50 任务（clean/randomized）、PiPER 真机 Clean Desk / QR Scan / Sweep Trash / Stack Bowls、A100 推理延迟。
- 主要结果: RoboTwin 平均 SR clean/randomized 为 0.87/0.85，接近 Motus 0.89/0.87，远高于 π0.5 0.43/0.44；A100 延迟 360ms（Motus 3231ms，Cosmos Policy 1413ms）；真机平均 SR 0.83（Motus 0.76，π0.5 0.69，Cosmos Policy 0.58）。
- 对比基线: π0.5、GigaBrain-0、X-VLA、Motus、Cosmos Policy。

## 评价
- 优势: 明确解决 WAM 的部署瓶颈，未来视频是训练期监督而非推理期刚需；比 Cosmos Policy/DreamZero 更偏实时闭环，比传统 VLA 又有视频动态先验。
- 局限: 零样本泛化与跨具身迁移不如 DreamZero 叙事完整；action-only 推理下到底保留多少 world-model 能力仍依赖训练分布。
- 对 VLA 领域的贡献: 为 WAM 方法线增加第三种定位：不是 Cosmos Policy 的 planning，也不是 DreamZero 的零样本 WAM，而是低延迟 action-centered WAM，值得在 world_model_vla 方法线中单列。
