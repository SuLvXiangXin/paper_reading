# 调研报告：World Model + VLA 方法路线全景

> 调研时间：2026-03-14（最后更新：基于 DreamZero 完整论文）
> 涉及论文：25+
> 覆盖时间跨度：2023.01 — 2026.02

## 1. 调研背景

传统 VLA 模型（RT-2, OpenVLA, π₀ 等）采用「感知→动作」直接映射范式：输入图像和语言指令，直接输出动作。这种范式缺乏对世界动态的建模能力，导致：
- 缺乏长程规划能力
- 泛化依赖数据覆盖，而非物理理解
- 难以从海量无动作标注的互联网视频中学习

**World Model + VLA** 路线通过引入世界模型，让 VLA 具备「想象未来」和「基于想象规划」的能力。本调研梳理该路线的三大流派及其代表论文。

## 2. 三大流派概览

| 流派 | 核心机制 | 代表 | 最高引用 |
|------|---------|------|---------|
| A: Hidden State → Action | WM 隐状态驱动动作 | FLARE, GR00T N1.5, DreamVLA | DreamVLA ~74 |
| B: 视频+动作联合去噪 | 统一 diffusion 框架 | DreamZero, UWM, GR-1/2, Cosmos Policy | GR-1 ~275 |
| C: 视频→IDM | 先生成视频再恢复动作 | UniPi, Seer, SuSIE, DeFI | UniPi ~449 |

## 3. 流派详细分析

### 3.1 流派A：Hidden State → Action Expert

**设计哲学**：不需要生成人能看懂的视频，只需要 latent space 中的未来状态表征就足以指导动作生成。

**关键论文（按影响力排序）：**

1. **DreamVLA** (2507.04447, NeurIPS 2025, ~74 citations)
   - 预测 comprehensive world knowledge（动态区域、3D 深度、语义）而非原始像素
   - 用 `<dream>` special tokens 做 world embedding
   - CALVIN ABC-D 4.44, 真实世界 76.7% 成功率

2. **VidMan** (2411.09153, NeurIPS 2024, ~39 citations)
   - 基于 Open-Sora 预训练视频扩散模型
   - Gating 机制从扩散 block 蒸馏隐式动力学到 action query
   - CALVIN 上比 GR-1 提升 11.7%

3. **FLARE** (2505.15659, NVIDIA GEAR, ~37 citations)
   - 极简设计：在 DiT 中加几个 "future tokens"
   - Cosine similarity loss 对齐 future observation embedding
   - 性能提升高达 26%，已被集成到 GR00T N1.5

4. **Genie Envisioner** (2508.05635, AgiBot, 新)
   - 统一 world foundation platform
   - GE-Base 世界模型 + GE-Act 动作生成 + GE-Sim 仿真评估
   - 大规模工业级应用（AgiBot G1 双臂平台）

5. **MinD** (2025)
   - 双系统设计：低频 world model 做战略规划 + 高频 diffusion policy 做反应式控制
   - 验证了 single-step latent 足以驱动精确控制

### 3.2 流派B：视频 + 动作联合去噪

**设计哲学**：视频预测和动作生成本质上反映同一个物理世界的动力学，应该在统一框架中联合学习。

**关键论文（按影响力排序）：**

1. **GR-1** (ByteDance, ICLR 2025, ~275 citations)
   - GPT 风格：预训练视频预测 → 微调动作生成
   - 开创「大规模视频预训练→机器人微调」范式
   - 虽非严格联合去噪，但验证了视频预训练对动作生成的价值

2. **GR-2** (2410.06158, ByteDance, ~187 citations)
   - GR-1 扩展版：互联网规模视频预训练（百万级数据）
   - 三阶段训练：视频预训练 → 机器人视频微调 → 动作微调

3. **UWM** (2504.02792, UW + Toyota, RSS 2025, ~65 citations)
   - **核心创新**：解耦动作和图像的 diffusion timestep
   - 单模型可灵活切换 policy / forward dynamics / inverse dynamics / video generator
   - 天然支持 action-free 数据预训练

4. **Cosmos Policy** (2601.16163, NVIDIA + Stanford, ~17 citations)
   - 直接在 Cosmos 视频模型中注入 action latent frames
   - **单阶段微调**，无需额外架构组件
   - 同时支持 visuomotor control 和 visual planning
   - 统一 policy + world model + value function

