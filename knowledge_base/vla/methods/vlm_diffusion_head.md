# VLM + Diffusion/Flow Head 方法线

## 核心思想
用预训练 VLM 作为视觉-语言编码器获取互联网级语义知识，再接一个 diffusion 或 flow matching 头生成连续动作。解决了纯自回归 VLA（RT-2, OpenVLA）动作离散化精度不足的问题，同时比纯 diffusion policy（无 VLM 预训练）具有更好的语义理解和泛化能力。

## 与其他方法线的对比
| 维度 | VLM + Action Token (RT-2, OpenVLA) | VLM + Diffusion/Flow Head (π0系列) | Transformer + Diffusion Head (Octo) | 纯 Diffusion Policy (DP) |
|------|-------------------------------------|-------------------------------------|--------------------------------------|-------------------------------|
| 动作表示 | 离散 token | 连续向量（flow matching/diffusion） | 连续向量（DDPM diffusion） | 连续向量（diffusion） |
| VLM 预训练 | ✅ | ✅ | ❌ | ❌ |
| 高频控制 | ❌（离散化限制） | ✅（50Hz action chunk） | ✅（action chunk） | ✅（action chunk） |
| 语义泛化 | ✅ | ✅ | 有限（冻结T5） | ❌ |
| 多模态分布 | 有限（离散近似） | ✅（flow matching 天然支持） | ✅（diffusion 天然支持） | ✅（diffusion 天然支持） |
| 跨具身 | ✅ | ✅ | ✅ | ❌（单任务） |
| 微调灵活性 | 受限 | 受限 | **✅（模块化设计）** | N/A |
| 开源 | OpenVLA ✅ | Being-H0.5 ✅, Xiaomi-Robotics-0 ✅ | **Octo ✅** | **✅** |

## 技术源头：Diffusion Policy (2023, Columbia/TRI/MIT)
**首次将 DDPM 系统性引入机器人策略学习的奠基工作**

Diffusion Policy 确立了后续所有 diffusion/flow 方法线的核心设计范式：
- **条件化去噪**：观测作为条件注入（而非联合分布），视觉编码器只需前向一次
- **Action sequence + receding horizon**：联合预测多步动作保证时间一致性，执行前几步后重新规划
- **Position control 协同**：首次证明 diffusion policy + position control >> velocity control
- **训练稳定性**：score function 绕过 EBM 归一化常数问题

这些设计被 Octo 和 π₀ 直接继承和扩展。

→ 详见方法线 [diffusion_policy.md](diffusion_policy.md) 和论文卡片 [papers/diffusion_policy_2023.md](../papers/diffusion_policy_2023.md)

## 前身工作：Octo (2024, UC Berkeley)
**首个在跨具身 GRP 中验证 diffusion head 优越性的开源工作**

Octo 不使用预训练 VLM，但其 diffusion head + action chunking + transformer backbone 的设计直接影响了 π₀ 的架构选择。Octo 的关键发现——diffusion head 大幅优于 MSE 和 discrete head（83% vs 35% vs 18%）——为 π₀ 采用 flow matching 提供了实验依据。

→ 详见方法线 [transformer_diffusion_head.md](transformer_diffusion_head.md) 和论文卡片 [papers/octo_2024.md](../papers/octo_2024.md)

## 奠基工作：π0 (2024, Physical Intelligence)
**首次将 VLM 与 flow matching 结合为 VLA**

### 架构设计
- **双 expert transformer**：VLM backbone (PaliGemma 3B) + Action expert (300M)
  - 两组权重共享 attention 层（通过 self-attention 交互），但 FFN 独立
  - Action expert 处理本体状态 + 噪声动作 token
- **Transfusion 风格混合训练**：文本 token 用 cross-entropy，动作 token 用 flow matching loss
- **Blockwise causal attention mask**：保护 VLM 预训练分布不被新 token 污染
- **Flow matching 细节**：
  - Linear-Gaussian (optimal transport) 路径
  - 10 步 Euler 积分推理
  - 自定义 beta 分布采样时间步（偏向高噪声，与图像生成不同）
- **Action chunking**：H=50 步，支持 50Hz 控制

