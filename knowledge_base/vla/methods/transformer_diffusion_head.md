# Transformer + Diffusion Head (Cross-embodiment Generalist Policy)

## 核心思想
不依赖预训练 VLM，直接用 ViT 风格 transformer backbone + diffusion action head 从大规模跨具身机器人数据训练通用策略。强调**灵活性**（支持多种输入/输出配置）和**可微调性**（高效适配新域）。

## 与 VLM + Diffusion/Flow Head 方法线的对比
| 维度 | Transformer + Diffusion Head (Octo) | VLM + Diffusion/Flow Head (π₀) |
|------|-------------------------------------|-------------------------------|
| 视觉编码器 | 浅层 CNN patch encoder（从头训练）| 预训练 SigLIP 400M |
| 语言编码器 | 冻结 t5-base (111M) | VLM 内置 (Gemma 2B) |
| Transformer | ViT-B (93M)，从头训练 | PaliGemma (3B) + Action Expert (300M) |
| 动作生成 | DDPM Diffusion (20步) | Flow Matching (10步 Euler) |
| 预训练数据 | 800k OXE 轨迹 | 10,000+ 小时自有 + OXE |
| 语义知识 | 无互联网级预训练 | VLM 带来丰富语义知识 |
| 模型规模 | 93M | 3.3B |
| 开源 | ✅ 完全开源 | ❌ |

## 奠基工作：Octo (2024, UC Berkeley)

### 架构设计
- **Transformer-first**：参数集中在 transformer backbone（非 ResNet），轻量 CNN 做 patch 编码
- **模块化 token 化**：
  - 任务 token（语言 / 目标图像）
  - 观测 token（多相机 + 本体感知）
  - Readout token（类似 [CLS]，被动聚合信息，不影响其他 token）
- **Block-wise masked attention**：
  - 观测 token 因果 attend 同时/更早步 + 任务 token
  - 缺失模态完全 mask
  - Readout token 可读不可被读
- **Diffusion action head**：轻量 3 层 MLP，DDPM 目标，20 步去噪
  - 只需 transformer 前向一次，去噪全在 head 内完成
  - 预测 action chunk

### 核心创新：微调灵活性
通过模块化设计，微调时可以：
- 添加新传感器：只需新 tokenizer + 位置编码
- 改变动作空间：只需新 action head
- 不修改预训练 transformer 权重
这是 Octo 相比 RT-1/RT-2/ViNT 等先前 GRP 的最大差异化优势。

### 关键实验发现
1. Diffusion head >> MSE head >> Discrete head（在跨具身 GRP 中）
2. ViT-first > ResNet-heavy（大数据集上）
3. 更多数据集 > 少数据集 > 单机器人数据
4. 模型规模正相关性能
5. 本体感知输入可能有害（因果混淆）
6. 数据 shuffle 对多数据集训练至关重要

→ 详见论文卡片 [papers/octo_2024.md](../papers/octo_2024.md)

## 后续发展
- **π₀ (2024)**：在 Octo 基础上引入预训练 VLM (PaliGemma) + flow matching action expert，实现质的飞跃。可视为 Octo 的 "VLM 升级版"
- **RDT (Robotics Diffusion Transformer)**：类似思路，用 diffusion transformer 做跨具身策略
- **OpenVLA**：走了不同路线（VLM + discrete action token），与 Octo 形成对比

## 方法线定位
这一方法线是 VLA 领域发展的重要中间阶段：
- 验证了 diffusion head + cross-embodiment 预训练 + action chunking 的组合价值
- 证明了模块化设计对灵活微调的重要性
- 为后续 VLM + Diffusion/Flow Head 方法线（π₀系列）奠定了技术和实验基础
- 但缺乏 VLM 预训练的语义知识限制了其零样本泛化上限
