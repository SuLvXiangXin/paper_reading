# RL-based Robot Locomotion 全景调研（详细版）

> 调研日期：2026-04-01
> 数据来源：Brave Search, Semantic Scholar, GitHub Awesome Lists, arXiv Surveys
> 覆盖范围：2018—2026，150+ 核心论文，14 大技术方向

---

## 一、领域全貌

基于深度强化学习（DRL）的机器人运动控制是过去 8 年机器人学最成功的方向之一。以 2018 年 sim-to-real 突破为起点，到 2025 年人形跑酷、载重行走和语言控制，该领域经历了从"能走"到"能跑能跳能听指令"的飞跃。

**三大机器人形态**：
- **四足机器人**（最成熟）：ANYmal (ETH), Unitree Go1/A1/Go2, MIT Mini Cheetah, Boston Dynamics Spot
- **双足/人形**（快速增长）：Cassie (Oregon State), Digit (Agility), Atlas (BD), Unitree H1/G1, OP-3
- **轮腿混合**（新兴方向）：ANYmal-W / Swiss-Mile (ETH), Ascento (ETH)

**核心研究机构版图**：
| 机构 | 主攻方向 | 代表人物 |
|------|---------|---------|
| ETH Zurich RSL | 四足全栈（盲行/感知/跑酷/轮腿） | Marco Hutter, Joonho Lee, Nikita Rudin, David Hoeller |
| UC Berkeley | 双足/人形、适应性、跑酷 | Pieter Abbeel, Sergey Levine, Koushil Sreenath, Jitendra Malik, Deepak Pathak |
| CMU | 敏捷运动、全身控制、力控 | Tairan He, Guanya Shi, Xuxin Cheng |
| MIT CSAIL | 快速运动、行为多样性 | Pulkit Agrawal, Gabriel Margolis |
| Google DeepMind | 双足足球、RL 算法 | Tuomas Haarnoja |
| KAIST | 四足鲁棒性、可变形地形 | Hyun Myung |
| UBC / Meta | 运动模仿（DeepMimic/AMP/ASE） | Xue Bin Peng |
| NVIDIA | 大规模训练基础设施、人形基础模型 | Zhengyi Luo, Yuke Zhu, Lin-Xi Fan |
| Tsinghua / ShanghaiQizhi | 人形跑酷 | Hang Zhao, Ziwen Zhuang |
| Oregon State | Cassie 双足行走 | Alan Fern, Jonathan Hurst |

---

## 二、技术演进时间线

```
2018  ┌─ Sim-to-Real 四足 (Tan/Google)     ─ 域随机化奠基
      └─ DeepMimic (Peng/UBC)              ─ 运动模仿奠基
2019     ANYmal Agile Skills (ETH) ★        ─ actuator network, 里程碑
2020  ┌─ Challenging Terrain (ETH) ★        ─ teacher-student 盲行范式
      └─ Imitating Animals (Google)         ─ 跨形态运动迁移
2021  ┌─ IsaacGym + legged_gym (ETH/NVIDIA) ─ 分钟级训练基础设施
      ├─ RMA (Berkeley/CMU)                 ─ 在线适应框架
      ├─ AMP (Peng/UBC)                     ─ 对抗式运动先验
      └─ Energy→Gait Emergence (Berkeley)   ─ 步态涌现
2022  ┌─ Perceptive Wild (ETH) ★            ─ 多模态感知户外
      ├─ Walk These Ways (MIT)              ─ 步态族编码
      ├─ Rapid Locomotion (MIT)             ─ 3.9m/s 记录
      └─ ASE (Peng/SIGGRAPH)               ─ 可复用技能嵌入
2023  ┌─ Robot Parkour (Stanford/CMU)       ─ 两阶段跑酷
      ├─ Extreme Parkour (CMU)              ─ 端到端跑酷
      └─ DreamWaQ (KAIST)                  ─ 隐式地形想象
2024  ┌─ ANYmal Parkour (ETH) ★            ─ 全跑酷赛道
      ├─ Humanoid Loco Transformer (Berkeley) ★ ─ 里程碑人形行走
      ├─ Soccer DeepMind ★                 ─ 双足足球
      ├─ Wheeled-Legged Nav (ETH) ★        ─ 10km 轮腿自主导航
      ├─ Humanoid Parkour (Tsinghua)        ─ 首个人形跑酷
      ├─ HOVER (CMU/NVIDIA)                ─ 多模式统一控制
      └─ ExBody/ExBody2 (UCSD)             ─ 全身表达性控制
2025  ┌─ SONIC (NVIDIA)                    ─ 42M参数大规模运动跟踪
      ├─ ASAP (CMU/NVIDIA)                 ─ 仿真-真实对齐
      ├─ GR00T N1 (NVIDIA)                 ─ 人形基础模型
      ├─ WoCoCo/FALCON/HugWBC             ─ 全身接触/力控/统一控制
      └─ Language/Audio-driven loco        ─ 语言/音频控制运动
2026  ┌─ Foundation model convergence      ─ Psi-0, BFM, GR00T N1.6
      └─ Sports & extreme skills           ─ 网球/跑酷/乒乓球
```

