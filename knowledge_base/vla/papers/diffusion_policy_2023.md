# Diffusion Policy: Visuomotor Policy Learning via Action Diffusion (2023)

## 基本信息
- 作者: Cheng Chi*, Zhenjia Xu*, Siyuan Feng, Eric Cousineau, Yilun Du, Benjamin Burchfiel, Russ Tedrake, Shuran Song
- 机构: Columbia University, Toyota Research Institute (TRI), MIT
- arXiv: 2303.04137
- 发表: RSS 2023（会议版），后扩展为 IJRR 期刊版
- 开源: ✅ 完全开源（代码、数据、训练细节）
- 链接: diffusion-policy.cs.columbia.edu

## 一句话总结
首次将 DDPM 扩散模型系统性地引入机器人视觉运动策略（visuomotor policy），通过将策略表示为条件去噪扩散过程，结合 action sequence prediction + receding horizon control + visual conditioning，在 4 个 benchmark 共 15 个任务上以平均 46.9% 的提升全面超越当时 SOTA（IBC、LSTM-GMM、BET），奠定了扩散模型在机器人策略学习中的基础。

## 问题
行为克隆（Behavior Cloning）中的策略学习面临三大核心挑战：
1. **多模态动作分布**: 人类示教数据在同一观测下可能对应多种合理动作（如从左绕或从右绕），传统显式策略（直接回归动作）会产生 mode averaging
2. **高维动作空间**: 预测动作序列（而非单步动作）对时间一致性至关重要，但高维输出空间使得现有方法（IBC 的采样、GMM 的模式数）难以有效建模
3. **训练不稳定**: 隐式策略（IBC）理论上能处理多模态，但基于 EBM 的 InfoNCE 训练需要负采样来估计归一化常数，导致严重的训练不稳定

**核心问题**: 如何设计一种策略表示，能够同时优雅地处理多模态动作分布、高维动作序列预测，并且训练稳定？

## 方法
- **方法线归属**: **Diffusion Policy（单任务/少任务 BC）**——这是一个独立的方法类别，是后续所有 "Diffusion/Flow Head" 方法线的技术源头
  - 直接影响: Octo 的 diffusion action head、π₀ 的 flow matching action expert
  - 与 VLM+Diffusion/Flow Head 的区别: Diffusion Policy 不使用预训练 VLM，是面向单任务/少任务的端到端视觉运动策略；后续工作将其思想扩展到跨具身大规模预训练场景
- **核心 idea**: 将机器人策略建模为条件去噪扩散过程——从高斯噪声出发，通过 K 步迭代去噪生成动作序列，每步由学到的 score function 梯度场指导。这使策略天然支持多模态分布、高维输出，且训练无需估计归一化常数（绕过了 EBM 训练不稳定的根源）。

### 关键技术点:

#### 1. 条件 DDPM 策略 (核心公式)
- **去噪过程**: A^{k-1}_t = α(A^k_t - γε_θ(O_t, A^k_t, k) + N(0, σ²I))
  - 从高斯噪声 A^K_t 出发，迭代 K 步去噪到 A^0_t
  - ε_θ 预测噪声（等价于预测 score function ∇log p(a|o) 的负值）
- **训练目标**: L = MSE(ε_k, ε_θ(O_t, A^0_t + ε_k, k))——直接监督噪声预测，无需归一化常数
- **关键设计**: 观测 O_t 作为**条件**（而非联合分布的一部分），去噪过程只作用于动作空间
  - vs Diffuser (Janner et al. 2022): 联合建模 p(A_t, O_t)，需要推断未来状态，慢且不准
  - 条件化使得视觉编码器只需前向一次（不随去噪步增加计算）

#### 2. 闭环动作序列预测 (Action Sequence + Receding Horizon)
- **三个时间尺度**:
  - 观测 horizon T_o: 输入最近 T_o 步的观测
  - 预测 horizon T_p: 预测未来 T_p 步动作
  - 执行 horizon T_a: 只执行前 T_a 步，然后重新规划
- **设计理由**:
  - T_p > 1: 联合预测动作序列保证时间一致性（避免连续帧从不同模态采样导致的 jittery 动作）
  - T_a << T_p: 执行一部分后重新规划，保持闭环响应性
  - Receding horizon: 上次预测的后续动作可 warm-start 下次推理
- **最优 T_a ≈ 8**: 过小（=1）失去时间一致性优势，过大则响应性差
- **对 idle action 的鲁棒性**: 序列预测天然抵抗遥操作中的停顿段（单步策略容易过拟合停顿）

#### 3. 两种网络架构
- **CNN-based (1D temporal ConvNet)**:
  - 改编自 Diffuser (Janner et al.)，用 FiLM 条件化观测和去噪步
  - 开箱即用，超参数不敏感
  - 缺点: 时间卷积的低频偏差导致在高频动作变化/速度控制任务上表现差
