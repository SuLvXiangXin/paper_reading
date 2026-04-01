# Context as Memory: Scene-Consistent Interactive Long Video Generation with Memory Retrieval (2025)

## 基本信息
- **作者**: Jiwen Yu*, Jianhong Bai*, Yiran Qin, Quande Liu†, Xintao Wang, Pengfei Wan, Di Zhang, Xihui Liu†
- **机构**: The University of Hong Kong + Zhejiang University + Kling Team, Kuaishou Technology（快手可灵）
- **arXiv**: 2506.03141
- **项目页**: https://context-as-memory.github.io/
- **发表时间**: 2025.06（v2: 2025.08）

---

## 一句话总结
将历史生成帧直接作为记忆，通过基于相机视野（FOV）重叠的检索模块选取相关帧，拼接至 DiT 输入实现场景一致的交互式长视频生成。

---

## 问题
**现有长视频生成方法缺乏长期记忆能力**：AR 方法（Diffusion Forcing、FramePack 等）只能利用时间窗口内的近期帧作为条件，一旦相机返回曾经访问的区域，场景内容会完全不同（如 Oasis 中简单左转再右转就产生截然不同的场景）。根本原因是这些方法只能感知"短期连续性"，缺乏将已生成内容显式存储并在需要时检索的机制。

---

## 方法

### 方法线归属
**长时一致性 → 帧级记忆（Frame-Level Memory）**

### 核心 Idea
把所有已生成帧视作动态增长的记忆库，利用相机位姿的 FOV 重叠关系从中检索真正相关的帧，将其与待预测帧一起沿帧维度拼接送入 DiT，无需任何额外模块即可实现长期场景一致性。

### 关键技术点

#### 1. Context-as-Memory 存储与条件化（Sec. 3.2）
- **存储格式**：直接存储 RGB 帧，无需特征嵌入提取或 3D 重建等后处理
- **条件化方式**：将 clean 上下文 latent $z_c$ 与 noisy 待预测 latent $z_t$ **沿帧维度拼接**，直接输入 DiT 的注意力计算
  - 无需额外 Adapter/ControlNet/Cross-Attention 等外挂模块
  - 天然支持可变长度上下文（长度随生成自动增长）
  - 预测时只更新 $z_t$，$z_c$ 保持不变
- **位置编码处理**：对预测帧保持预训练 RoPE 位置编码不变，对上下文帧分配新的位置编码，利用 RoPE 灵活处理可变长度序列

#### 2. Memory Retrieval — FOV 重叠检索（Sec. 3.3）
全量上下文计算面临三重问题：计算开销大、近邻帧高度冗余、无关帧引入噪声。提出基于相机轨迹的规则式检索：

**FOV 重叠检测**：
- 已知每帧的相机内外参（由相机控制模型的条件信号直接获得，无需估计）
- 将相机 FoV 简化为 XY 平面上的两条左右边界射线，检查两帧的四条射线之间的交叉情况
- 过滤相机距离过近（几乎重合）或过远（交叉点超出范围）的情况
- 所有帧间 FOV 重叠关系预计算，推理时无额外开销

**逐级过滤策略**（消融实验验证有效性）：
1. **FOV 过滤**（最关键）：仅保留与待预测帧有视野重叠的历史帧
2. **Non-adjacent 去冗余**（有效）：在连续帧序列中只随机保留一帧，消除相邻帧的高度冗余
3. **Far-space-time 补充**（效果有限）：额外补充时间/空间上最远的几帧，弥补可能遗漏的长程信息

**训练细节**：
- 训练时随机选取长视频中一段作为预测序列，从剩余帧中用 Memory Retrieval 选 $k-1$ 帧 + 预测段首帧（保连续性）= $k$ 帧上下文
- 10% 概率只用最近帧，模拟生成初期无历史上下文的情况

#### 3. 基础模型与相机控制（Sec. 3.1）
- **基础模型**：1B 参数 DiT + Causal 3D VAE（时间压缩比4，77帧→20 latents），内部研发的文生视频模型（类似 Kling）
- **相机控制**：参照 ReCamMaster，相机外参 $[R,t] \in \mathbb{R}^{f \times 12}$ 经 MLP encoder 映射后叠加到空间注意力输出
- **生成分辨率**：640×352，77帧/段

#### 4. UE5 数据集构建（Sec. 3.4）
- 无公开长视频+相机标注数据集，用 Unreal Engine 5 渲染
- 100 条视频 × 7601帧（约 253 秒@30fps），12 种场景风格
- 相机轨迹：随机采样端点生成 B-spline 曲线，移动限制在 XY 平面，每段旋转<60°
- 每 77 帧用多模态 LLM（MiniCPM-V）自动标注 caption

---

## 实验

### Baselines
在同一基础模型 + 数据集 + 训练配置下公平比较：
1. **1st Frame as Context**：仅用第一帧作条件
2. **1st Frame + Random Context**：第一帧 + 随机历史帧
3. **DFoT（Diffusion Forcing Transformer）**[Song et al. 2025]：用固定窗口内最近帧
4. **FramePack**[Zhang & Agrawala 2025]：层次压缩历史帧为2帧