★ = Science Robotics 发表

---

## 三、技术路线一：Sim-to-Real 迁移

**核心问题**：仿真训练的策略如何零样本迁移到真实机器人？

### 3.1 域随机化（Domain Randomization）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Sim-to-Real: Learning Agile Locomotion for Quadruped Robots** (Tan et al., Google Brain) | 2018 | 1804.10332 | ~935 | 首个 RL sim-to-real 成功；Minitaur 机器人；域随机化 + 解析电机模型 |
| **Sim-to-Real Transfer with Dynamics Randomization** (Peng et al.) | 2018 | -- | ~500 | 系统化域随机化方法论；OpenAI Hopper/Ant |
| **PACE: Systematic Sim-to-Real for Diverse Legged Robots** (Bjelonic et al.) | 2025 | 2509.06342 | 新 | 仅需 20s 真实数据做参数辨识，消除域随机化需求；10+ 机器人零样本迁移；CoT 降低 32% |

### 3.2 Actuator Network（执行器建模）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Learning Agile and Dynamic Motor Skills for Legged Robots** (Hwangbo et al., ETH) | 2019 | 1901.08652 | ~1651 | **ANYmal 里程碑**；神经网络建模执行器动力学（actuator net）替代解析模型；速度跟踪 + 跌倒恢复 |

### 3.3 Teacher-Student 特权学习

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Learning Quadrupedal Locomotion over Challenging Terrain** (Lee et al., ETH) | 2020 | 2010.11251 | ~1545 | **开创 teacher-student 范式**：teacher 用地形高度图，student 仅本体感知蒸馏；ANYmal 盲行楼梯/碎石 |
| **CTS: Concurrent Teacher-Student RL** | 2024 | 2405.10830 | -- | 同步训练 teacher/student（改良 PPO），误差降低 17-22% |
| **VMTS: Vision-Assisted Teacher-Student for Multi-Terrain Bipedal** | 2025 | 2503.07049 | -- | 混合专家 teacher-student + 视觉输入用于双足多地形 |

### 3.4 在线快速适应

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **RMA: Rapid Motor Adaptation for Legged Robots** (Kumar et al., Berkeley/CMU) | 2021 | 2107.04034 | ~800 | **两阶段适应框架**：base policy + 适应模块（从本体感知历史在线推断环境参数）；A1 无需微调部署 |
| **ASAP: Aligning Simulation and Real-World Physics** (He et al., CMU/NVIDIA) | 2025 | 2502.01143 | -- | delta-action 模型弥合动力学差距，用于敏捷人形运动技能 |
| **VR-Robo: Real-to-Sim-to-Real via 3DGS** | 2025 | 2502.01536 | -- | 3D Gaussian Splatting 数字孪生做仿真；RGB-only 策略迁移 |

---

## 四、技术路线二：大规模并行训练基础设施

| 论文/工具 | 年份 | arXiv | 核心贡献 |
|-----------|------|-------|---------|
| **MuJoCo** (DeepMind, 开源) | 2012/2021 | -- | 通用高精度物理仿真器；学术研究标准 |
| **Learning to Walk in Minutes** (Rudin et al., ETH/NVIDIA) | 2021 | 2109.11978 | ~887 | **IsaacGym + legged_gym 框架**；4096 并行环境，ANYmal 分钟级收敛；开源，成为领域标准 |
| **IsaacLab / Isaac Gym** (NVIDIA) | 2021→2024 | -- | GPU 大规模并行仿真；支持所有主流机器人 |
| **Humanoid-Gym** (Gu et al.) | 2024 | 2404.05695 | -- | 针对人形机器人的 Isaac Gym 框架；支持 H1 sim-to-sim/real pipeline |
| **DayDreamer: World Models for Physical Robot Learning** | 2022 | 2206.14176 | -- | 世界模型提升样本效率；真实机器人上从头学习 |

---

## 五、技术路线三：奖励设计与自动化

### 5.1 手工奖励与能量最小化

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Minimizing Energy Consumption → Emergence of Gaits** (Fu et al., Berkeley) | 2021 | 2111.01674 | ~250 | **里程碑**：单一能量最小化奖励自然涌现步行/小跑步态转换；不需要手工设计步态奖励 |
| **DeepTransition: Viability → Gait Transitions** (Shafiee et al., EPFL) | 2024 | 2306.07419 | -- | 可行性（避免摔倒）驱动步态转换；walk→trot→pronk 自然涌现；Nature Communications |

### 5.2 LLM 自动化奖励生成

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Eureka: Human-Level Reward Design via Coding LLMs** (Ma et al., NVIDIA/Penn) | 2024 | 2310.12931 | ~300+ | GPT-4 进化式生成奖励代码；29 个任务 83% 超过人类专家；Unitree H1 快速奔跑 |
| **STRIDE: Automating Reward Design for Humanoid Locomotion** | 2025 | 2502.04692 | -- | GPT-4o mini 自动奖励生成 + 课程学习；人形机器人像职业运动员冲刺 |

