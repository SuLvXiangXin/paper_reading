# Whole-Body Control 领域调研报告

> 调研日期：2026-03-17
> 锚点论文：SONIC (2511.07820), HOVER (2410.21229), BeyondMimic (2508.08241)
> 方法：Semantic Scholar 引用图谱法（三锚点交叉引用）

---

## 一、三篇锚点论文详情

### 1. SONIC: Supersizing Motion Tracking for Natural Humanoid Whole-Body Control
- **arXiv**: 2511.07820
- **年份**: 2025
- **引用数**: 33
- **机构**: NVIDIA (Zhengyi Luo, Ye Yuan, Jan Kautz, LinxiJimFan, Yuke Zhu 等)
- **核心贡献**:
  - 首次展示 WBC 基础模型 Scaling 效果：网络从 1.2M → 42M 参数，数据集 100M+ 帧/700小时
  - 以运动跟踪（motion tracking）作为可扩展的通用任务，利用动捕数据提供密集监督
  - 训练消耗 9000 GPU 小时
  - 统一 Token 空间支持 VR 遥操作、人体视频、VLA 模型等多种输入
  - 实时通用运动规划器（kinematic planner）连接运动跟踪和下游任务执行
- **方法线归属**: **Foundation Model WBC / Motion Imitation + Scaling**

### 2. HOVER: Versatile Neural Whole-Body Controller for Humanoid Robots
- **arXiv**: 2410.21229
- **年份**: 2024 (ICRA 2025)
- **引用数**: 113
- **机构**: CMU + NVIDIA + UT Austin (Tairan He, Guanya Shi, Jan Kautz, Yuke Zhu 等)
- **核心贡献**:
  - 关键洞见：全身运动模仿可作为所有控制任务的**通用抽象**
  - 多模态策略蒸馏（Multi-mode Policy Distillation）：将速度控制、关节角控制、末端执行器控制等多种模式统一到单一策略
  - 无需为每种控制模式重新训练策略，实现模式间无缝切换
- **方法线归属**: **Multi-mode Policy Distillation / Unified WBC**

### 3. BeyondMimic: From Motion Tracking to Versatile Humanoid Control via Guided Diffusion
- **arXiv**: 2508.08241
- **年份**: 2025
- **引用数**: 119
- **机构**: UC Berkeley (Qiayuan Liao, K. Sreenath, C.K. Liu)
- **核心贡献**:
  - 紧凑运动跟踪框架：统一设置+共享超参数，掌握空中翻转（aerial cartwheels）、旋踢（spin-kicks）、翻踢（flip-kicks）、冲刺等高动态运动
  - 统一潜在扩散模型（latent diffusion model）：支持多样化目标规格、无缝任务切换、动态技能组合
  - 利用**分类器引导（classifier guidance）**实现测试时优化，零样本泛化到未见任务（运动填补、操纵杆遥操作、避障）
  - 零样本迁移到真实硬件
- **方法线归属**: **Diffusion-based WBC / Motion Tracking + Guided Diffusion**

---

## 二、Top References（被三篇锚点论文共同引用，按引用数排序）

| 引用数 | arXiv | 论文 | 年份 | 类别 |
|-------|-------|------|------|------|
| 550 | 2503.14734 | GR00T N1: Open Foundation Model for Generalist Humanoid Robots | 2025 | Foundation Model |
| 307 | 2303.03381 | Real-world humanoid locomotion with reinforcement learning | 2023 | Locomotion RL |
| 249 | 2406.10454 | HumanPlus: Humanoid Shadowing and Imitation from Humans | 2024 | Teleoperation+Imitation |
| 241 | 2407.01512 | Open-TeleVision: Teleoperation with Immersive Active Visual Feedback | 2024 | Teleoperation |
| 240 | 2406.08858 | OmniH2O: Universal and Dexterous H2H Whole-Body Teleoperation | 2024 | WB Teleoperation |
| 231 | 2305.06456 | PHC: Perpetual Humanoid Control for Real-time Simulated Avatars | 2023 | Motion Imitation |
| 213 | 2402.16796 | Exbody: Expressive Whole-Body Control for Humanoid Robots | 2024 | Expressive WBC |
| 209 | 2403.04436 | H2O: Learning Human-to-Humanoid Real-Time WB Teleoperation | 2024 | WB Teleoperation |
| 182 | 2401.16889 | RL for versatile, dynamic, and robust bipedal locomotion control | 2024 | Bipedal Locomotion |
| 156 | 2502.01143 | ASAP: Aligning Sim and Real-World Physics for Agile Humanoid WBC | 2025 | Sim-to-Real |
| 144 | 2406.10759 | Humanoid Parkour Learning | 2024 | Agile Locomotion |
| 132 | 2401.17583 | Agile But Safe: Collision-Free High-Speed Legged Locomotion | 2024 | Safe Locomotion |
| 115 | 2305.02195 | CALM: Conditional Adversarial Latent Models for Virtual Characters | 2023 | Motion Prior |
| 112 | 2310.04582 | Universal Humanoid Motion Representations for Physics-Based Control | 2023 | Motion Representation |
| 109 | 2409.14393 | MaskedMimic: Unified Physics-Based Character Control | 2024 | Motion Imitation |
| 94 | 2406.06005 | WoCoCo: Learning Whole-Body Humanoid Control with Sequential Contacts | 2024 | Loco-Manipulation |
| 84 | 2410.11792 | OKAMI: Manipulation Skills through Single Video Imitation | 2024 | Video Imitation |

