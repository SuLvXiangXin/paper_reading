# VLM + Action Token 方法线

## 核心思路
将预训练 VLM 直接微调为机器人策略，将连续动作离散化为 token，复用 VLM 的 next-token prediction 框架输出动作。

## 代表工作
| 模型 | 年份 | 参数量 | VLM backbone | 开源 | 关键特点 |
|------|------|--------|-------------|------|----------|
| **RT-2** | **2023** | **12B/55B** | **PaLI-X / PaLM-E** | ❌ | **首个 VLA，定义了"动作即语言"范式，提出 co-fine-tuning 策略，证明 VLM 预训练知识可迁移到机器人控制** |
| RT-2-X | 2023 | 55B | PaLI-X | ❌ | RT-2 + Open X-Embodiment 数据，co-train with Internet data |
| **OpenVLA** | 2024 | 7B | Prismatic (SigLIP+DINOv2+Llama2) | ✅ | 首个开源通用 VLA，7B 超越 55B RT-2-X |
| RFM-1 | 2024 | 未公开 | 未公开 | ❌ | Covariant 的闭源 VLA |

## 技术要点

### 动作离散化
- 每维动作独立量化为 256 个 bin
- **RT-2（奠基方案）**: 连续维度均匀分 256 bin，动作表示为字符串 `"terminate Δpos_x Δpos_y Δpos_z Δrot_x Δrot_y Δrot_z gripper"` → 如 `"1 128 91 241 5 101 127"`
- OpenVLA 改进: 用 1st-99th 百分位数替代 min-max，避免离群值影响
- 离散化后映射到 LLM 词表中的 token

### 词表映射策略
- **RT-2-PaLI-X**: 直接使用数字 token（PaLI-X 对 0-1000 每个整数有独立 token）
- **RT-2-PaLM-E**: 覆盖 256 个最低频 token 作为动作词表（一种 symbol tuning）
- OpenVLA: 覆盖 Llama tokenizer 中最不常用的 256 个 token

### 输入/输出格式
- **RT-2 定义的 VQA 格式**: `"Q: what action should the robot take to [task instruction]? A:"` → 输出动作 token 字符串
- **输出约束**: 推理时限制解码词表仅采样有效动作 token（RT-2 首创），保证输出可在真机执行

### 训练目标
- 标准 next-token prediction + cross-entropy loss
- 仅在 action token 上计算 loss（忽略 prompt token 的 loss）

### Co-training / Co-fine-tuning 策略
- **RT-2（首创）**: 同时在机器人数据和互联网 VL 数据上微调，保留预训练知识，防止灾难性遗忘
  - 消融验证: co-fine-tuning (63%) > fine-tuning only (52%) > from scratch (9%)（55B 模型未见任务）
  - RT-2-PaLI-X: 机器人数据约 50%；RT-2-PaLM-E: 约 66%
- RT-2-X: 继承 co-fine-tuning，扩展到跨具身数据
- OpenVLA: 仅在机器人数据上微调（导致语义泛化弱于 RT-2-X），未采用 co-fine-tuning
- **后续发展**: π₀.5 将 co-training 扩展到 5 类异构数据源（机器人 + 高层语义 + 网络数据等），是 RT-2 co-fine-tuning 思想的进一步发展

### Chain-of-Thought 推理（RT-2 首次探索）
- 在输出动作前先生成自然语言计划: `"Plan: pick rxbar chocolate. Action: 1 128 124 ..."`
- 在单一 VLA 模型中首次统一高层规划和低层控制
- 后续发展为层次化 VLA（π₀.5 的高层子任务预测 + 低层动作生成）

## 优势
1. **架构极简**: 无需额外 action head，直接复用 VLM 的 autoregressive decoder
2. **直接继承 VLM 知识**: 预训练的视觉-语言对齐能力直接用于机器人控制，语言 grounding 能力强
3. **涌现能力**: RT-2 证明了符号理解、多语言、常识推理等能力可从互联网预训练"涌现"到机器人控制
4. **生态成熟**: 可直接使用 LLM 社区的训练/推理工具（FSDP, FlashAttention, LoRA, 量化等）
5. **扩展性好**: 理论上可以随 VLM 的进步直接受益

## 劣势
1. **离散化精度损失**: 256 bin 对高精度操作不够（如精细装配）
2. **不支持 action chunking**: 每步只预测一个动作，无法输出未来动作块，导致：
   - 高频控制困难（50Hz ALOHA 无法使用）
   - 动作不平滑，缺乏时序一致性
3. **推理速度受 LLM 限制**: 自回归逐 token 生成，7B 模型仅 ~6Hz；RT-2 55B 仅 1-3Hz
4. **高维动作空间困难**: N 维动作需 N 个 token，自回归 N 步推理
5. **不能迁移新运动技能**: VLM 预训练只迁移语义知识，物理技能仍受限于机器人训练数据

## 与其他方法线的对比

### vs VLM + Diffusion/Flow Head (π₀)
- Action Token: 简单直接，但离散精度有限，不支持 action chunking
- Flow Head: 连续动作更精确，支持高频 action chunk，但需额外 action expert 参数和 flow matching 训练
- π₀ 论文实验: 在灵巧任务上 flow matching 大幅超越 action token（OpenVLA 在 50Hz 任务上几乎无法工作）

### vs Transformer + Diffusion Head (Octo)
- Action Token: 有 VLM 预训练的语义知识，语言 grounding 更强
- Diffusion Head: 连续动作更精确，支持 action chunking，但缺乏 VLM 预训练
- OpenVLA 在多物体/多指令任务上优于 Octo，但 Octo 在精细操作上更好

## 发展脉络
```
RT-2 (2023.07, 首创VLA概念, 闭源, 12B-55B)
  ├── RT-2-X (2023, +跨具身OXE数据, 闭源)
  │     └── OpenVLA (2024.06, 开源替代, 7B超越55B RT-2-X)
  └── 暴露的局限（离散化精度、无action chunking）
        └── 推动 VLM + Flow Head 方法线（π₀, 2024.10）的出现
```

## 关键经验

### 来自 RT-2 论文
1. **Co-fine-tuning 至关重要**: 保留互联网数据可防止预训练知识遗忘，显著提升泛化
2. **预训练 >> 从头训练**: 大模型从头训练几乎无法泛化（5B from scratch: 9%）
3. **模型规模正相关泛化**: 55B > 5B，符合 scaling law
4. **VLM 预训练数据组成影响能力分布**: PaLM-E（更多数学训练）在数学推理上优于 PaLI-X（视觉为主）

### 来自 OpenVLA 论文
1. **视觉编码器必须微调**: 与 VLM 训练不同，VLA 训练中冻结视觉编码器性能大幅下降
2. **多 epoch 训练**: VLA 需要 27+ epochs（LLM/VLM 通常仅 1-2 epochs）
3. **SigLIP+DINOv2 融合**: 比单编码器在空间推理上更强，成为后续 VLA 研究的常见选择
4. **LoRA 足够**: rank=32 即可匹配全量微调性能，仅需 1.4% 参数
5. **4-bit 量化无损**: 推理显存从 17GB 降至 7GB，性能无损
