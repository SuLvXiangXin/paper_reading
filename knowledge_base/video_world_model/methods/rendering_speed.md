# 渲染速度 (Rendering Speed)

> 核心挑战：在保持生成质量的前提下大幅降低延迟、提升吞吐，支持流式/交互式视频生成。

---

## 技术路线分类

### 路线 A：双向 → 因果蒸馏（Bidirectional → Causal Distillation）

**核心思想**：预训练双向扩散模型质量最高，通过知识蒸馏将其压缩为因果自回归模型，同时减少去噪步数。

#### CausVid (2024.12) ⭐ 奠基之作
- **论文**: From Slow Bidirectional to Fast Autoregressive Video Diffusion Models
- **arXiv**: 2412.07772 | **引用**: ~180 | **录用**: CVPR 2025
- **机构**: MIT CSAIL + Adobe Research
- **核心方法**:
  - **块级因果注意力**：块内双向 + 块间因果，在 3D VAE 潜空间操作
  - **非对称 DMD 蒸馏**：双向 teacher → 因果 student，绕过弱因果 teacher 的质量瓶颈
  - **ODE 轨迹初始化**：用 teacher ODE 对做 MSE 预训练，稳定后续蒸馏
  - **KV 缓存推理**：推理时缓存历史块 KV，实现常数步骤复杂度
- **性能**: 初始延迟 1.3s，9.4 FPS（单 H100），相比 CogVideoX 延迟降低 160×
- **关键洞见**: 非对称设计（强双向 teacher 监督因果 student）是抑制误差累积的关键
- [详细卡片](../papers/causvid_2024.md)

---

### 路线 B：系统级优化（System-level Optimization）

不修改模型结构，通过注意力稀疏化、缓存、并行化等工程手段提速。

#### 稀疏注意力子路线

**核心挑战**：视频 DiT 中 3D 全注意力的 FLOPs 因 token 数二次增长，但朴素的 2D/3D 滑动窗口（SWA）无法高效实现——mixed block 使理论 FLOPs 减少无法转化为实际加速。

##### Sliding Tile Attention / STA (2025.02) ⭐ 系统级优化代表作
- **论文**: Fast Video Generation with Sliding Tile Attention
- **arXiv**: 2502.04507 | **录用**: ICML 2025
- **机构**: UCSD + UC Berkeley + 清华 + MBZUAI
- **核心洞见**:
  - 视频 DiT（HunyuanVideo）存在强 3D 局部性：仅 15.52% token 窗口即覆盖 70% 注意力得分
  - 不同 head 的局部性强度不同（head specialization），但对 prompt 稳定——可离线搜索最优窗口
  - SWA 在高维下效率差的根因：mixed block（部分被 mask 的块）既无法跳过 FLOPs 又需额外 mask 计算
- **核心方法**: 将滑动单元从 token 改为 tile（token 立方体，大小=FA block size），使同 tile 内 query 共享 key 集合→注意力图仅含 dense + empty block，zero mixed blocks
- **内核实现**: ThunderKittens + FA3 producer-consumer 范式，asynchronous KV loading，masking 逻辑完全由 producer 处理与计算重叠
- **性能** (HunyuanVideo 720P 5s):
  - 内核：10.45× over FA2，MFU 58.79%（内核效率 94.09%）
  - 端到端 training-free：945s → 501s（1.89×），VBench 降幅 <0.25%
  - 端到端 finetuning：945s → **268s（3.53×）**，VBench 仅降 0.09%
- [详细卡片](../papers/sliding_tile_attention_2025.md)

##### 同期稀疏注意力工作（并行）
| 论文 | 方法 | 加速方式 |
|------|------|---------|
| SageAttention2 | 异常值平滑高效注意力 | 硬件感知注意力计算（量化） |
| SpargeAttention | 无需训练精确稀疏注意力 | 动态预测稀疏模式 |
| SparseVideoGen (Xi et al., 2025) | 时空稀疏 | 静态头专项化稀疏 |
| XAttention | 块稀疏注意力 | 稀疏化注意力图 |

#### 缓存加速子路线

| 论文 | 方法 | 原理 |
|------|------|------|
| ∆-DiT | 特征偏移缓存 | 缓存残差，跳过早期 DiT block；质量弱于 STA（同加速比下 PSNR 差 10+）|
| FasterCache | 全注意力特征缓存 | 缓存 KV 特征复用相邻步 |
| PAB (Pyramid Attention Broadcast) | 金字塔广播 | 不同注意力层按频率广播 |

---

### 路线 C：少步训练方法（Few-step Training）

直接训练因果模型使用少步去噪，无蒸馏教师。

- **Diffusion Forcing** (Chen et al., 2024): 变噪声水平扩散，支持 AR 推理
- **Pyramid Flow** (Jin et al., 2024): 金字塔流匹配，支持 AR 推理，2.5 FPS

---

## STA 核心机制图解：mixed block 问题与解法

