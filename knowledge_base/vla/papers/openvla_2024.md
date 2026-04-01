# OpenVLA: An Open-Source Vision-Language-Action Model (2024)

## 基本信息
- 作者: Moo Jin Kim*, Karl Pertsch*, Siddharth Karamcheti*, Ted Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov, Ethan Foster, Grace Lam, Pannag Sanketi, Quan Vuong, Thomas Kollar, Benjamin Burchfiel, Russ Tedrake, Dorsa Sadigh, Sergey Levine, Percy Liang, Chelsea Finn
- 机构: Stanford University, UC Berkeley, Toyota Research Institute, Google DeepMind, Physical Intelligence, MIT
- arXiv: 2406.09246
- 链接: https://openvla.github.io
- 开源: ✅ 完全开源（模型检查点、训练代码、微调 notebook、HuggingFace AutoModel 集成）

## 一句话总结
首个开源的 7B 参数通用 VLA 模型，基于 Prismatic VLM（SigLIP+DINOv2 融合视觉编码器 + Llama 2 7B）在 970k Open X-Embodiment 轨迹上微调，以 7x 更少参数超越闭源 RT-2-X (55B) 16.5% 绝对成功率，并首次系统探索 VLA 的参数高效微调（LoRA）和量化推理。

## 问题
VLA（将预训练 VLM 微调为机器人策略）展现了强大的泛化潜力（如 RT-2），但存在两大阻碍其广泛应用的问题：
1. **封闭不可获取**：现有最强 VLA（RT-2-X, RFM-1, Lingo-2）均为闭源，社区无法复现、修改或研究
2. **缺乏高效微调指南**：先前 VLA 工作不探索微调到新任务/机器人的方法，而这对实际部署至关重要——特别是在消费级 GPU 上的高效微调

**核心目标**：构建一个开源、高性能的通用 VLA，并提供完整的微调和部署工具链，使 VLA 像开源 LLM 一样可被社区广泛使用和研究。

## 方法
- **方法线归属**: VLM + Action Token（该方法线的代表性开源工作）
  - 与 RT-2 同属一条方法线：将动作离散化为 token，用 VLM 的 next-token prediction 直接输出
  - 与 Octo（Transformer + Diffusion Head）和 π₀（VLM + Flow Head）形成方法线对比
- **核心 idea**: 在强开源 VLM（Prismatic-7B，融合 SigLIP+DINOv2 视觉特征 + Llama 2 7B）上直接微调 robot action prediction，将连续动作离散化为 256 bin 的 token 映射到 LLM 词表，用标准 next-token prediction loss 训练。

### 关键技术点:

#### 1. 架构设计（Prismatic VLM backbone）
- **视觉编码器（600M）**: 融合 SigLIP + DINOv2 两个预训练编码器
  - 图像分别通过两个编码器，特征沿通道维拼接
  - SigLIP 提供高层语义特征，DINOv2 提供空间/几何特征
  - 相比 CLIP-only 或 SigLIP-only，融合编码器在空间推理上更强（实验验证比 LLaVA 高 10%）
- **投影器**: 2 层 MLP，将视觉特征映射到语言模型输入空间
- **LLM backbone**: Llama 2 7B
- **输入分辨率**: 224×224（实验发现 384×384 无性能提升但训练慢 3x）

#### 2. 动作离散化（Action Tokenization）
- 每维动作独立离散化为 256 个 bin（与 RT-2 相同策略）
- **改进**: 使用 1st-99th 百分位数而非 min-max 设置 bin 边界，避免离群值拉伸区间降低有效粒度
- **词表映射**: 覆盖 Llama tokenizer 中最不常用的 256 个 token（因 Llama 仅预留 100 个 special token，不够 256 个）
- 输出 N 维动作 = N 个离散 token，标准 next-token prediction + cross-entropy loss（仅在 action token 上计算 loss）
- 典型输出: 7D（Δx, Δy, Δz, Δroll, Δpitch, Δyaw, gripper）

#### 3. 训练数据（970k 轨迹）
- 基于 Open X-Embodiment 数据集精选
- **筛选标准**: 仅保留操作类数据集、至少有一个第三人称相机、单臂末端执行器控制
- **数据配比**: 基于 Octo 的混合权重（下调低多样性数据集，上调高多样性数据集）
- **DROID 数据**: 尝试加入（10% 权重），但 action token accuracy 持续偏低，最终在训练后 1/3 移除
- 27 个数据集（详见 Table 3），比 RT-2-X 的 350k 轨迹大近 3x

