# VLA 领域知识图谱

## 方法分类
- **Diffusion Policy (BC + Diffusion 奠基)**: 将 DDPM 引入机器人策略学习的奠基工作，条件去噪扩散 + action sequence + receding horizon，是后续所有 diffusion/flow 方法线的技术源头（Diffusion Policy）
- **Transformer + Diffusion Head (Cross-embodiment GRP)**: 无VLM预训练，ViT transformer + diffusion head 从跨具身数据训练通用策略（Octo, RDT）→ **RDT2 升级为 VLM + Flow Head**（+Qwen2.5-VL-7B, +10K小时UMI数据, 三阶段渐进训练）
- **VLM + Action Token**: 大视觉语言模型直接输出离散化动作 token（RT-2, OpenVLA）
- **VLM + Diffusion/Flow Head**: VLM 提特征，扩散/flow 模型生成连续动作（π₀, π₀.5, Being-H0.5）
- **层次化 VLA (Hierarchical VLA)**: 统一模型同时做高层语义推理+低层动作生成（π₀.5, Hi Robot, **MEM**）
- **VLM-as-Controller 系统框架 (Agentic Robotics)**: 现成VLM做高层元控制器，调度低层VLA策略；分离式层次化编排（SayCan, Inner Monologue, **RoboClaw**）
- **世界模型 + VLA**: 预测未来状态再规划动作，三大流派：隐式(FLARE)、联合去噪(**Cosmos Policy**, **DreamZero**, UWM)、视频→IDM(UniPi, Seer)
- **交互式数据收集 (Interactive Data Collection)** 🆕: deploy-then-collect 范式，DAgger-inspired，人类仅在策略失败时介入修正；与模型设计正交，专注于数据收集效率（**RoboCopilot**, **GCENT/Genie Centurion**, **RaC**——显式recovery+correction配对+两条规则，10x数据效率+test-time scaling）
- **VLA RL 后训练 (RL Post-training)** 🆕: 通过 RL 或 rejection sampling 对预训练 VLA 进行在线微调，解决 compounding error 和探索问题；价值函数路线（HIL-SERL, Q-Chunking, PA-RL）vs rejection sampling 路线（**Hi-ORS**）vs 离线 ACP 路线（**Evo-RL**）vs RL Token 路线（**RLT**——冻结 VLA 暴露紧凑表征 + 轻量 actor-critic + chunk-level RL，数小时真机超人类速度）
- **轻量化 VLA (Lightweight VLA)** 🆕: 在保持性能的同时大幅减少参数量和计算开销，面向消费级 GPU 实时部署；代表: TinyVLA, SmolVLA, **Evo-1**（0.77B，无机器人预训练 Meta-World SOTA）
- **VLA 3D 空间感知增强** 🆕: 在纯 RGB 输入下为 VLA 注入 3D 几何先验；显式方案（SpatialVLA, PointVLA，需 RGB-D）vs 隐式方案（**Evo-0**，VGGT + Cross-Attention，仅 RGB）
- **冻结VLM + 分类式动作解码（Tripartite）** 🆕: 完全冻结大VLM作语义先验，分离出可训练Pons编译器 + 高频分类动作解码器（ParaCAT），两阶段特征缓存训练提速40%（**SaiVLA-0**，LIBERO 99.0% SOTA）
- **奖励学习**: 从人类反馈或视频中学习奖励函数

→ 详见 [methods/index.md](methods/index.md)

## 任务类型
- **桌面操作 (Manipulation)**: 抓取、推移、组装
- **灵巧手 (Dexterous)**: 多指操作
- **导航 (Navigation)**: 移动到目标位置
- **长时序任务**: 需要多步规划
- **长时记忆任务** 🆕: 需要保持跨分钟级记忆（MEM 评测：菜谱准备、厨房清洁、三明治制作，跨度 15 分钟）
- **移动操作 (Mobile Manipulation)**: 移动底盘+机械臂协同完成家庭任务（π₀.5的核心评测场景）
- **跨具身泛化 (Cross-Embodiment)**: 单一模型/检查点控制多种形态的机器人（Being-H0.5 的核心场景）
- **双臂操作 (Bimanual Manipulation)**: 需要双臂协调的高难度操作（Cosmos Policy 的 ALOHA、DreamZero 的 AgiBot G1 评测场景）
- **部分可观测任务** 🆕: 物体被遮挡/自遮挡、需要记住物体位置等（MEM 的 Find Object、Unpack Groceries 等）