### 5.3 VLM 零样本奖励

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **VLM-RMs: VLMs as Zero-Shot Reward Models** | 2023 | 2310.12921 | -- | CLIP-based VLM 做零样本奖励；自然语言描述驱动 MuJoCo 人形运动 |
| **RL-VLM-F: RL from VLM Feedback** | 2024 | 2402.03681 | -- | VLM 做成对偏好标注；从偏好标签学习奖励函数 |

---

## 六、技术路线四：课程学习（Curriculum Learning）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Rapid Locomotion via RL** (Margolis et al., MIT) | 2022 | 2205.02824 | ~250 | 自适应速度课程：动态调整速度目标难度；Mini Cheetah 3.9 m/s 记录 |
| **Scaling Rough Terrain Locomotion with Automatic Curriculum RL** | 2026 | 2601.17428 | -- | 基于学习进度的自动课程；ANYmal D 2.5 m/s 越楼梯/坡道/碎石 |
| **CurricuLLM: Automatic Task Curricula via LLMs** | 2024 | 2409.18382 | -- | LLM 自动设计课程；ICRA 2025 |
| **SoloParkour: Constrained RL for Visual Parkour** | 2024 | 2409.13678 | -- | 跑酷作为约束 RL；联合训练于递增难度地形课程 |

---

## 七、技术路线五：运动模仿（Motion Imitation / AMP 体系）

**核心思想**：从动捕数据/视频中提取运动风格，避免手工设计奖励。

### 7.1 DeepMimic → AMP → ASE 主线

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **DeepMimic** (Peng et al., UBC) | 2018 | 1804.02717 | ~1500+ | **开山之作**：参考动作引导 DRL；物理角色学翻跟头/武术/舞蹈；ACM SIGGRAPH |
| **Learning Agile Locomotion by Imitating Animals** (Peng et al., Google/Berkeley) | 2020 | 2004.00784 | ~800+ | 真实动物动捕（狗）→ 四足运动；跨形态迁移；RSS 2020 |
| **AMP: Adversarial Motion Priors** (Peng et al., UBC) | 2021 | 2104.02180 | ~600+ | **里程碑**：判别器替代手工奖励；从非结构化动捕数据学风格；可组合不同技能；ACM SIGGRAPH |
| **ASE: Adversarial Skill Embeddings** (Peng et al.) | 2022 | -- | ~300+ | 大规模可复用技能嵌入空间；技能条件策略；SIGGRAPH 2022 |
| **CALM: Conditional Adversarial Latent Models** | 2023 | -- | ~115 | 条件对抗潜变量模型；可控运动生成 |
| **Learning Agile Skills via Adversarial Imitation of Rough Partial Demos** | 2023 | -- | ~80 | 从粗糙/部分演示学习敏捷技能；CoRL 2023 |

### 7.2 全身运动跟踪（大规模）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **PHC: Perpetual Humanoid Control** (Luo et al., CMU/NVIDIA) | 2023 | -- | ~231 | 通用人形运动跟踪；AMASS 数据集大规模训练 |
| **MaskedMimic: Unified Physics-Based Character Control** | 2024 | -- | ~109 | 遮蔽式模仿：统一的物理角色控制框架 |
| **SONIC: Supersizing Motion Tracking for Humanoid WBC** (Luo et al., NVIDIA) | 2025 | 2511.07820 | -- | **最新 SOTA**：42M 参数；AMASS 大规模训练；99.6% 未见动作成功率（vs 先前 58%）；Scaling Law 在运动控制中成立 |
| **GMT: General Motion Tracking for Humanoid** | 2025 | 2506.14770 | -- | 统一单策略框架；优先局部位姿/速度一致性 |
| **ExBody: Expressive Whole-Body Control** (Cheng et al., UCSD) | 2024 | 2402.16796 | ~213 | 上肢模仿人类动捕，下肢跟踪速度指令；RSS 2024 |
| **ExBody2: Advanced Expressive WBC** | 2024 | 2412.13196 | ~112 | ExBody 升级版；更强泛化性和动态运动 |

---

## 八、技术路线六：CPG + RL 混合方法

**核心思想**：中央模式发生器（CPG）提供节律骨架，RL 学习残差/调制。

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **CPG-RL: Learning CPGs for Quadruped Locomotion** (Bellegarda et al., EPFL) | 2022 | 2211.00458 | ~100+ | RL 调制 CPG 振荡器幅频；A1 承重 115% 体重；IEEE RA-L |
| **SYNLOCO: Synthesizing CPG and RL** | 2023 | 2310.06606 | -- | CPG 节律 + RL 适应性集成；Go1 多地形/负载测试 |
| **AllGaits: Learning All Quadruped Gaits and Transitions** | 2024 | 2411.04787 | -- | CPG-DRL 实现全部 9 种动物步态 + 转换；基于 CoT 最优步态选择 |
| **DeepTransition: Viability-Driven Gait Transitions** (Shafiee et al.) | 2024 | 2306.07419 | -- | 可行性驱动步态转换（walk/trot/pronk）；Nature Communications |

