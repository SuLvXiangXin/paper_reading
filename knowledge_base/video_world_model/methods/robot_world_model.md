# 通用机器人世界模型

> 子方向：用动作条件视频生成来模拟机器人未来状态，目标是支持策略评估、在线规划、实时遥操作和机器人数据扩展。

---

## 技术路线概述

机器人世界模型和通用视频生成模型的核心差异不在画质，而在**动作可控性**和**评估可信度**：同一初始观测下，不同动作序列必须产生不同且物理合理的未来，并且生成结果要能反映真实策略的成功/失败趋势。

| 路线 | 代表工作 | 数据来源 | 动作条件 | 主要用途 |
|------|----------|----------|----------|----------|
| 策略评估型世界模型 | [1X World Model](../papers/1x_world_model_2025.md) | web-scale 视频 + 1X 机器人 rollout | 机器人低层动作 latent | checkpoint / 架构 / 数据选择 |
| 人类视频预训练型通用机器人世界模型 | [DreamDojo](../papers/dreamdojo_2026.md) | 44k 小时第一视角人类视频 + 少量目标机器人数据 | 连续 latent action -> 目标机器人连续动作 | OOD 接触交互模拟、策略评估、模型预测规划、实时遥操作 |

---

## 关键问题

### 1. 动作可控性而非单纯视频质量
- 机器人世界模型必须学习 `p(s_{t+1} | s_t, a_t)`，不能只是从初始帧生成一个 plausible future。
- 反事实动作尤其关键：miss、pat、fast reach、失败抓取等动作在专家演示中少见，却决定模型能否用于评估和规划。

### 2. 数据覆盖与 embodiment gap
- 真实机器人数据采集成本高、硬件差异大，单一机器人数据很难覆盖开放世界物体、场景和技能。
- 人类视频覆盖广，但缺少机器人动作标签；直接 action-free 预训练只能学习物理外观，难以学习动作-结果因果关系。
- DreamDojo 的连续 latent action 将人类视频中的动作变化压缩为统一代理动作，先学习交互动力学，再用目标机器人数据把代理动作空间适配到机器人动作空间。

### 3. 离线评估到在线交互
- 1XWM 证明视频世界模型可用于离线 policy evaluation，但偏 task-specific。
- DreamDojo 进一步把世界模型蒸馏到实时自回归推理，使其能接入 live teleoperation 和 test-time model-based planning。

---

## DreamDojo 方法线

### 人类视频预训练
- 以 DreamDojo-HV、EgoDex、In-lab 构成大规模第一视角交互视频混合，总量约 44,711 小时。
- 用自监督 latent action model 从相邻帧中抽取连续动作 embedding，作为所有人类视频的统一动作标签。
- 相比 action-free 预训练，latent action 预训练更直接地保留动作因果信息，后训练到机器人动作空间时上界更高。

关键实现：
- latent action model 是 700M spatiotemporal Transformer VAE，输入相邻帧，输出 32 维连续动作 embedding，再用该 embedding 和前一帧重建后一帧。
- bottleneck + KL 正则让 embedding 更像“动作变化量”，而不是图像内容压缩，因此可跨人类手部、机器人和不同采集设备使用。
- 在世界模型预训练时，latent action 经 MLP 投影后加到 timestep embedding 中，并进入 DiT block 的 adaptive layer norm；MLP 最后一层零初始化，减少对 Cosmos-Predict2.5 初始能力的扰动。

### 目标机器人后训练
- 机器人动作转为相对动作，降低不同轨迹/姿态下的建模复杂度。
- 按视频 tokenizer 的时间压缩比进行 chunked action injection，让每个 video latent 只接收对应时间窗口的动作，减少未来动作污染当前预测。
- 在 flow matching 外加入 temporal consistency loss，直接约束相邻 latent 的动态变化。

关键实现：
- DreamDojo 基于 Cosmos-Predict2.5 / WAN2.2 latent video diffusion，标准训练目标是 flow matching。
- WAN2.2 的时间压缩比为 4，因此每个 latent frame 对应 4 个像素帧；DreamDojo 将 4 个连续机器人动作拼成 action chunk，只注入到对应 latent。
- temporal consistency loss 约束预测 velocity 的相邻差分与 GT velocity 的相邻差分一致，目标是提升动作跟随、物体完整性和接触动态。
- 后训练时重置 action MLP 第一层以匹配目标机器人动作空间，其余权重全量 finetune；默认 13 帧 clip，第一帧作条件，后续 12 步为 relative actions。

### 实时自回归蒸馏
- 将 bidirectional diffusion teacher 蒸馏为 causal autoregressive student。
- 训练时让 student 使用自己的历史输出作为上下文，缓解 rollout 分布和训练分布不一致。
- DreamDojo 的 student 在 GR-1 长时评测中达到 10.81 FPS，并拥有 12 帧上下文，适合实时遥操作和在线规划。

关键实现：
- student 继承 teacher 权重，但把双向 attention 换成 causal attention，并将去噪步数减少到 4。
- warmup 阶段用 teacher ODE trajectory 监督 student；distillation 阶段用 student 自己生成的历史帧作为上下文，再用 distribution matching loss 对齐 teacher 分布。
- 训练时让 student 生成长于 teacher horizon 的序列，再随机抽窗口回传梯度，以模拟长时交互中的误差积累。

---

## 与 1X World Model 的关系

| 维度 | 1X World Model | DreamDojo |
|------|----------------|-----------|
| 目标 | 策略离线评估 | 通用动作条件机器人模拟 + 评估/规划/遥操作 |
| 数据重点 | 机器人 rollout，尤其自主失败数据 | 大规模人类第一视角视频 + 少量目标机器人数据 |
| 动作接口 | 机器人动作 latent | 连续 latent action 代理动作，后训练适配机器人动作 |
| 泛化重点 | 任务内 checkpoint / 架构选择 | 未见物体、未见环境、反事实动作 |
| 输出能力 | 未来视频 + state value | 未来视频，外接 value model 做规划/评估 |

---

## 关键概念

| 概念 | 定义 | 相关工作 |
|------|------|----------|
| 连续 latent action | 从相邻视频帧中自监督抽取的低维连续动作 embedding，用作无标注视频的代理动作条件 | DreamDojo, AdaWorld |
| 人类视频预训练 | 用大规模第一视角人类交互视频学习物体动力学和接触先验，再迁移到机器人 embodiment | DreamDojo |
| Relative Action Rebaselining | 将绝对机器人关节/末端位姿改写为相对初始姿态的动作，降低动作空间复杂度 | DreamDojo |
| Chunked Action Injection | 按视频 latent 的时间压缩窗口注入对应动作片段，避免未来动作干扰当前 latent 预测 | DreamDojo |
| World Model as Evaluator | 用世界模型预测策略执行后果，并用生成结果或 value head 判断策略优劣 | 1XWM, DreamDojo |

---

## 开放问题

1. **失败建模偏乐观**：生成式世界模型容易产生比真实世界更顺滑的成功过程，细粒度失败和接触不稳定仍难模拟。
2. **多视角支持不足**：当前机器人策略常用多相机输入，单视角视频世界模型难以直接替代完整仿真器。
3. **预训练知识保持**：目标机器人后训练可能遗忘人类视频中的广泛交互知识，参数高效适配和正则策略仍值得研究。
4. **实时性与质量权衡**：少步自回归蒸馏能达到在线速度，但长时质量和罕见动作仍低于慢速 teacher。
