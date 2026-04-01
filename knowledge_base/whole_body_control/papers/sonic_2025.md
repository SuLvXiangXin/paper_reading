# SONIC: Supersizing Motion Tracking for Natural Humanoid Whole-Body Control

- **arXiv**: 2511.07820
- **年份**: 2025（v2: 2025-12-04）
- **机构**: NVIDIA
- **作者**: Zhengyi Luo†, Ye Yuan†, Tingwu Wang†, Chenran Li†, Sirui Chen*, Fernando Castañeda*, Zi-Ang Cao*, Jiefeng Li*, David Minor*, Qingwei Ben*, Xingye Da*, Runyu Ding, Cyrus Hogg, Lina Song, Edy Lim, Eugene Jeong, Tairan He, Haoru Xue, Wenli Xiao, Zi Wang, Simon Yuen, Jan Kautz, Yan Chang, Umar Iqbal, Linxi "Jim" Fan‡, Yuke Zhu‡（†共同一作，‡项目负责人）
- **引用数**: 33（截至 2026-03）
- **方法线归属**: **Foundation Model WBC / Motion Imitation + Scaling**
- **项目主页**: https://nvlabs.github.io/SONIC/

## 一句话总结

三轴 Scaling 运动跟踪，得到统一人形全身控制基础模型。

## 解决的问题

当前人形机器人控制领域存在明显的「Scaling 鸿沟」：大语言模型、视频生成模型已展示出随规模显著涌现的能力，但人形控制策略仍停留在小型 MLP（几百万参数）、单 GPU 训练数天、单任务的阶段。根本原因在于任务选择：运动目标（如行走、起身、遥操作）各不相同，需要为每项任务手动设计奖励函数，导致无法统一扩展。即使找到可扩展的目标，现实场景还要求一个控制器同时支持遥操作、导航、视觉语言命令等多种接口，构建兼具扩展性与灵活性的系统极具挑战。SONIC 提出以运动跟踪（Motion Tracking）作为统一的可扩展基础任务，借助动作捕捉数据的密集监督信号绕开奖励工程问题，并通过统一 Token 空间实现多种接口的单策略控制。

## 核心方法

### 整体架构

SONIC 由三大组件构成：（1）基于 PPO 训练的**通用控制策略**（Universal Control Policy），包含多编码器→量化器→双解码器的 encoder-decoder 架构；（2）**运动规划器**（Generative Kinematic Motion Planner），将用户意图（速度、风格、技能目标）转化为短时运动参考帧；（3）**GENMO 多模态运动生成模型**，从视频/文本/音乐生成人体运动。三者协作，通过统一 Token 空间对接不同输入接口，最终在 Unitree G1 人形机器人上实现 50 Hz 实时部署。整体设计的核心思想是将「运动跟踪」从演示特定的模仿推广到通用人形控制的基础能力。

### Scaling 三个维度

**数据规模**（最显著收益）：对比 LaFAN（0.4M 帧）→ 内部子集（7.4M 帧）→ 完整数据集（100M 帧），成功率和 MPJPE 均随数据量单调提升，100M 帧配置效益最大。训练数据来自 170 名受试者（含男女，身高 145–199 cm）的自建高质量动捕库，涵盖运动、日常活动、格斗等数千种行为，总计 700 小时、100M+ 帧（50 Hz）。**网络规模**：从 1.2M 参数→ 16M→ 42M 参数，成功率和跟踪精度均稳步提升；42M 参数为最终配置，编码器/解码器均为多层 MLP（见表 1 详细参数）。**算力规模**：8 GPU→ 32 GPU→ 128 GPU 训练至收敛，更多并行 GPU 带来更好的渐近性能，而非仅加快训练速度；最终完整训练消耗 32,000 GPU 小时（128 GPU × 3 天），摘要中提及的 9,000 GPU 小时为缩放实验中的算力轴坐标点。三轴缩放均单调改善性能，其中数据规模效果最显著。

### 统一 Token 空间（Universal Token Space）

通用控制策略采用三个专用编码器分别处理不同输入：**机器人运动编码器** ℰᵣ（编码 Fᵣ 帧机器人关节位置/速度）、**人体运动编码器** ℰₕ（编码 Fₕ 帧 SMPL 3D 关节位置）、**混合编码器** ℰₘ（编码当前帧上体关键点 + Fₘ 帧下体机器人运动）。三个编码器均为 MLP（hidden=[2048,1024,512,512]），将异构输入映射到同一隐层空间，再经 FSQ（Finite Scalar Quantization）量化为统一 Token z。z 通过动作解码器（hidden=[4096,4096,2048,2048,1024,1024,512,512]）生成关节目标，同时通过运动解码器辅助重建机器人运动（提供隐式跨体素 retargeting 监督）。训练损失包含 PPO 损失、重建损失、Token 对齐损失和 Cycle 损失，强制不同模态的 Token 空间对齐。多帧输入（Fᵣ=Fₕ=Fₘ=10帧，帧间隔 Δt=0.1s）赋予策略前瞻能力，提升鲁棒性。

