# 长时渲染质量：Forcing 家族方法分类

> 子方向：长时间序列渲染稳定性，核心挑战是 exposure bias / train-test gap 导致的误差累积

---

## 技术路线概述

Forcing 家族的核心问题是：自回归视频生成中，推理时每帧条件于**自己之前生成**的帧，而训练时条件于**ground truth**帧，这种 train-test 分布差异（exposure bias）导致推理时误差积累，表现为画面过曝、静止、暗化乃至崩溃。

**技术演进主线**：
```
Professor Forcing (2016, 654引用)   — 训练时使用自生成样本消除 exposure bias（首提概念）
  └─ Diffusion Forcing (2024, 374引用) — 帧级异构噪声调度的 AR 视频生成
       └─ CausVid (2024.12, 180引用)   — 双向→因果蒸馏 + DMD，实现流式生成
            └─ Self-Forcing (2025.06, 189引用) ⭐ 奠基之作  [→论文卡片](../papers/self_forcing_2025.md)
                 ├─ Self-Forcing++ (2025.10)  — 滑窗蒸馏解锁分钟级生成
                 ├─ Rolling Forcing (2025.09)  — 联合多帧去噪 + attention sink
                 ├─ Reward Forcing (2025.12)  — 奖励蒸馏 + EMA-Sink
                 ├─ Resampling Forcing (2025.12) — teacher-free 自重采样
                 ├─ LongLive (2025.09) ⭐    — KV-recache + streaming long tuning + 交互式生成 [→论文卡片](../papers/longlive_2025.md)
                 ├─ Memory Forcing (2025.10)   — 时空记忆 (见 long_consistency.md)
                 └─ Geometry Forcing (2025.07) — 3D 对齐 (见 long_consistency.md)
```

---

## 各方法详解

### 1. Self-Forcing (2025.06) ⭐ [→完整论文卡片](../papers/self_forcing_2025.md)
- **arXiv**: 2506.08009 | **引用**: 189 | **机构**: Adobe Research + UT Austin | **发表**: NeurIPS 2025
- **核心 idea**: 训练时直接执行 AR self-rollout（不用 GT 帧），以自生成帧作为 context，用 holistic 视频级分布匹配损失（DMD/SiD/GAN）从根本上消除 exposure bias
- **关键技术**:
  1. **Self-Rollout + 训练时 KV caching**：训练与推理结构完全对齐，无需特殊 attention mask，可使用 FlashAttention-3
  2. **少步扩散（4步）+ 随机步数采样**：每次从 [1,T] 随机选一步 s 用于输出，兼顾效率与全步监督
  3. **随机梯度截断**：仅对最终去噪步计算梯度，KV cache 梯度也被截断，控制内存消耗
  4. **Rolling KV Cache**：O(TL) 复杂度支持无限长视频；训练时限制最后帧不 attend 第一帧，模拟 rolling 条件
  5. **Holistic 分布匹配**：DMD/SiD/GAN 三种目标均可，对比 TF/DF 的逐帧 MSE
- **实验结果**：chunk-wise 17 FPS + 0.69s 延迟 + VBench Total 84.31（超越慢速双向 Wan2.1 的 84.26）
- **明确指出 CausVid 缺陷**：CausVid 训练时 DMD 匹配的是 Diffusion Forcing 输出的分布，而非真实推理分布，导致优化目标错误
- **局限**: 超出训练上下文长度（≤5s）后质量下降；梯度截断限制长程学习

### 2. CausVid (2024.12) [→完整论文卡片](../papers/causvid_2024.md)
- **arXiv**: 2412.07772 | **引用**: 180 | **机构**: MIT CSAIL + Adobe Research | **录用**: CVPR 2025
- **核心 idea**: 非对称蒸馏——双向 teacher 监督因果 student，block causal attention + KV cache
- **局限**: 依赖重叠帧保持时序一致，引入 over-exposure 伪影；train-test 失配（Self-Forcing 明确指出此问题）

