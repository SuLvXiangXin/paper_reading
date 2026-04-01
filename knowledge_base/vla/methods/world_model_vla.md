# World Model + VLA 方法路线

## 概述

将 World Model 引入 VLA 是一条区别于传统「感知→动作」直接映射的方法路线。核心思想是：**先理解/预测世界动态，再据此生成动作**，使 VLA 具备「想象」和「规划」能力。

这条路线根据 World Model 输出如何与动作生成衔接，分为三大流派：

```
World Model + VLA
├── 流派A: Hidden State → Action Expert     （隐式世界模型）
├── 流派B: 视频+动作联合去噪               （统一世界模型）
└── 流派C: 先生成视频 → Inverse Dynamics    （显式世界模型 + IDM）
```

---

## 流派A：Hidden State → Action Expert（隐式世界模型）

### 核心思路
用 World Model 的**隐状态/latent representation** 来指导动作生成，不需要显式生成视频帧。World Model 在 latent space 中预测未来状态，这些 latent 表征直接作为 action decoder 的条件输入。

### 优势
- **推理高效**：不需要像素级视频生成，计算量远低于显式视频生成方案
- **信息密度高**：latent 表征可以聚焦动作相关信息，过滤冗余像素
- **端到端训练友好**：隐式目标更容易优化

### 劣势
- **可解释性差**：latent space 无法直观观察，难以调试
- **世界模型质量难以评估**：不像视频生成可以人眼查看

### 代表论文

| 论文 | arXiv | 机构 | 时间 | 引用 | 要点 |
|------|-------|------|------|------|------|
| **FLARE** | 2505.15659 | NVIDIA GEAR | 2025.05 | ~37 | 在 VLA 的 DiT 中加入 "future tokens"，通过 cosine similarity loss 对齐未来观测的 latent embedding。简单有效，+26% 性能提升 |
| **GR00T N1.5** | — | NVIDIA GEAR | 2025 | — | 在 GR00T N1 基础上加入 FLARE 对齐机制，使人形机器人策略具备隐式前瞻能力，支持从人类视频学习 |
| **Genie Envisioner** | 2508.05635 | AgiBot | 2025.08 | 新 | GE-Base 大规模 world model 编码时空语义结构，GE-Act 利用 world model hidden state 生成动作。统一平台同时支持策略学习和评估 |
| **MinD** | — | — | 2025 | — | 用 world model 的单步 latent 预测来 condition diffusion policy，避免生成完整视频帧，验证了 compact latent 足以驱动精确控制 |
| **VidMan** | 2411.09153 | — | 2024.11 (NeurIPS 2024) | ~39 | 预训练视频扩散模型（基于 Open-Sora），用 gating 机制从扩散过程中蒸馏隐式动力学知识到 action query。CALVIN 上比 GR-1 提升 11.7% |
| **DreamVLA** | 2507.04447 | — | 2025.07 (NeurIPS 2025) | ~74 | 预测 comprehensive world knowledge（动态区域、3D 深度、高层语义）而非原始像素，用这些知识驱动 inverse dynamics |
| **iVideoGPT** | — | 清华 | 2024 (NeurIPS 2024) | — | 可交互的 VideoGPT，学习 latent world model，可作为下游策略基座。支持百万级人类和机器人数据预训练 |

### 关键论文关系
```
DreamerV3 (2023, latent WM + RL, 奠基)
    │
    ├── FLARE (2025, latent alignment + VLA DiT)
    │       └── GR00T N1.5 (2025, FLARE 集成到工业级模型)
    │
    ├── VidMan (2024, video diffusion → implicit dynamics distillation)
    │
    ├── MinD (2025, single-step latent → diffusion policy)
    │
    └── DreamVLA (2025, comprehensive world knowledge prediction)

Genie Envisioner (2025, 独立体系, world foundation platform)
iVideoGPT (2024, autoregressive latent world model)
```

---

## 流派B：视频 + 动作联合去噪（统一世界模型）