### 运动规划器（Kinematic Planner）

通用运动规划器是一个自回归运动补间（Motion In-betweening）生成模型，与跟踪策略在相同大规模数据集上训练。输入为历史机器人状态（关节位置、根节点位置）作为上下文关键帧，以及来自用户指令（速度、方向、风格）或技能目标（蹲、爬、拳击）生成的目标关键帧；输出为 0.8–2.4s 的运动片段。规划在隐空间进行（下采样率 4），采用掩码 Token 预测策略（Masked Token Prediction）迭代细化生成，神经骨干网络为 Transformer 或 Conv1D。规划器在笔记本 CPU/GPU 上推理仅需 <5ms，Jetson Orin 上 12ms，每 100ms 或用户指令更新时触发重规划，确保高响应性。通过调节骨盆高度（0.3–0.8m）平滑控制，支持 0–6.0m/s 全速域导航及 0–360° 任意方向控制。规划器与跟踪策略解耦设计，使得新任务（导航风格、拳击、蹲爬）无需重训练基础策略，具备极强的扩展灵活性。

### 训练数据

内部动捕库由 170 名受试者采集，男女均衡，身高正态分布（均值 174.3cm，std 10.9cm），涵盖日常活动、运动、格斗等数千种行为，同一动作由多受试者多次完成，提供丰富的个体内/个体间变化。单段时长 1–180 秒，共计 700 小时、100M+ 帧（50 Hz）。人体运动到机器人的 retargeting 基于 GMR（Araujo et al., 2025）和 PyRoki（Kim et al., 2025）改进而来。测试集来自 AMASS 数据集的随机子集（9 小时，1,602 条轨迹），SONIC 未在 AMASS 上训练，凸显了强泛化能力。

## Scaling 实验结果

对比实验在 MuJoCo 模拟器中统一评估（支持所有基线实现），主要指标：成功率（Succ）、MPJPE（mm，越低越好）、速度距离 Eᵥₑₗ、加速度距离 Eₐcc。**与基线对比**（图2d-g）：SONIC vs. Any2Track / BeyondMimic / GMT：成功率 99.6% vs. 58.3%/84.2%/94.3%；MPJPE 42.7mm vs. 202.3/65.0/57.4；速度距离 4.1 vs. 14.9/12.7/9.1；加速度距离 1.2 vs. 6.1/4.9/2.5，全面大幅领先。**三轴缩放消融**：数据量（图2a）：0.4M→7.4M→100M 帧，成功率从约 93.5% 升至约 98.5%，MPJPE 从约 49 降至约 37；网络规模（图2b）：1.2M→16M→42M 参数，成功率与 MPJPE 持续改善；算力（图2c）：0.5K→2K→9K GPU 小时，同样单调提升，且大规模并行训练的渐近性能优于小规模训练。**真实世界评估**：50 条多样化运动轨迹（舞蹈、跳跃、运动操控）在 Unitree G1 上零样本部署，成功率 100%，sim-to-real 性能匹配，MPJPE 约 40.9mm。

## 下游任务支持

**VR 全身遥操作**：穿戴 PICO 头显、两个脚踝追踪器和手持控制器，实时流式传输全身 SMPL 姿态，经人体运动编码器 ℰₕ 进入通用 Token，实现低延迟、稳定、拟人化控制（图5下）。**VR 3 点遥操作**（数据采集）：仅需 PICO 头显和控制器（无脚踝追踪器），输出头部+双腕 SE(3) 姿态、手指关节角、腰高、移动模式和导航指令；下体运动由运动规划器生成混合指令，经混合编码器 ℰₘ 控制。300 条 apple→plate 抓取演示平均延迟 121.9ms，右腕位置误差均值 6cm，方向误差均值 0.145 rad。**VLA 接入（GR00T N1.5）**：用 300 条遥操作演示微调 GR00T N1.5，VLA 输出相同 3 点遥操作格式的指令（头/腕位姿+腰高+导航），通过运动规划器和混合编码器驱动 SONIC 执行，在 apple→plate 移动操控任务上达 95% 成功率（20 次试验），验证了与基础模型的兼容性。**视频/文本/音乐多模态控制**：GENMO 模型（Li et al., ICCV 2025）从单目摄像头视频（≥60fps 实时估计）、自然语言文本或音乐节奏生成人体运动，传入 SONIC 的人体运动编码器 ℰₕ 执行；支持模态间无缝切换，无需重新初始化。**交互式游戏手柄控制**：运动规划器直接接收手柄速度/风格/技能指令，生成多样运动参考，拳击、蹲爬等均无需额外专用模型。

## 实现细节