---

## 九、技术路线七：MPC + RL 混合控制

**核心思想**：MPC 提供稳定性保障，RL 提升敏捷性；或用 RL 学习 MPC 代理模型。

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Data Efficient RL for Legged Robots** (Yang et al., Berkeley) | 2019 | 1907.03613 | ~200+ | 仅 4.5 分钟真实数据学 MPC 步行策略；CoRL 2019 |
| **Learning Agile Locomotion via RL-augmented MPC** | 2023 | 2310.09442 | -- | RL 增强 MPC；A1 达 8.5 rad/s 转速、3 m/s 速度；零样本迁移 Go1/AlienGo |
| **Real-Time Whole-Body Control with MPPI** | 2024 | 2409.10469 | -- | 首次在真实腿式机器人硬件上部署全身采样 MPC（MPPI） |
| **Diffusion-MPC: Flexible Locomotion with Diffusion MPC** | 2025 | 2510.04234 | -- | 扩散式 MPC；测试时奖励适应无需重训练 |
| **Legged MPC with Smooth Neural Surrogates** | 2025 | 2601.12169 | -- | 重尾似然的学习动力学代理；单冻结模型实现多步态和非平坦地形 |

---

## 十、技术路线八：层次化 RL 与多技能控制

**核心思想**：高层规划器选择技能/目标，低层控制器执行；专家网络集成。

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **MELA: Multi-Expert Learning of Adaptive Locomotion** | 2021 | -- | -- | 门控网络集成预训练专家；多技能（小跑/转向/跌倒恢复）在真实四足上演示；Science Robotics |
| **Walk These Ways** (Margolis & Agrawal, MIT) | 2022 | 2212.03238 | ~200 | 单策略编码步态族（频率/步幅/身高可调）；Go1 实时步态切换；CoRL 2022 |
| **HOVER: Versatile Neural WBC for Humanoid** (He et al., CMU/NVIDIA) | 2024 | 2410.21229 | ~113 | **多模式策略蒸馏**：统一导航/全身操控/桌面操作于一策略；ICRA 2025 |
| **HugWBC: Unified Humanoid WBC for Fine-Grained Locomotion** | 2025 | 2502.03206 | -- | 首个支持细粒度步态（行走/奔跑/跳跃/单跳）+ 可定制频率/步高/身体俯仰的统一控制器 |
| **LocoFormer: Generalist Locomotion via Long-Context Adaptation** (Liu et al., CMU) | 2025 | 2509.23745 | -- | 大规模 RL + 激进域随机化 + 长上下文 Transformer；零样本控制未见腿式/轮式机器人；跨片段适应涌现；CoRL 2025 Best Paper Finalist |
| **SkillBlender: Humanoid Loco-Manipulation via Skill Blending** | 2025 | 2506.09366 | -- | 动态混合预训练目标条件原语技能；CoRL Workshop 2024 |

---

## 十一、技术路线九：四足感知行走（Perceptive Locomotion）

**核心思想**：融合深度/RGB/高度图感知，应对未知复杂地形。

| 论文 | 年份 | 机构 | arXiv | 引用 | 核心贡献 |
|------|------|------|-------|------|---------|
| **Perceptive Locomotion in the Wild** (Miki et al., ETH) | 2022 | ETH | 2201.08117 | ~983 | **里程碑**：注意力融合本体感知 + 外部感知；ANYmal 全季节户外；DARPA SubT 获奖控制器；Science Robotics |
| **Learning Vision-Guided Quad Locomotion with Cross-Modal Transformers** | 2022 | -- | -- | ~100 | Transformer 做视觉-本体感知跨模态融合；ICLR 2022 |
| **DTC: Deep Tracking Control** (Hoeller et al., ETH) | 2024 | ETH | -- | ~80 | 深度跟踪控制：精确参考轨迹跟踪；Science Robotics |
| **Elevation Mapping for Locomotion using GPU** | 2022 | ETH | -- | ~70 | GPU 加速高度图实时构建；IROS 2022 |
| **DreamWaQ** (KAIST) | 2023 | KAIST | 2301.10602 | ~100 | 隐式地形想象：VAE 从本体感知推断地形嵌入；ICRA 2023 |
| **Learning Quadrupedal Locomotion on Deformable Terrain** | 2023 | KAIST | -- | -- | 可变形地形（沙/泥）上的四足运动；Science Robotics |
| **Robust RL-Based Locomotion for Resource-Constrained Quadrupeds** | 2025 | -- | 2505.12537 | -- | 小型四足的实时高度图感知运动控制 |

---

## 十二、技术路线十：敏捷运动与跑酷（Parkour / Agile）

**特点**：2023-2025 年爆发期；从四足跑酷到人形跑酷。

### 12.1 四足跑酷

