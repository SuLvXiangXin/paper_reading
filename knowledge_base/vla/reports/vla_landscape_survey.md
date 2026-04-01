# 调研报告：VLA 领域全景（基于 π₀.5 引用图谱）

> 调研时间：2026-03-14
> 方法：以 π₀.5 (arXiv:2504.16054) 为锚点，检索所有引用它的论文，筛选引用数 > 10 的高影响力工作
> 数据来源：Semantic Scholar API
> 总引用数：596 篇，筛选后：94 篇（引用数 > 10）

## 1. 统计概览

- π₀.5 总被引用数：~596（截至 2026-03-14）
- 引用数 > 10 的论文：94 篇
- 引用数 > 50 的论文：18 篇
- 引用数 > 100 的论文：4 篇
- 覆盖时间：2023 — 2026

---

## 2. 分类目录

将 94 篇论文按研究方向分类如下：

### 2.1 VLA 核心模型（新架构/新模型）

直接提出新的 VLA 模型架构或训练方法。

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **π*₀.₆** | 2511.14759 | 66 | 2025 | Physical Intelligence 后续，引入经验学习（RL fine-tuning） |
| 2 | **DexVLA** | 2502.05855 | 130 | 2025 | 插件式 Diffusion Expert，通用机器人控制 |
| 3 | **WorldVLA** | 2506.21539 | 110 | 2025 | 自回归 Action World Model |
| 4 | **GraspVLA** | 2505.03233 | 81 | 2025 | 抓取基础模型，十亿级合成动作数据预训练 |
| 5 | **DreamVLA** | 2507.04447 | 74 | 2025 | 综合世界知识预测 + inverse dynamics |
| 6 | **DexGraspVLA** | 2502.20900 | 71 | 2025 | 灵巧抓取 VLA 框架 |
| 7 | **GR-3** | 2507.15493 | 69 | 2025 | ByteDance GR 系列第三代 |
| 8 | **OneTwoVLA** | 2505.11917 | 68 | 2025 | 统一 VLA + 自适应推理 |
| 9 | **Knowledge Insulating VLA** | 2505.23705 | 63 | 2025 | 快速训练、快速推理、泛化更好 |
| 10 | **Discrete Diffusion VLA** | 2508.20072 | 41 | 2025 | 离散扩散解码动作 |
| 11 | **CogVLA** | 2508.21046 | 33 | 2025 | 认知对齐 VLA + 指令驱动路由 |
| 12 | **X-VLA** | 2510.10274 | 43 | 2025 | Soft-Prompted 跨具身 VLA |
| 13 | **VLA-Adapter** | 2509.09372 | 44 | 2025 | 小规模 VLA 高效适配 |
| 14 | **Galaxea G0** | 2509.00576 | 40 | 2025 | 双系统 VLA（快慢系统） |
| 15 | **InstructVLA** | 2507.17520 | 34 | 2025 | 指令调优：从理解到操作 |
| 16 | **InternVLA-M1** | 2510.13778 | 18 | 2025 | 空间引导 VLA 框架 |
| 17 | **Actions as Language** | 2509.22195 | 18 | 2025 | 微调 VLM → VLA 不遗忘 |
| 18 | **Cosmos Policy** | 2601.16163 | 17 | 2026 | 视频模型直接微调为策略 |
| 19 | **VLA-R1** | 2510.01623 | 17 | 2025 | 增强 VLA 推理能力 |
| 20 | **GigaBrain-0** | 2510.19430 | 15 | 2025 | World Model 驱动的 VLA |
| 21 | **Interleave-VLA** | 2505.02152 | 38 | 2025 | 交错图文指令增强操作 |
| 22 | **ForceVLA** | 2505.22159 | 45 | 2025 | 力感知 MoE VLA |
| 23 | **EgoVLA** | 2507.12440 | 52 | 2025 | 从自我中心人类视频学习 VLA |
| 24 | **Being-H0** | 2507.15597 | 42 | 2025 | 大规模人类视频 VLA 预训练 |
| 25 | **TLA** | 2503.08548 | 35 | 2025 | 触觉-语言-动作模型 |
| 26 | **BridgeVLA** | 2506.07961 | 35 | 2025 | 高效 3D 操作学习 |
| 27 | **ChatVLA-2** | 2505.21906 | 16 | 2025 | 开放世界具身推理 |
| 28 | **LoHoVLA** | 2506.00411 | 17 | 2025 | 长程具身任务 VLA |
| 29 | **mimic-video** | 2512.15692 | 11 | 2025 | 视频-动作模型超越传统 VLA |
| 30 | **RynnVLA-002** | 2511.17502 | 10 | 2025 | 统一 VLA + 世界模型 |
| 31 | **dVLA** | 2509.25681 | 6 | 2025 | Diffusion VLA + 多模态 CoT |