---

## 三、Top Citations（引用这三篇锚点论文的后续工作）

### 高引用后续工作（>30次引用）

| 引用数 | arXiv | 论文 | 年份 | 类别 |
|-------|-------|------|------|------|
| 156 | 2502.01143 | ASAP: Aligning Simulation and Real-World Physics | 2025 | Sim-to-Real |
| 112 | 2412.13196 | ExBody2: Advanced Expressive Humanoid WBC | 2024 | Expressive WBC |
| 107 | 2505.02833 | TWIST: Teleoperated Whole-Body Imitation System | 2025 | Teleoperation |
| 69 | 2506.14770 | GMT: General Motion Tracking for Humanoid WBC | 2025 | Motion Tracking |
| 66 | 2505.03738 | AMO: Adaptive Motion Optimization for Hyper-Dexterous WBC | 2025 | Dexterous WBC |
| 66 | 2502.08378 | Learning Humanoid Standing-up Control across Diverse Postures | 2025 | Getting-Up |
| 65 | 2502.10363 | BeamDojo: Agile Humanoid Locomotion on Sparse Footholds | 2025 | Agile Locomotion |
| 56 | 2506.12851 | KungfuBot: Physics-Based Humanoid WBC for Highly-Dynamic Skills | 2025 | High-Dynamic |
| 51 | 2506.08931 | CLONE: Closed-Loop WB Humanoid Teleoperation | 2025 | Teleoperation |
| 51 | 2505.06776 | FALCON: Learning Force-Adaptive Humanoid Loco-Manipulation | 2025 | Loco-Manipulation |
| 47 | 2502.12152 | Learning Getting-Up Policies for Real-World Humanoid Robots | 2025 | Recovery |
| 45 | 2509.26633 | OmniRetarget: Interaction-Preserving Data Generation | 2025 | Data/Retargeting |
| 41 | 2510.02252 | Retargeting Matters: General Motion Retargeting | 2025 | Motion Retargeting |
| 38 | 2503.19901 | TokenHSI: Physical Human-Scene Interactions | 2025 | Scene Interaction |
| 37 | 2505.07294 | HuB: Learning Extreme Humanoid Balance | 2025 | Balance |
| 33 | 2511.07820 | SONIC (anchor 1) | 2025 | - |
| 31 | 2507.07356 | UniTracker: Universal Whole-Body Motion Tracker | 2025 | Motion Tracking |
| 29 | 2511.02832 | TWIST2: Scalable Humanoid Data Collection System | 2025 | Data Collection |
| 29 | 2508.21043 | HITTER: Humanoid Table Tennis via Hierarchical Planning | 2025 | Sports |

### 新兴前沿工作（2025-2026，引用数较低但话题前沿）

| 引用数 | arXiv | 论文 | 类别 |
|-------|-------|------|------|
| 26 | 2504.21738 | LangWBC: Language-directed Humanoid WBC | 语言引导 |
| 27 | 2509.16757 | HDMI: Interactive WBC from Human Videos | 视频学习 |
| 25 | 2510.05070 | ResMimic: Motion Tracking to Loco-Manipulation | 运动跟踪→操作 |
| 14 | 2511.15200 | VIRAL: Visual Sim-to-Real at Scale for Humanoid Loco-Manipulation | 视觉Sim2Real |
| 13 | 2512.11047 | WholeBodyVLA: Unified Latent VLA for WB Loco-Manipulation | VLA+WBC |
| 4 | 2506.20487 | A Survey of Behavior Foundation Model: Next-Generation WBC | 综述 |
| 3 | 2601.12799 | FRoM-W1: General WBC with Language Instructions | 语言引导 |
| 0 | 2603.12263 | Ψ₀: Open Foundation Model for Universal Humanoid Loco-Manipulation | 基础模型 |

---

## 四、领域重要论文分类