| 论文 | 年份 | 机构 | arXiv | 引用 | 核心贡献 |
|------|------|------|-------|------|---------|
| **Robot Parkour Learning** (Zhuang et al., Stanford/CMU) | 2023 | Stanford | 2309.05665 | ~150 | 两阶段：specialist 技能 + 蒸馏统一策略；低成本四足跨越/攀爬/钻越 |
| **Extreme Parkour with Legged Robots** (Cheng et al., CMU) | 2023 | CMU | 2309.14341 | ~180 | 单一端到端策略；像素→电机；高跳/远跳/倒立；ICRA 2024 |
| **ANYmal Parkour** (Hoeller et al., ETH) | 2024 | ETH | 2306.14874 | ~120 | ANYmal D 全跑酷赛道；技能库 + 导航规划器；最高 2 m/s；Science Robotics |
| **PIE: Parkour with Implicit-Explicit Learning** | 2024 | -- | 2408.13740 | -- | 隐式-显式学习框架；IEEE RA-L |
| **SoloParkour: Constrained RL for Visual Parkour** | 2024 | ETH | 2409.13678 | -- | 约束 RL + 安全保障；Solo12 机器人 |

### 12.2 人形跑酷

| 论文 | 年份 | 机构 | arXiv | 引用 | 核心贡献 |
|------|------|------|-------|------|---------|
| **Humanoid Parkour Learning** (Zhuang et al., Tsinghua) | 2024 | Tsinghua | 2406.10759 | ~150 | **首个端到端人形跑酷**；无需运动参考；分形地形噪声课程；H1 跳台/越沟/钻越 |
| **Deep Whole-Body Parkour** | 2026 | -- | 2601.07701 | -- | G1 全身跑酷 + 深度感知 + ONNX 推理 |
| **Hiking in the Wild: Scalable Perceptive Parkour for Humanoids** | 2026 | -- | 2601.07718 | -- | 户外可扩展人形跑酷框架 |
| **Walk the PLANC: Physics-Guided RL for Constrained Footholds** | 2026 | -- | 2601.06286 | -- | 踏石/跳板/窄梁上的精确落脚点放置 |

---

## 十三、技术路线十一：双足/人形行走

### 13.1 Cassie 平台（Oregon State / UC Berkeley）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Learning Locomotion Skills for Cassie: Iterative Design** (Xie et al.) | 2019 | -- | ~200 | Cassie 首个 RL sim-to-real；无域随机化零样本迁移；CoRL 2019 |
| **Learning Memory-Based Control for Human-Scale Bipedal** (Siekmann et al.) | 2020 | 2006.02402 | ~150 | RNN 记忆策略；5K 跑完赛 |
| **Sim-to-Real of All Common Bipedal Gaits via Periodic Reward** (Siekmann et al.) | 2021 | 2011.01387 | ~150 | 周期性奖励组合；站立/行走/跳跃/奔跑/跳步全覆盖；RSS 2021 |
| **Blind Bipedal Stair Traversal via Sim-to-Real RL** (Siekmann et al.) | 2021 | 2105.08328 | ~100 | 首个人尺度双足盲行爬楼梯；纯地形随机化无需奖励修改；RSS 2021 |
| **RL for Robust Parameterized Bipedal Locomotion** (Li et al.) | 2021 | 2103.14295 | ~200 | 鲁棒参数化控制；马达故障/未知负载/摩擦变化均可应对；ICRA 2021 |
| **RL for Versatile, Dynamic, Robust Bipedal Control** (Li et al.) | 2024 | 2401.16889 | ~150 | Cassie 双历史架构；行走/奔跑/站立/推力恢复；IJRR |

### 13.2 全尺寸人形平台（Digit / H1 / G1）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **Real-World Humanoid Locomotion with RL** (Radosavovic et al., Berkeley) | 2024 | 2303.03381 | ~322 | **里程碑**：首个完全学习的人形行走（Digit）；因果 Transformer 上下文适应；广场/草坪/人行道零样本；Science Robotics |
| **Learning Humanoid Locomotion over Challenging Terrain** (Radosavovic et al.) | 2024 | 2410.03654 | ~60 | 盲行人形越野（4+ 英里远足 + 旧金山最陡街道） |
| **Agile Soccer Skills for a Bipedal Robot** (Haarnoja et al., DeepMind) | 2024 | 2304.13653 | ~200 | 小型人形 1v1 足球；20-DOF 全身 RL；视觉端到端；动态射门/起身/反应对抗；Science Robotics |
| **HugWBC: Unified Humanoid WBC** | 2025 | 2502.03206 | -- | 细粒度多步态 + 可定制参数的统一控制器 |
| **Gait-Conditioned RL with Multi-Phase Curriculum** | 2025 | 2505.20619 | -- | 循环策略统一站立/行走/奔跑；G1 无动捕 |
| **Natural Humanoid Locomotion with Generative Motion Prior** | 2025 | 2503.09015 | -- | 生成式运动先验产生自然人形运动 |

---

## 十四、技术路线十二：全身控制与 Loco-Manipulation

