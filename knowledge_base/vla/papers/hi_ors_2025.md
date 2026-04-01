# Hi-ORS: Human-in-the-loop Online Rejection Sampling for Robotic Manipulation

## 基本信息
- **arXiv**: 2510.26406 (2025.10.30)
- **作者**: Guanxing Lu, Rui Zhao†, Haitao Lin, He Zhang, Yansong Tang（Tsinghua SIGS + Tencent Robotics X）
- **方法线归属**: **VLA RL 后训练 / Rejection Sampling Post-training**
- **关键词**: VLA post-training, rejection sampling, human-in-the-loop, flow matching supervision, test-time scaling

## 核心问题

**RL fine-tune VLA 为什么不稳定？** 本文识别出两大根本原因：

- **I1: 不准确的值估计**（Inaccurate Value Estimation）
  Q 函数在高维动作空间（action chunking 指数扩大动作空间）中难以准确估计，易出现 overestimation，导致不稳定更新。

- **I2: 低效的监督信号**（Inefficient Supervision）
  RL 只监督最终动作 `log πθ(at|st)`，忽略了 VLA 的中间计算（flow matching 的迭代去噪步骤、autoregressive 的 token 预测），信号稀疏。

## 方法：Hi-ORS

用**拒绝采样**代替价值函数，同时提供密集中间步骤监督。

### B1. Rejection Sampling（解决 I1）
- **评估阶段**：对当前策略生成的轨迹计算累计奖励 R(τ)，按阈值过滤：
  `Im(τ) = 1[R(τ) ≥ m]`
  只保留真实成功轨迹，完全避免 Q 函数 overestimation。
- **渐进阈值调度**：m₁ ≤ m₂ ≤ ... ≤ mN，随训练进行提高门槛，保证单调提升。
- **奖励**：人工标注二值奖励（任务完成=1），不用学习的 reward model。

### B2. Reward-Weighted Flow Matching（解决 I2）
- **改进阶段**：用接受轨迹做加权监督：
  `L = E[Im(τ) · ||vθ(u, st, xu) − (x1 − x0)||²]`
  在所有去噪时间步 u 上都监督速度场，提供密集学习信号（不只监督最终动作）。
- 对 autoregressive VLA 则监督所有 token 预测步骤。

### C. 人类干预（Varied Frequency）
- 支持任意时刻介入：相对末端控制 / 绝对关节控制，多次介入可产生混合人机轨迹。
- **高频记录**（人类介入期）+ **低频执行**（自主期）：人类精细修正行为被密集捕获，同时避免自主期的抖动。
- 关键：只保留最终 R(τ) ≥ m 的人类修正轨迹，防止劣质干预污染数据。
- 效果：提供 error-recovery 的反事实示教（展示在即将失败的状态下该怎么做）。

### D. 异步 Actor-Learner 基础设施
- 1 GPU 在线推理 + G-1 GPU 并行学习（ZeRO-2），推理/学习流水线分离。
- 吞吐提升 ~2×，机械臂暂停时训练仍可继续。
- 延迟构成：模型推理 ~160ms + 通信 ~400ms + 动作执行 ~900ms，每轮训练 ~1.5s，自然 UTD ≈ 1。

## 实验结果

**3 个真机任务，2 种本体**（Paxini Tora One 人形机器人 + Dobot X-Trainer 协作臂）：

| 任务 | 难度 | Hi-ORS | HIL-SERL | Q-Chunking | BC |
|------|------|--------|----------|------------|----|
| Raise-Hand | 简单 | ~100% | ~100%（有震荡回退） | 较低 | 较低 |
| Pack-Detergent | 中等 | 最高 | 发散 | 次优 | 低 |
| Insert-Moisturizer | 困难（接触丰富） | **80%** @ 1.5h | 不收敛 | 次优 | ~57% |