### 3. Self-Forcing++ (2025.10) 📄 [→完整论文卡片](../papers/self_forcing_plus_plus_2025.md)
- **arXiv**: 2510.02283 | **引用**: 59 | **机构**: UCLA + ByteDance Seed
- **核心 idea**: 让学生先生成长视频（刻意产生误差积累），再用短视频 teacher 在滑动窗口上做 Extended-DMD 蒸馏，使学生学会从退化状态恢复
- **关键技术**:
  1. **Backward Noise Initialization**: 对长视频自生成 latent 重新加噪，保证时序依赖在噪声空间中得以保持
  2. **Extended-DMD（滑动窗口蒸馏）**: $i \sim \text{Unif}\{1,...,N-K+1\}$ 均匀采样窗口，teacher 对任意短窗口的评判等价于对长视频质量的约束
  3. **Rolling KV Cache（训推统一）**: 训练推理均用 rolling window（21 latent frames），彻底消除 train-test 失配，无需重叠帧和 attention sink
  4. **GRPO + 光流奖励**: 可选后处理，压制帧间突跳（光流方差 24.52→2.00）
  5. **Visual Stability 评测指标**: 揭露 VBench 评测偏差，用 Gemini-2.5-Pro 评分（0-100）
- **扩展性**: 训练预算 25× 可生成 255s（4min 15s），发现清晰 scaling law
- **局限**: 训练慢（self-rollout）、无长期记忆机制、不支持交互式 prompt 切换

### 4. LongLive (2025.09) ⭐ [→完整论文卡片](../papers/longlive_2025.md)
- **arXiv**: 2509.22622 | **引用**: 65 | **机构**: NVIDIA + MIT + HKUST(GZ) + HKU + THU（Song Han, Enze Xie, Yukang Chen）
- **核心 idea**: 帧级因果 AR 框架，通过 KV-recache 刷新 prompt 切换边界的 KV cache 语义，同时采用流式长训练和 frame-level attention sink，实现**实时交互式**长视频生成
- **关键技术**:
  1. **KV-Recache**：在 prompt 切换时，用已生成视频帧 + 新 prompt 重新计算 KV cache，既保留视觉连续性，又刷新 prompt 语义；训练时集成 recache 操作保证训推对齐
  2. **Streaming Long Tuning**：train-long–test-long 策略；逐 5s clip 滚动生成，detach 历史帧，仅对当前 clip 施加 teacher (Wan2.1-14B) DMD 监督；梯度局部化避免 OOM
  3. **短窗口注意力 + Frame Sink**：局部时间窗口降低计算复杂度；将第一帧 chunk 作为永久全局 anchor，拼接到所有层的 K/V；发现 attention sink 需在解决 train-test 失配后才能生效
  4. **LoRA 微调**：rank=256（约 27% 参数），兼顾效率与质量
- **实验结果**：20.7 FPS（最快）+ VBench Total 84.87（最高）+ VBench-Long Total 83.52（SOTA）；交互式 60s 视频比 SkyReels-V2 快 41×；32 GPU-days 训练代价
- **关键区分**：Forcing 家族中**唯一**同时支持流式交互 prompt 切换和高速（>17 FPS）推理的方法
- **重要发现**：attention sink 在未解决 train-test 失配时无效（纠正了 Self-Forcing 等工作的误解）

### 5. Rolling Forcing (2025.09)
- **arXiv**: 2509.25161 | **引用**: 55 | **机构**: NTU + Tencent
- **核心 idea**: 联合去噪方案——同时去噪多帧，噪声水平渐进递增，放松严格因果性
- **关键技术**:
  - 多帧联合去噪 + 渐进噪声水平
  - Attention sink 做全局上下文锚定
  - 高效少步蒸馏
- **对比 Self-Forcing++**: 同期并行工作，两者均无需 teacher 的长视频监督

### 6. Reward Forcing (2025.12)
- **arXiv**: 2512.04678 | **引用**: 14 | **机构**: 蚂蚁集团 (Yujun Shen)
- **核心 idea**: EMA-Sink（指数移动平均 sink token 融合长期/近期上下文）+ Rewarded DMD（偏向高奖励样本分布）
- **亮点**: 单 H100 达 23.1 FPS

### 7. Resampling Forcing (2025.12)
- **arXiv**: 2512.15702 | **引用**: 9 | **机构**: 上海 AI Lab + CUHK (林达华)
- **核心 idea**: Teacher-free 框架，通过 self-resampling 模拟推理误差，配合稀疏因果掩码 + history routing
- **亮点**: 无需任何 teacher 监督，纯从训练过程自适应