#### 4. 关键训练设计决策（小规模实验验证）
- **VLM 选择**: Prismatic > LLaVA > IDEFICS-1（Prismatic 因 SigLIP+DINOv2 在语言 grounding 任务上领先 10%+）
- **视觉编码器必须微调**: 与 VLM 训练的最佳实践相反——VLA 训练中冻结视觉编码器性能大幅下降（需要适应精细空间细节）
- **多 epoch 训练**: 与 LLM/VLM 的 1-2 epoch 不同，VLA 训练需 27 epochs 才能达到 >95% action token accuracy
- **学习率**: 固定 2e-5（与 VLM 预训练相同），无 warmup

#### 5. 参数高效微调（首次系统探索）
- **LoRA（推荐方案）**: rank=32，应用于所有线性层，仅训练 1.4% 参数
  - 性能匹配全量微调（68.2% vs 69.7%），VRAM 从 163GB 降至 60GB
  - 单卡 A100，10-15 小时，计算量降低 8x
- **Sandwich fine-tuning**: 仅解冻视觉编码器 + token embedding + 最后一层，VRAM 64GB
- **冻结视觉编码器**: 性能大幅下降（47%），说明视觉特征适应至关重要
- **仅微调最后一层**: 性能最差（30.3%）

#### 6. 量化推理
- **4-bit 量化（推荐）**: VRAM 从 16.8GB 降至 7GB，性能无损（71.9% vs 71.3%）
- **8-bit 量化**: 推理速度过慢（A5000 仅 1.2Hz），导致控制频率不匹配，性能下降（58.1%）
- **关键洞察**: 性能下降不是因为量化精度损失，而是推理速度过慢改变了系统动力学

### 架构细节
| 组件 | 规模 |
|------|------|
| 视觉编码器 (SigLIP + DINOv2) | 600M |
| MLP 投影器 | 2 层 |
| LLM backbone (Llama 2) | 7B |
| **总参数** | **~7.6B** |
| 输入分辨率 | 224×224 |
| 训练硬件 | 64× A100, 14 天（21,500 A100-hours）|
| Batch size | 2048 |
| 推理速度 | ~6Hz (RTX 4090, bfloat16) |
| 推理显存 | 15GB (bfloat16), 7GB (int4) |

## 实验

### A. 开箱即用多机器人评测（vs RT-1-X, RT-2-X, Octo）

#### BridgeData V2 WidowX（17 个任务，170 rollouts）
- **评测维度**: 视觉泛化、运动泛化、物理泛化、语义泛化、语言 grounding
- **结果**:
  - OpenVLA **全面超越 RT-2-X (55B)**，除语义泛化外所有类别领先
  - RT-1-X 和 Octo 表现较差（尤其在有干扰物的场景中）
  - RT-2-X 在语义泛化上更强（因更大规模互联网预训练 + co-training 保留预训练知识）

#### Google Robot（12 个任务，60 rollouts）
- **结果**: OpenVLA 与 RT-2-X 表现相当，均显著优于 RT-1-X 和 Octo
- in-distribution: OpenVLA 88% vs RT-2-X 85%
- OOD: OpenVLA 44% vs RT-2-X 33.3%

#### 总计（29 个任务）
- **OpenVLA 超越 RT-2-X 16.5% 绝对成功率**，用 7B vs 55B（7x 更少参数）

### B. 数据高效微调评测（vs Diffusion Policy, Octo）
- **设置**: 7 个 Franka 任务（Franka-Tabletop + Franka-DROID），10-150 demonstrations
- **对比**: Diffusion Policy (full), Diffusion Policy (matched), Octo (fine-tuned), OpenVLA (fine-tuned), OpenVLA (scratch)
- **结果**:
  - **窄单指令任务**: Diffusion Policy 竞争力强或更优（动作更平滑精确）
  - **多指令多物体任务**: OpenVLA 显著领先（语言 grounding 能力强，+20.4% vs Diffusion Policy）
  - **总体**: OpenVLA 总成功率最高，是唯一在所有任务上均 >50% 的方法
  - **OpenVLA vs OpenVLA (scratch)**: 大规模机器人预训练带来明显提升，尤其在语言 grounding 任务上

### C. 参数高效微调
| 策略 | 成功率 | 训练参数 | VRAM |
|------|--------|----------|------|
| Full FT | 69.7% | 7,188M | 163GB (2×GPU) |
| LoRA r=32 | 68.2% | 97.6M | 59.7GB |
| Sandwich | 62.1% | 914M | 64GB |
| Frozen vision | 47.0% | 6,760M | 156GB |
| Last layer | 30.3% | 465M | 51.4GB |

### D. 量化推理
| 精度 | 成功率 | VRAM |
|------|--------|------|
| bfloat16 | 71.3% | 16.8GB |
| int4 | 71.9% | 7.0GB |
| int8 | 58.1% | 10.2GB |