### 流派 A：运动模仿与物理控制（Motion Imitation / Physics-Based Control）
> 从人体动捕数据学运动先验，强化学习跟踪参考运动

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| DeepMimic | 1804.02717 | 运动模仿RL开山之作 | 564 |
| PHC (Perpetual Humanoid Control) | 2305.06456 | 实时仿真人形控制 | 231 |
| UHMP (Universal Humanoid Motion Repr.) | 2310.04582 | 通用运动表示，物理控制 | 112 |
| MaskedMimic | 2409.14393 | 遮蔽运动填补，统一物理控制 | 109 |
| HOVER | 2410.21229 | 多模式策略蒸馏，通用WBC | 113 |
| BeyondMimic | 2508.08241 | 扩散引导，零样本泛化 | 119 |
| SONIC | 2511.07820 | 运动跟踪Scaling，基础模型 | 33 |
| Retargeting Matters | 2510.02252 | 通用运动重定向 | 41 |
| GMT | 2506.14770 | 通用运动跟踪 | 69 |
| UniTracker | 2507.07356 | 统一全身运动跟踪器 | 31 |

### 流派 B：全身遥操作（Whole-Body Teleoperation）
> 人类操作员→实时控制机器人，同时收集数据训练自主策略

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| H2O | 2403.04436 | 首个学习型实时全身遥操作 | 209 |
| OmniH2O | 2406.08858 | VR+语言+RGB多模态遥操作 | 240 |
| HumanPlus | 2406.10454 | 遥操作→行为克隆，全站任务 | 249 |
| Open-TeleVision | 2407.01512 | 沉浸式主动视觉遥操作 | 241 |
| TWIST | 2505.02833 | 全身遥操作系统 | 107 |
| TWIST2 | 2511.02832 | 可扩展便携遥操作数据收集 | 29 |
| CLONE | 2506.08931 | 闭环全身长时域遥操作 | 51 |
| HOMIE | 2502.13013 | 等构外骨骼驾驶舱 | 104 |

### 流派 C：Sim-to-Real 迁移
> 解决仿真与真实物理世界的差距

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| ASAP | 2502.01143 | 对齐仿真与真实物理，敏捷WBC | 156 |
| VIRAL | 2511.15200 | 视觉Sim2Real规模化Loco-Manipulation | 14 |
| BeamDojo | 2502.10363 | 稀疏踩踏点上的敏捷运动 | 65 |

### 流派 D：高动态运动（Agile / Athletic Motion）
> 跑酷、竞技体育、极端运动

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| Humanoid Parkour Learning | 2406.10759 | 端到端视觉全身控制跑酷 | 144 |
| KungfuBot | 2506.12851 | 高动态武术动作 | 56 |
| KungfuBot2 | 2509.16638 | 多种运动技能 | 17 |
| HITTER | 2508.21043 | 乒乓球机器人，分层规划 | 29 |
| HuB | 2505.07294 | 极端平衡控制 | 37 |
| BeyondMimic | 2508.08241 | 空中翻转、旋踢、冲刺 | 119 |

### 流派 E：Loco-Manipulation（移动操作）
> 腿部移动 + 手臂操作的全身协同

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| WoCoCo | 2406.06005 | 序贯接触全身人形控制 | 94 |
| FALCON | 2505.06776 | 力自适应Loco-Manipulation | 51 |
| OKAMI | 2410.11792 | 单视频模仿操作技能 | 84 |
| ResMimic | 2510.05070 | 运动跟踪→全身Loco-Manipulation | 25 |
| OmniRetarget | 2509.26633 | 保持交互的数据生成 | 45 |
| HDMI | 2509.16757 | 从人类视频学交互式WBC | 27 |
| AMO | 2505.03738 | 高度灵巧全身控制自适应运动优化 | 66 |

### 流派 F：表达性全身控制（Expressive WBC）
> 模仿人类表情/舞蹈等非功能性动作

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| Exbody | 2402.16796 | 上半身模仿+下半身速度跟踪 | 213 |
| ExBody2 | 2412.13196 | 教师策略过滤+学生策略迁移 | 112 |
| CALM | 2305.02195 | 条件对抗潜变量模型 | 115 |

### 流派 G：基础模型 / 大规模预训练
> Foundation Models for Humanoid Control

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| GR00T N1 | 2503.14734 | NVIDIA开源人形基础模型 | 550 |
| SONIC | 2511.07820 | 42M参数运动跟踪基础模型 | 33 |
| ASAP | 2502.01143 | 敏捷WBC + 物理对齐 | 156 |
| Ψ₀ (Psi-0) | 2603.12263 | 通用Loco-Manipulation开源基础模型 | 0 |

### 流派 H：语言/VLA 引导的全身控制
> 语言指令 + 视觉语言动作模型

| 论文 | arXiv | 核心贡献 | 引用 |
|------|-------|---------|------|
| LangWBC | 2504.21738 | 端到端语言引导WBC | 26 |
| FRoM-W1 | 2601.12799 | 语言指令通用WBC | 3 |
| WholeBodyVLA | 2512.11047 | 统一VLA for Loco-Manipulation | 13 |
| SENTINEL | 2511.19236 | 端到端语言动作模型全身控制 | 2 |