→ 详见 [tasks/index.md](tasks/index.md)

## 技术组件
- **动作表示**: 离散 token / 连续向量 / action chunk / FAST tokenizer / 混合方案 / 混合连续flow+离散masked prediction（Being-H0.5）/ **latent frame injection**（Cosmos Policy：动作编码为 latent frame 插入视频 diffusion 序列）
- **动作解码**: Diffusion (DDPM) / Flow Matching / MSE / Discrete Cross-entropy / **Latent Video Diffusion**（Cosmos Policy：动作直接在视频 diffusion 过程中去噪生成）/ **联合 flow matching velocity prediction**（DreamZero：视频+动作共享速度场预测）
- **动作空间**: position control vs velocity control（Diffusion Policy）/ 零填充对齐（π₀）/ **统一物理语义槽位**（Being-H0.5，将人手MANO+30种机器人映射到共享空间）/ **relative joint positions**（DreamZero 默认）
- **视觉编码器**: SigLIP, DINOv2, ViT, ViT-22B (PaLI-X), ViT-4B (PaLM-E), 浅层CNN patch encoder; SigLIP+DINOv2 融合（OpenVLA/Prismatic 验证有效）; **Wan2.1 Spatiotemporal VAE**（DreamZero + Cosmos Policy）; **视频编码器**（MEM：空间-时间分离注意力 ViT，16帧<300ms，不引入新参数）🆕
- **语言编码器**: T5, Gemma, Gemma3-4B（MEM）🆕, Llama 2, UL2, PaLM, InternVL-3.5（Being-H0.5）, 冻结 vs 微调; **T5-XXL cross-attention**（Cosmos Policy，继承自 Cosmos-Predict2）; **Wan2.1 text encoder (冻结)**（DreamZero）; **InternVL 2.5-2B MLP 二值分类头**（GCENT Task Sentinel，步骤成功检测）🆕; **Qwen2.5-0.5B**（Evo-1，0.5B 高效语义理解）🆕
- **注意力设计**: Block-wise causal mask, Readout token, MoT共享注意力+独立FFN, **chunk-wise autoregressive attention mask + teacher forcing**（DreamZero：当前chunk attend前序clean chunks）, **空间-时间分离注意力**（MEM：ViT每4层交替空间双向+时间因果注意力）🆕
- **记忆机制** 🆕: 密集帧历史(Octo)、池化记忆(ContextVLA)、本体感知记忆(TA-VLA)、关键帧(BPP/MeMeR)、点轨迹(TraceVLA)、潜在记忆(Sam2Act)、语言记忆(OneTwoVLA)、**多尺度混合模态记忆**（MEM：短时视频+长时语言，15分钟）
- **架构创新**: Mixture-of-Flow（MoF，Being-H0.5：共享基础层+路由特化专家）、流形保持门控（MPG）、通用异步分块（UAC）、**Latent Frame Injection + Conditioning Mask**（Cosmos Policy：无架构修改的多模态适配）、**闭环 KV Cache 替换**（DreamZero：用真实观测替换预测帧消除累积误差，WAM 独有优势）
- **数据策略**: cross-embodiment, co-training/co-fine-tuning (RT-2首创), verbal instruction, augmentation, **人类中心学习**（Being-H0/H0.5: 人手运动作为物理母语）, **EAP自重置数据收集**（RoboClaw: 正-逆动作对实现自主数据循环采集）, **Rollout Experience Learning**（Cosmos Policy：从策略 rollout 数据微调世界模型和价值函数）, **多样性优先非重复数据 + 任务淘汰机制**（DreamZero：颠覆传统重复示教范式）, **人类干预修正数据**（MEM：失败→修正数据训练上下文适应）🆕, **倒带精修（Rewind-and-Refine）+ Task Sentinel 自动监控**（GCENT：关节状态缓冲倒带失效点 + 步骤成功检测，1:N 可扩展，数据效率提升 2.25x）🆕
- **高效微调**: LoRA（OpenVLA 验证 rank=32 匹配全量微调）, 量化推理（4-bit 无损）, ESA（Being-H0.5: slot-wise adapter）
- **推理加速**: DDIM（Diffusion Policy）、Euler 步数减少（π₀ 10步）、Consistency Models、多TPU云服务（RT-2）、**1-step denoising**（Cosmos Policy：1步去噪仅损失0.7%成功率）、**DreamZero-Flash**（解耦视频/动作噪声调度 + DiT Caching + CFG并行 + NVFP4量化 → 38x 加速实现 7Hz）
- **输出约束**: 推理时限制解码词表仅采样有效动作 token（RT-2首创）
- **规划方法**: **Best-of-N + World Model + Value Function**（Cosmos Policy：采样N动作→预测未来状态→选最高价值，ensemble + majority mean）
- **系统接口**: MCP工具协议（RoboClaw: Start/Terminate/Switch Policy, Env Summary, Call Human）

