# DreamDojo: A Generalist Robot World Model from Large-Scale Human Videos (2026)

## 基本信息
- 作者: Shenyuan Gao, William Liang, Kaiyuan Zheng, Ayaan Malik 等
- 机构: NVIDIA + HKUST + UC Berkeley + UW + Stanford + KAIST + UofT + UCSD + UT Austin
- arXiv: 2602.06949
- 项目页面: https://dreamdojo-world.github.io/
- 日期: 2026.02

## 标签
- domain: video_world_model
- method_tags: [通用机器人世界模型, 人类视频预训练, 连续 latent action, 自回归蒸馏]
- task_tags: [动作条件视频预测, 机器人策略评估, 模型预测规划, 实时遥操作]
- component_tags: [连续 latent action, relative action, chunked action injection, temporal consistency loss, Self-Forcing distillation]
- benchmark_tags: [In-lab Eval, EgoDex Eval, DreamDojo-HV Eval, Counterfactual Eval, GR-1 Long Eval]
- data_tags: [DreamDojo-HV, EgoDex, In-lab, GR-1, AgiBot]
- robot_tags: [Fourier GR-1, Unitree G1, AgiBot, YAM]
- application_tags: [policy evaluation, model-based planning, live teleoperation]

## 一句话总结
DreamDojo 用 4.4 万小时第一视角人类交互视频和连续 latent action 预训练动作可控的视频世界模型，再用少量目标机器人数据后训练，使模型能在未见物体/环境中模拟接触丰富的机器人未来，并支持策略评估、模型预测规划和实时遥操作。

## 问题
现有机器人视频世界模型主要依赖有限机器人遥操作数据，覆盖的物体、场景和反事实动作不足，导致 OOD 接触交互中物理建模和动作响应弱；而大规模人类视频虽然丰富，却缺少统一、细粒度的动作标签，直接做 action-free 预测难以学习动作-结果因果关系。同时，扩散式世界模型推理慢，难以用于在线规划和实时交互。

## 方法
- 方法线归属: 通用机器人世界模型 -> 人类视频预训练 + latent action proxy + 目标机器人后训练 + 自回归蒸馏
- 核心 idea: 机器人世界模型需要学习 `p(s_{t+1}|s_t,a_t)`，但机器人视频少、人类视频多且无动作标签。DreamDojo 的解法是先把无标注人类第一视角视频转成“带代理动作”的训练数据，学习开放世界接触动力学；再用少量目标机器人数据把代理动作接口换成真实机器人连续动作；最后把慢速双向扩散 teacher 蒸馏成实时因果自回归 student。
- 详细流程:
  - **阶段 1: 人类视频预训练数据**。预训练混合包含 In-lab、EgoDex 和 DreamDojo-HV，总计 44,711 小时、约 1.179M trajectories。DreamDojo-HV 是主体，含 43,827 小时众包第一视角视频，覆盖家庭、工业、零售、教育、行政等场景，以及 6,015 个技能和 43,237 个物体。In-lab 带 Manus glove + Vive tracker，可验证真动作标注上界；EgoDex 带 Apple Vision Pro 手/指姿态，可补充日常灵巧操作。
  - **阶段 2: continuous latent action 作为 proxy action**。作者训练一个 700M spatiotemporal Transformer VAE：encoder 输入相邻两帧 `f_t, f_{t+1}`，输出 32 维连续 latent action；decoder 输入 `f_t` 和 latent action 重建 `f_{t+1}`。低维瓶颈和 KL 正则迫使 embedding 保留“使后一帧发生变化的动作信息”，而不是完整场景外观，因此可跨人手、机器人和不同采集设备复用。
  - **阶段 3: 动作条件世界模型预训练**。底座是 Cosmos-Predict2.5 latent video diffusion，使用 WAN2.2 tokenizer 和 flow matching。对每段视频先抽取 latent actions，再用轻量 MLP 投到 timestep embedding 维度，和 timestep embedding 相加后进入 DiT block 的 adaptive layer norm。action MLP 最后一层零初始化，避免一开始破坏预训练视频模型。
  - **阶段 4: 机器人动作接口设计**。目标机器人后训练时不用绝对关节位姿，而是把动作重置为相对每个 latent frame 起始姿态的 relative action，降低不同初始姿态下的动作分布跨度。由于 WAN2.2 时间压缩比为 4，每个 video latent 对应 4 帧，模型把连续 4 个动作组成 chunk，只注入到对应 latent frame，避免把未来动作作为全局条件污染当前预测。
  - **阶段 5: temporal consistency loss**。除标准 flow matching 外，额外约束相邻 latent 的预测速度差：让 `(z_{i+1}-z_i)` 对齐 GT velocity difference `(v_{i+1}-v_i)`。这个 loss 比逐帧重建更直接地监督物体运动、接触变化和动作响应，实验中能提高 action following、物体完整性并减少 artifact，最终目标为 `L_flow + 0.1 L_temporal`。
  - **阶段 6: 目标机器人后训练**。在人类视频预训练后，针对 GR-1、G1、AgiBot、YAM 等目标 embodiment，将 action MLP 第一层重置为目标动作空间，其余权重连同世界模型全量 finetune。默认后训练用 13 帧 clip，第一帧作条件帧，后续 12 步动作作 relative action，约 10 Hz 采样。
  - **阶段 7: 实时自回归蒸馏**。teacher 是后训练后的双向扩散模型，推理慢且固定 horizon。student 继承 teacher 权重，但把 bidirectional attention 换成 causal attention，并把去噪步数从 35/50 类设置缩到 4。蒸馏先 warmup，让 student 拟合 teacher ODE trajectory；再让 student 用自己的历史输出作上下文，通过 distribution matching loss 贴近 teacher 分布，从而缓解长时 rollout 的 train-test gap。训练时还让 student 生成超过 teacher horizon 的长片段，并随机取窗口回传梯度，提高长时鲁棒性。