### 关键设计决策及其理由
1. **为什么用 flow matching 而非自回归？** 高频 action chunk (50 步 × 18 维) 的离散化会导致巨大的 token 序列和精度损失
2. **为什么用 action expert 而非直接在 VLM 上加 MLP head？** 独立权重避免 VLM backbone 被动作训练破坏，实验证明性能更好
3. **为什么时间步采样偏向高噪声？** 机器人观测对动作的约束远强于文本对图像的约束，低噪声时预测更难（不是简单的恒等映射）

→ 详见论文卡片 [papers/pi0_2024.md](../papers/pi0_2024.md)

## 后续发展

### π0.5 (2025, Physical Intelligence)
在 π0 基础上增加：
- 统一模型内的层次化推理（高层文本 token + 低层 flow matching 动作）
- 预训练用 FAST discrete token → 后训练加 flow matching 的两阶段设计
- 5 类异构数据 co-training 实现 open-world 泛化
→ 详见 [papers/pi05_2025.md](../papers/pi05_2025.md)

### Being-H0.5 (2026, BeingBeyond) — 跨具身泛化方向的代表
在 π₀ 系列基础上走出差异化路线：
- **人类中心学习**：16K 小时 egocentric 人类视频作为"物理母语"预训练
- **统一动作空间**：将人手 MANO 和 30 种机器人映射到物理语义对齐的共享槽位（vs π₀.5 的独立 MLP 头）
- **Mixture-of-Flow (MoF)**：共享基础专家（通用运动原语）+ Top-K 路由特化专家（具身特定），解决 flow-based VLA 的容量瓶颈
- **流形保持门控 (MPG)**：SWD 衡量上下文可靠性，门控 feature residual + 无门控先验偏置，解决分布偏移下的动作抖动
- **通用异步分块 (UAC)**：训练时随机延迟采样 + 推理时双线程异步，单一检查点适配不同机器人的控制频率/延迟
- **VLM backbone**：InternVL-3.5（vs π₀ 的 PaliGemma）
- **开源**：模型权重、训练管线、部署基础设施全部开源
- **结果**：LIBERO 98.9%, RoboCasa 53.9% SOTA；5 种真机平台跨具身泛化显著优于 π₀.5
→ 详见 [papers/being_h05_2026.md](../papers/being_h05_2026.md)

### Xiaomi-Robotics-0 (2026, Xiaomi) — 实时部署方向的代表 🆕
聚焦 VLA 实时异步执行的工程优化：
- **两阶段预训练**：(1) VLM + Choice Policies 学动作预测 + VL co-training 防遗忘；(2) 冻结 VLM，训 16 层 DiT（flow matching）
- **Λ-shape attention mask**（核心贡献）：解决 Training RTC 的 action prefix shortcut——紧邻前缀的 token 可看到前缀（保证过渡平滑），后续 token 不可见前缀（强制关注视觉/语言，保持反应性）
- **消费级 GPU 部署**：RTX 4090 上 80ms（5 步 flow-matching），30Hz 异步执行
- **VLM backbone**：Qwen3-VL-4B-Instruct（4.7B 总参数）
- **开源**：预训练/后训练检查点 + 推理代码
- **结果**：LIBERO 98.7%, CALVIN 4.80/4.75, SimplerEnv 85.5%/74.7%/79.2% 全面 SOTA
→ 详见 [papers/xiaomi_robotics_0_2026.md](../papers/xiaomi_robotics_0_2026.md)

### RDT (Robotics Diffusion Transformer)
- 用 diffusion transformer 架构做跨具身机器人策略
- 类似思路但不基于 VLM backbone

### 与图像生成领域的联系
- **Transfusion** (Zhou et al. 2024)：单 transformer 混合自回归 + diffusion，π0 借鉴其混合损失设计
- **Playground v3** (Liu et al. 2024)：diffusion 部分用独立权重，π0 借鉴其 action expert 设计
- **Stable Diffusion 3** (Esser et al. 2024)：flow matching + rectified flow，π0 借鉴其 flow matching 路径选择
- **BAGEL** (2025)：MoT 架构用于图像理解+生成，Being-H0.5 借鉴其 MoT 设计原则