```
传统 token-wise SWA（NATTEN）：
  每个 query 的 key 范围略有不同 → 产生大量 mixed block（部分 mask）
  → mixed block 无法省 FLOPs，且需计算 mask → 比 dense 更慢

STA（tile-wise sliding）：
  同 tile 内 query 共享相同 key 集合 → 注意力图仅有 dense + empty block
  → empty block 直接跳过，dense block 无 mask 开销
  → FLOPs 减少 ∝ 实际加速

数学保证（定理 3.2）：
  若 W ≡ 0 (mod T)，STA 产生 0 个 mixed block
  每个 query tile 精确对应 (W/T)³ 个 dense key tile
```

---

## 核心技术解析：非对称蒸馏（Asymmetric Distillation）

```
  双向 Teacher (sdata，冻结)
         ↓ 分布匹配损失（DMD）
  因果 Student (Gϕ，可训练)    ←→    在线得分函数 (sgen，跟踪生成器分布)

  关键：teacher 保持双向注意力，student 使用因果注意力
  → teacher 的全局信息监督消除了 student 因果推理中的误差累积
```

**为何非对称优于对称（从因果 teacher 蒸馏）**：
- 因果 teacher 本身质量低于双向 teacher（~2 pts 帧质量差距）；
- 因果 teacher 的误差累积会传递给 student；
- DMD 的灵活性（允许 teacher/student 架构不同）是关键使能条件。

---

## 性能对比

### 双向→因果蒸馏（128 帧, 640×352, 单 H100）

| 方法 | 延迟(s) | 吞吐(FPS) | VBench时序质量 | 因果/AR |
|------|---------|----------|--------------|---------|
| CogVideoX-5B | 208.6 | 0.6 | 89.9 | ✗ |
| Pyramid Flow | 6.7 | 2.5 | 89.6 | 部分 |
| CausVid | **1.3** | **9.4** | **94.7** | ✓ |

### 系统级优化（HunyuanVideo 720P 5s，H100）

| 方法 | 内核延迟 | 端到端延迟 | 端到端加速 | 质量损失 |
|------|---------|-----------|-----------|---------|
| FA3（基线） | 265ms | 945s | 1.0× | — |
| CLEAR | 307ms | 2567s | 0.37× | -0.34pt |
| Tiled NATTEN | 208ms | 1858s | 0.51× | -0.02pt |
| Swin | 48ms | 762s | 1.24× | -3.71pt |
| **STA (training-free)** | **25ms** | **501s** | **1.89×** | **-0.25pt** |
| **STA (finetuned)** | **25ms** | **268s** | **3.53×** | **-0.09pt** |

---

## 后续影响

CausVid 确立了"双向→因果蒸馏"的方法范式，被以下工作继承或参照：
- **Self-Forcing** (2025.06, 189引用): 用 AR rollout 训练解决 exposure bias，进一步改进蒸馏思路
- **Reward Forcing** (2025.12): 在 CausVid 基础上加入奖励对齐的 DMD，达到 23.1 FPS
- **Matrix-Game 2.0** (2025.08): 游戏视频 AR 生成，同样采用因果架构+少步蒸馏
- **Yume 1.5** (2025.12): 双向注意力蒸馏实现实时流式加速

STA 是第一个将 3D SWA 真正落地的高效实现，预期影响：
- 作为高 MFU 的稀疏注意力基础设施，与量化（SageAttention）、步数蒸馏、并行化等正交叠加
- 推动视频 DiT 内核优化的标准参照（MFU、kernel efficiency 指标体系）

---

## 关键概念

| 概念 | 定义 |
|------|------|
| Mixed Block | FlashAttention block 中部分被 mask 的块，无法省 FLOPs 且需 mask 计算，是 SWA 效率差的根因 |
| Dense Block | 全部保留的 FA block，GPU 计算最友好 |
| Empty Block | 全部被 mask 的 FA block，可直接跳过 |
| Tile（STA） | (T,T,T) 大小的 token 立方体，T³ = FA block size；同 tile 内 query 共享 key 集合 |
| Head Specialization | 不同 attention head 的局部性强度不同，但对 prompt 稳定；可离线搜索最优窗口 |
| Attention Recall | 某局部窗口内注意力得分占总得分的比例，用于量化 3D 局部性强度 |
| MFU（Model FLOP Utilization）| 实际 FLOP 吞吐 / 理论峰值 FLOP，衡量硬件利用效率 |
| Kernel Efficiency | 稀疏内核 MFU / 全注意力 MFU，衡量稀疏化的实际效率转化率 |

---

## 开放问题

1. **VAE 延迟瓶颈**：当前 3D VAE 需攒 5 帧 latent 才能出像素，帧级 VAE 可再降一个数量级延迟；
2. **多样性损失**：逆 KL 散度目标导致 mode-seeking，EM-Distillation / Score Implicit Matching 等可能改善；
3. **超长视频误差积累**：30 秒内良好，更长序列仍需改进（Self-Forcing 等后续工作尝试解决）；
4. **实时部署**：量化+编译+并行化可能将 9.4 FPS 推向真正实时（30+ FPS）；
5. **STA 窗口整除约束**：W 必须整除 T，限制配置灵活性，非均匀窗口方案仍是开放问题；
6. **极短序列效率退化**：低分辨率视频（短序列）时 STA 加速比有限（Wan 2.1 仅 1.60×），序列长度与稀疏性收益的关系仍需研究。