- **Transformer-based (Time-series Diffusion Transformer)**:
  - 改编 minGPT 架构，噪声动作作为 decoder input token，观测通过 cross-attention 注入
  - Causal attention mask 保证时间因果性
  - 在复杂任务和高频动作变化任务上表现更好
  - 缺点: 对超参数更敏感
- **推荐策略**: 先试 CNN，不行再试 Transformer

#### 4. 视觉编码器
- ResNet-18（无预训练），spatial softmax pooling（保留空间信息），GroupNorm（替代 BatchNorm，兼容 EMA）
- 不同相机视角用独立编码器，各时间步独立编码后拼接
- 端到端训练效果最好（优于 ImageNet 和 R3M 预训练冻结特征）
- 消融发现: CLIP ViT-B/16 微调效果最佳（98% on Square task），但需要预训练

#### 5. 推理加速 (DDIM)
- 训练 100 步去噪，推理只需 10 步（DDIM 解耦训练/推理步数）
- 在 Nvidia 3080 上实现 0.1s 推理延迟，满足实时控制需求

### 核心优势机制分析

#### 多模态动作分布
- **两个来源**: (1) 随机初始化 A^K_t ~ N(0,I) 决定收敛到哪个模态盆地; (2) 去噪过程中的随机扰动允许在模态间迁移
- **vs LSTM-GMM**: 偏向单一模态
- **vs IBC**: 偏向单一模态
- **vs BET**: 无法 commit 到单一模态（缺乏时间一致性）
- **Diffusion Policy**: 学习到所有模态，且序列预测保证 commit 到单一模态

#### 与位置控制的协同
- **关键发现**: Diffusion Policy + position control >> Diffusion Policy + velocity control
  - 这与当时主流做法相反（大多数 BC 工作使用速度控制）
- **原因**: (1) 位置控制下多模态更显著，Diffusion Policy 更擅长处理; (2) 位置控制的累积误差小，更适合序列预测

#### 训练稳定性
- **vs IBC (EBM)**: IBC 需要通过负采样估计归一化常数 Z(o,θ)，导致训练不稳定（loss 尖刺、评估震荡）
- **Diffusion Policy 绕过 Z**: score function ∇_a log p(a|o) = -∇_a E(a,o) - ∇_a log Z (=0)，训练和推理都不涉及 Z
- 超参数在不同任务间大致一致

#### 与控制理论的联系
- 在线性系统 + 线性反馈策略的简单情况下，最优去噪器收敛到 a = -Ks（正确的线性反馈）
- 多步预测时，学习器隐式学习了任务相关的动力学模型
- 非线性情况下可能出现多模态预测

## 实验

### Benchmark 覆盖
- **4 个 benchmark, 15 个任务**: RoboMimic (5 tasks × PH/MH), Push-T, Block Pushing, Franka Kitchen
- **维度覆盖**: 仿真+真机, 2DoF~6DoF, 单臂/双臂, 刚体/液体, 单人/多人示教
- **观测类型**: 状态观测 + 图像观测

### 仿真结果
- **RoboMimic (Tab 1, 2)**: 全面碾压。状态策略上 DiffusionPolicy-T 在 Square/Transport/ToolHang 等复杂任务上达到 1.00/0.89/1.00（max），远超 LSTM-GMM 的 0.95/0.76/0.67
- **Push-T**: 状态观测 0.95（CNN）/0.95（Transformer），图像观测 0.91（CNN）
- **Block Pushing (Tab 4)**: DiffusionPolicy-T 的 p2=0.94 vs BET 的 0.71（长时域多模态任务）
- **Kitchen (Tab 4)**: DiffusionPolicy-C 的 p4=0.99 vs BET 的 0.44（213% 提升，长时域多模态）
- **平均提升**: 46.9% across all benchmarks

### 真机结果
- **Push-T (UR5)**: 95% 成功率, 0.80 IoU（接近人类 0.84），vs LSTM-GMM 20%, IBC 0%
- **Mug Flipping (6DoF)**: 90% 成功率 vs LSTM-GMM 0%
- **Sauce Pouring**: 79% 成功率, 0.74 IoU（接近人类 0.79）
- **Sauce Spreading**: 100% 成功率, 0.77 coverage（接近人类 0.79）
- **鲁棒性**: 对视觉遮挡（手挡摄像头 3 秒）、物理扰动（移动物体）均表现稳健；能合成从未示教过的纠正行为

### 双臂真机结果（扩展版）
- **Egg Beater**: 55% 成功率（需触觉反馈遥操作采集数据）
- **Mat Unrolling**: 75% 成功率
- **Shirt Folding**: 75% 成功率
- 所有双臂任务使用与单臂相同的超参数，无需调参