### 14.1 全身遥操作（Teleoperation-based WBC）

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **H2O: Learning Human-to-Humanoid Real-Time WBC** | 2024 | -- | ~209 | 首个人形→人形实时全身控制；人类运动重定向 |
| **OmniH2O: Universal Dexterous Humanoid WBC** | 2024 | -- | ~240 | 通用灵巧人形全身控制；多种遥操作模式 |
| **Open-TeleVision: Teleoperation with Immersive Visual Feedback** | 2024 | 2407.01512 | ~241 | 沉浸式主动视觉反馈遥操作；CoRL 2024 |
| **HOMIE: Humanoid Loco-Manipulation with Exoskeleton** | 2025 | 2502.13013 | ~104 | 外骨骼驾驶舱遥操作人形全身 |

### 14.2 力控与负载适应

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **FALCON: Force-Adaptive Humanoid Loco-Manipulation** (Zhang et al., CMU) | 2025 | 2505.06776 | -- | 双智能体力适应框架；搬运(0-20N)/推车(0-100N)/开门(0-40N)；L4DC 2026 |
| **SoFTA: Learning Gentle Humanoid Locomotion + EE Stabilization** (Li et al., CMU) | 2025 | 2505.24198 | -- | 末端执行器加速度降低 2-5x；满杯行走/行走拍视频；RSS 2025 |
| **WoCoCo: Humanoid WBC with Sequential Contacts** (Zhang et al., CMU/ETH) | 2024 | 2406.06005 | ~94 | 端到端序贯接触 RL；跑酷/箱子搬运/舞蹈/崖壁攀爬；CoRL 2024 |

### 14.3 视觉驱动 Loco-Manipulation

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **VisualMimic: Visual Humanoid Loco-Manipulation** (Yin et al., Stanford) | 2025 | 2509.20322 | -- | 零样本视觉运动策略；箱子抬举/推动/足球运球 |
| **VIRAL: Visual Sim-to-Real for Humanoid Loco-Manipulation** | 2025 | 2511.15200 | -- | G1 RGB 策略；连续全身操作 54 个循环 |
| **WholeBodyVLA: Unified Latent VLA for WBC** | 2025 | 2512.11047 | -- | VLA 统一全身运动操控；语言/视觉/动作联合；ICLR 2026 |

---

## 十五、技术路线十三：轮腿混合（Wheeled-Legged）

| 论文 | 年份 | 机构 | arXiv | 引用 | 核心贡献 |
|------|------|------|-------|------|---------|
| **Rolling in the Deep: Hybrid Locomotion** (Bjelonic et al., ETH) | 2020 | ETH | -- | ~100 | 在线轨迹优化；ANYmal-W 旋转/跳跃/单轮站立 |
| **Robust Navigation for Wheeled-Legged Robots** (Lee et al., ETH) | 2024 | ETH | 2405.01792 | ~143 | **里程碑**：端到端 RL 步行↔驾驶无缝切换；苏黎世/塞维利亚 10km 自主导航；速度 3x / CoT -53%；Science Robotics |
| **RL for Blind Stair Climbing: Legged and Wheeled-Legged** (Chamorro et al.) | 2024 | -- | 2402.06143 | -- | 特权地形信息 + 非对称 AC；Ascento 15cm 台阶爬行；同时适用 Go1/Cassie/ANYmal |
| **ATRos: Energy-Efficient Agile Wheeled-Legged** | 2025 | -- | 2510.09980 | -- | RL 无预定步态的混合行走-驾驶；能效感知奖励 |
| **Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds** | 2026 | -- | 2601.10723 | -- | 预测功率建模 + 残差 RL；轮式四足降低 35% 能耗 |

**产品化代表**：Swiss-Mile（ETH RSL spinoff）——轮腿配送机器人，已在苏黎世测试。Ascento（ETH）——轮式双足，擅长室内外混合环境。

---

## 十六、技术路线十四：语言/基础模型驱动运动

### 16.1 语言条件化运动

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **LangWBC: Language-directed Humanoid WBC** | 2025 | 2504.21738 | -- | 端到端语言→动作；RL teacher + CVAE student；G1 零样本部署 |
| **SENTINEL: End-to-End Language-Action Model for Humanoid** | 2025 | 2511.19236 | -- | 首个完全端到端语言→动作模型（无中间运动表示）；Flow Matching + 残差 RL；G1 99.45% 稳定执行 |
| **FRoM-W1: General Humanoid Control with Language** | 2026 | 2601.12799 | -- | 通用人形控制基础模型 |
| **Long-Horizon Locomotion+Manipulation via LLMs** | 2024 | 2404.05291 | -- | 多 LLM 智能体（规划/计算/代码/重规划）四足长程任务 |
| **LocoVLM: VLM-Grounded Versatile Legged Locomotion** | 2026 | 2602.10399 | -- | LLM teacher + VLM student；指令接地技能数据库；87% 指令准确率 |

### 16.2 音频/多模态驱动

| 论文 | 年份 | arXiv | 核心贡献 |
|------|------|-------|---------|
| **Do You Have Freestyle? Expressive Humanoid via Audio Control** | 2025 | 2512.23650 | 首个音频驱动人形运动——音乐控制表达性行走和舞蹈 |