**网络结构**：三个编码器均为 MLP hidden=[2048,1024,512,512]，动作解码器 hidden=[4096,4096,2048,2048,1024,1024,512,512]，动作维度 29（对角高斯），Critic 同动作解码器结构。量化器为 FSQ（Mentzer et al., 2023）。运动规划器骨干为 Transformer 或 Conv1D，在隐空间（下采样率 4）做掩码 Token 预测。**训练**：PPO + 重建损失 + Token 对齐损失 + Cycle 损失联合优化；6D 旋转表示（Zhou et al., 2019）；系统域随机化（摩擦、弹性、关节默认值、质心偏移、随机扰动）。**仿真环境**：Isaac Lab（GPU 加速，用于缩放实验），MuJoCo（对比基线）。**GPU 与时间**：最终完整训练 128 GPU × 3 天 = 32,000 GPU 小时；缩放消融最大点 9,000 GPU 小时（约 128 GPU × 3 天的某时间点）。**部署**：Unitree G1（29 自由度），板载 Jetson Orin GPU，TensorRT + CUDA Graph 加速；策略推理 1–2ms，运动规划器 12ms；策略环路 50Hz，运动规划器 10Hz，低级 PD 控制器 500Hz，用户输入采集 100Hz；"最新数据优先"策略减少 jitter。

## 与相关工作的关系

**vs. HOVER（He et al., ICRA 2025, 2410.21229）**：HOVER 构建了多模式控制框架的原型，SONIC 在其基础上大幅扩展数据规模和算力（从单 GPU 几天到 128 GPU 几天），并增加了统一 Token 空间和运动规划器；SONIC 本质上将 HOVER 的框架推向了基础模型规模。**vs. PHC（Luo et al., ICCV 2023）**：PHC（Perpetual Humanoid Control）是 SONIC 第一作者 Zhengyi Luo 的前作，提出了物理人形实时运动跟踪的基础框架，SONIC 在此基础上做了大规模扩展。**vs. BeyondMimic / GMT / Any2Track**：这三篇 2025 年运动跟踪工作均局限于较小训练集（LaFAN 或 AMASS 量级），成功率和精度被 SONIC 大幅超越；SONIC 的测试集（9 小时、1602 轨迹）量级即相当于部分工作的训练集，体现规模优势。**vs. GR00T N1/N1.5**：SONIC 与 GR00T N1.5 形成了互补关系——SONIC 作为低层 System 1 控制器（快速反应式全身运动），GR00T N1.5 作为高层 System 2 规划器（慢速推理），两者通过统一 Token 接口连接，共同构成完整的人形机器人 pipeline。**WBC Scaling 的独特贡献**：SONIC 是首个系统展示 WBC 三轴（数据/模型/算力）scaling law 的工作，将人形控制的规模提升到 100M 帧数据、42M 参数、32,000 GPU 小时，同时保持 zero-shot 泛化和 sim-to-real 鲁棒性。

## 局限性与未来工作

当前版本尚未正式处理安全性、顺从性和长期部署的能效问题；输入噪声（如视频遮挡、VR 追踪漂移）对策略的影响尚待量化。VLA 集成实验仅在 apple-to-plate 单任务上验证（300 条演示），向更丰富任务分布的扩展是未来核心方向。作者计划研究跨更多样化数据集的 Scaling Laws，使能 VLA 指导的全身移动操控，并探索规划器、Tokenizer 和策略的联合训练以消除模态 gap。此外，GENMO 与 SONIC 目前串联（先生成人体运动再跟踪），联合端到端训练有望进一步提升多模态控制精度。

## 关键引用

| 论文 | 贡献 |
|------|------|
| HOVER (He et al., ICRA 2025, arXiv 2410.21229) | 多模式 WBC 框架原型，SONIC 直接扩展自此 |
| PHC (Luo et al., ICCV 2023) | 物理人形运动跟踪基础框架，Zhengyi Luo 前作 |
| BeyondMimic (Liao et al., 2025, arXiv 2508.08241) | 引导扩散运动跟踪，SONIC 主要对比基线 |
| GMT (Chen et al., 2025, arXiv 2506.14770) | 通用运动跟踪，对比基线 |
| Any2Track (Zhang et al., 2025, arXiv 2509.13833) | 运动跟踪基线 |
| GR00T N1.5 (Bjorck et al., 2025) | 下游 VLA 接入对象，实验验证 System 1+2 |
| GENMO (Li et al., ICCV 2025) | 多模态人体运动生成，SONIC 多模态控制的上游 |
| AMASS (Mahmood et al., ICCV 2019) | 标准评测动捕数据集（SONIC 仅用于测试）|
| FSQ (Mentzer et al., 2023, arXiv 2309.15505) | 有限标量量化，SONIC Token 空间量化器 |
| TWIST (Ze et al., 2025, arXiv 2505.02833) | 遥操作全身模仿系统，评测集来源一致 |
| DeepMimic (Peng et al., SIGGRAPH 2018) | 运动模仿 RL 奠基工作 |
| OmniH2O (He et al., 2024, arXiv 2406.08858) | 人→人形全身遥操作前作 |