5. **DreamZero** (2602.15922, NVIDIA GEAR, ~6, 极新)
   - 14B World Action Model，基于 Wan2.1-I2V-14B 视频扩散骨干
   - 自回归 chunk-wise 架构，视频+动作共享去噪 timestep（初始训练），DreamZero-Flash 解耦噪声用于推理加速
   - **零样本任务泛化比 VLA SOTA 提升 2x+**（未见任务 39.5% vs 16.3%）
   - 7Hz 实时闭环控制（38x 推理加速：CFG并行+DiT Caching+NVFP4+Flash）
   - 跨具身迁移：video-only 数据（无动作标注）实现 42%+ 相对提升
   - 少样本具身适配：30 分钟 play data 适配全新机器人
   - **关键发现**：多样非重复数据 >> 重复示教数据（50% vs 33%）；VLA 在同样多样数据上完全失败（0%）
   - **故障模式洞察**：大多数失败源于视频生成错误而非动作预测→改进视频骨干直接提升策略

6. **PAD** (2411.18179, 清华, NeurIPS 2024)
   - DiT 架构联合去噪 future image + action
   - 实验验证了 joint denoising 优于分开训练

7. **RynnVLA-002** (2511.17502, 阿里达摩院, ~10)
   - 自回归统一框架：VLA + World Model
   - 证明联合学习动力学和动作规划相互增强

### 3.3 流派C：先生成视频 → Inverse Dynamics Model

**设计哲学**：将规划（世界模型预测未来画面）和控制（从画面变化推导动作）解耦，各自发挥优势。

**关键论文（按影响力排序）：**

1. **UniPi** (2302.00111, Google/MIT, NeurIPS 2024, **~449 citations**)
   - **开山之作**，首次将 VLA 问题转化为 text-guided video generation + IDM
   - 证明互联网视频知识可迁移到机器人控制
   - 奠定了整个流派C的方法论框架

2. **SuSIE** (2310.10639, UC Berkeley, **~264 citations**)
   - 简化方案：不生成完整视频，只用 InstructPix2Pix 做 image editing 生成子目标
   - Goal-conditioned policy 执行子目标
   - 轻量高效，广泛被后续工作引用

3. **3D-VLA** (2403.09631, UMass, ICML 2024, **~262 citations**)
   - 将 world model 扩展到 3D 场景
   - 集成 3D 推理、多模态生成、动作规划
   - 独立技术路线（3D 表征 vs 2D 视频）

4. **LAPA** (2410.11758, MSR + UW, ICLR 2025, **~191 citations**)
   - 用 VQ-VAE 从视频帧对中提取 latent actions
   - 大规模无标注视频预训练 VLA
   - 证明 latent action 是利用人类视频的有效桥梁
   - GR00T N1 采用了类似的 latent action 思路

5. **Seer** (2412.15109, 上海AI Lab, ICLR 2025 **Oral**)
   - **端到端 PIDM**：闭环视觉预测 + inverse dynamics
   - CALVIN ABC-D SOTA (avg length 4.28)
   - DROID 预训练 → 真实世界微调效果显著

6. **F1** (2509.06951, 2025)
   - Mixture-of-Transformer 三专家：Understanding → Generation → Action
   - 统一理解-生成-动作到一个 decoder-only transformer
   - Next-scale prediction 训练 foresight generation

7. **DeFI** (OpenReview, 2025)
   - 解耦 Forward/Inverse dynamics 预训练
   - Forward 用大规模无动作视频，Inverse 用机器人数据
   - 端到端微调时两部分协同互利

8. **mimic-video** (2512.15692, NVIDIA, 2024)
   - 基于 Cosmos-Predict2 视频骨干
   - Partial denoising 提取 latent visual plans（不需完整去噪）
   - 轻量 action decoder 做 IDM

9. **VPP** (2412.14803, 2024)
   - 用视频预测模型的**内部表征**直接做 IDM 输入
   - 避免多步去噪，高频闭环控制

## 4. 跨流派对比

### 4.1 性能基准

| 模型 | 流派 | CALVIN ABC-D | 真实世界 | 跨具身 |
|------|------|-------------|---------|--------|
| Seer | C | **4.28** (SOTA) | 强 | — |
| DreamVLA | A | 4.44 | 76.7% | — |
| DreamZero | B | — | **2x+ SOTA VLA**（39.5% unseen tasks） | 30min 迁移 + video-only 42%+ |
| GR00T N1.5 | A | — | — | 多具身预训练 |
| UWM | B | — | 强 | action-free 预训练 |
| Cosmos Policy | B | — | ALOHA 93.6 avg | — |

### 4.2 工程化程度

| 模型 | 开源 | 代码质量 | 工业部署 |
|------|------|---------|---------|
| Seer | 完整开源 | 高 | 研究导向 |
| GR00T N1/N1.5 | 部分开源 | 高 | NVIDIA 工业级 |
| Genie Envisioner | 开源 | 高 | AgiBot 工业级 |
| UWM | 开源 | 高 | 研究导向 |
| DreamZero | **已开源（权重+推理代码+评测）** | 高 | NVIDIA 工业级 |
| Cosmos Policy | 开源 | 高 | NVIDIA 生态 |

