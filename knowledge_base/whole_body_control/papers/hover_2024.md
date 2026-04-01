# HOVER: Versatile Neural Whole-Body Controller for Humanoid Robots

- **arXiv**: 2410.21229
- **年份**: 2024 (ICRA 2025)
- **机构**: NVIDIA + CMU + UC Berkeley + UT Austin + UC San Diego
- **作者**: Tairan He*, Wenli Xiao*, Toru Lin, Zhengyi Luo, Zhenjia Xu, Zhenyu Jiang, Jan Kautz, Changliu Liu, Guanya Shi, Xiaolong Wang, Linxi "Jim" Fan†, Yuke Zhu†（* 共同一作，† GEAR Team Leads）
- **引用数**: 113
- **方法线归属**: **Multi-mode Policy Distillation / Unified WBC**
- **项目主页**: https://hover-versatile-humanoid.github.io

## 一句话总结

全身运动模仿作统一抽象，多模式策略蒸馏合并 15+ 控制模式为单一策略。

## 解决的问题

人形机器人全身控制需要支持导航、遥操作、桌面操作等截然不同的任务，每种任务依赖不同的控制接口：导航依赖根部速度跟踪，桌面操作需要关节角跟踪，而遥操作则要求末端执行器（头手）的运动学位置跟踪。现有方法（ExBody、H2O、OmniH2O、HumanPlus）各自为一种控制模式单独设计命令空间和奖励，策略之间不可复用，开发成本高且灵活性差。当机器人从步行（使用速度跟踪）切换到双臂操作（需要关节角或末端位置跟踪）时，无法在运行时无缝切换模式。此外，上游操作策略（VLA）在不同配置空间（关节角 vs 末端位置）输出动作，低层控制器也需要能适配这些多样接口。

## 核心方法

### 整体架构

HOVER 采用两阶段训练框架：**阶段一**训练一个 Oracle（全身运动跟踪）策略，以大规模 MoCap 数据为目标，获得通用运动先验；**阶段二**通过 DAgger 蒸馏，将 Oracle 策略的运动技能迁移到单一多模式学生策略中，学生策略支持 15+ 种控制模式，覆盖 ExBody、HumanPlus、H2O、OmniH2O 等先前工作的所有模式。统一命令空间由上身和下身两个控制区域组成，每个区域独立支持三种控制维度，通过 mode mask 和 sparsity mask 灵活激活。

### 阶段一：全身运动跟踪 Oracle 策略（WBT）

Oracle 策略 `π_oracle(a_t | s^{p-oracle}_t, s^{g-oracle}_t)` 使用完整特权信息（全身刚体位置、速度、朝向及前一帧参考 vs 当前帧的差值）作为 goal state，以 PPO 算法训练。输入包含人形机器人全身刚体位置 `p_t`、朝向 `θ_t`、线速度、角速度及前一帧动作；goal state 包含参考姿态 `(θ̂_{t+1}, p̂_{t+1})` 与当前状态的差值，以及绝对参考姿态。输出是 19 维目标关节位置，送入 PD 控制器驱动电机。奖励由三部分组成：惩罚项（力矩越限、DoF 位置/速度越限、终止惩罚）、正则化项（DoF 加速度/速度、动作变化率、力矩、脚部朝向、接触力、滑步）、任务奖励（DoF 位置/速度误差、全身关键点位置/旋转/速度误差、根部速度/旋转误差）。训练数据来自 AMASS MoCap 数据集，经过三步 Retargeting：(1) 人形机器人前向运动学计算关键点位置；(2) 优化 SMPL 参数与机器人关键点对齐；(3) 用梯度下降将 AMASS 中人体动作 retarget 到机器人关节空间，过滤掉不可行运动，得到数据集 Q̂。

### 阶段二：多模式策略蒸馏（Multi-mode Distillation）

这是论文的核心创新。学生策略 `π_student(a_t | s^{p-student}_t, s^{g-student}_t)` 使用受限的本体感知输入（无特权信息）：`s^{p-student}_t = [q, q̇, ω_base, g]_{t-25:t} ∪ [a_{t-25:t-1}]`，将过去 25 步的关节位置、速度、基座角速度、重力向量及动作历史堆叠作为输入，不依赖任何全局状态。