### 主要 Benchmark
- 真机评测：BridgeData V2 WidowX（17 tasks）、Google Robot（12 tasks）、Franka-Tabletop（4 tasks）、Franka-DROID（3 tasks）
- 仿真：LIBERO（附录 E，90 个任务，微调评测）

## 评价

### 优势
1. **首个高性能开源通用 VLA**：填补了 VLA 领域的开源空白，提供了完整的训练/微调/部署工具链，对社区意义重大——类比 Llama 对 LLM 社区的意义
2. **强劲的开箱即用性能**：7B 参数超越 55B RT-2-X 16.5%，证明了好的 VLM backbone + 更大更干净的数据比单纯堆参数更重要
3. **融合视觉编码器的贡献**：SigLIP+DINOv2 的双编码器设计被实验验证在空间推理和语言 grounding 上优于单编码器，这一设计后来被广泛采用
4. **首次系统性探索 VLA 微调策略**：LoRA、量化推理、各种微调策略的系统对比，提供了实用的部署指南
5. **丰富的设计决策消融**：VLM backbone 选择、图像分辨率、视觉编码器冻结/微调、训练 epoch 数等经验对后续研究极有价值
6. **消费级 GPU 可用**：4-bit 量化仅需 7GB VRAM 推理，LoRA 微调仅需单卡 A100

### 局限
1. **仅支持单图像输入**：不支持多相机、本体感觉、观测历史——限制了在复杂真实场景中的应用（π₀/π₀.5 均支持多图像+本体感觉）
2. **不支持 action chunking**：每步仅预测一个动作 token 序列，无法像 Diffusion Policy/π₀ 那样预测未来动作块，导致：
   - 高频控制场景（如 ALOHA 50Hz）无法使用
   - 灵巧操作任务中动作不够平滑
   - π₀ 论文中明确指出这是 OpenVLA 在灵巧任务上表现差的主要原因
3. **离散化动作精度有限**：256 bin 的离散化不可避免地损失精度，对精细操作不友好（相比 flow matching 的连续动作生成）
4. **推理频率较低**：~6Hz (RTX 4090)，7B 模型的自回归推理较慢
5. **语义泛化弱于 RT-2-X**：因仅在机器人数据上微调（不与互联网数据 co-train），预训练 VLM 的语义知识部分遗忘
6. **可靠性不够高**：多数任务成功率 <90%，距离实际部署还有差距
7. **无 co-training with Internet data**：RT-2 通过同时在机器人数据和互联网 VL 数据上训练来保留预训练知识，OpenVLA 未采用此策略

### 对 VLA 领域的贡献
1. **开源生态建设**：OpenVLA 是 VLA 领域最重要的开源工作之一，直接使得后续大量研究可以在其基础上迭代（类似 Octo 对 GRP 领域的贡献）
2. **验证了 VLM + Action Token 方法线的竞争力**：用远小于 RT-2-X 的模型实现更好性能，说明方法线本身可行，问题在于具体实现细节
3. **SigLIP+DINOv2 融合编码器的推广**：这一设计成为后续 VLA 研究中的常见选择
4. **VLA 微调的 baseline**：首次建立了 VLA 微调的系统性评估框架和 baseline，后续工作（如 π₀ 的微调实验）均以 OpenVLA 为重要对比基线
5. **实用性指南**：LoRA 微调、4-bit 量化推理等实践为 VLA 的实际部署提供了路线图
6. **暴露了 Action Token 方法线的瓶颈**：不支持 action chunking、离散化精度损失等问题被后续工作（π₀ 的 flow matching）直接针对并解决

### 与其他工作的关系
- **vs RT-2-X**: 同属 VLM + Action Token 方法线，但 OpenVLA 开源、更小（7B vs 55B）、性能更好（+16.5%）；RT-2-X 在语义泛化上更强（co-training 保留预训练知识）
- **vs Octo**: Octo 是 Transformer + Diffusion Head（93M），OpenVLA 是 VLM + Action Token（7B）；OpenVLA 因 VLM 预训练在语言 grounding 和泛化上更强，但 Octo 的 diffusion head 在动作精度上有优势
- **vs π₀**: π₀ 在 OpenVLA 基础上解决了其核心局限——用 flow matching 替代离散化，支持 action chunking 和高频控制，在灵巧任务上大幅超越 OpenVLA。π₀ 论文中 OpenVLA 作为重要基线被比较
- **vs Diffusion Policy**: 在窄任务上 Diffusion Policy 更精确（action chunking + 连续动作），在多物体/多指令任务上 OpenVLA 更强（VLM 预训练的语言 grounding）
- **时间线定位**: Octo (2024.01) → OpenVLA (2024.06) → π₀ (2024.10)，OpenVLA 处于 VLA 从"小模型+diffusion"向"大 VLM+flow matching"过渡的中间阶段