→ 详见 [components/index.md](components/index.md)

## 主要 Benchmark
- LIBERO, SimplerEnv, CALVIN, RLBench, Language Table
- RoboMimic, Push-T, Block Pushing, Franka Kitchen（Diffusion Policy 的评测基准）
- **RoboCasa**（家庭场景仿真，Cosmos Policy 67.1% SOTA）
- 真机评测：BridgeV2 (WidowX), Google Robot, Franka (Tabletop/DROID), UR5, RT-1 Robot (7DoF mobile manipulator), 多机构多机器人
- **ALOHA 双臂操作平台**（Cosmos Policy 93.6 avg score SOTA）
- Open-world评测：mock homes, real homes（π₀.5引入）
- **跨具身真机评测**：5 种平台（PND Adam-U, Franka+Inspire, Unitree G1, BeingBeyond D1, SO-101）（Being-H0.5 引入）
- **AgiBot G1 双臂移动操作平台**（RoboClaw + DreamZero + **GCENT** 的真机评测平台）
- **DROID-Franka 开放数据集评测**（DreamZero 开源 checkpoint）
- **Genie Sim 3.0**（100 仿真任务，DreamZero 未用仿真数据展示非平凡性能）
- **RoboArena 真机评测**（DreamZero 开源评测代码）
- **长时记忆真机评测** 🆕：MEM 提出的记忆能力评测套件（Swap Mugs, Find Object, Unpack Groceries, Scoop Coffee, Grilled Cheese, Window Cleaning, Recipe Setup, Clean Kitchen）
- **GCENT 真机任务套件** 🆕：Sandwich Assembly（8步双臂长时序）/ Connector Insertion（高精度接触丰富）/ Microwave-Heating（5种操作长时序）/ Typing（键盘打字指令跟随），专为数据收集范式评测设计

→ 详见 [benchmarks/index.md](benchmarks/index.md)