## 方法线演进脉络
```
Diffusion Policy (2023, 单任务BC, 条件DDPM+action sequence+receding horizon)
    ↓ 扩展到跨具身
Octo (2024, 无VLM, 93M, 开源, diffusion head继承自DP)
    ↓ 引入 VLM 预训练
π₀ (2024, PaliGemma + Flow, 3.3B, flow matching替代DDPM)
    ├── π₀.5 (2025, +层次化推理 + open-world, 闭源)
    │       ↑ 任务复杂度方向
    ├── Being-H0.5 (2026, +人类中心学习 + 统一动作空间 + MoF + 30具身, 开源)
    │       ↑ 跨具身泛化方向
    └── Xiaomi-Robotics-0 (2026, +Λ-shape mask异步执行 + 消费级GPU, 开源)
            ↑ 实时部署方向
```

## 异步执行技术演进 🆕
异步执行是 VLA 实时部署的关键问题。由于大参数量导致推理延迟（数百毫秒），同步执行时机器人会出现停顿。异步执行允许机器人在推理期间继续运动，但需要保证连续动作 chunk 之间的一致性。

### 技术演进线
```
RTC (Black et al. 2025): 推理时 inpainting，training-free 但效果有限
  → Training RTC (Black et al. 2025): 训练时 action prefix conditioning，提升一致性
    → Xiaomi-Robotics-0 (2026): Λ-shape attention mask 解决 shortcut，兼顾一致性与反应性
  → Being-H0.5 UAC (2026): 通用异步分块，随机延迟采样+双线程，适配多种控制频率
```

### Action Prefix Shortcut 问题
Training RTC 将前一次推理的已提交动作作为 clean prefix 拼接在 noisy action 之前。这保证了时间一致性，但引入了 **shortcut 问题**：后续时间步的动作预测可以利用连续动作之间的时序相关性，简单"复制"前缀而非关注视觉/语言输入，导致策略反应性下降。在 Towel Folding 等需要反应性纠错的任务中，表现为陷入重复循环。

### Λ-shape Attention Mask（Xiaomi-Robotics-0 提出）
一种针对 DiT 中 action prefix conditioning 的注意力掩码设计：
- 紧邻前缀的 noisy action token 可以 attend to clean prefix → 保证过渡平滑
- 后续 noisy action token 不能 attend to clean prefix → 强制关注视觉/语言信号
- 配合 RoPE 位置偏移（+10）区分 clean vs noisy token
- 配合动态 loss 重加权（基于 L1 误差优先纠正大偏差）

## π₀.5 vs Being-H0.5 vs Xiaomi-Robotics-0 对比 🆕
| 维度 | π₀.5 (2025) | Being-H0.5 (2026) | Xiaomi-Robotics-0 (2026) |
|------|-------------|-------------------|--------------------------|
| **核心方向** | 开放世界长时序任务泛化 | 跨具身泛化 | 实时部署效率 |
| **具身多样性** | ~10 种 | 30 种 | 1 种（双臂） |
| **异步执行** | 简单异步 | UAC（通用异步分块） | Λ-shape mask（解决 shortcut） |
| **层次化推理** | ✅ | ❌ | ❌ |
| **VL 能力保留** | 部分（多数 benchmark 近零） | 未重点评测 | ✅（几乎匹配原始 VLM） |
| **VLM backbone** | PaliGemma (Gemma 2B) | InternVL-3.5 | Qwen3-VL-4B |
| **推理延迟** | 未公开 | 未公开 | 80ms (RTX 4090) |
| **LIBERO** | 96.9% | 98.9% | 98.7% |
| **开源** | ❌ (OpenPi 微调代码) | ✅ | ✅ |

## 方法线总结
VLM + Diffusion/Flow Head 是当前 VLA 领域最有前景的方法线之一，其核心优势在于：
1. 继承 VLM 的互联网级语义知识（语言理解、视觉识别、常识推理）
2. 通过 flow matching/diffusion 精确建模连续动作分布（技术传承自 Diffusion Policy）
3. 支持高频 action chunking，适合灵巧操作（源自 Diffusion Policy 的 action sequence prediction）
4. 天然支持多模态动作分布（同一观测可能对应多种合理动作，Diffusion Policy 首次验证）

**2025-2026 的发展趋势**：该方法线正在分化为三个互补方向：
- **任务复杂度方向**（π₀.5）：层次化推理、开放世界泛化、长时序多阶段任务
- **跨具身泛化方向**（Being-H0.5）：统一动作空间、人类中心学习、30+ 具身支持、开源
- **实时部署方向**（Xiaomi-Robotics-0）：异步执行优化、VL 能力保留、消费级 GPU 部署、开源 🆕
