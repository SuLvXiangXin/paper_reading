# Image Generation 领域总览

## 领域简介

研究文本引导图像生成与编辑，聚焦扩散模型架构演进（U-Net → DiT → MM-DiT）及训练无关编辑方法。

## 架构演进

```
U-Net (SD1, SDXL)
  └─ 单向 cross-attention (text→image)

DiT (PixArt-α/σ)
  └─ 保留 cross-attention，引入 transformer 主干

MM-DiT (SD3, Flux.1)          ← 当前主流
  └─ 双向全注意力：text & image 拼接后统一 attention
  └─ 子块：I2I / T2I / I2T / T2T

MM-DiT-X (SD3.5-M)
  └─ 前 13 块额外加 image-only self-attention

MM-DiT* (Flux.1 单分支块)
  └─ text+image 共享权重，57块中后38块为此变体
```

## 主要模型参数一览

| 模型 | 架构 | 参数量 | 推理时间(1024px, 28步, A6000) |
|------|------|--------|------|
| SD1 | U-Net | 860M | 5.0s |
| SDXL | U-Net | 2.6B | 5.6s |
| SD3-M | MM-DiT | 2B | 7.1s |
| SD3.5-M | MM-DiT-X | 2.2B | 9.6s |
| SD3.5-L | MM-DiT | 8B | 24.7s |
| Flux.1-dev | MM-DiT* | 11.9B | 27.8s |

## 图像编辑方法分类

### 训练无关方法（Attention-based）
- **U-Net 时代**: Prompt-to-Prompt (P2P), MasaCtrl, Attend-and-Excite
- **MM-DiT 时代**: [本域首篇] mmdit_editing_2025 — q_i/k_i 替换 + T2I 局部混合

### 基于 Inversion 的方法
- DDIM Inversion, Null-text Inversion, RF Inversion (Rectified Flow)
- 与 attention-based 方法可叠加使用

### 需要训练的方法
- InstructPix2Pix, InstructDiffusion 等

## 子目录

- `papers/` — 论文卡片
- `methods/` — 方法分类深析
- `reports/` — 调研报告

## 关键概念速查

**MM-DiT 注意力块分解**（来自 mmdit_editing_2025）：
- **I2I**：图像自注意力，保留空间/几何信息
- **T2I**：text query × image key，类 cross-attention，可生成定位 mask
- **I2T**：image query × text key，新增，实验发现不如 T2I 精准
- **T2T**：文本内部注意力，近似单位矩阵，编辑时**不可修改**

**MM-DiT 规模缩放律**：模型越大，注意力定位越准但噪声越多（与 ViT register 论文一致）
