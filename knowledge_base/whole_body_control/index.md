# Whole-Body Control (WBC) 领域总览

> 领域别名：全身控制 / 类人机器人控制 / 运动仿人 / Loco-Manipulation
> 创建日期：2026-03-17
> 锚点论文：SONIC (2511.07820), HOVER (2410.21229), BeyondMimic (2508.08241)

## 领域定义

Whole-Body Control (WBC) 研究如何让类人机器人（humanoid robots）协调全身关节（上半身+下半身）完成复杂运动和操作任务。核心挑战：

1. **高自由度协调**：人形机器人通常有 30+ DoF，需同时控制腿部（步态）和手臂（操作）
2. **Sim-to-Real Transfer**：仿真训练的策略在真实硬件上的物理差距
3. **多模态控制接口**：速度命令、关节角度、人体姿态、语言、视觉等多种输入形式
4. **运动多样性**：从平稳行走到高动态技巧（parkour、翻跟头、踢腿）

## 技术主线

| 主线 | 核心思想 | 代表论文 |
|------|---------|---------|
| **运动模仿 (Motion Imitation)** | 从人体动捕数据学习动作先验，强化学习跟踪 | DeepMimic, PHC, HOVER, SONIC |
| **动作蒸馏 (Policy Distillation)** | 多技能/多模态专家策略蒸馏为统一策略 | HOVER, AMO, ASAP |
| **全身遥操作 (WB Teleoperation)** | 人→机器人实时运动映射 + 学习自主策略 | H2O, OmniH2O, HumanPlus, TWIST |
| **扩散策略 (Diffusion Policy)** | 扩散模型生成运动轨迹，分类器引导泛化 | BeyondMimic, DiffuseLoco, PDP |
| **敏捷运动 (Agile Locomotion)** | 跑酷、高动态运动，融合感知 | Parkour Learning, BeamDojo, KungfuBot |
| **Loco-Manipulation** | 边走边操作，手脚协同 | WoCoCo, FALCON, CLONE, OmniH2O |
| **Foundation Models** | 大规模预训练，泛化到多任务 | GR00T N1, SONIC (42M参数), ASAP |

## 关键论文（按引用数）

| 引用数 | arXiv | 论文 | 年份 |
|-------|-------|------|------|
| 550 | 2503.14734 | GR00T N1: Open Foundation Model for Generalist Humanoid | 2025 |
| 307 | 2303.03381 | Real-world humanoid locomotion with RL | 2023 |
| 249 | 2406.10454 | HumanPlus: Humanoid Shadowing and Imitation | 2024 |
| 241 | 2407.01512 | Open-TeleVision | 2024 |
| 240 | 2406.08858 | OmniH2O: Universal H2H Whole-Body Teleoperation | 2024 |
| 231 | 2305.06456 | PHC: Perpetual Humanoid Control | 2023 |
| 213 | 2402.16796 | Exbody: Expressive Whole-Body Control | 2024 |
| 209 | 2403.04436 | H2O: Learning Human-to-Humanoid Real-Time WB Teleoperation | 2024 |
| 182 | 2401.16889 | RL for versatile bipedal locomotion | 2024 |
| 156 | 2502.01143 | ASAP: Aligning Sim and Real Physics | 2025 |
| 144 | 2406.10759 | Humanoid Parkour Learning | 2024 |
| 119 | 2508.08241 | **BeyondMimic** (anchor) | 2025 |
| 113 | 2410.21229 | **HOVER** (anchor) | 2024 |
| 112 | 2412.13196 | ExBody2: Advanced Expressive WBC | 2024 |
| 109 | 2409.14393 | MaskedMimic | 2024 |
| 107 | 2505.02833 | TWIST | 2025 |
| 33 | 2511.07820 | **SONIC** (anchor) | 2025 |

## 研究前沿（2025-2026）

- **大规模基础模型**：SONIC (42M参数, 700h动捕数据), GR00T N1
- **运动重定向**：OmniRetarget, Retargeting Matters, SPIDER
- **交互式全身控制**：HDMI, CLONE, TWIST2
- **语言引导WBC**：LangWBC, FRoM-W1, TextOp
- **具身运动控制(VLA+WBC)**：WholeBodyVLA, SENTINEL, VIRAL
- **高动态运动**：KungfuBot, Thor, OmniXtreme, BeyondMimic (空中翻转、旋踢)

## 子目录
- `papers/` — 论文卡片
- `methods/` — 方法分类
- `reports/` — 调研报告
- `components/` — 技术组件（Sim2Real, 运动重定向, 遥操作接口等）