### 核心思路
在**同一个 diffusion/flow-matching 框架**中同时去噪视频帧和动作序列。视频预测和动作生成共享底层 dynamics 表征，实现强对齐。本质上是把 World Model 和 Policy 统一到一个模型中。

### 优势
- **视频-动作强对齐**：共享去噪过程保证视觉预测和动作生成一致
- **端到端训练**：一个模型同时学会预测世界变化和生成动作
- **天然支持 action-free 数据**：可以在无动作标注的视频上做预训练（只去噪视频部分）
- **统一三合一潜力**：同一模型可同时作为 policy、world model、value function（Cosmos Policy 首次实现）

### 劣势
- **计算开销大**：需要同时处理视频帧和动作的去噪，模型体量大
- **推理延迟高**：视频帧去噪步数多
- **训练复杂**：需要平衡视频和动作两个模态的学习

### 代表论文

| 论文 | arXiv | 机构 | 时间 | 引用 | 要点 |
|------|-------|------|------|------|------|
| **DreamZero** | 2602.15922 | NVIDIA GEAR | 2026.02 | ~6（新） | 14B WAM，基于 Wan2.1 视频扩散骨干。视频+动作共享去噪 timestep，7Hz 实时闭环。零样本任务泛化比 VLA SOTA 提升 2x。少样本跨具身迁移 |
| **UWM** | 2504.02792 | UW + Toyota | 2025.04 (RSS 2025) | ~65 | 核心创新：**解耦动作和图像的 diffusion timestep**。单一 transformer 联合建模 p(o,a,o')，推理时通过控制 timestep 灵活切换 policy/forward/inverse dynamics/video generator |
| **PAD** | 2411.18179 | 清华 | 2024.11 (NeurIPS 2024) | — | DiT 架构融合所有模态输入，同时联合去噪 future image 和 action。验证了视觉预测和动作生成共享物理动力学 |
| **Cosmos Policy** | 2601.16163 | NVIDIA + Stanford | 2026.01 | ~17 | **Latent frame injection**: 将 action/proprio/value 编码为 latent frames 注入预训练视频 diffusion 序列，无架构修改单阶段微调。**统一 policy+WM+value function**，通过 conditioning mask 切换功能。支持 best-of-N model-based planning。LIBERO 98.5%, RoboCasa 67.1% (50 demos) SOTA |
| **CoVAR** | 2512.16023 | — | 2024.12 | — | Multi-Modal Diffusion 同时生成视频和动作。探索了共生成的 co-generation 范式 |
| **AVID** | 2410.12822 | — | 2024.10 | — | 将 action conditioning 加入预训练视频扩散模型，Product of Experts 方式融合 action-conditioned 和 unconditional video score |
| **GR-1** | — | ByteDance | 2024 (ICLR 2025) | ~275 | GPT 风格模型，预训练视频预测 + 微调动作生成。虽然非严格联合去噪，但开创了视频预训练→动作微调范式 |
| **GR-2** | 2410.06158 | ByteDance | 2024.10 | ~187 | GR-1 的扩展版，先大规模互联网视频预训练，再机器人视频微调，最后动作微调。三阶段训练 |
| **RynnVLA-002** | 2511.17502 | 阿里达摩院 | 2025.11 | ~10 | 统一 VLA + World Model 的自回归框架，联合学习环境动力学和动作规划，证明两者相互增强 |

### Cosmos Policy 关键技术贡献（流派B 内的突破）🆕

Cosmos Policy 是流派B中首个将**预训练视频模型**无架构修改地同时适配为 policy + world model + value function 的工作：

1. **Latent Frame Injection**：将 action chunk、proprio、value 标准化→flatten→duplicate 为 latent volume，直接覆写视频 diffusion 序列中的 placeholder latent frames。这是比 UWM（自定义架构从头训练）和 Video Policy（多阶段+独立 action module）更简洁的视频→策略适配方案。

2. **Conditioning Mask 切换功能**：同一模型通过不同的 conditioning mask 实现三种功能：
   - Policy: 条件 s → 生成 (a, s', V(s'))
   - World Model: 条件 (s,a) → 生成 (s', V(s'))
   - Value Function: 条件 (s,a,s') → 生成 V(s')