## 发展脉络
```
RT-2 (2023.07, 首个VLA, VLM+Action Token, 定义"动作即语言"范式)
  ├── RT-2-X (2023, +跨具身OXE数据)
  └── 启发开源替代 → OpenVLA (2024.06, 7B超越55B)

Diffusion Policy (2023, DDPM用于BC策略, 单任务奠基)
  → Octo (2024.01, 开源GRP奠基, 将diffusion head扩展到跨具身预训练)
    → RDT (2024, Transformer+Diffusion Head, 无VLM)
      → RDT2 (2025, +Qwen2.5-VL-7B+10K小时UMI数据+RVQ三阶段训练, "4U"零样本跨具身泛化)
    → OpenVLA (2024.06, 开源VLA奠基, VLM+Action Token, 7B超越RT-2-X 55B)
      → π₀ (2024.10, VLM+Flow Head, flow matching替代DDPM, 解决OpenVLA的离散化/action chunking局限) 
        ├── π₀.5 (2025, 层次化+开放世界, 任务复杂度方向)
        │   ├── MEM/π₀.6-MEM (2025, +多尺度记忆, 视频编码器+语言记忆, 15分钟任务) 🆕
        │   └── RoboClaw (2026, 系统框架, VLM元控制器+EAP, 基于π₀.5)
        └── Being-H0.5 (2026, 人类中心+统一动作空间+30具身, 跨具身泛化方向, 开源)

Video Model → Policy (视频预训练→机器人策略, 世界模型路线)
  Cosmos-Predict2 (NVIDIA, 视频生成基础模型)
    → Cosmos Policy (2026, latent frame injection, 统一policy+WM+value, LIBERO/RoboCasa/ALOHA SOTA)
  Wan2.1-I2V-14B (NVIDIA, 视频生成基础模型)
    → DreamZero (2026, 14B WAM, 自回归chunk-wise, 零样本泛化2x+, 跨具身video-only迁移, 7Hz实时)

VLM-as-Controller 系统演进线:
SayCan (2022) → Inner Monologue (2022) → RoboClaw (2026, +全生命周期统一+EAP自重置)

交互式数据收集演进线 🆕:
DAgger (2011) → HG-DAgger (2018) → Fleet-DAgger (2022)
  → RoboCopilot (2024, 双边遥操作硬件+HG-DAgger, 双臂操作落地)
  → GCENT/Genie Centurion (2025, 倒带机制+Task Sentinel, 1:N多机器人, 真机VLA精调)
  → RoboClaw (2026, VLM元控制器全生命周期统一)

VLA RL 后训练演进线 🆕:
SERL (2024, Q-function RL for robot)
  → HIL-SERL (2024, +HITL人类干预, Q-function+RL, 接触丰富任务验证)
  → Q-Chunking (2025, +action chunking distillation稳定RL, 主要仿真)
  → PA-RL (2024, +监督目标稳定在线训练)
  → Hi-ORS (2025, 拒绝采样完全替代Q函数, +reward-weighted flow matching全步骤监督, +HITL error recovery, 真机1.5h 80%)
  → Evo-RL (2026, 离线ACP：优势标签注入task text，LeRobot基础，完全开源真机RL)
  → RLT (2025, PI, RL Token紧凑表征+冻结VLA+轻量actor-critic+chunk-level RL, 数小时真机, 超人类速度, 涌现新策略)

轻量化 VLA 方法线（新增）:
TinyVLA (2024, 子10亿参数, 仍需机器人预训练) → SmolVLA (2025, 2.25B, Meta-World 68.2%)
  → Evo-1 (2025, 0.77B, InternVL3-1B+Cross-only DiT+两阶段语义保护, Meta-World 80.6% SOTA, 无机器人预训练)

冻结VLM + 分类动作解码方法线（新增）:
SaiVLA-0 (2026.03, Synthoid.ai, 冻结VLM三元架构Cerebrum+Pons+ParaCAT, {-1,0,+1}分类动作, 两阶段特征缓存-40%训练时间, LIBERO 99.0% SOTA)

VLA 3D 空间感知方法线（新增）:
3D-VLA/SpatialVLA/PointVLA (显式RGB-D依赖, 需额外传感器)
  → Evo-0 (2025, VGGT隐式几何先验+Cross-Attention融合, 仅RGB, π₀基础, RLBench +15pp)
```

