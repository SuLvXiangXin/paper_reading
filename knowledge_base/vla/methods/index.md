# 方法分类概览

## Diffusion Policy (BC + Diffusion 奠基)
将扩散模型系统性引入机器人行为克隆的奠基工作。通过将策略表示为条件去噪扩散过程（DDPM），结合 action sequence prediction 和 receding horizon control，实现对多模态动作分布的精确建模、高维动作序列的稳定生成和训练稳定性。
- 代表：**Diffusion Policy** (Chi et al. 2023)
- 优势：多模态建模精确、训练稳定（无需负采样）、高维输出空间 scaling 好、与 position control 协同好
- 劣势：单任务/少任务框架、无语言条件、推理延迟高于简单方法
- **历史地位**：是后续所有 diffusion/flow 动作生成方法的技术源头
→ 详见 [diffusion_policy.md](diffusion_policy.md)

## Transformer + Diffusion Head (Cross-embodiment Generalist Policy)
不依赖预训练 VLM，直接用 ViT 风格 transformer + diffusion/flow head 从大规模跨具身数据训练通用策略。
- 代表：**Octo**, RDT
- 优势：架构简单、开源可复现、支持灵活微调
- 劣势：缺乏 VLM 预训练的语义知识，语言理解能力有限
- 与 Diffusion Policy 的关系：将 Diffusion Policy 的 diffusion head 思想扩展到跨具身预训练场景
- 与 VLM + Diffusion/Flow Head 的关系：是后者的前身/轻量版本，π₀ 可视为 Octo 的 "VLM 升级版"
→ 详见 [transformer_diffusion_head.md](transformer_diffusion_head.md)

## VLM + Action Token
将动作离散化为 token，直接用 VLM 的 next-token prediction 输出。
- 代表：RT-2, OpenVLA
- 优势：直接复用 VLM 预训练知识
- 劣势：离散化损失精度，高维动作空间困难
→ 详见 [vlm_action_token.md](vlm_action_token.md)

## VLM + Diffusion/Flow Head
VLM 作为视觉语言编码器提取特征，用扩散模型或 flow matching 生成连续动作。
- 代表：π₀, π₀.5, GR00T N1, **EgoScale**, **Being-H0.5**
- 优势：连续动作更精确，适合灵巧操作
- 劣势：推理较慢，训练复杂
- 与 Diffusion Policy 的关系：继承了条件化生成 + action chunking 的核心设计，升级为 flow matching + 与预训练 VLM 结合
- **2025-2026 分化为三个方向**（更新）：
  - **任务复杂度方向**：π₀.5（层次化推理 + 开放世界泛化）→ MEM（+多尺度记忆）🆕
  - **跨具身泛化方向**：Being-H0.5（统一动作空间 + 人类中心学习 + 30 种具身 + MoF 架构）
  - **实时部署方向**：Xiaomi-Robotics-0（Λ-shape mask + 消费级 GPU）
→ 详见 [vlm_diffusion_head.md](vlm_diffusion_head.md)

## 层次化VLA (Hierarchical VLA)
统一模型同时进行高层语义推理（子任务预测）和低层动作生成，类似chain-of-thought。
- 代表：π₀.5, Hi Robot, RT-H, HAMSTER, **MEM** 🆕
- 优势：高层推理利用语义知识、低层控制利用动作数据，互不干扰又协同
- 劣势：需要子任务标注数据；高层推理频率与低层不同需设计
- 关键区分：与"两个独立模型"的层次化方案（SayCan, BUMBLE等）不同，统一模型方案通过共享权重实现更好的知识迁移
- **MEM 的演进** 🆕：从"层次化推理"到"层次化记忆"——高层策略从无状态子任务预测升级为有状态语言记忆管理
→ 详见 [hierarchical_vla.md](hierarchical_vla.md)

## VLA 记忆方法 🆕
为 VLA 策略添加历史信息记忆，使策略能基于过去的观测/事件做决策，解决部分可观测性、长时序任务追踪、上下文适应等问题。
- **密集帧历史**：直接输入过去 K 帧观测（Octo, BET）。简单直接，但帧数受限于计算开销
- **压缩观测记忆**：通过池化(ContextVLA)、关键帧选择(BPP/MeMeR)、点轨迹(TraceVLA)等压缩历史观测
- **本体感知记忆**：仅记忆过去的关节状态（TA-VLA），低开销但无环境信息
- **潜在记忆**：用隐状态表示记忆（Sam2Act, MemoryVLA），尚未在长时序场景充分验证
- **语言记忆**：用自然语言描述过去事件（OneTwoVLA），适合语义级长时记忆但丢失空间细节
- **多尺度混合模态记忆**：**MEM (2025)** 首创——短时视觉记忆（视频编码器，~54s）+ 长时语言记忆（摘要机制，~15min），两者互补，是目前最系统的 VLA 记忆方案
  - **核心洞察**：没有单一模态能同时满足短时精细记忆和长时语义记忆，应按时间尺度匹配不同模态
  - **关键发现**：(1) 预训练记忆能力远优于仅后训练引入，(2) 多样化预训练数据自然缓解 causal confusion，(3) 压缩语言记忆减少训练-推理分布偏移
  - **附赠能力**：上下文适应（in-context adaptation）——策略从短时记忆中的失败经历调整操作策略