3. **Model-Based Planning**：Dual deployment（原始 checkpoint 作 policy，rollout 微调 checkpoint 作 planning model）+ best-of-N + ensemble + majority mean 聚合。

4. **数据效率**：RoboCasa 仅用 50 demos 超越用 300 demos 的 FLARE/Video Policy/GR00T-N1.5，验证视频预训练先验的强大价值。

### 关键论文关系
```
Video Diffusion 预训练范式:
GR-1 (2024, video pretrain → action finetune, 开创者)
    └── GR-2 (2024, 互联网规模视频预训练)

联合去噪范式:
Diffuser (2022, state+action 联合去噪, 源头)
    ├── PAD (2024, DiT + image+action 联合去噪)
    ├── UWM (2025, 解耦 timestep, 灵活推理)
    ├── DreamZero (2026, 14B WAM, 零样本泛化)
    └── CoVAR (2024, multi-modal co-generation)

视频模型直接微调 (无架构修改):
Cosmos Policy (2026, latent frame injection, 单阶段, 统一policy+WM+value) ← SOTA
    ↑ 与 FLARE/GR00T N1.5 (流派A) 同为 NVIDIA 的平行探索
AVID (2024, Product of Experts action conditioning)
RynnVLA-002 (2025, autoregressive unified)
```

### 流派B内技术路线对比 🆕

| 维度 | Cosmos Policy | DreamZero | UWM | Video Policy |
|------|--------------|-----------|-----|-------------|
| **基座模型** | Cosmos-Predict2 2B | Wan2.1 14B | 从头训练 | 视频模型+独立action module |
| **架构修改** | 无 | 无 | 自定义 | 需要独立action module |
| **训练阶段** | 单阶段 | 单阶段 | 单阶段 | 多阶段 |
| **世界模型** | ✅ (显式future state) | ✅ (视频预测) | ✅ (灵活切换) | ❌ |
| **价值函数** | ✅ (统一) | ❌ | ❌ | ❌ |
| **Planning** | ✅ (best-of-N) | ❌ | ❌ | ❌ |
| **零样本泛化** | ❌ | ✅ | ❌ | ❌ |
| **LIBERO** | 98.5% | — | — | 94.0% (Long) |
| **RoboCasa** | 67.1% (50 demos) | — | 60.8% (1000 demos) | 66.0% (300 demos) |

---

## 流派C：先生成视频 → Inverse Dynamics Model（显式世界模型 + IDM）

### 核心思路
两阶段 pipeline：**第一步**用视频生成模型做视觉规划（预测未来应该看到什么画面），**第二步**用 Inverse Dynamics Model (IDM) 从预测的视频/图像中恢复动作序列。本质是把规划和控制解耦。

### 优势
- **可利用海量无动作视频**：视频模型可以在互联网视频上预训练，不需要动作标注
- **可解释性强**：可以直接查看生成的视频/子目标图像来理解模型规划
- **模块化**：视频模型和 IDM 可以独立开发和改进

### 劣势
- **两阶段误差累积**：视频生成错误会传递到 IDM
- **IDM 瓶颈**：从两帧图像恢复精确动作是 ill-posed 问题
- **推理延迟**：需要先跑视频生成，再跑 IDM

### 代表论文