### 8. Infinity-RoPE (2025.11)
- **arXiv**: 2511.20649 | **引用**: 9 | **机构**: Virginia Tech
- **核心 idea**: Training-free 推理框架，Block-Relativistic RoPE + KV Flush + RoPE Cut
- **定位**: 不蒸馏/不微调，仅修改位置编码和 cache 策略

### 9. UltraViCo (2025.11)
- **arXiv**: 2511.20123 | **引用**: 3 | **机构**: 清华
- **核心 idea**: Training-free，通过常数衰减因子抑制超出训练窗口 token 的注意力，将外推极限推到 4×

---

## 关键技术对比

| 方法 | 需要 teacher 监督 | 需要长视频数据 | 无重叠帧 | 无 attention sink | 最长视频 | 训推完全对齐 | 交互式 prompt 切换 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| CausVid | ✓（短视频） | ✗ | ✗ | — | ~5s | ✗ | ✗ |
| **Self-Forcing** | **✓（短视频）** | **✗** | **✓** | **—** | **~5s** | **✓（训练时也用 KV cache）**| ✗ |
| **LongLive** | **✓（短视频）** | **✗** | **✓** | **✗（有 frame sink）** | **240s** | **✓** | **✓（KV-recache）** |
| Rolling Forcing | ✓（短视频） | ✗ | ✓ | ✗ | 分钟级 | ✓ | ✗ |
| **Self-Forcing++** | **✓（短视频）** | **✗** | **✓** | **✓** | **4min 15s** | **✓** | ✗ |
| Reward Forcing | ✓（短视频） | ✗ | ✓ | EMA-Sink | — | ✓ | ✗ |
| Resampling Forcing | ✗（teacher-free） | ✗ | ✓ | ✗ | — | ✓ | ✗ |
| Infinity-RoPE | training-free | — | — | — | — | — | ✗ |
| UltraViCo | training-free | — | — | — | — | — | ✗ |

---

## 核心技术维度

### Backward Noise Initialization（反向加噪初始化）
多个工作（CausVid、Self-Forcing、Self-Forcing++）均采用对已生成 clean latent 重新加噪的技术，但目标不同：
- CausVid/Self-Forcing：提升单视频质量，无需真实训练数据
- **Self-Forcing++**：跨帧时序一致性保持，使长视频采样窗口保留与前序帧的因果关联

### Distribution Matching Distillation（分布匹配蒸馏）
DMD 系列（DMD, DMD2）是核心蒸馏技术：
- 标准 DMD：$\nabla_\theta L_{DMD} = -E_t[s^{real}(\Phi(G_\theta(z),t)) - s^{fake}(\Phi(G_\theta(z),t))]$
- **Self-Forcing** 的关键改进：DMD 匹配的是**真实推理分布**（而非 CausVid 中 Diffusion Forcing 生成的错误分布）
- **Extended-DMD（Self-Forcing++）**：在均匀采样的长视频窗口上计算，将短 teacher 知识扩展到长视频监督
- **LongLive Streaming Long Tuning**：逐 clip 滚动 DMD，每步只对当前 clip 施加监督，历史帧 detach

### Rolling KV Cache
- CausVid：推理时用，训练时不用（失配）
- **Self-Forcing**：**训练时也用 KV cache（核心创新）**，推理 rolling；训练时特殊 attention mask 模拟 rolling 边界条件
- **Self-Forcing++ / LongLive / Rolling Forcing**：训推统一使用 rolling cache
- **LongLive KV-Recache**：在 prompt 切换时重建 cache，用新 prompt + 已生成帧刷新语义，解决交互式场景下的"prompt 惯性"问题

### Attention Sink（注意力锚点）
- **Self-Forcing** 早期：发现单独的 attention sink token 在长视频中无效
- **LongLive**：揭示 attention sink 有效性的前提是先解决 train-test 失配（streaming long tuning 之后 frame sink 才能生效）
- **Frame Sink（LongLive）**：将第一帧的所有 latent token 作为永久 sink，提供全局语义锚定；相比 CausVid/Self-Forcing 的重叠帧策略，不引入 over-exposure 伪影
- **EMA-Sink（Reward Forcing）**：指数平均历史 sink token，融合长/近期上下文