## VLM-as-Controller 系统框架 (Agentic Robotics Framework)
使用现成VLM/LLM作为高层元控制器，通过工具调用/API调度低层VLA策略执行，实现系统级的层次化控制。
- 代表：SayCan (2022), Inner Monologue (2022), **RoboClaw (2026)**
- 优势：灵活模块化（VLM/VLA可独立替换）、运行时推理适应、可扩展策略库
- 劣势：VLM推理延迟、高层/低层知识不共享、系统复杂度高
- 与层次化VLA的区别：分离式外部编排 vs 统一模型内层次化推理
- **RoboClaw的新贡献**：(1) 统一数据收集和部署的决策循环，(2) EAP自重置数据收集，(3) MCP工具接口标准化，(4) 部署轨迹闭环回流训练
→ 详见 [vlm_as_controller.md](vlm_as_controller.md)

## World Model + VLA（世界模型路线）
将 World Model 引入 VLA，使模型具备「想象」和「规划」能力。分为三大流派：
- **流派A: Hidden State → Action**：用 world model 隐状态驱动动作生成（FLARE, GR00T N1.5, Genie Envisioner, DreamVLA）
- **流派B: 视频+动作联合去噪**：同一 diffusion 框架同时去噪视频和动作（DreamZero, UWM, Cosmos Policy, GR-1/GR-2）
- **流派C: 视频→Inverse Dynamics**：先生成视频再用 IDM 恢复动作（UniPi, Seer, SuSIE, DeFI, F1）
→ 详见 [world_model_vla.md](world_model_vla.md)

## Human Data Pretraining for VLA（人类数据预训练路线）
> 2024-2026 年兴起的重要方法方向

利用大规模人类视频（特别是 egocentric 视角）预训练 VLA 模型的视觉-动作表征，再通过少量对齐数据迁移到机器人控制。
- 代表：**EgoScale** (NVIDIA 2026), **Being-H0/H0.5** (BeingBeyond 2025-2026), EgoVLA, EgoMimic, DexWild
- **核心思路**：人类是最可扩展的操作数据源；egocentric 视角 + 3D 手部追踪 → 提取 wrist trajectory + finger joint actions → 作为 VLA 预训练的动作监督
- **Being-H0.5 的独特贡献**：
  - 将人手 MANO 参数映射到统一动作空间（腕部→EEF，手指→精细操作槽位），与 30 种机器人共享同一表示
  - 混合连续 flow matching + 离散 masked token prediction 的双通道人类运动监督
  - UniHand-2.0：35K+ 小时（16K 人类 + 14K 机器人 + 5K VLM），迄今最大具身预训练语料
- **关键发现（EgoScale）**：
  - Scaling Law: L = 0.024 - 0.003·ln(D), R² = 0.9983
  - 离线 validation loss 与真机性能强相关
  - One-shot 泛化在大规模预训练 + 对齐 mid-training 后涌现
- **与机器人数据预训练的区别**：需要额外的 embodiment alignment 阶段（mid-training 或 co-training），但数据获取成本远低于遥操作
→ 详见 [reports/human_hand_data_robot_policy_survey.md](../reports/human_hand_data_robot_policy_survey.md)

## 奖励学习路线
从人类视频或偏好中学习奖励函数，用 RL 训练策略。
→ 详见 [reward_learning.md](reward_learning.md)

## 方法演进关系图
```
Diffusion Policy (2023, 单任务BC)
    │
    ├── Octo (2024, 跨具身, 无VLM) ──→ π₀ (2024, +VLM, +Flow Matching)
    │                                        │
    │                                        ├── π₀.5 (2025, +层次化, 任务复杂度方向)
    │                                        │     ├── MEM (2025, +多尺度记忆, 15分钟任务) 🆕
    │                                        │     └── RoboClaw (2026, 系统框架, π₀.5作底层VLA)
    │                                        │
    │                                        ├── Being-H0.5 (2026, +人类中心+统一动作空间+MoF, 跨具身方向, 开源)
    │                                        │
    │                                        └── GR00T N1 (2025, NVIDIA)
    │                                              │
    │                                              └── EgoScale (2026, +人类数据scaling)
    │
    └── ACT (2023, CVAE路线, 互补)

RT-2 (2023, VLM+离散Token) ──→ OpenVLA (2024, 开源版)

VLM-as-Controller 演进线:
SayCan (2022) → Inner Monologue (2022) → RoboClaw (2026, +全生命周期统一+EAP)

Human Data 支线:
R3M (2022) → EgoMimic (2024) → Being-H0 (2025) → Being-H0.5 (2026, 35K小时, 30具身)
                              → EgoVLA/DexWild (2025) → EgoScale (2026, 20K小时)

VLA 记忆方法演进线 🆕:
密集帧历史 (Octo/BET) → 压缩记忆 (ContextVLA/TraceVLA/BPP) → 多尺度混合模态记忆 (MEM, 2025)
```
