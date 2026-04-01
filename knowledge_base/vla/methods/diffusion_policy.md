# Diffusion Policy (BC + Diffusion 奠基方法线)

## 核心思想
将机器人视觉运动策略表示为**条件去噪扩散过程**（Conditional DDPM）：从高斯噪声出发，通过 K 步迭代去噪生成动作序列，每步由学到的 score function 梯度场指导。关键创新在于将扩散模型的生成能力应用于机器人动作空间，结合 action sequence prediction 和 receding horizon control。

## 技术贡献

### 1. 条件化去噪（vs 联合建模）
- 观测 O_t 作为条件注入去噪过程，而非与动作一起作为联合分布建模
- **vs Diffuser (Janner 2022)**: Diffuser 联合建模 p(A,O)，需推断未来状态，慢且不准
- **影响**: 这一设计被后续所有 diffusion/flow policy 采用（Octo, π₀ 均使用条件化）

### 2. Action Sequence + Receding Horizon
- 三时间尺度: 观测 horizon T_o / 预测 horizon T_p / 执行 horizon T_a
- 联合预测多步动作保证时间一致性，但只执行前 T_a 步保持闭环响应性
- **最优 T_a ≈ 8 步**
- **影响**: 直接演变为 Octo 的 action chunking (20步) → π₀ 的 action chunk (50步 @ 50Hz)

### 3. Position Control 的重新认识
- 首次系统性证明 Diffusion Policy + position control >> velocity control
- 原因: (1) position control 下多模态更显著，diffusion 更擅长处理; (2) 累积误差更小
- **影响**: 改变了社区从 velocity control 为主的惯例

### 4. 训练稳定性（vs EBM/IBC）
- Score function ∇_a log p(a|o) 不依赖归一化常数 Z，绕过了 EBM 负采样不稳定的根源
- 超参数跨任务通用

### 5. 两种架构选择
| | CNN-based (1D Temporal ConvNet) | Transformer-based (Time-series Diffusion Transformer) |
|---|---|---|
| 条件注入 | FiLM (Feature-wise Linear Modulation) | Cross-attention |
| 优点 | 开箱即用，超参不敏感 | 高频动作变化更好，复杂任务更强 |
| 缺点 | 低频偏差（卷积归纳偏置） | 超参敏感 |
| 推荐 | 首选尝试 | 需要时切换 |

## 与后续工作的关系

### Diffusion Policy → Octo (2024)
- **继承**: diffusion head（DDPM去噪生成动作）、action chunking、连续动作空间
- **扩展**: 从单任务 BC 到跨具身大规模预训练；diffusion head 简化为轻量 3 层 MLP（只需 transformer 前向一次）
- **差异**: Octo 的 diffusion head 只是架构的一个组件（依附于 ViT backbone），而 Diffusion Policy 中 diffusion 是策略本身

### Diffusion Policy → π₀ (2024)
- **继承**: 连续动作生成 + action chunking + 条件化设计
- **升级**: DDPM → Flow Matching（更高效：10 步 Euler vs 100 步 DDPM）；与预训练 VLM (PaliGemma) 结合
- **差异**: π₀ 引入 VLM 的互联网级语义知识，支持语言条件和跨具身泛化

### Diffusion Policy vs IBC (Implicit BC)
- 理论上的表达力相似（都能建模多模态分布）
- Diffusion Policy 通过 score function 绕过归一化常数，训练大幅更稳定
- IBC 在实验中全面落后（多个任务 0% 成功率）

### Diffusion Policy vs BET (Behavior Transformer)
- BET 用 k-means 聚类 + offset 预测处理多模态
- BET 缺乏序列预测的时间一致性（无法 commit 到单一模态）
- Diffusion Policy 的序列去噪天然保证了模态内的一致性

## 方法线定位
Diffusion Policy 是 VLA 领域 **"扩散/流式生成动作"** 这一核心技术路线的**起点和奠基工作**。它：
1. 首次系统性证明扩散模型在机器人策略学习中全面优于传统 BC 方法
2. 确立了 "条件化 DDPM + action sequence + receding horizon + position control" 的设计范式
3. 为后续 Octo（跨具身扩展）和 π₀（VLM + flow matching 升级）提供了直接的技术基础
4. 其核心设计决策（条件化 vs 联合建模、action chunking、position control）已成为领域共识

→ 论文卡片: [papers/diffusion_policy_2023.md](../papers/diffusion_policy_2023.md)