---

## 五、关键研究主题与趋势

### 主题 1：运动跟踪作为通用接口
- 三篇锚点论文的核心共识：运动跟踪提供了连接人类动作到机器人控制的自然桥梁
- HOVER 和 SONIC 都认为全身运动模仿是多种控制模式的通用抽象
- BeyondMimic 进一步用扩散模型将运动跟踪升华为可组合的技能空间

### 主题 2：Scaling Laws 来到机器人控制
- SONIC 是首批明确探索 WBC Scaling 的工作：3个Scaling轴（网络、数据、计算）均带来性能提升
- 对比 VLA 领域，WBC 的 Scaling 仍处于早期阶段（百亿参数模型尚未出现）
- 数据质量和多样性比纯量更关键（700小时高质量动捕 vs. 随机视频）

### 主题 3：多模式控制统一
- HOVER 的多模式蒸馏范式（速度控制、关节控制、末端执行器控制）被广泛采用
- 后续工作：AMO（高度灵巧）、UniTracker（统一跟踪器）继续扩展控制模式
- 趋势：从"多个专用策略"到"单一通用策略"

### 主题 4：扩散模型在WBC的崛起
- BeyondMimic 证明扩散模型可以实现技能组合和零样本泛化
- 关联工作：CLoSD, DiffuseLoco, PDP, BiRoDiff
- 分类器引导是关键技术：测试时优化，无需重新训练

### 主题 5：遥操作→自主策略
- H2O → OmniH2O → HumanPlus → TWIST → CLONE 的发展脉络
- 趋势：遥操作不只是部署工具，更是数据收集管道
- TWIST2 专注可扩展数据收集基础设施

### 主题 6：Sim-to-Real 仍是瓶颈
- ASAP 通过对齐仿真和真实物理显著提升性能
- VIRAL 专门研究视觉 Sim-to-Real 规模化
- 所有锚点论文均在真实硬件上验证，Sim2Real 质量直接决定可用性

### 主题 7：高动态运动的突破
- BeyondMimic 展示了前所未有的高动态技能（空中翻转、旋踢）
- KungfuBot/KungfuBot2 聚焦武术类高动态运动
- Humanoid Parkour 推动了跑酷等户外挑战性场景

### 主题 8：全身+VLA 的融合趋势
- WholeBodyVLA, SONIC (支持VLA输入), VIRAL 等开始探索
- GR00T N1 作为基础模型，上层可接VLA任务规划
- 预测：WBC 基础控制器 + VLA 上层规划将成主流架构

---

## 六、重要数据集与基准

| 数据集 | 来源 | 内容 | 规模 |
|--------|------|------|------|
| AMASS | 2019 | 动作捕捉数据集合 | 大规模 |
| SONIC 数据集 | 2025 | 高质量动捕 | 100M帧, 700h |
| OmniH2O-6 | 2024 | 六种日常任务全身控制数据 | - |

---

## 七、关键作者/机构图谱

| 机构 | 代表作者 | 代表论文 |
|------|---------|---------|
| CMU (Carnegie Mellon) | Tairan He, Guanya Shi, Changliu Liu | HOVER, H2O, OmniH2O |
| NVIDIA | Jan Kautz, LinxiJimFan, Yuke Zhu, Zhengyi Luo | SONIC, GR00T N1, HOVER |
| UC Berkeley | K. Sreenath, Qiayuan Liao, Zhongyu Li | BeyondMimic, Humanoid Parkour |
| UC San Diego | Xiaolong Wang | Exbody, ExBody2, HOVER |
| Stanford | Chelsea Finn, Zipeng Fu | HumanPlus |

---

## 八、速查表：从任务出发找论文

| 想做的任务 | 首选论文 |
|-----------|---------|
| 让机器人模仿人体动作 | HOVER, SONIC, BeyondMimic |
| 实时遥操作全身 | H2O, OmniH2O, TWIST |
| 边走边操作物体 | WoCoCo, FALCON, OmniH2O |
| 高动态技巧（翻滚、跑酷） | BeyondMimic, Humanoid Parkour, KungfuBot |
| 用语言控制机器人 | LangWBC, FRoM-W1, WholeBodyVLA |
| 解决Sim2Real差距 | ASAP, VIRAL |
| 从人类视频学控制 | HumanPlus, HDMI, OKAMI |
| 训练基础模型 | SONIC, GR00T N1 |
| 舞蹈/表达性动作 | Exbody, ExBody2 |
| 从失败姿势恢复站立 | Getting-Up Policies (2502.12152), Standing-up (2502.08378) |