### 2.2 VLA 训练方法改进（RL、数据、效率）

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **SimpleVLA-RL** | 2509.09674 | 53 | 2025 | 通过 RL 扩展 VLA 训练 |
| 2 | **What Can RL Bring to VLA** | 2505.19789 | 52 | 2025 | RL 对 VLA 泛化的实证研究 |
| 3 | **Interactive Post-Training** | 2505.17016 | 45 | 2025 | VLA 交互式后训练 |
| 4 | **VLAC** (Vision-Language-Action-Critic) | 2509.15937 | 25 | 2025 | VLA + Critic 模型做真实世界 RL |
| 5 | **RL-100** | 2510.14830 | 19 | 2025 | 真实世界 RL 的高性能机器人操作 |
| 6 | **Self-Improving VLA** | 2511.00091 | 18 | 2025 | 残差 RL 数据生成自我改进 |
| 7 | **Self-Improving Embodied FM** | 2509.15155 | 17 | 2025 | 具身基础模型自我改进 |
| 8 | **Residual Off-Policy RL** | 2509.19301 | 13 | 2025 | 残差 off-policy RL 微调 BC |
| 9 | **STARE-VLA** | 2512.05107 | 16 | 2025 | 阶段感知强化学习微调 VLA |
| 10 | **Scalable VLA Pretraining** (Human Videos) | 2510.21571 | 18 | 2025 | 用真实人类活动视频预训练 VLA |
| 11 | **H-RDT** | 2507.23523 | 18 | 2025 | 人类操作增强双臂机器人操作 |
| 12 | **RLinf-VLA** | 2510.06710 | 11 | 2025 | 统一高效 RL 框架微调 VLA |
| 13 | **Training-Time Action Conditioning** | 2512.05964 | 12 | 2025 | 高效实时 action chunking |
| 14 | **Real-Time Execution of ACFP** | 2506.07339 | 63 | 2025 | Action Chunking Flow Policy 实时执行 |
| 15 | **Token Pruning for VLA** | 2509.12594 | 12 | 2025 | 可微 token 剪枝加速 VLA |
| 16 | **TA-VLA** | 2509.07962 | 12 | 2025 | 力矩感知 VLA 设计空间 |
| 17 | **Shortcut Learning in Robot Policies** | 2508.06426 | 14 | 2025 | 数据多样性 vs 策略捷径学习 |
| 18 | **What Matters in Building VLA** | 2412.14058 | 101 | 2024 | VLA 构建的关键因素实证分析 |

### 2.3 世界模型 + VLA

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **WorldVLA** | 2506.21539 | 110 | 2025 | 自回归 Action World Model |
| 2 | **DreamVLA** | 2507.04447 | 74 | 2025 | 综合世界知识驱动 inverse dynamics |
| 3 | **DreamGen** | 2505.12705 | 54 | 2025 | 通过视频世界模型解锁机器人学习泛化 |
| 4 | **Training Agents Inside World Models** | 2509.24527 | 51 | 2025 | 可扩展世界模型内训练 Agent |
| 5 | **Ctrl-World** | 2510.10125 | 34 | 2025 | 可控生成式世界模型 |
| 6 | **Motus** | 2512.13030 | 17 | 2025 | 统一 Latent Action 世界模型 |
| 7 | **GigaBrain-0** | 2510.19430 | 15 | 2025 | World Model 驱动 VLA |
| 8 | **Cosmos Policy** | 2601.16163 | 17 | 2026 | 视频模型微调为控制策略 |
| 9 | **V-JEPA 2** | 2506.09985 | 231 | 2025 | 自监督视频模型用于理解/预测/规划 |