- **vs BC**：平均 +23.3%
- **vs HIL-SERL**：无后期震荡回退；困难任务 HIL-SERL 不收敛，Hi-ORS 稳定收敛
- **vs Q-Chunking**：Hi-ORS 的 outcome-based 估计优于 distillation loss 稳定训练

### Test-Time Scaling
- Insert-Moisturizer 上展示 trial budget 可扩展性：1 次→50%, 2 次→60%, 3 次→80%
- BC 无此效应（重试后基本不提升），说明 Hi-ORS 学会了真正的 error-recovery 而非单次投机

### 消融（Insert-Moisturizer）
| 变体 | 训练时间 | 成功率 |
|------|----------|--------|
| **Hi-ORS** | **1.5h** | **80%** |
| Cyclical Scheduler | 1.3h | 50% |
| Reward Classifier（替代人标奖励） | 1.5h | 60% |
| 去除 Human Correction | — | **0%**（完全无法完成） |
| 去除 No-ops Filter | 2.2h | 20% |
| 去除 Short Episode Filter | 1.5h | 60% |
| 固定 5-step 执行频率 | 1.0h | 10% |
| 固定 25-step 执行频率 | 1.5h | 40% |

关键发现：
- **人类干预不可缺少**（去除后 0%）：没有人类示教 error recovery 行为几乎无法靠自主探索发现
- **Reward Classifier 有害**：在人类修正数据上产生 false positive，污染训练
- **数据过滤至关重要**：no-ops filter 和 short episode filter 缺一不可
- **Varied Frequency 关键**：高/低频自适应策略显著优于任意固定频率

## 与相关工作的关系

### 同类 VLA RL 后训练工作
| 方法 | 核心机制 | 局限 |
|------|---------|------|
| **HIL-SERL** [Luo+2024] | 价值函数 RL + 人类介入 | 高维 action space 下值估计不准，不稳定 |
| **Q-Chunking** [Li+2025] | Action chunking RL + distillation loss | 主要在仿真验证，蒸馏损失限制进一步提升 |
| **PA-RL** [Mark+2024] | 监督目标稳定在线训练 | 动作优化仍依赖精确值估计，与 HITL 冲突 |
| **iRe-VLA** [Guo+2025] | IL/RL 交替训练 | 主要仿真验证 |
| **Hi-ORS（本文）** | **拒绝采样 + reward-weighted flow 监督** | 完全 value-free，实际真机验证 |

### 人类在回路相关工作
- **RaC** [Hu+2025]：专注 error recovery 数据收集，仍重度依赖人力，无自我改进
- **Hi-ORS**：保留监督学习目标的同时实现自我改进（online filtered self-training）

### LLM 拒绝采样类比
从 STaR [Zelikman+2022] 和 ReST [Gulcehre+2023] 等 LLM 迭代自我改进方法迁移到机器人学习：
- LLM：采样多个候选回答 → 过滤通过验证的 → 在其上重训练
- Hi-ORS：online rollout → reward 过滤 → reward-weighted 监督（+ 密集中间步骤）

## 技术细节

### 基础模型
- **π₀**（PaliGemma-3B backbone + 300M flow matching action expert）
- 方法论上适用于任意 flow matching VLA 或 autoregressive VLA

### 数据过滤流水线
1. 去除 no-ops（末端变换范数 < 阈值）→ 防止卡顿影响 action chunking
2. 去除极短 episode → 防止错误的动作 chunk 边界
3. 奖励门控（Im(τ) = 1[R(τ) ≥ m]）→ 只保留成功轨迹

### 动态阈值
- 随训练迭代提高奖励门槛，确保数据质量单调提升（类似 self-play 难度渐进）

## 局限性与未来工作
- 仅在 3 个任务和 2 种本体上验证，未扩展到多任务或长时序
- 随机环境下 acceptance threshold scheduler 可能偏向高方差结果
- 人类干预不可缺少（纯自主版本 0% 成功）——如何降低人力依赖值得研究