命令空间的关键设计是**双重 Mask**：`s^{g-student}_t = M_sparsity ⊙ [M_mode ⊙ s^{g-upper}_t, M_mode ⊙ s^{g-lower}_t]`。Mode Mask `M_mode` 从三种模式中选一种（运动学位置跟踪 / 关节角跟踪 / 根部跟踪），上身和下身独立选择；Sparsity Mask `M_sparsity` 进一步稀疏化，仅激活部分身体关键点（如只跟踪左手，或只跟踪头部）。两个 Mask 均从伯努利分布 `B(0.5)` 随机采样，在每个 episode 开始时固定，运行全程不变。

蒸馏使用 **DAgger 框架**：用学生策略在仿真中展开轨迹，同时查询 Oracle 策略给出参考动作 `â_t`，最小化 MSE 损失 `L = ||â_t - a_t||²₂`。这种方式让学生策略在自己产生的分布上学习，避免了 behavior cloning 的 compounding error 问题。

### 支持的控制模式（15+ 种）

统一命令空间包含三类控制维度，可对上/下身独立组合：

| 模式类型 | 输入格式 | 典型应用 |
|---------|---------|---------|
| **运动学位置跟踪** | 目标 3D 关键点位置（头、双手、双肩、双肘、双踝等） | 遥操作（VR/MoCap/外骨骼）、H2O/OmniH2O 风格 |
| **局部关节角跟踪** | 各关节电机目标角度（上身/下身独立） | 表达性运动模仿（ExBody/HumanPlus 风格）、桌面操作 |
| **根部跟踪** | 目标根部线速度、高度、翻滚/俯仰/偏航角 | 导航、地形穿越（velocity command 风格） |

具体模式举例：ExBody 模式（上身关节角 + 下身根部跟踪）、HumanPlus 模式（全身关节角 + 根部）、H2O 模式（上身/下身关键点运动学跟踪）、OmniH2O 模式（头+双手运动学跟踪）、Left/Right/Two-Hand 模式、Head 模式等。

## 关键洞见

全身运动学模仿（kinematic motion imitation）天然包含所有控制模式所需的运动知识——无论是关节角、末端位置还是根部速度，都是全身运动学状态的子集或派生量。因此，以全身 MoCap 数据训练的 Oracle 策略已经隐式掌握了平衡、协调、步态稳定性等通用运动技能，蒸馏时只需通过 Mask 告诉学生"你需要跟踪哪些维度"即可复用这些技能。这与单独为每种模式设计奖励并从头训练的方式形成鲜明对比——后者容易对特定奖励函数过拟合，泛化能力差。

多模式统一策略还能利用不同模式间的共享物理知识（保持平衡、人体运动节律等），形成跨模式的正向迁移，使得单一策略在每种模式上均**优于**专门为该模式单独训练的 specialist 策略。

## 实验结果

### 仿真评估（AMASS 数据集 Q̂）

HOVER 在所有 4 种主要控制模式下均优于对应的 specialist 基线，在 12 项指标中至少有 7 项达到统计显著优势：

| 模式 | 指标 | Specialist | HOVER |
|------|------|-----------|-------|
| ExBody | Eg-mpjpe (mm) ↓ | 275 | **185** |
| HumanPlus | Eg-mpjpe (mm) ↓ | 266 | **182** |
| H2O | Eg-mpjpe (mm) ↓ | 137 | **121** |
| OmniH2O | Eg-mpjpe (mm) ↓ | 149 | **128** |
| Right Hand | Eg-mpjpe (mm) ↓ | 220 | **128** |
| Two Hands | Eg-mpjpe (mm) ↓ | 137 | **120** |

与多模式 RL 基线（相同 Mask 设计但从头用 RL 训练）相比，HOVER 在 32/32 个指标和模式组合上均胜出，证明蒸馏框架的关键作用。

### 真实机器人评估（Unitree H1，20 个站立运动序列）

HOVER 在真实机器人上的 11/12 项指标优于 specialist 策略（ExBody、HumanPlus、OmniH2O 三种模式）。成功演示了根部俯仰运动跟踪、全身运动学跟踪（含高动态跑步动作）、模式切换（步行中从 ExBody 切换到 H2O 模式，后退/转身中从 HumanPlus 切换到 OmniH2O 模式），以及 Vision Pro 实时遥操作（随机 Mask 头手位置的稀疏跟踪）。

### Survival Rate

所有模式下 HOVER 存活率均在 98.9%~99.1%，与 Oracle（99.3%）和各 specialist 相当，表明蒸馏未损失稳定性。

## 实现细节