### 16.3 人形基础模型

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **GR00T N1: Open Foundation Model for Humanoid** (NVIDIA) | 2025 | 2503.14734 | -- | NVIDIA 开源人形基础模型；运动+操作统一 |
| **SONIC** (Luo et al., NVIDIA) | 2025 | 2511.07820 | -- | 42M 参数大规模运动跟踪；验证 Scaling Law 在人形控制中成立 |
| **Psi-0: Universal Humanoid Loco-Manipulation Foundation Model** | 2026 | 2603.12263 | -- | 通用全身操控基础模型 |
| **BFM-Zero: Promptable Behavioral Foundation Model** | 2025 | 2511.04131 | -- | 可 Prompt 的行为基础模型 |

---

## 十七、技术路线补充：扩散策略 for Locomotion

| 论文 | 年份 | arXiv | 引用 | 核心贡献 |
|------|------|-------|------|---------|
| **DiffuseLoco: Real-Time Legged Locomotion from Offline Datasets** (Huang et al.) | 2024 | 2404.19264 | ~50 | 多技能扩散策略；离线数据集训练；边缘端实时推理；零样本 sim-to-real；CoRL 2024 |
| **BiRoDiff: Diffusion Policies for Bipedal Locomotion** | 2024 | 2407.05424 | -- | 轻量级扩散步行控制器；捕获多模态步态；泛化到未见坡度 |
| **Offline Adaptation of Quad Locomotion via Diffusion** (O'Mahoney et al.) | 2024 | 2411.08832 | -- | 无分类器引导扩散；ANYmal 离线行为适应；ICRA 2025 |
| **Diffusion-based Learning of Contact Plans for Agile Locomotion** | 2024 | 2403.03639 | -- | 扩散学习多模态接触计划；结合 MCTS + NMPC；Humanoids 2024 |
| **Diffusion-MPC** | 2025 | 2510.04234 | -- | 扩散式 MPC；测试时奖励适应 |

---

## 十八、代表性机器人平台与对应关键论文

| 平台 | 类型 | 研究机构 | 关键论文（引用数） |
|------|------|---------|-----------------|
| **ANYmal** | 四足 | ETH RSL | Hwangbo 2019(~1651), Lee 2020(~1545), Miki 2022(~983), Rudin 2021(~887), Hoeller 2024(~120) |
| **MIT Mini Cheetah** | 四足 | MIT | Margolis 2022(~250), Walk These Ways 2022(~200) |
| **Unitree A1/Go1** | 四足 | Berkeley/MIT | RMA 2021(~800), Extreme Parkour 2023(~180) |
| **Spot** | 四足 | BD + RAI | BD Blog 2024, RAI 2025(2504.17857) |
| **Cassie** | 双足 | Oregon State / Berkeley | Xie 2019(~200), Siekmann 2021(~150), Li 2024(~150) |
| **Digit** | 人形 | UC Berkeley | Radosavovic 2024(~322) |
| **Unitree H1/G1** | 人形 | CMU/UCSD/Tsinghua | ExBody 2024(~213), HOVER 2024(~113), Humanoid Parkour 2024(~150) |
| **OP-3** | 人形 | DeepMind | Haarnoja 2024 Soccer(~200) |
| **ANYmal-W / Swiss-Mile** | 轮腿 | ETH | Lee 2024(~143) |
| **Ascento** | 轮式双足 | ETH | Klemm 2019(~100), Chamorro 2024 |

---

## 十九、引用数 Top 15（领域"名人堂"）

| 排名 | 论文 | 年份 | 引用 | 一句话总结 |
|------|------|------|------|-----------|
| 1 | Hwangbo et al. — Agile Motor Skills (ETH) | 2019 | ~1651 | actuator network + ANYmal sim-to-real 里程碑 |
| 2 | Lee et al. — Challenging Terrain (ETH) | 2020 | ~1545 | teacher-student 盲行范式开创者 |
| 3 | DeepMimic (Peng/UBC) | 2018 | ~1500+ | 运动模仿开山之作 |
| 4 | Miki et al. — Perceptive Wild (ETH) | 2022 | ~983 | 多模态感知户外部署，DARPA SubT |
| 5 | Tan et al. — Sim-to-Real (Google) | 2018 | ~935 | 最早 RL sim-to-real 成功 |
| 6 | Rudin et al. — Walk in Minutes (ETH) | 2021 | ~887 | IsaacGym 并行训练范式 |
| 7 | Imitating Animals (Peng/Google) | 2020 | ~800+ | 动物动捕→机器人运动迁移 |
| 8 | RMA (Kumar/Berkeley) | 2021 | ~800 | 在线适应框架，被广泛复用 |
| 9 | AMP (Peng/UBC) | 2021 | ~600+ | 对抗式运动先验，替代手工奖励 |
| 10 | ASE (Peng) | 2022 | ~300+ | 大规模可复用技能嵌入 |
| 11 | Radosavovic et al. — Humanoid Loco (Berkeley) | 2024 | ~322 | 首个完全学习的人形行走 |
| 12 | OmniH2O — Dexterous Humanoid WBC | 2024 | ~240 | 通用灵巧人形全身控制 |
| 13 | ExBody — Expressive WBC (UCSD) | 2024 | ~213 | 表达性全身控制先驱 |
| 14 | Haarnoja et al. — Soccer (DeepMind) | 2024 | ~200 | 双足足球端到端 |
| 15 | Lee et al. — Wheeled-Legged (ETH) | 2024 | ~143 | 轮腿混合 10km 自主导航 |

---

## 二十、推荐阅读路径

### 入门路线（按顺序读）
1. **Tan et al. 2018** (1804.10332) — sim-to-real 基本问题
2. **Lee et al. 2020** (2010.11251) — teacher-student 范式
3. **Rudin et al. 2021** (2109.11978) — 现代训练基础设施
4. **RMA 2021** (2107.04034) — 在线适应机制
5. **Miki et al. 2022** (2201.08117) — 感知行走标杆

### 运动模仿专线
6. **DeepMimic 2018** (1804.02717) → **AMP 2021** (2104.02180) → **ASE 2022** → **SONIC 2025** (2511.07820)

### 敏捷运动专线
7. **Extreme Parkour 2023** (2309.14341) → **ANYmal Parkour 2024** (2306.14874) → **Humanoid Parkour 2024** (2406.10759)

### 人形行走专线
8. **Siekmann 2021** (2011.01387) → **Radosavovic 2024** (2303.03381) → **HOVER 2024** (2410.21229) → **HugWBC 2025** (2502.03206)

### 前沿方向
9. **Eureka 2024** (2310.12931) — 自动化奖励
10. **DiffuseLoco 2024** (2404.19264) — 扩散策略
11. **LocoFormer 2025** (2509.23745) — 跨形态泛化
12. **SENTINEL 2025** (2511.19236) — 语言端到端控制

### 综述精读
- **Ha et al. 2024** (2406.01152) — 最全面综述，IJRR

---

## 二十一、开放问题与趋势（2025-2026）

1. **Scaling Law 成立**：SONIC 证明更大模型 + 更多数据 → 运动跟踪质量单调提升
2. **基础模型收敛**：GR00T N1, Psi-0, BFM-Zero 等朝通用人形控制基础模型演进
3. **语言/音频控制**：SENTINEL 实现完全端到端语言→动作；音频驱动舞蹈运动
4. **力控 Loco-Manipulation**：FALCON/SoFTA 等关注行走时的力反馈与载荷适应
5. **跨形态泛化**：LocoFormer 单一策略控制未见四足/轮腿机器人，Zero-shot
6. **扩散策略**：DiffuseLoco 引入多模态动作分布，离线数据驱动
7. **能效优化**：PACE 等关注实际部署中的能耗问题
8. **与操作融合**：WoCoCo, WholeBodyVLA 等推动运动与操作的统一框架

---

## 二十二、相关资源

### 核心综述论文
| 标题 | arXiv | 侧重 |
|------|-------|------|
| Learning-based Legged Locomotion: SotA and Future Perspectives (Ha et al.) | 2406.01152 | **最全面**，四足+双足，IJRR |
| Deep RL for Robotics: Survey of Real-World Successes (Tang et al.) | 2408.03539 | 更广泛 DRL for Robotics 视角 |
| Deep RL for Bipedal Locomotion: A Brief Survey (Bao et al.) | 2404.17070 | 聚焦双足，AI Review |
| Humanoid Locomotion and Manipulation (Gu et al.) | 2501.02116 | 人形全身控制，17 位作者 |
| Imitation Learning for Legged Robot Locomotion (Mirza & Singh) | -- | 模仿学习视角，Frontiers |

### GitHub Awesome Lists
| 仓库 | 侧重 |
|------|------|
| [awesome-legged-locomotion-learning](https://github.com/gaiyi7788/awesome-legged-locomotion-learning) | 最全，78+ 篇，含代码链接 |
| [awesome-rl-for-legged-locomotion](https://github.com/apexrl/awesome-rl-for-legged-locomotion) | ETH/KAIST 核心，按机构分组 |
| [Awesome_Quadrupedal_Robots](https://github.com/curieuxjy/Awesome_Quadrupedal_Robots) | 四足专项 |
| [awesome-humanoid-robot-learning](https://github.com/YanjieZe/awesome-humanoid-robot-learning) | 人形机器人学习 |
| [awesome-wheeled-legged](https://github.com/XinLang2019/awesome-wheeled-legged) | 轮腿混合 |
| [awesome-loco-manipulation](https://github.com/aCodeDog/awesome-loco-manipulation) | 运动+操作 |
| [bipedal-robot-learning-collection](https://github.com/zita-ch/bipedal-robot-learning-collection) | 双足专项 |

---

*本报告基于多源调研汇总，引用数为近似值（截至 2026-04）。后续可逐篇精读并创建论文卡片。*