## 5. 关键洞察

### 5.1 流派演进趋势
- **从显式到隐式**：UniPi (2023) 生成完整视频 → VPP (2024) 用内部表征 → FLARE (2025) 只对齐 latent
- **从两阶段到端到端**：UniPi 两阶段 pipeline → Seer 端到端 PIDM → DreamZero 统一去噪
- **从小规模到大规模**：UniPi 小模型验证 → DreamZero 14B → Genie Envisioner 统一平台

### 5.2 数据利用方式的关键区别
- **流派A**：主要用机器人数据，部分支持人类视频（FLARE, LAPA）
- **流派B**：天然支持无动作视频预训练（UWM, GR-2, Cosmos Policy）；**DreamZero 进一步证明 video-only 跨具身数据可实现 42%+ 任务泛化提升**
- **流派C**：Forward model 用任意视频，Inverse model 用机器人数据（DeFI, AMPLIFY）

### 5.3 实时性
- 多数早期工作（UniPi, SuSIE）是开环执行，不适合实时控制
- DreamZero 实现了 14B 模型的 7Hz 实时闭环（通过模型和系统优化：38x 加速）
- FLARE 由于只预测 latent 而非视频，推理开销极小

### 5.4 VLA vs WAM 的本质差异（DreamZero 的核心发现）🆕
- **数据效率**: VLA 从多样非重复数据学习完全失败（0%），WAM 成功（50%）→这是方法范式差异而非规模差异
- **VLA**: 学"观测→动作"直接映射，需要密集重复数据覆盖状态-动作空间
- **WAM**: 学"观测→视觉未来→动作"（video prediction + implicit IDM），视频预训练提供物理先验→动作学习难度大幅降低
- **Scaling 行为不同**: WAM 14B >> 5B（50% vs 21%，清晰 scaling）；VLA 放大到相同规模仍 0%
- **故障模式不同**: WAM 失败主要来自视频生成质量→改进视频骨干即可；VLA 失败来自缺乏物理理解→需要更多数据

## 6. 推荐精读论文

按优先级排序：

1. **UniPi** (2302.00111) — 开山之作，理解整个流派的起点
2. **DreamZero** (2602.15922) — 最新 SOTA WAM，系统性证明 WAM 2x+ 优于 VLA，揭示两者本质差异
3. **Seer** (2412.15109) — ICLR Oral，端到端 PIDM 范式，性能最强
4. **Cosmos Policy** (2601.16163) — 统一 policy+WM+value，无架构修改适配
5. **UWM** (2504.02792) — 解耦 timestep 的优雅设计
6. **FLARE** (2505.15659) — 极简有效的隐式世界模型
7. **GR-1/GR-2** — 视频预训练范式的工业级验证
8. **DeFI** — 解耦 Forward/Inverse 预训练的清晰框架
9. **LAPA** (2410.11758) — Latent action 预训练，利用无标注视频的关键工作

## 7. DreamZero vs Cosmos Policy：NVIDIA 流派B的双子星 🆕

NVIDIA 在流派B内同时推出两个互补的 WAM：

| 维度 | DreamZero | Cosmos Policy |
|------|-----------|---------------|
| **基座** | Wan2.1-I2V-14B | Cosmos-Predict2-2B |
| **规模** | 14B | 2B |
| **架构** | 自回归 chunk-wise + teacher forcing | 双向并行 + conditioning mask |
| **timestep** | 共享（训练）→ 解耦（Flash） | 共享（hybrid log-normal-uniform） |
| **核心能力** | 零样本泛化（未见任务/环境） | 任务特定微调 + model-based planning |
| **数据哲学** | 多样非重复（500h）→ 泛化 | 任务特定 demo + rollout → 精度 |
| **跨具身** | ✅（video-only 42%+, 30min 适配） | ❌ |
| **Planning** | ❌ | ✅（best-of-N + value function） |
| **Value Function** | ❌ | ✅（统一训练） |
| **推理速度** | 7Hz (2x GB200) | 0.16s/chunk 1-step (1x H100) |
| **真机基准** | AgiBot G1（2x+ vs VLA SOTA） | ALOHA（93.6 avg score, 超越 π₀.5） |
| **仿真基准** | Genie Sim 3.0（非平凡） | LIBERO 98.5%, RoboCasa 67.1% |
| **互补关系** | 广度（泛化到新任务/新环境） | 深度（在特定任务上精准 + 规划） |