- **网络结构**: 三层 MLP，层维度 [512, 256, 128]（与 OmniH2O 相同）
- **机器人平台**: Unitree H1，19-DOF，质量 51.5kg，身高 1.8m
- **仿真环境**: IsaacGym（GPU 并行物理模拟）
- **动作空间**: 19 维目标关节位置，PD 控制器执行
- **Oracle 训练**: PPO 算法，使用 domain randomization（物理参数随机化）以支持 sim-to-real 迁移
- **蒸馏训练**: DAgger 在线蒸馏，使用学生展开的轨迹查询 Oracle 标注
- **Mask 采样**: Mode mask 和 sparsity mask 均从 B(0.5) 采样，每 episode 开始时固定
- **历史窗口**: 学生策略堆叠过去 25 步本体感知和动作历史
- **MoCap 数据集**: AMASS（大规模人体运动捕捉数据集）

## 与相关工作的关系

| 工作 | 上身命令 | 下身命令 | 多模式 |
|------|---------|---------|-------|
| ExBody [12] | 关节角 | 根部 | ✗ |
| H2O [10] | 运动学位置（6点） | 运动学位置（2点） | ✗ |
| OmniH2O [9] | 运动学位置（头+双手） | 无 | ✗ |
| HumanPlus [13] | 关节角 | 关节角 + 根部 | ✗ |
| MHC [21] | 运动学位置 + 根部 | 运动学位置 + 根部 | ✓（但不支持任意子集） |
| **HOVER (ours)** | 运动学位置 + 关节角 | 运动学位置 + 关节角 + 根部 | ✓（任意组合） |

HOVER 的核心区别在于：(1) 它是第一个在实机上支持**任意**控制模式任意组合的统一 WBC；(2) 与 MHC 相比，HOVER 通过蒸馏（而非 RL from scratch）获得更好性能，且支持运动学位置跟踪；(3) 与计算机图形学中的 MaskedMimic 思路类似但针对真实机器人，无需额外训练子策略。

PHC（Perpetual Humanoid Controller）是运动学全身控制的图形学经典工作，HOVER 沿用了其运动跟踪 Oracle 的设计思路，但进一步将其扩展为多模式的工程化控制器。ExBody2（2412.13196）在 HOVER 基础上进一步探索了表达性动作；ASAP（2502.01143）解决了 sim-to-real 物理对齐问题。

## 局限性与未来工作

- **模式切换无自动触发机制**：当前模式切换需要外部手动触发，论文指出未来工作将探索自动模式切换模块，根据任务上下文自主决定激活哪种控制模式。
- **下肢运动学跟踪未充分利用**：OmniH2O 模式的下身设为 N/A（不跟踪），对于需要精确脚部位置的任务（如踏点跨越障碍）能力有限。
- **文本截断**：本卡片基于前 30 页 / 80K 字符提取，可能遗漏附录中的超参数细节。
- **适用范围**：仅在 Unitree H1（19-DOF）上验证，对手指灵巧操作（dexterous manipulation）不适用。

## 关键引用

1. **OmniH2O** [9] (2406.08858) — Tairan He et al.，通用人到人形机器人遥操作，Kinematic 位置跟踪先驱，HOVER Oracle 网络结构来源
2. **H2O** [10] (2403.04436) — Tairan He et al.，实时全身遥操作，HOVER Retargeting 流程参考
3. **ExBody** [12] (2402.16796) — Xuxin Cheng et al.，表达性全身控制（上身关节角+下身根部）
4. **HumanPlus** [13] (2406.10454) — Zipeng Fu et al.，全身关节角跟踪与模仿
5. **MHC** [21] (2408.07295) — Dugar et al.，最接近的多模式 WBC 先驱，但不支持任意子集
6. **MaskedMimic** [44] — 计算机图形学中多模式运动控制蒸馏，方法论启发来源
7. **AMASS** [17] — Mahmood et al.，大规模 MoCap 数据集，Oracle 训练数据来源
8. **DAgger** [22] — Ross et al.，蒸馏框架，在线数据收集避免 compounding error
9. **PPO** [18] (1707.06347) — Schulman et al.，Oracle 策略训练算法
10. **IsaacGym** [23] (2108.10470) — NVIDIA，GPU 并行仿真环境

## 被引用情况（重要下游工作）

- **ASAP** (2502.01143, 156引) — Sim2Real 物理对齐，直接在 HOVER 基础上工作
- **ExBody2** (2412.13196, 112引) — 进阶表达性 WBC
- **TWIST** (2505.02833, 107引) — 遥操作系统
- **GMT** (2506.14770, 69引) — 通用运动跟踪
- **AMO** (2505.03738, 66引) — 高度灵巧 WBC
- **BeamDojo** (2502.10363, 65引) — 稀疏踏点敏捷运动
