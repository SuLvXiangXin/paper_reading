# Latent Action 方法线：重建 vs 对齐

## 概述

Latent Action（潜在动作）是利用无动作标注视频进行VLA预训练的核心技术。核心思想：从视觉状态转变中提取隐含的动作信息，构建一个"潜在动作空间"，使VLA能够在没有显式动作标签的视频上学习操作先验。

这条方法线根据如何学习潜在动作空间，分为两大范式：

```
Latent Action 方法线
├── 重建范式 (Reconstruction-based)    — LAPA, UniVLA, IGOR
└── 对齐范式 (Alignment-based)         — JALA
```

---

## 范式A：重建式潜在动作 (Reconstruction-based)

### 核心思路
用 IDM（逆动力学模型）从当前帧和未来帧推断潜在动作 z，再用 FDM（前向动力学模型）从 z 和当前帧重建未来帧。FDM 的重建约束确保 z 编码了动作相关信息。

### 典型管线
```
(v_t, v_{t+1}) → IDM → z → VQ-VAE → ẑ（离散化）
(v_t, ẑ) → FDM → v̂_{t+1}（重建未来帧）
```
然后将离散化的 ẑ 作为 pseudo-label 训练 VLA 预测潜在动作 token。

### 代表工作
| 论文 | 年份 | 机构 | 核心特点 |
|------|------|------|----------|
| **LAPA** | 2024 | MSR+UW | 开山之作，VQ-VAE IDM + pixel reconstruction FDM |
| **UniVLA** | 2024 | — | 重建式 latent action + 大规模机器人数据联合预训练 |
| **IGOR** | 2024 | — | Image-goal representations 作为 atomic control units |
| **Video2Skill** | 2024 | — | 视频到技能的 latent action 提取 |

### 优势
- FDM 提供像素级密集监督
- 潜在动作经过 VQ-VAE 量化后可直接作为 token 使用

### 劣势
- **FDM 是瓶颈**: 对细粒度手部操作，精确重建未来帧非常困难
- **多阶段管线**: 先训 IDM+FDM → 提取 pseudo-label → 再训 VLA，复杂且慢
- **噪声积累**: FDM 重建质量直接影响潜在动作质量，野外视频的背景变化/遮挡使 FDM 更易受干扰
- **信息冗余**: 大量计算用于重建与动作无关的像素（背景、光照等）

---

## 范式B：对齐式潜在动作 (Alignment-based) — JALA

### 核心思路
完全绕过像素重建。VLA Transformer 的中间层 hidden state 作为 **predictive embedding**，通过 L1 损失与 IDM（Perceiver）推断的潜在动作 z 对齐。同时，当有动作标签时，VLA 输出层还预测真实动作 token（MCP）。

### 管线
```
(v_t, v_{t+δ}) → LAP (Perceiver) → z（潜在动作）
         ↕ L1 对齐
VLA context → hidden state → h（predictive embedding）
         ↓
MCP: h → predict action tokens（有标签时）
```

### 关键创新：联合对齐 (Joint Alignment)
- **Predictive embedding** 同时受两个约束：
  1. 向下：预测真实动作 token（当标签可用时）→ 编码动作语义
  2. 横向：与 IDM latent action 对齐 → 编码视觉动力学
- 无标签数据只有约束 2，有标签数据同时受约束 1+2
- 这构成了一个**统一的潜在动作空间**，自然支持异构数据混合训练

### 代表工作
| 论文 | 年份 | 机构 | 核心特点 |
|------|------|------|----------|
| **JALA** | 2026 | PKU+BeingBeyond | 首个对齐式 latent action，Perceiver IDM + decoupled EMA + hybrid masking |

### 优势
- **无需 FDM**: 完全绕过像素重建，更高效
- **单阶段训练**: 端到端联合训练，68小时 vs LAPA的86小时（同backbone/数据）
- **行为中心**: 对齐损失只关注动作相关的动力学信号，不浪费计算在背景像素上
- **野外视频鲁棒**: 不受背景噪声/遮挡对重建质量的影响
- **统一接口**: predictive embedding 同时连接预训练（token预测）和后训练（flow matching）

### 劣势
- **层选择敏感**: 第19层（共28层）最优，深层大幅下降
- **解耦EMA关键且脆弱**: 去掉后性能骤降至56.6%（从96.9%）
- **暂时仅在人手操作场景验证**: 通用性有待更多场景验证

---

## 两大范式对比

| 维度 | 重建范式 (LAPA等) | 对齐范式 (JALA) |
|------|-------------------|----------------|
| **FDM需求** | 必需（重建未来帧） | 无需 |
| **训练阶段** | 多阶段（IDM+FDM → pseudo-label → VLA） | 单阶段端到端 |
| **监督信号** | 像素级密集（含大量动作无关信息） | 动力学级稀疏（行为中心） |
| **野外视频适应性** | 差（FDM被背景噪声干扰） | 好（仅对齐边界帧动力学） |
| **训练效率** | 较低 | 较高（JALA比LAPA†省>20%时间） |
| **异构数据支持** | 有限（需先提取所有pseudo-label） | 天然支持（标签/无标签统一目标） |
| **实验对比** | LAPA†: LIBERO 83.5% | JALA: LIBERO 96.9% |
| **验证充分度** | 较多工作验证 | 目前仅JALA一项 |

## 与其他方法线的关系

- **与 World Model 流派C (视频→IDM) 的区别**: 流派C先生成完整视频再用IDM恢复动作（两阶段），Latent Action方法不生成视频而是直接从帧对提取latent action用于预训练
- **与 VLM + Action Token 的关系**: JALA预训练时用token预测，但latent action对齐是额外的监督信号
- **与 VLM + Flow Head 的关系**: JALA后训练时用flow matching head，predictive embedding作为条件输入

## 发展脉络
```
Video Pretraining (VPT, 2022) → Inverse Dynamics 思想
    ↓
LAPA (2024, 重建式 latent action, IDM + FDM + VQ-VAE)
    ├── UniVLA (2024, +机器人数据, 大规模)
    └── IGOR (2024, image-goal 表征)
    
    ←对比→
    
JALA (2026, 对齐式 latent action, predictive embedding + IDM alignment)
    └── 基于 Being-H0 (2025, 人手视频VLA预训练)
```