### 技术传承线
```
RT-2 (2023, 首创VLA)
├── 核心贡献: VLA概念 + 动作token化 + co-fine-tuning + 涌现能力 + chain-of-thought尝试
├── → RT-2-X (2023): +跨具身数据
├── → OpenVLA (2024): 开源版, 更好VLM backbone, 更大数据
├── → π₀ (2024): 继承VLM预训练思想, flow matching替代离散token
├── → π₀.5 (2025): co-fine-tuning思想 → 多源异构co-training; chain-of-thought → 层次化推理
│     └── → MEM (2025): 层次化推理 → 层次化记忆（+语言记忆自主管理+视频编码器短时记忆）🆕
└── → Being-H0.5 (2026): co-training 扩展到人类视频+30具身; 统一动作空间替代独立头

Diffusion Policy (2023)
├── 核心贡献: 条件DDPM策略 + action sequence + receding horizon + position control
├── → Octo (2024): 继承 diffusion head + action chunking, 扩展到跨具身预训练
├── → π₀ (2024): 继承 action chunking + 连续动作生成思想, 升级为 flow matching + VLM
├── → Being-H0.5 (2026): 继承 flow matching, 加入 MoF/MPG/UAC 解决跨具身部署问题
├── → ACT (2023): 同时期互补路线 (CVAE替代diffusion)
└── → Cosmos Policy (2026): 继承 diffusion 生成动作思想, 升级为视频模型 latent diffusion + 统一WM/value

Cosmos-Predict2 (2025, 视频生成基础模型)
├── → Cosmos Policy (2026): latent frame injection, 无架构修改适配为 policy+WM+value
├── → mimic-video (2024): partial denoising + IDM (流派C)
└── 与 FLARE/GR00T N1.5 (流派A) 共享 NVIDIA Cosmos 生态

Wan2.1-I2V (2025, 视频生成基础模型)
└── → DreamZero (2026): 自回归chunk-wise联合去噪, 最小架构修改
    - 核心区别于 Cosmos Policy: 14B(vs 2B)、自回归(vs 双向)、多样数据零样本泛化(vs 任务微调+规划)

VLM-as-Controller (系统框架演进)
├── SayCan (2022): LLM规划+affordance grounding, 开环执行
├── Inner Monologue (2022): +运行时反馈+重规划
├── Code as Policies (2022): LLM生成控制代码
└── RoboClaw (2026): +全生命周期统一(收集/训练/部署)+EAP自重置+MCP工具+过程监督+闭环学习

交互式数据收集 (Human-in-the-loop, 独立技术支线) 🆕
├── DAgger / HG-DAgger (2011/2018): 理论奠基
├── RoboCopilot (2024): 双边遥操作硬件解决工程瓶颈, 落地双臂操作
└── GCENT (2025): 倒带机制+Task Sentinel, 1:N可扩展, 数据效率 2.25x, 真机 VLA 精调
    - 核心差异化: 唯一将 Rewind + Task Sentinel + 多机器人 三者系统集成的真机数据收集框架
    - 与 RoboCopilot 互补: RoboCopilot 强调硬件无缝接管; GCENT 强调状态缓冲倒带+自动监控扩展性

Being-H0 (2025, 人类中心学习概念验证)
└── → Being-H0.5 (2026): 数据200×扩展, 统一动作空间, MoT/MoF架构, 跨具身泛化

SaiVLA-0 (2026, 三元架构, Synthoid.ai)
├── 核心贡献: 冻结VLM多层缓存 + Pons编译器 + ParaCAT分类动作头，完全分离语义/编译/执行
├── 独特之处: 唯一用{-1,0,+1}三元分类解码的VLA，并行K步解码，两阶段缓存训练
└── 与Figure Helix类似的双系统思想，但形式化为可独立升级的三元架构

VLA 记忆方法演进线 🆕:
密集帧历史 (Octo/BET, ~数秒)
├── 压缩记忆: Pool Memory (ContextVLA), Proprio (TA-VLA), Keyframe (BPP/MeMeR), Point Tracks (TraceVLA)
├── 潜在记忆: Sam2Act, MemoryVLA
├── 纯语言记忆: OneTwoVLA
└── **多尺度混合模态记忆: MEM (2025, 视频+语言, 15分钟, 首次系统解决)**
```