### 评测设计（新颖点）
由于无标准记忆评测方案，提出两种评测协议：
- **Ground Truth Comparison**：从 GT 帧中选上下文，评测预测帧与 GT 的一致性（PSNR/LPIPS）
- **History Context Comparison（更强）**：相机"旋转离开再旋转回来"，对比新生成帧与历史生成帧，直接测量模型自身的记忆能力

### 主要结果（Table 1）

| 方法 | GT: PSNR↑ | GT: LPIPS↓ | HC: PSNR↑ | HC: LPIPS↓ |
|------|-----------|------------|-----------|------------|
| 1st Frame only | 15.72 | 0.5282 | 14.53 | 0.5456 |
| + Random Context | 17.70 | 0.4847 | 17.07 | 0.3985 |
| DFoT | 17.63 | 0.4528 | 15.70 | 0.5102 |
| FramePack | 17.20 | 0.4757 | 15.65 | 0.4947 |
| **Context-as-Memory（ours）** | **20.22** | **0.3003** | **18.11** | **0.3414** |

**关键发现**：
- C-a-M 在所有指标上显著领先（PSNR +2.5dB vs 最佳 baseline）
- **随机上下文反而优于 DFoT 和 FramePack**：原因是后者仅利用最近帧，相邻帧冗余大，有效信息少；随机选择反而平均覆盖了更多样的历史内容
- FramePack 的指数衰减压缩进一步损失了关键信息

### 消融实验（Table 2, 3）

**Context Size 消融**（Table 2）：
- Size=1 vs Size=20：PSNR 从 15.72→20.22（GT），速度从 1.60→0.97 fps
- Size=20 是性能与速度的最优折中点（size=30 性能边际收益微小但速度代价大）

**Memory Retrieval 策略消融**（Table 3）：
- Random → FOV+Random → FOV+Non-adj → FOV+Non-adj+Far：
  - PSNR: 17.70 → 19.17 → 20.11 → **20.22**
  - FOV 过滤和 Non-adj 去冗余贡献最大，Far-space-time 影响有限

### 开域泛化（Fig. 6, 8, 9）
- 用互联网图片（日本风景、Black Myth Wukong、The Legend of Zelda 等）作为初始帧
- "旋转离开再旋转回来"轨迹验证记忆一致性
- 结果：在训练集未见风格/场景上表现良好

---

## 与相关工作对比

| 工作 | 记忆存储 | 检索方式 | 条件注入 | 额外模块 | 验证场景 |
|------|---------|---------|---------|---------|---------|
| **WorldMem** | 帧+状态 | Memory bank + attention | Cross-Attention | 需要 | Minecraft (~10s) |
| **VMem** | Surfel 索引 | 3D 几何 | — | 需要 3D | — |
| **SPMem** | 显式 3D 存储 | 3D 锚定 | — | 需要 3D | — |
| **Context-as-Memory** | 原始 RGB 帧 | FOV 重叠（规则式） | 帧维度拼接 | **无需** | 多样场景+开域 |

**vs WorldMem**：WorldMem 用 cross-attention 注入记忆，需要额外模块；C-a-M 直接拼接，更简洁且支持更多样的场景（WorldMem 仅验证 Minecraft 约 10s）。

**vs FramePack**：FramePack 的层次压缩导致远端历史指数级信息损失；C-a-M 保留原始分辨率帧，通过相关性筛选保持信息量。

**vs DFoT**：DFoT 固定窗口近邻帧条件，相邻帧冗余高；C-a-M 从全局历史检索，突破时间窗口限制。

---

## 评价

### 优势
1. **极简设计**：无需 3D 重建、特征嵌入、额外 Adapter/Cross-Attention 等，直接帧级拼接
2. **物理直觉清晰**：FOV 重叠是判断"需要看同一区域"的充分条件，规则式检索无需学习
3. **开域泛化强**：基础模型预训练先验 + 多样 UE5 场景训练，泛化到未见风格
4. **评测设计有价值**：History Context Comparison 协议对记忆能力的评估更严格，可被领域复用
5. **数据构建方法论**：利用游戏引擎构建精准标注长视频数据集，为领域提供方法参考

### 局限
1. **仅支持静态场景**：动态物体/角色的记忆处理尚未解决
2. **FOV 检索在遮挡复杂场景失效**：如多房间相互连通的室内场景
3. **相机运动限制在 XY 平面**：训练数据只覆盖平面移动+绕Z轴旋转，复杂3D轨迹未验证
4. **误差累积固有问题**：长视频生成中的累积误差尚需更大数据/模型解决
5. **1B 基础模型能力受限**：复杂开域场景下基础模型质量是瓶颈
6. **UE5 数据 → 真实域 gap**：渲染数据与真实视频存在视觉差异

### 对视频世界模型领域的贡献
1. **确立了"帧级直接存储+拼接"作为记忆机制的简洁范式**，对比 3D 重建类方法展现了设计上的帕累托优越性（简单、有效、通用）
2. **FOV 重叠检索**将相机控制信号（已有条件）复用为记忆检索依据，是"免费获得的先验"的良好利用示例
3. **提出记忆评测协议**（GT Comparison + History Context Comparison），为后续工作提供标准化评测框架
4. **揭示了相邻帧冗余问题**：DFoT/FramePack 仅利用近邻帧的策略在记忆任务上反而不如随机选取，这一反直觉发现对领域有指导意义