### 训练范式对比
| 训练范式 | context 来源 | 损失类型 | 训练与推理对齐 | 支持长视频 |
|---------|-------------|---------|--------------|---------|
| Teacher Forcing | GT 干净帧 | 帧级 MSE | ✗ | ✗ |
| Diffusion Forcing | GT 带噪帧 | 帧级 MSE | 部分 | ✗ |
| CausVid | DF 生成帧（非推理分布）| DMD | ✗（分布错位）| ✗ |
| **Self Forcing** | **自身生成帧（=推理分布）**| **Holistic 分布匹配** | **✓** | ✗（短片段）|
| **LongLive Streaming Long Tuning** | **自身滚动生成的长序列** | **逐 clip DMD（局部）** | **✓** | **✓（train-long–test-long）** |
| **Self-Forcing++ Extended-DMD** | **长视频均匀采样窗口** | **滑窗 DMD** | **✓** | **✓（滑窗监督）** |

---

## 评测指标演化

| 指标 | 问题 | Self-Forcing++ 的修正 |
|------|------|---------------------|
| VBench Image Quality | 对过曝/退化帧打分偏高 | 揭露偏差，对比同视频早/晚帧分数差 |
| VBench Aesthetic Quality | 同上 | 同上 |
| Dynamic Degree | 运动崩溃方法得分反而高（静止=高得分）| 配合 Visual Stability 综合评估 |
| **Visual Stability（新）** | — | 用 Gemini-2.5-Pro 评曝光稳定性，0-100分 |
| CLIP Score（分段）| 无法评估交互式 prompt 切换的语义对齐 | **LongLive** 自建数据集，按 prompt 边界分段计算 CLIP score |

---

## 关键概念

| 概念 | 定义 | 提出/首用 |
|------|------|---------|
| Exposure Bias | AR 训练用 GT 条件、推理用自生成条件的分布差异 | Professor Forcing (2016) |
| Distribution Matching Distillation (DMD) | 最小化 student/teacher 输出分布 KL 散度 | CausVid, Self-Forcing, LongLive |
| Rolling KV Cache | 推理时滑动窗口 KV 缓存，支持流式长视频 | Self-Forcing, Self-Forcing++, LongLive |
| Backward Noise Initialization | 对已生成 clean latent 重新加噪作为 student/teacher 评分起点 | CausVid, Self-Forcing, Self-Forcing++ |
| Extended-DMD | 在自生成长视频的均匀采样短窗口上计算 DMD loss | **Self-Forcing++** |
| Visual Stability | 用 Gemini-2.5-Pro 评曝光稳定性（修正 VBench 偏差）| **Self-Forcing++** |
| Frame Sink | 将视频第一帧所有 latent 作为永久全局 anchor，不被 rolling 逐出 | **LongLive** |
| KV-Recache | Prompt 切换时用已生成帧 + 新 prompt 重建 KV cache，刷新语义同时保持视觉连续 | **LongLive** |
| Streaming Long Tuning | 逐 clip 滚动 DMD，训练时在自生成的长序列上逐片段施加局部监督 | **LongLive** |
| FOV Overlap Retrieval | 根据相机视野（Field of View）的几何重叠关系筛选记忆帧 | **Context as Memory** |
| History Context Comparison | "旋转离开再旋转回来"评测协议，直接测量模型自身记忆一致性 | **Context as Memory** |
| Frame-Dimension Concatenation | 将上下文帧与预测帧沿帧维度拼接输入 DiT，无需额外模块 | **Context as Memory**, ReCamMaster |
| Mixed Block | FlashAttention 中部分被 mask 的 block，是 SWA 效率差根因；STA 从算法上消除 | **STA** |
| Tile（STA） | (T,T,T) token 立方体，T³=FA block size；STA 以 tile 为单位滑动消除 mixed block | **STA** |
| Head Specialization | 不同 attention head 的局部性强度不同但对 prompt 稳定，可离线搜索最优窗口 | **STA** |
| Attention Recall | 局部窗口内注意力得分占总得分比例，量化视频 DiT 的 3D 局部性 | **STA** |
| Kernel Efficiency | 稀疏内核 MFU / 全注意力 MFU，衡量稀疏化实际效率转化率 | **STA** |