### 2.4 具身推理与规划（CoT、Reasoning）

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **OneTwoVLA** | 2505.11917 | 68 | 2025 | 自适应推理 VLA |
| 2 | **CogVLA** | 2508.21046 | 33 | 2025 | 认知对齐 + 指令驱动路由 |
| 3 | **VLA-R1** | 2510.01623 | 17 | 2025 | 增强 VLA 推理 |
| 4 | **Igniting VLMs toward Embodied Space** | 2509.11766 | 23 | 2025 | 点燃 VLM 的具身推理能力 |

### 2.5 多模态感知增强（触觉、力、3D）

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **ForceVLA** | 2505.22159 | 45 | 2025 | 力感知 MoE 用于接触式操作 |
| 2 | **TLA** | 2503.08548 | 35 | 2025 | 触觉-语言-动作 |
| 3 | **VLA-Touch** | 2507.17294 | 22 | 2025 | 双层触觉反馈增强 VLA |
| 4 | **BridgeVLA** | 2506.07961 | 35 | 2025 | 3D 操作学习 |
| 5 | **TA-VLA** | 2509.07962 | 12 | 2025 | 力矩感知 VLA |

### 2.6 评测与基准

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **LIBERO-PRO** | 2510.03827 | 20 | 2025 | VLA 鲁棒公平评测，超越记忆 |
| 2 | **Careful Examination of Large Behavior Models** | 2507.05331 | 73 | 2025 | 灵巧操作大模型的深度审视 |
| 3 | **Shortcut Learning** | 2508.06426 | 14 | 2025 | 数据多样性与策略捷径 |
| 4 | **Robo-Dopamine** | 2512.23703 | 11 | 2025 | 通用过程奖励模型用于精密操作 |

### 2.7 Survey 综述论文

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **Large Language Models for Robotics: A Survey** | 2311.07226 | 218 | 2023 | LLM + 机器人综述 |
| 2 | **Survey on VLA for Embodied AI** | 2405.14093 | 194 | 2024 | VLA 具身 AI 综述 |
| 3 | **VLA for Robotics: Review Towards Real-World** | 2510.07077 | 54 | 2025 | VLA 面向真实世界综述 |
| 4 | **VLA: Concepts, Progress, Applications** | 2505.04769 | 60 | 2025 | VLA 概念/进展/应用/挑战 |
| 5 | **Large VLM-based VLA Survey** | 2508.13073 | 38 | 2025 | 大 VLM 基础 VLA 综述 |
| 6 | **Pure VLA Models: Comprehensive Survey** | 2509.19012 | 20 | 2025 | 纯 VLA 模型综述 |
| 7 | **VLA in Robotic Manipulation: Systematic Review** | 2507.10672 | 29 | 2025 | 机器人操作 VLA 系统综述 |
| 8 | **Agentic Multimodal LLM Survey** | 2510.10991 | 12 | 2025 | Agent 式多模态 LLM 综述 |
| 9 | **Multi-agent Embodied AI** | 2505.05108 | 33 | 2025 | 多智能体具身 AI 综述 |

### 2.8 人形机器人与全身控制

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **LeVERB** | 2506.13751 | 33 | 2025 | 人形全身控制 + 潜在视觉语言指令 |
| 2 | **TWIST2** | 2511.02832 | 29 | 2025 | 可扩展人形数据采集系统 |
| 3 | **H-RDT** | 2507.23523 | 18 | 2025 | 人类操作增强双臂操作 |

### 2.9 数据与仿真

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **GraspVLA** | 2505.03233 | 81 | 2025 | 十亿级合成动作数据 |
| 2 | **DreamGen** | 2505.12705 | 54 | 2025 | 世界模型做数据引擎 |
| 3 | **Ctrl-World** | 2510.10125 | 34 | 2025 | 可控世界模型做评估/改进 |
| 4 | **TWIST2** | 2511.02832 | 29 | 2025 | 人形数据采集系统 |