### 关键消融
- **Action horizon**: T_a=8 为最优平衡点（时间一致性 vs 响应性）
- **位置 vs 速度控制**: Diffusion Policy 位置控制显著优于速度控制（基线方法相反）
- **延迟鲁棒性**: 位置控制下延迟高达 4 步仍维持峰值性能
- **视觉编码器 (Tab 5)**: CLIP ViT-B/16 微调 98% > ResNet-34 微调 94% > 从头训练 ResNet-18 94%; 冻结预训练特征效果差
- **CNN vs Transformer**: CNN 开箱即用更稳，Transformer 在复杂任务/高频动作上更强但需调参

### 对比基线
- LSTM-GMM (BC-RNN): 混合高斯 + LSTM
- IBC (Implicit BC): 基于 EBM 的隐式策略
- BET (Behavior Transformer): k-means 聚类 + offset 预测

## 评价

### 优势
1. **奠基性贡献**: 这是将扩散模型引入机器人策略学习的里程碑工作，直接催生了 Octo（diffusion head）、π₀（flow matching）、ACT 等后续工作的方法基础
2. **系统性极强**: 15 个任务、4 个 benchmark、状态+图像、仿真+真机、单臂+双臂的全面评估，是机器人学习领域少见的大规模系统性实验
3. **深入的机制分析**: 不仅展示了性能优势，还从多模态表达、训练稳定性、位置控制协同、序列预测等多个角度提供了深入的 insight
4. **实用性强**: 默认超参数跨任务通用（CNN 版本）、推理速度满足实时控制（DDIM 加速到 0.1s）、端到端视觉训练、鲁棒性好
5. **Action sequence + receding horizon 的组合**: 这一设计后来成为 VLA 领域的标准做法（Octo 的 action chunking、π₀ 的 50 步 action chunk）

### 局限
1. **单任务/少任务框架**: 不涉及跨具身预训练或大规模多任务学习，泛化能力有限（这在 Octo/π₀ 中得到解决）
2. **无语言条件**: 不支持语言指令，仅基于视觉观测（这限制了其在通用机器人策略中的适用性）
3. **推理延迟仍高于简单方法**: 10 步去噪推理 vs LSTM-GMM 的单次前向，对极高频控制场景仍有压力
4. **Transformer 版本调参敏感**: 作者自己承认 Transformer 版本对超参数敏感，限制了易用性
5. **数据规模有限**: 示教数据量级为百级（90-284 条），未探索大规模数据下的 scaling behavior
6. **行为克隆的固有局限**: 依赖高质量示教数据，无法利用次优或负面数据（作者在局限性中已指出）

### 对 VLA 领域的贡献
1. **技术源头**: Diffusion Policy 是 VLA 领域 "diffusion/flow 生成动作" 这一技术路线的起点。从 Diffusion Policy → Octo (diffusion head) → π₀ (flow matching) → π₀.5 的演进线是 VLA 领域最重要的技术脉络之一
2. **Action chunking + receding horizon 的范式确立**: 这一设计在后续几乎所有 VLA 工作中被采用（Octo 20 步 chunk、π₀ 50 步 chunk）
3. **Position control 的重新认识**: Diffusion Policy 的实验结论（position control 优于 velocity control）影响了后续工作的动作空间设计
4. **条件化 vs 联合建模的决策**: 将观测作为条件（而非 Diffuser 的联合分布）这一设计被后续所有 diffusion/flow policy 采用
5. **训练稳定性论证**: 对 EBM (IBC) vs Score function (DDPM) 训练稳定性的分析为后续方法选择提供了理论依据

### 与其他工作的关系
- **Diffuser (Janner et al. 2022)**: Diffuser 在 RL/planning 中使用 diffusion 建模联合状态-动作轨迹; Diffusion Policy 将其改造为 BC 框架、条件化观测、只生成动作序列、支持闭环控制
- **IBC (Florence et al. 2021)**: 理论优势相似（多模态）但 IBC 训练不稳定; Diffusion Policy 通过 score function 绕过归一化常数问题
- **Octo (2024)**: 将 Diffusion Policy 的 diffusion head 思想扩展到跨具身大规模预训练; 用轻量 3 层 MLP diffusion head（只需 transformer 前向一次）
- **π₀ (2024)**: 将 diffusion 升级为 flow matching（更高效的 10 步推理）、与预训练 VLM 结合; action chunking + flow matching 直接继承自 Diffusion Policy 的设计思想
- **ACT (Action Chunking with Transformers)**: 同时期的另一条 action chunking 路线（CVAE），与 Diffusion Policy 互补