| 论文 | arXiv | 机构 | 时间 | 引用 | 要点 |
|------|-------|------|------|------|------|
| **UniPi** | 2302.00111 | Google / MIT | 2023.01 (NeurIPS 2024) | **~449** | **开山之作**。Text-guided video generation + inverse dynamics model。首次证明可以通过视频生成做通用策略学习。利用互联网视频知识迁移 |
| **SuSIE** | 2310.10639 | UC Berkeley | 2023.10 | **~264** | 用 InstructPix2Pix 图像编辑模型生成下一个视觉子目标（而非完整视频），然后用 goal-conditioned policy 执行。轻量高效的子目标规划 |
| **Seer** | 2412.15109 | 上海AI Lab | 2024.12 (ICLR 2025 **Oral**) | 新 | **端到端 PIDM**：将视觉预测和 inverse dynamics 闭环到一个 Transformer 中。CALVIN ABC-D SOTA (4.28)。在 DROID 上预训练后真实世界效果显著 |
| **F1** | 2509.06951 | — | 2025.09 | — | Mixture-of-Transformer 三专家架构：理解专家 → 生成专家（foresight image）→ 动作专家（predictive inverse dynamics）。统一理解-生成-动作 |
| **DeFI** | OpenReview | — | 2025 | — | 核心创新：**解耦 Forward（视频预测）和 Inverse（动作预测）的预训练**。Forward 用大规模无动作视频，Inverse 用机器人数据，各自利用最优数据源 |
| **mimic-video** | 2512.15692 | NVIDIA | 2024.12 | — | 基于 Cosmos-Predict2 视频骨干，partial denoising 提取 latent visual plans，轻量 action decoder 做 IDM。Flow Matching 统一框架 |
| **VPP** | 2412.14803 | — | 2024.12 | — | 视频预测模型的**内部表征**直接作为 inverse dynamics 的输入，避免多步去噪生成完整帧。高频闭环控制 |
| **ForeAct** | 2602.12322 | — | 2026.02 | 新 | 高效 foresight image generator 做规划，100 万+ 多任务跨具身数据预训练 |
| **VPDD** | 2402.14407 | — | 2024.02 | — | 用 VQ-VAE 离散化视频 token，discrete diffusion 做视频预测，再从预测视频中学习动作。支持大规模无动作人类视频预训练 |
| **AMPLIFY** | 2506.14198 | — | 2025.06 | 新 | 三阶段框架：解耦 forward dynamics（任意视频训练）和 inverse dynamics（交互数据训练），用 latent keypoint motion 做中间表征 |
| **RoboDreamer** | 2404.12377 | — | 2024.04 | — | 组合式世界模型，video diffusion 做规划 + inverse dynamics 提取动作。支持复杂长程任务分解 |
| **3D-VLA** | 2403.09631 | UMass | 2024.03 (ICML 2024) | **~262** | 将 World Model 扩展到 3D：用 3D 场景表征做世界建模，支持 3D 推理和规划。集成人机交互视频和机器人演示 |
| **LAPA** | 2410.11758 | MSR + UW | 2024.10 (ICLR 2025) | **~191** | 用 VQ-VAE 从视频帧对中提取 latent actions，大规模无标注视频预训练 VLA。证明 latent action 是利用人类视频的有效桥梁 |

### 关键论文关系
```
UniPi (2023, 开山之作: text→video→IDM)
    │
    ├── SuSIE (2023, 简化为 image editing → subgoal → policy)
    │
    ├── Seer (2024, 端到端 PIDM, 闭环 visual prediction + IDM)
    │       └── F1 (2025, MoT 三专家, 统一 understand-generate-act)
    │
    ├── DeFI (2025, 解耦 forward/inverse pretraining)
    │       └── AMPLIFY (2025, latent keypoint motion 中间表征)
    │
    ├── mimic-video (2024, partial denoising visual plans + IDM)
    │
    ├── VPP (2024, 内部表征做 IDM, 不生成完整帧)
    │
    └── VPDD (2024, discrete diffusion video + action)

3D-VLA (2024, 独立体系, 3D世界建模)
LAPA (2024, latent action 预训练, 利用无标注视频)
RoboDreamer (2024, 组合式长程规划)
```

---

## 三大流派对比