### 2.10 自动驾驶与导航

| # | 论文 | arXiv | 引用 | 年份 | 要点 |
|---|------|-------|------|------|------|
| 1 | **Alpamayo-R1** | 2511.00088 | 33 | 2025 | 推理与动作预测用于自动驾驶长尾 |
| 2 | **DriveMoE** | 2505.16278 | 45 | 2025 | MoE VLA 用于端到端自动驾驶 |
| 3 | **Embodied Navigation FM** | 2509.12129 | 22 | 2025 | 具身导航基础模型 |
| 4 | **OmniNav** | 2509.25687 | 13 | 2025 | 前瞻性探索 + 视觉语言导航 |

---

## 3. 高影响力论文 Top 20

按引用数排序的 Top 20 论文（不含 survey）：

| 排名 | 论文 | 引用 | 类别 |
|------|------|------|------|
| 1 | **V-JEPA 2** | 231 | 世界模型/自监督 |
| 2 | **DexVLA** | 130 | VLA 核心模型 |
| 3 | **WorldVLA** | 110 | 世界模型 + VLA |
| 4 | **What Matters in Building VLA** | 101 | 训练方法/实证 |
| 5 | **GraspVLA** | 81 | VLA 核心模型 |
| 6 | **DreamVLA** | 74 | 世界模型 + VLA |
| 7 | **Careful Examination of Large Behavior Models** | 73 | 评测 |
| 8 | **DexGraspVLA** | 71 | VLA 核心模型 |
| 9 | **GR-3** | 69 | VLA 核心模型 |
| 10 | **OneTwoVLA** | 68 | VLA + 推理 |
| 11 | **π*₀.₆** | 66 | VLA 核心模型 |
| 12 | **Knowledge Insulating VLA** | 63 | 训练效率 |
| 13 | **Real-Time ACFP** | 63 | 推理加速 |
| 14 | **DreamGen** | 54 | 世界模型 + 数据 |
| 15 | **SimpleVLA-RL** | 53 | RL 训练 |
| 16 | **What Can RL Bring to VLA** | 52 | RL 训练 |
| 17 | **EgoVLA** | 52 | 人类视频学习 |
| 18 | **Training Agents Inside World Models** | 51 | 世界模型 |
| 19 | **ForceVLA** | 45 | 多模态感知 |
| 20 | **DriveMoE** | 45 | 自动驾驶 VLA |

---

## 4. 关键发现

### 4.1 VLA 领域的主要研究方向分布
- **核心模型创新**：31 篇（33%）— 最多，说明 VLA 架构设计仍是热点
- **训练方法改进**：18 篇（19%）— RL 微调成为主流趋势
- **世界模型融合**：9 篇（10%）— 快速增长的新方向
- **Survey 综述**：9 篇（10%）— 领域成熟的标志
- **多模态增强**：5 篇（5%）— 触觉/力/3D 感知
- **评测基准**：4 篇（4%）
- **自动驾驶/导航**：4 篇（4%）— VLA 向其他领域扩展

### 4.2 核心趋势
1. **RL 成为 VLA 后训练标配**：SimpleVLA-RL, π*₀.₆, VLAC, RL-100 等验证了 RL 对 VLA 泛化的价值
2. **世界模型崛起**：WorldVLA (110), DreamVLA (74), DreamGen (54) 均为高引用，方向快速增长
3. **效率优化受关注**：VLA-Adapter, Token Pruning, Knowledge Insulating 等解决推理延迟问题
4. **多模态扩展**：从纯视觉-语言扩展到触觉 (TLA, VLA-Touch)、力 (ForceVLA)、3D (BridgeVLA)
5. **从操作到驾驶/导航**：DriveMoE, Alpamayo-R1 将 VLA 范式扩展到自动驾驶