## 关键转折点
- **RT-2 (2023)**: 首次定义 VLA 范式，证明互联网 VLM 预训练知识可迁移到机器人低层控制，展示涌现能力
- **Diffusion Policy (2023)**: 证明扩散模型在机器人策略学习中全面优于传统方法（IBC, GMM, BET），确立了 diffusion/flow 生成动作的技术范式
- **Octo → OpenVLA**: 从"无VLM预训练的小模型"到"基于VLM预训练的大模型"，验证VLM知识对机器人泛化至关重要
- **OpenVLA → π₀**: 从"离散action token"到"连续flow matching"，解决了精细操作和高频控制的瓶颈
- **π₀ → π₀.5 + Being-H0.5**: VLM+Flow Head 方法线分化为两个互补方向——**任务复杂度**（π₀.5: 层次化+开放世界）和**跨具身泛化**（Being-H0.5: 统一动作空间+人类中心学习+30具身）
- **π₀.5 → MEM (2025)** 🆕: 从"层次化推理"到"层次化记忆"——高层策略从无状态子任务预测升级为有状态语言记忆管理，同时低层策略通过视频编码器获得短时视觉记忆。首次系统性证明多尺度混合模态记忆使 VLA 端到端执行 15 分钟任务，解锁上下文适应能力，且不损害灵巧操作性能
- **Cosmos Policy (2026)**: 确立"视频模型→机器人策略"的最简适配范式（latent frame injection），首次在同一模型中统一 policy+world model+value function，验证**视频预训练先验在低层控制场景可超越 VLM 预训练先验**（超越 π₀.5, OpenVLA-OFT+）
- **DreamZero (2026)**: 确立 WAM 作为独立方法范式，首次系统证明 WAM 在零样本泛化上 **2x+ 优于 SOTA VLAs**，揭示 VLA 和 WAM 的本质差异（语义先验 vs 时空动力学先验），**颠覆数据收集范式**（多样非重复 > 重复示教），并通过 video-only 数据实现高效跨具身迁移
- **RoboClaw (2026)**: 代表"系统级agentic框架"思路的成熟——不追求更好的VLA模型，而是用VLM元控制器将现有VLA组织成可自主运行的全生命周期系统
- **GCENT/Genie Centurion (2025)** 🆕: 将"deploy-then-collect"范式系统落地于真机 VLA 精调——倒带机制集中覆盖关键失效点，Task Sentinel 自动监控使 1:N 多机器人监督成立（效率 1.86~1.92），同等数据效率提升 2.25x。揭示了**数据质量集中度**（vs 均匀覆盖）和**倒带策略阶段性使用**（早期助失败恢复/后期助首次成功）两个重要规律
- **贯穿主线**: 
  - 开源 vs 闭源的竞争——RT-2闭源促使OpenVLA开源，π₀.5闭源促使Being-H0.5开源
  - RT-2的co-fine-tuning → π₀.5的多源异构co-training → Being-H0.5的人类中心+跨具身co-training——数据策略的持续演进
  - RT-2的chain-of-thought探索 → π₀.5的层次化推理 → **MEM的层次化记忆**——统一推理与控制的持续深化 🆕
  - 独立头/零填充 → 统一物理语义动作空间——跨具身表示的演进
  - SayCan的外部规划 → RoboClaw的全生命周期agentic系统——系统级智能的演进
  - **VLM 预训练 vs 视频预训练之争**：π₀/π₀.5 基于 VLM（静态图文语义），Cosmos Policy / DreamZero 基于视频模型（时空动力学），DreamZero 的 2x+ 优势提供了"视频预训练先验更适合物理泛化"的强证据
  - **数据范式之争**：传统 VLA 需要重复示教覆盖状态-动作空间，WAM 从多样非重复数据有效学习——DreamZero 证明这是方法范式差异而非规模差异（14B VLA 在多样数据上仍 0%）
  - **记忆是 VLA 实用化的关键** 🆕：从无记忆（π₀/OpenVLA）→ 短时帧历史（Octo）→ 多尺度混合记忆（MEM），记忆能力的演进使 VLA 从"单步反应"走向"长程有状态决策"
  - **数据收集效率是 VLA 规模化的关键** 🆕：传统 1:1 遥操作 → RoboCopilot 交互式介入 → GCENT 倒带+自动监控 1:N，数据收集从"全程人力消耗"走向"按需精准介入"
  - **VLA RL 后训练：从 Q-function 到 Rejection Sampling 到 ACP** 🆕：HIL-SERL 用价值函数（不稳定），Hi-ORS 用 outcome-based 拒绝采样（无Q函数，真机1.5h），Evo-RL 用离线 ACP（advantage 注入 task text，更精细 per-step 信号，完全开源）
  - **VLA 轻量化与语义保护** 🆕：大参数 VLA（π₀ 3.5B）端到端训练破坏 VLM 语义空间；Evo-1 通过两阶段训练（先冻结VLM，再解冻微调）保护语义，0.77B 超越 3.5B 模型（Meta-World 80.6% vs 47.9%），揭示语义保护比参数规模更关键
  - **3D 空间感知：从显式到隐式** 🆕：显式方案需深度传感器（SpatialVLA/PointVLA），Evo-0 用 VGGT 视觉几何基础模型从纯 RGB 隐式提取几何先验，单层 Cross-Attention 融合即 +15pp，部署更灵活