| 维度 | 流派A: Hidden State | 流派B: 联合去噪 | 流派C: 视频→IDM |
|------|-------------------|----------------|----------------|
| **World Model 形式** | 隐式 latent | 统一 diffusion | 显式视频生成 |
| **动作生成方式** | latent-conditioned policy | 与视频共同去噪 | Inverse Dynamics |
| **推理效率** | 高 | 低（需去噪视频） | 中（需先生成再推理） |
| **可解释性** | 低 | 中（可看视频输出） | 高（可看生成视频/子目标） |
| **利用无动作数据** | 有限 | 天然支持 | 天然支持 |
| **误差传播** | 端到端，不累积 | 端到端，不累积 | 两阶段累积 |
| **代表最高引用** | DreamVLA (~74) | GR-1 (~275) | UniPi (~449) |
| **最强性能** | GR00T N1.5 | **Cosmos Policy (LIBERO 98.5%, RoboCasa 67.1%)** 🆕 | Seer (CALVIN 4.28) |
| **工业落地** | NVIDIA (GR00T) | NVIDIA (DreamZero, Cosmos Policy), ByteDance (GR) | AgiBot, 上海AI Lab |

## 发展趋势

1. **流派融合**：越来越多工作融合多个流派。如 DreamVLA 预测 world knowledge（流派A思路）但用 inverse dynamics 出动作（流派C思路）；Cosmos Policy 是流派B但也可以做 planning（流派C功能）
2. **从显式到隐式**：早期工作（UniPi, SuSIE）生成完整像素级视频/图像，新工作（FLARE, VPP, MinD）倾向使用 latent representation，更高效
3. **规模化**：DreamZero 14B、Genie Envisioner 大规模平台，说明 World Model + VLA 在向大模型方向发展
4. **利用互联网视频**：LAPA、GR-2、DeFI 等验证了大规模无动作视频对 VLA 预训练的价值
5. **闭环化**：从 UniPi 的开环视频规划，到 Seer/F1 的端到端闭环 PIDM，再到 DreamZero 的 7Hz 实时控制，闭环实时性不断提升
6. **统一化**：Cosmos Policy 展示了同一模型同时作为 policy+world model+value function 的可行性，模型功能边界持续扩展 🆕
7. **视频预训练 vs VLM 预训练之争**：Cosmos Policy 在低层控制场景超越 VLM-based VLA (π₀.5, OpenVLA-OFT+)，支持"时空动力学先验 > 静态语义先验"的假说，但 VLM 路线在语义泛化和开放世界上仍有优势 🆕

## 与现有 VLA 方法路线的关系

```
传统 VLA 方法路线:
├── VLM + Action Token (RT-2, OpenVLA)
├── VLM + Diffusion/Flow Head (π₀, π₀.5)
├── Transformer + Diffusion Head (Octo)
└── 层次化 VLA (π₀.5, Hi Robot)

World Model + VLA (本调研):
├── 流派A: Hidden State → Action (FLARE, GR00T N1.5)
├── 流派B: 联合去噪 (DreamZero, UWM, Cosmos Policy ← SOTA) 🆕
└── 流派C: 视频→IDM (UniPi, Seer, DeFI)
```

World Model 路线是对传统「感知→动作」直接映射范式的升级：引入**对世界动态的建模**，使 VLA 从「反射式」升级为「规划式」。这与 Kahneman 的双系统理论呼应：传统 VLA 是 System 1（快速反射），World Model + VLA 引入了 System 2（深思熟虑）。

### NVIDIA 在 World Model + VLA 的双线布局 🆕
NVIDIA 同时推进流派A和流派B，代表了两种互补思路：
- **流派A (FLARE/GR00T N1.5)**：隐式世界模型，推理高效，适合实时人形机器人控制
- **流派B (Cosmos Policy/DreamZero)**：显式视频预测，支持 planning，适合需要精确操作的桌面/双臂任务
- 两者共享 Cosmos 视频基础设施但面向不同应用场景