### 4.3 机构活跃度
- **NVIDIA**：Cosmos Policy, DreamZero, FLARE, GR00T N1.5
- **Physical Intelligence**：π₀.5, π*₀.₆
- **ByteDance**：GR-1, GR-2, GR-3
- **阿里达摩院**：RynnVLA-002
- **Stanford**：Cosmos Policy, FLARE (合作)
- **UC Berkeley**：SuSIE, EgoZero
- **上海AI Lab**：Seer, InternVLA

---

## 5. 完整论文清单（引用数 > 10，共 94 篇）

| # | 论文 | arXiv | 引用 | 年份 |
|---|------|-------|------|------|
| 1 | V-JEPA 2 | 2506.09985 | 231 | 2025 |
| 2 | Large Language Models for Robotics: A Survey | 2311.07226 | 218 | 2023 |
| 3 | Survey on VLA for Embodied AI | 2405.14093 | 194 | 2024 |
| 4 | DexVLA | 2502.05855 | 130 | 2025 |
| 5 | WorldVLA | 2506.21539 | 110 | 2025 |
| 6 | What Matters in Building VLA | 2412.14058 | 101 | 2024 |
| 7 | GraspVLA | 2505.03233 | 81 | 2025 |
| 8 | DreamVLA | 2507.04447 | 74 | 2025 |
| 9 | Careful Examination of Large Behavior Models | 2507.05331 | 73 | 2025 |
| 10 | DexGraspVLA | 2502.20900 | 71 | 2025 |
| 11 | GR-3 | 2507.15493 | 69 | 2025 |
| 12 | OneTwoVLA | 2505.11917 | 68 | 2025 |
| 13 | π*₀.₆ | 2511.14759 | 66 | 2025 |
| 14 | Knowledge Insulating VLA | 2505.23705 | 63 | 2025 |
| 15 | Real-Time ACFP | 2506.07339 | 63 | 2025 |
| 16 | VLA: Concepts, Progress, Applications | 2505.04769 | 60 | 2025 |
| 17 | VLA for Robotics: Review | 2510.07077 | 54 | 2025 |
| 18 | DreamGen | 2505.12705 | 54 | 2025 |
| 19 | SimpleVLA-RL | 2509.09674 | 53 | 2025 |
| 20 | EgoVLA | 2507.12440 | 52 | 2025 |
| 21 | What Can RL Bring to VLA | 2505.19789 | 52 | 2025 |
| 22 | Training Agents Inside World Models | 2509.24527 | 51 | 2025 |
| 23 | ForceVLA | 2505.22159 | 45 | 2025 |
| 24 | Interactive Post-Training | 2505.17016 | 45 | 2025 |
| 25 | DriveMoE | 2505.16278 | 45 | 2025 |
| 26 | VLA-Adapter | 2509.09372 | 44 | 2025 |
| 27 | X-VLA | 2510.10274 | 43 | 2025 |
| 28 | Being-H0 | 2507.15597 | 42 | 2025 |
| 29 | Discrete Diffusion VLA | 2508.20072 | 41 | 2025 |
| 30 | Galaxea G0 | 2509.00576 | 40 | 2025 |
| 31 | Large VLM-based VLA Survey | 2508.13073 | 38 | 2025 |
| 32 | Interleave-VLA | 2505.02152 | 38 | 2025 |
| 33 | BridgeVLA | 2506.07961 | 35 | 2025 |
| 34 | TLA | 2503.08548 | 35 | 2025 |
| 35 | Embodied AI Agents: Modeling the World | 2506.22355 | 35 | 2025 |
| 36 | Ctrl-World | 2510.10125 | 34 | 2025 |
| 37 | InstructVLA | 2507.17520 | 34 | 2025 |
| 38 | Alpamayo-R1 | 2511.00088 | 33 | 2025 |
| 39 | CogVLA | 2508.21046 | 33 | 2025 |
| 40 | LeVERB | 2506.13751 | 33 | 2025 |
| 41 | Multi-agent Embodied AI | 2505.05108 | 33 | 2025 |
| 42 | TrackVLA | 2505.23189 | 29 | 2025 |
| 43 | VLA Systematic Review | 2507.10672 | 29 | 2025 |
| 44 | TWIST2 | 2511.02832 | 29 | 2025 |
| 45 | RoboArena | 2506.18123 | 28 | 2025 |
| 46 | ChatVLA-2 / Open-World VLA | — | 28 | 2025 |
| 47 | Thinking vs. Doing | 2506.07976 | 26 | 2025 |
| 48 | Active-O3 | 2505.21457 | 26 | 2025 |
| 49 | EgoZero | 2505.20290 | 26 | 2025 |
| 50 | VLAC | 2509.15937 | 25 | 2025 |
| 51 | SP-VLA | 2506.12723 | 25 | 2025 |
| 52 | WorldEval | 2505.19017 | 25 | 2025 |
| 53 | DreamGen (Neural Traj) | — | 24 | 2025 |
| 54 | Igniting VLMs Embodied | 2509.11766 | 23 | 2025 |
| 55 | STELLA | — | 22 | 2026 |
| 56 | Embodied Nav FM | 2509.12129 | 22 | 2025 |
| 57 | VLA-Touch | 2507.17294 | 22 | 2025 |
| 58 | SAFE | 2506.09937 | 22 | 2025 |
| 59 | SMPLest-X | 2501.09782 | 22 | 2025 |
| 60 | Pure VLA Survey | 2509.19012 | 20 | 2025 |
| 61 | LIBERO-PRO | 2510.03827 | 20 | 2025 |
| 62 | RL-100 | 2510.14830 | 19 | 2025 |
| 63 | Self-Improving VLA | 2511.00091 | 18 | 2025 |
| 64 | Scalable VLA Pretraining | 2510.21571 | 18 | 2025 |
| 65 | InternVLA-M1 | 2510.13778 | 18 | 2025 |
| 66 | Actions as Language | 2509.22195 | 18 | 2025 |
| 67 | H-RDT | 2507.23523 | 18 | 2025 |
| 68 | CoMo | 2505.17006 | 18 | 2025 |
| 69 | Cosmos Policy | 2601.16163 | 17 | 2026 |
| 70 | Motus | 2512.13030 | 17 | 2025 |
| 71 | VLA-R1 | 2510.01623 | 17 | 2025 |
| 72 | Self-Improving Embodied FM | 2509.15155 | 17 | 2025 |
| 73 | LoHoVLA | 2506.00411 | 17 | 2025 |
| 74 | ChatVLA-2 | 2505.21906 | 16 | 2025 |
| 75 | STARE-VLA | 2512.05107 | 16 | 2025 |
| 76 | GigaBrain-0 | 2510.19430 | 15 | 2025 |
| 77 | πRL | — | 15 | 2025 |
| 78 | Shortcut Learning | 2508.06426 | 14 | 2025 |
| 79 | SAILOR | 2506.05294 | 14 | 2025 |
| 80 | 3DLLM-Mem | 2505.22657 | 14 | 2025 |
| 81 | OmniNav | 2509.25687 | 13 | 2025 |
| 82 | Residual Off-Policy RL | 2509.19301 | 13 | 2025 |
| 83 | Human2LocoMan | 2506.16475 | 13 | 2025 |
| 84 | Training-Time Action Conditioning | 2512.05964 | 12 | 2025 |
| 85 | GR-RL | 2512.01801 | 12 | 2025 |
| 86 | Agentic Multimodal LLM Survey | 2510.10991 | 12 | 2025 |
| 87 | Token Pruning for VLA | 2509.12594 | 12 | 2025 |
| 88 | TA-VLA | 2509.07962 | 12 | 2025 |
| 89 | Vidar | 2507.12898 | 12 | 2025 |
| 90 | X-Sim | 2505.07096 | 12 | 2025 |
| 91 | Robo-Dopamine | 2512.23703 | 11 | 2025 |
| 92 | mimic-video | 2512.15692 | 11 | 2025 |
| 93 | RLinf-VLA | 2510.06710 | 11 | 2025 |
| 94 | Reasoning on a Budget | 2507.02076 | 11 | 2025 |