- 关键技术点:
  - **为什么 latent action 比 action-free 预训练重要**: action-free 只能学“从画面猜 plausible future”，容易忽略同一初始帧下不同动作导致不同后果；latent action 把人类视频变成动作条件数据，使预训练阶段就学习动作-结果因果。
  - **为什么不用 MANO/手套动作作统一标签**: 这些标签需要额外设备或强人体估计器，且主要描述手部，难覆盖手臂、身体移动、遮挡和跨 embodiment 迁移；latent action 从像素自监督抽取，成本更低、格式统一。
  - **为什么要 relative + chunked action**: relative action 降低连续动作空间复杂度；chunked injection 保持动作和 video latent 的时间因果对齐，是反事实动作可控性的关键工程设计。
  - **为什么蒸馏不只是加速**: student 的 causal autoregressive 结构可以用 12 帧上下文滚动生成，比 teacher 的单条件帧更适合遮挡、相机抖动和实时交互。

## 实验
- Benchmark: In-lab Eval、EgoDex Eval、DreamDojo-HV Eval、Counterfactual Eval、EgoDex-novel Eval、DreamDojo-HV-novel Eval、GR-1 Long Eval；下游还评估 AgiBot fruit packing。
- 主要结果: latent action 预训练明显优于 action-free 预训练，并接近带额外采集设备的 retargeted action / MANO 上界；DreamDojo-14B 在 In-lab、EgoDex、DreamDojo-HV 和 Counterfactual OOD 评测上均优于直接后训练 Cosmos-Predict2.5，人评中相对 Cosmos-Predict2.5 的 physics correctness / action following 胜率分别为 73.50% / 72.55%。相对动作、chunked injection 和 temporal loss 叠加后，Counterfactual Eval PSNR 从 19.448 提升到 20.980。蒸馏 student 达到 10.81 FPS，虽低于 teacher 质量但具备实时滚动交互能力。策略评估中 DreamDojo success rate 与真机 success rate Pearson r=0.995、MMRV=0.003；模型预测规划在 AgiBot fruit packing 中最高带来 17% 绝对成功率提升，并较均匀采样接近 2x。
- 对比基线: Cosmos-Predict2.5 直接后训练、action-free human video pretraining、retargeted action / MANO 理想动作标注、不同人类数据混合规模、teacher vs distilled student。

## 评价
- 优势: 把机器人世界模型的覆盖来源从昂贵机器人数据扩展到大规模人类第一视角视频；连续 latent action 是比被动视频预训练更适合动作可控迁移的接口；系统性覆盖 OOD 物体、未见环境、反事实动作和下游策略评估/规划，定位比 1XWM 更接近通用机器人模拟器。
- 局限: 仍依赖超大规模私有视频与 H100 训练资源；对罕见快速动作和失败细节建模不足，策略评估存在偏乐观倾向；当前主要是单视角模拟，不天然支持多视角状态估计；后训练如何最大程度保留人类视频预训练知识仍未充分研究。
- 对视频世界模型领域的贡献: 提供了“人类视频 -> latent action 代理动作 -> 目标机器人后训练 -> 实时 AR 蒸馏”的通用机器人世界模型路线，说明视频世界模型不只服务通用视频生成，也可以成为机器人策略评估、在线规划和虚拟遥操作的基础仿真层。
