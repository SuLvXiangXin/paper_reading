# Latent Action Pretraining 方法线

## 核心思路
从无动作标注的视频中自动发现和编码"潜在动作"（latent actions），用这些潜在动作预训练 VLA 模型，最后在少量有标注机器人数据上微调映射到真实动作空间。打破了 VLA 预训练必须依赖动作标签的核心假设。

## 代表工作
| 模型 | 年份 | 参数量 | VLM backbone | 开源 | 关键特点 |
|------|------|--------|-------------|------|----------|
| **LAPA** | **2024 (ICLR 2025)** | **7B** | **LWM-Chat-1M** | ✅ | **首个无标注视频VLA预训练，VQ-VAE潜在动作，超越OpenVLA** |

## 三阶段训练流程

### 阶段一: Latent Action Quantization
用 VQ-VAE 从帧对 (x_t, x_{t+H}) 中学习离散潜在动作 z_t。

**架构**: C-ViViT 变体（~300M 参数）
- **编码器**: Patch Embedding → Spatial Transformer → Causal Transformer → CNN → Vector Quantization
  - 输入两帧 → 各自 patch embedding → spatial transformer → causal transformer 获得 e1, e2
  - 差值 d1 = e2 - e1 → 最近邻量化为 codebook token
- **解码器**: Cross Attention(sg[p1], z_t) → Spatial Transformer → 重建 x_{t+H}
  - **关键**: 对 x_t 的 patch embedding 施加 stop gradient，防止表征坍塌
  - **改进**: 用 cross attention（而非 GENIE 的 additive embedding）融合 z_t 和 x_t
- **训练目标**: L2 重建损失
- **防梯度坍塌**: NSVQ（噪声替代向量量化）+ 早期 codebook 替换

**潜在动作空间**:
- 表示为 s 个 token 的序列，每个 token 来自大小 |C| 的 codebook
- 默认: s=4, |C|=8 → 8^4 = 4096 种离散动作组合
- 总生成空间 8^4 = 4096，远小于 OpenVLA 的 256^7 ≈ 7.2×10^16

**双重角色**:
- 编码器 = 逆动力学模型（IDM）：从帧对提取动作
- 解码器 = 世界模型：给定当前帧和动作，预测未来帧

### 阶段二: Latent Pretraining
用阶段一编码器标注所有视频 → VLM 做行为克隆预测潜在动作。

- 在 VLM 上添加独立的 latent action head（单层 MLP, vocab |C|）
- 输入: 语言指令 + 当前图像 x_t → 输出: 潜在动作 z_t
- 冻结视觉编码器，解冻语言模型
- **不需要任何真实动作标签**

### 阶段三: Action Finetuning
在少量有标注轨迹上微调，学习潜在动作→真实动作的映射。

- **丢弃** latent action head，替换为新 action head
- 连续动作等频分箱离散化为 256 bin（同 RT-2/OpenVLA）
- 冻结视觉编码器，解冻语言模型

## 关键技术洞察

### 潜在动作作为通用"动作 tokenizer"
类比 NLP 中 BPE tokenizer 将文本切分为 subword：
- BPE: 从语料库统计中自动学习 subword 词表，不需要语言学先验
- Latent Actions: 从视频帧对中自动学习动作词表，不需要动力学先验（如关节角度、末端位姿）
- 核心优势: 动作粒度由数据驱动，而非人为预定义

### 跨具身共享潜在动作空间
实验证明（Figure 6）：即使具身形态和环境不同，同一潜在动作对应语义相似的运动（如 [1,1,3,2] = 向下向左，[3,2,0,1] = 向上）。这意味着：
- 潜在动作空间自然支持跨具身预训练
- 不需要 Octo/OpenVLA 那样的零填充对齐
- 避免了对特定具身形态动作空间的过拟合

### 避免动作空间过拟合的优势
传统有标注预训练（OpenVLA, ActionVLA）直接学习特定具身形态的动作分布 → 跨具身微调时需要克服动作分布偏移。LAPA 预训练在具身无关的潜在空间中 → 微调时从"空白"状态学习目标动作空间，反而更灵活。

### 预训练效率来源
1. **更小的动作空间**: 8^4 = 4096 vs 256^7，预测任务更简单
2. **VLM backbone 优势**: LWM（Large World Model）预训练包含 next-frame prediction，隐式理解视频动态
3. **收敛快**: 单 epoch 即达最优（vs OpenVLA 需 27+ epochs）

## 与其他方法的关系

### vs VLM + Action Token (RT-2, OpenVLA)
| 维度 | Action Token | Latent Action |
|------|-------------|---------------|
| 预训练数据需求 | 必须有动作标签 | 不需要动作标签 |
| 动作离散化 | 手工等频分箱 | VQ-VAE 自动学习 |
| 跨具身处理 | 零填充对齐不同维度 | 统一潜在空间 |
| 预训练效率 | 低（21,500 A100-hours） | 高（272 H100-hours） |
| 精细操作 | 较好 | 较弱（抓取等） |
| 数据可扩展性 | 受限于有标注数据 | 可利用互联网规模视频 |

### vs World Model 流派C (UniPi)
| 维度 | UniPi (视频→IDM) | LAPA (潜在动作) |
|------|-----------------|-----------------|
| 利用无标注视频 | ✅ | ✅ |
| 需要生成视频帧 | ✅（计算昂贵、误差累积） | ❌（直接在潜在空间） |
| IDM 依赖 | 需训练独立 IDM | IDM 内嵌于 VQ-VAE 编码器 |
| 长时序规划 | 视频生成质量瓶颈 | 潜在动作更鲁棒 |
| 跨环境迁移 | 弱（视频分布敏感） | 强（潜在动作抽象化） |

### vs VPT (Video PreTraining)
| 维度 | VPT | LAPA |
|------|-----|------|
| IDM 训练 | 需要动作标签训练 IDM | 完全无监督（VQ-VAE） |
| 伪标签质量 | 依赖 IDM 精度 | 依赖 VQ-VAE 重建质量 |
| 跨环境鲁棒性 | 弱（IDM 不鲁棒） | 强（潜在动作抽象化） |

## 发展脉络
```
GENIE (2024, VQ-VAE 潜在动作用于交互式环境生成, 未用于机器人)
  │
  └── LAPA (2024, 将潜在动作扩展为 VLA 预训练方法, 首次超越有标注SOTA)
        │
        ├── Being-H0 系列 (2025-2026, 大规模人类视频 VLA 预训练)
        ├── JALA (2026, Joint-Aligned Latent Action, 更精细的人手动作编码)
        └── 未来: Web-scale Video → VLA Foundation Model
```

## 开放问题
1. **精细操作**: 如何在保持无标注预训练优势的同时提升抓取等精细动作能力？可能需要更大的潜在动作空间或层次化设计
2. **Internet 规模扩展**: LAPA 目前仅在 ~200k 视频上验证，扩展到百万/千万级互联网视频的效果如何？
3. **非操作视频**: 导航、自动驾驶、全身控制的视频是否也能通过潜在动作预训练？
4. **与 flow matching 结合**: 潜在动作预训练 + flow matching 动作生成（替代离散 token）能否同时获得无标注预训练和连续精细控制的优势？
5. **Action chunking**: 当前潜在动作对应单步转移，能否扩展到预测潜在动作序列实现 chunking？
