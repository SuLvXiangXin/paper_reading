# Fast Video Generation with Sliding Tile Attention (2025)

## 基本信息
- 作者: Peiyuan Zhang, Yongqi Chen*, Runlong Su*, Hangliang Ding, Ion Stoica, Zhengzhong Liu, Hao Zhang
- 机构: UC San Diego, University of Michigan, Tsinghua University, UC Berkeley, MBZUAI
- arXiv: 2502.04507
- 发表: ICML 2025

## 一句话总结
通过"以 tile 为单位滑动"代替"以 token 为单位滑动"，STA 彻底消除 2D/3D 滑动窗口注意力中的 mixed block，首次让高阶稀疏注意力的墙钟加速与 FLOP 节省成正比，HunyuanVideo 端到端推理从 945s 降至 268–501s。

## 问题
3D 全注意力的计算复杂度为 O(N²)，在 720P 5s 视频（115K tokens）生成时，注意力占总推理时间 85%（945s 中的 800s）。经典的滑动窗口注意力（SWA）理论上可以降低 FLOPs，但已有 2D/3D SWA 实现（NATTEN、CLEAR）均无法将 FLOPs 减少转化为实际加速——原因在于"混合块（mixed block）"大量存在，导致无效计算和 masking overhead。

## 方法
- **方法线归属**: 渲染速度 → 路线 B：系统级优化（稀疏注意力 + 硬件感知内核）
- **核心 idea**: 将滑动单元从单个 token 改为 tile（token 的空间立方体组），使同一 tile 内所有 query 共享相同的 key 集合，从而将注意力图中的 mixed block 归零，实现完全由 dense block + empty block 构成的 GPU 友好计算模式。
- **关键技术点**:
  - **Tile 重排（Tiling & Reordering）**: 将 3D 视频切成不重叠的 (T,T,T) 立方 tile，按 tile 内连续序号展平，保证同 tile 内 token 的序列号相邻；tile 大小 T³ = FlashAttention block size B。
  - **消除 mixed block（理论保证）**: 定理证明 STA 在 W 整除 T 时产生 0 个 mixed block，而 Tiled NATTEN 在同样配置下仍有大量 mixed block（见 Table 1）。
  - **硬件感知内核（ThunderKittens + FA3 范式）**: 采用 producer-consumer 双 warpgroup 设计——producer 异步从 HBM 加载 KV 块，consumer 始终做 dense 计算，inter-block mask 逻辑完全由 producer 处理并与计算重叠，计算 warpgroup 对稀疏模式完全透明。MFU 达 58.79%，内核效率 94.09%。
  - **Head 专项化（Head Specialization）感知的窗口配置**: 观察到不同 attention head 的局部性强度不同，但跨 prompt 极为稳定（std ≈ 0）；设计 Algorithm 1 通过 MSE 损失剖析自动为每个 head 搜索最优窗口大小，仅需 16 条 prompt 校准，无需训练。
  - **Finetuning 模式**: 固定激进稀疏度（91% sparsity）微调模型，三路 loss：注意力蒸馏损失 L_attn（每层中间输出 MSE）+ 最终层对齐损失 L_final + flow matching 数据损失 L_data；8 H100×8h 即可完成。
  - **Training-free 全关注保护**: 前 T0 步保持全注意力（捕捉全局结构），后续步骤切换 STA（精细化局部细节）。

## 实验
- **Benchmark**: VBench, 人工评估（MovieGen Bench 200条）, SSIM/PSNR/CD-FVD vs HunyuanVideo baseline
- **主要结果**:
  - 内核级：STA（ThunderKittens, 91% sparsity）比 FA2 快 10.45×，比 FA3 快 10.45/1.03 ≈ 10.1×，MFU 58.79%
  - 端到端（HunyuanVideo 720P 5s）：
    - Training-free：501s（FA3 945s → 1.89× 加速），VBench 降幅 <0.25%
    - Finetuning：268s → **3.53× 加速**，VBench 82.62%（vs full attn 82.71%，仅降 0.09%）
  - 人工评估：STA-tf-1.89× vs ∆-DiT-1.36×，STA win rate 66.5% vs 10.0%；STA-t-2.43× vs ∆-DiT-1.8×，70.0% vs 11.0%
  - 还验证于 Wan 2.1（SSIM 85.81, PSNR 24.42, 1.60× 加速）和 FLUX 图像超分
- **对比基线**:
  - **CLEAR（FlexAttention）**: 90% sparsity 下反而慢 0.86×（mixed block 问题）
  - **NATTEN / Tiled NATTEN**: 最大 1.27× 加速，MFU 仅 8.20%
  - **Swin（非滑动，分块）**: 效率高（5.54×）但破坏局部连通性，VBench 降 3.71 pts，微调后更差
  - **∆-DiT（缓存加速）**: 同加速比下 SSIM/PSNR 大幅落后（50步：18.09 vs 28.76 PSNR）

## 评价
- **优势**:
  1. 算法与系统协同设计：一个简单的"sliding unit 从 token → tile"改动，从根本上解决了多年来 SWA 无法高效落地的工程问题，且有严格数学证明（定理 3.1/3.2）。
  2. Plug-and-play：training-free 模式无需任何训练即可获得 1.89× 加速，适合快速部署现有模型。
  3. 与其他加速手段正交（缓存、步数蒸馏），可叠加使用。
  4. 方法通用性强：同样适用于 2D（FLUX）和其他 3D DiT（Wan 2.1）。
- **局限**:
  1. 要求窗口大小 W 整除 tile 大小 T，限制了配置的灵活性。
  2. 需要修改 token 排列顺序（tile 展平），对已有推理 pipeline 有一定改造成本。
  3. Finetuning 虽然代价小（8h），但仍需合成数据和对应的蒸馏流程。
  4. 极低分辨率（sequence length 短）时加速效果会减弱（Wan 2.1 仅 1.60×）。
- **对视频世界模型领域的贡献**:
  - 确立了"3D 局部性"作为视频 DiT 的可利用结构性先验，且量化了各 head 的局部性强度（attention recall 指标）。
  - 为视频 DiT 推理加速提供了第一个真正硬件高效的 3D 稀疏注意力实现，填补了 NATTEN/CLEAR 等方法理论上可行、实践中反而更慢的空白。
  - 为后续研究（量化注意力、稀疏注意力、分布式推理）提供了高 MFU 的基准内核。
