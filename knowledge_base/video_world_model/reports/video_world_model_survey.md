# 视频世界模型全景调研

> 基于彭德刚框架，以 Wan / Cosmos / Self-Forcing / FastVideo 为锚点，2026.03 整理

---

## 一、核心目标与基础方向

**核心目标**：视频世界模型（Video World Model），期望全方位提升性能。

**基础方向**：
- **时序连续性**：随基础模型（Wan 1127引用、HunyuanVideo 995引用、CogVideoX 1524引用）进展，问题已不大
- **渲染分辨率**：通过高分辨率生成技术优化
- **性能提升**：多分支技术并行推进（详见第八节）

**基础模型引用数对比**（截至 2026.03）：

| 模型 | arXiv | 引用数 | 机构 |
|------|-------|--------|------|
| DiT | 2212.09748 | 4,942 | Meta |
| Flow Matching | 2210.02747 | 3,560 | Meta |
| Rectified Flow | 2209.03003 | 2,419 | — |
| Video Diffusion Models | 2204.03458 | 2,362 | Google |
| Stable Video Diffusion | 2311.15127 | 2,153 | Stability AI |
| Consistency Models | 2303.01469 | 1,605 | OpenAI |
| CogVideoX | 2408.06072 | 1,524 | 智谱 |
| **Wan** | 2503.20314 | **1,127** | 阿里 |
| HunyuanVideo | 2412.03603 | 995 | 腾讯 |
| Open-Sora | 2412.20404 | 542 | — |
| Latte | 2401.03048 | 466 | — |
| **Cosmos** | 2501.03575 | **465** | NVIDIA |
| Movie Gen | 2410.13720 | 439 | Meta |
| LTX-Video | 2501.00103 | 305 | — |

---

## 二、三维一致性

**子方向**：相机精准渲染、多视角一致性。

### FantasyWorld (2025.09)
- **论文**: Geometry-Consistent World Modeling via Unified Video and 3D Prediction
- **arXiv**: 2509.21657 | **引用**: 3 | **录用**: ICLR 2026
- **机构**: Alibaba AMAP + 北京邮电大学
- **核心方法**: 在冻结的视频基础模型上增加可训练几何分支，单次前向传播联合建模视频 latent 和隐式 3D 场。跨分支监督使几何线索引导视频生成，同时视频先验正则化 3D 预测。
- **关键贡献**: 实现 3D-aware 视频表示，支持新视角合成等下游任务

**相关高引工作**（从锚点引用网络中发现）：

| 引用数 | 论文 | arXiv | 说明 |
|--------|------|-------|------|
| 160 | Gen3C | 2503.03751 | 3D 感知一致世界生成 |
| 24 | Geometry Forcing | 2507.07982 | 视频扩散嫁接 3D 表示（详见第五节） |
| 11 | Geometry-aware 4D Video Gen | 2507.01099 | 几何感知 4D 视频用于机器人 |

---

## 三、物理合理性

**子方向**：多智能体交互、Actor 和场景交互。侧重交互逻辑与物理规则建模。

**相关高引工作**（从 Cosmos 引用网络中发现）：

| 引用数 | 论文 | arXiv | 说明 |
|--------|------|-------|------|
| 84 | Cosmos-Reason1 | 2503.15558 | 物理常识→具身推理（NVIDIA） |
| 67 | Do generative video models understand physical principles? | 2501.09038 | 物理理解评测 |
| 56 | WorldScore | 2504.00983 | 统一世界生成评测 |

此方向尚无代表性独立技术工作，主要依赖基础模型和数据。

---

## 四、长时渲染质量

**核心挑战**：长时间序列下的渲染稳定性与质量，尤其是 exposure bias（train-test gap）导致的误差累积。

### 4.1 Self-Forcing (2025.06) ⭐ 奠基之作
- **论文**: Self Forcing: Bridging the Train-Test Gap in Autoregressive Video Diffusion
- **arXiv**: 2506.08009 | **引用**: 189 | **机构**: Adobe Research
- **核心方法**: 训练时用 AR rollout + KV caching 让每帧条件于自身之前生成的帧（而非 GT），从根本上消除 exposure bias。Rolling KV cache 实现单 GPU 亚秒延迟的实时流式生成。
- **影响**: 催生整个 "Forcing 家族"，定义了长时渲染质量的方法论范式
- **关键前驱**: Professor Forcing (2016, 654引用) → Diffusion Forcing (2024, 374引用) → Self-Forcing

### 4.2 LongLive (2025.08)
- **论文**: LongLive: Real-time Interactive Long Video Generation
- **arXiv**: 2509.22622 | **引用**: 65 | **机构**: HKUST + NVIDIA (Song Han, Enze Xie)
- **核心方法**: 帧级 AR 框架 + KV-recache（平滑 prompt 转换）+ streaming long tuning（训练-推理长度对齐）+ frame-level attention sink（长程一致性）。1.3B 模型在 32 GPU-days 微调后可生成分钟级视频，单 H100 达 20.7 FPS。

### 4.3 Rolling Forcing (2025.09)
- **论文**: Rolling Forcing: Autoregressive Long Video Diffusion in Real Time
- **arXiv**: 2509.25161 | **引用**: 55 | **机构**: NTU + Tencent
- **核心方法**: 联合去噪方案——同时去噪多帧，噪声水平渐进递增，放松严格因果性以抑制误差增长。引入 attention sink 做全局上下文锚定，并设计高效少步蒸馏算法。

### 4.4 Self-Forcing++ (2025.10)
- **论文**: Self-Forcing++: Towards Minute-Scale High-Quality Video Generation
- **arXiv**: 2510.02283 | **引用**: 59 | **机构**: UCLA
- **核心方法**: 无需长视频 teacher——利用短片段 teacher 知识引导学生模型处理自生成长视频中的采样片段，将视频长度扩展至 teacher 能力的 20 倍（最长 4 分 15 秒），避免 over-exposure 和误差累积。

### 4.5 Infinity-RoPE (2025.11)
- **论文**: Action-Controllable Infinite Video Generation Emerges From Autoregressive Self-Rollout
- **arXiv**: 2511.20649 | **引用**: 9 | **机构**: Virginia Tech
- **核心方法**: **Training-free** 推理时框架。三组件：Block-Relativistic RoPE（移动局部参考系消除固定时间位置）、KV Flush（刷新 KV cache 实现细粒度动作控制）、RoPE Cut（单次 rollout 内多剪切场景转换）。

### 4.6 MagicWorld (2025.11)
- **论文**: Interactive Geometry-driven Video World Exploration
- **arXiv**: 2511.18886 | **引用**: 3 | **机构**: vivo
- **核心方法**: 集成 3D 几何先验和历史检索的交互视频世界模型。Action-Guided 3D Geometry Module (AG3D) 构建点云做视角转换；History Cache Retrieval (HCR) 检索相关历史帧缓解误差累积。

### 4.7 UltraViCo (2025.11)
- **论文**: Breaking Extrapolation Limits in Video Diffusion Transformers
- **arXiv**: 2511.20123 | **引用**: 3 | **机构**: 清华大学
- **核心方法**: **Training-free plug-and-play**。发现注意力发散是质量退化和内容重复的统一原因，通过常数衰减因子抑制训练窗口外 token 的注意力，将外推极限从 2x 推到 4x（Dynamic Degree 提升 233%）。

### 4.8 LongVie 1 (2025.08)
- **论文**: Multimodal-Guided Controllable Ultra-Long Video Generation
- **arXiv**: 2508.03694 | **引用**: ~几 | **机构**: 复旦 + 上海 AI Lab
- **核心方法**: 端到端 AR 框架，支持密集和稀疏多模态控制信号引导，带退化感知训练策略。

### 4.9 LongVie 2 (2025.12)
- **论文**: Multimodal Controllable Ultra-Long Video World Model
- **arXiv**: 2512.13604 | **引用**: 3 | **机构**: 复旦 + 上海 AI Lab
- **核心方法**: 三阶段训练：(1) 多模态引导 + 隐式世界级监督，(2) 退化感知训练弥合 train-inference gap，(3) 历史上下文引导跨片段对齐。支持 5 分钟连续生成。

### 4.10 Resampling Forcing (2025.12)
- **论文**: End-to-End Training for Autoregressive Video Diffusion via Self-Resampling
- **arXiv**: 2512.15702 | **引用**: 9 | **机构**: 上海 AI Lab + CUHK (林达华)
- **核心方法**: **Teacher-free** 框架，通过 self-resampling 方案在训练中模拟推理时模型误差。使用稀疏因果掩码实现时间因果性 + 并行训练，引入 history routing 动态检索 top-k 相关历史帧。

### 4.11 Reward Forcing (2025.12)
- **论文**: Efficient Streaming Video Generation with Rewarded Distribution Matching Distillation
- **arXiv**: 2512.04678 | **引用**: 14 | **机构**: 蚂蚁集团 (Yujun Shen)
- **核心方法**: EMA-Sink（指数移动平均 sink tokens 融合被驱逐帧，捕获长期上下文 + 近期动态，防止初始帧复制）+ Rewarded DMD（偏置输出分布向高奖励样本，增强运动动态）。单 H100 达 23.1 FPS。

### Forcing 家族技术路线图

```
Professor Forcing (2016, 654引用)
  └─ Diffusion Forcing (2024, 374引用)
       └─ Self-Forcing (2025.06, 189引用) ⭐ 核心
            ├─ Self-Forcing++ (2025.10, 59引用) — 无长视频teacher
            ├─ Rolling Forcing (2025.09, 55引用) — 联合去噪+少步蒸馏
            ├─ Reward Forcing (2025.12, 14引用) — 奖励蒸馏+EMA-Sink
            ├─ Resampling Forcing (2025.12, 9引用) — 自重采样teacher-free
            ├─ Memory Forcing (2025.10, 15引用) — 时空记忆（见第五节）
            └─ Geometry Forcing (2025.07, 24引用) — 3D对齐（见第五节）
```

---

## 五、长时一致性

**核心挑战**：长时间序列下的场景、角色与逻辑一致性。核心技术路线是 **记忆机制**（Memory）。

### 5.1 WorldMem (2025.04) ⭐ 早期代表
- **论文**: WORLDMEM: Long-term Consistent World Simulation with Memory
- **arXiv**: 2504.12369 | **引用**: 61 | **机构**: S-Lab, NTU
- **核心方法**: Memory bank 存储帧和状态（位姿、时间戳），memory attention 机制提取相关信息重建已观察场景。引入时间戳建模静态世界和动态演化。

### 5.2 Context as Memory (2025.06)
- **论文**: Scene-Consistent Interactive Long Video Generation with Memory Retrieval
- **arXiv**: 2506.03141 | **引用**: 61 | **机构**: 港大 + 浙大 + 快手
- **核心方法**: 直接用历史上下文帧作为记忆（帧格式存储、无后处理），通过沿帧维度拼接上下文和预测帧来条件化。Memory Retrieval 模块通过相机位姿的 FOV 重叠计算选择相关上下文帧。

### 5.3 VMem (2025.06)
- **论文**: Consistent Interactive Video Scene Generation with Surfel-Indexed View Memory
- **arXiv**: 2506.18903 | **引用**: 32 | **录用**: ICCV 2025 Highlight | **机构**: Oxford
- **核心方法**: Surfel-Indexed View Memory——基于 3D 表面元素（surfels）几何索引过去视图，高效检索最相关历史视图生成新视角。以远低于使用全部历史帧的成本实现一致的长期环境探索。

### 5.4 SPMem (2025.06)
- **论文**: Video World Models with Long-term Spatial Memory
- **arXiv**: 2506.05284 | **引用**: 55 | **机构**: Stanford + SJTU + CUHK + 上海 AI Lab
- **核心方法**: 受人类记忆启发的几何锚定长期空间记忆。显式 3D 记忆存储和检索机制，构建专用数据集训练和评估。解决重访时场景一致性问题，防止遗忘。

### 5.5 DeepVerse (2025.06)
- **论文**: 4D Autoregressive Video Generation as a World Model
- **arXiv**: 2506.01103 | **引用**: 17 | **机构**: 上海 AI Lab
- **核心方法**: 4D 交互世界模型，将前一时间步的几何预测显式融入当前预测（条件于动作）。显式几何约束捕获更丰富的时空关系和物理动力学，减少漂移。提供几何感知记忆检索实现长期空间一致性。

### 5.6 Geometry Forcing (2025.07)
- **论文**: Marrying Video Diffusion and 3D Representation for Consistent World Modeling
- **arXiv**: 2507.07982 | **引用**: 24 | **机构**: Microsoft Research + 清华
- **核心方法**: 将视频扩散模型的中间表示对齐到预训练几何基础模型的特征。两个对齐目标：Angular Alignment（方向一致性，余弦相似度）和 Scale Alignment（从归一化扩散表示回归非归一化几何特征）。

### 5.7 Memory Forcing (2025.10)
- **论文**: Spatio-Temporal Memory for Consistent Scene Generation on Minecraft
- **arXiv**: 2510.03198 | **引用**: 15 | **机构**: CUHK-Shenzhen
- **核心方法**: 几何索引空间记忆 + 混合训练框架。Hybrid Training 引导模型在探索时依赖时间记忆、重访时依赖空间记忆。Chained Forward Training 扩展 AR 训练处理更大位姿变化。Point-to-Frame Retrieval 将可见点映射到源帧。

### 5.8 WorldPack (2025.10)
- **论文**: Pack and Force Your Memory: Long-form and Consistent Video Generation
- **arXiv**: 2510.01784 | **引用**: 10 | **机构**: ShanghaiTech + Tencent Hunyuan
- **核心方法**: (1) **MemoryPack**——可学习上下文检索机制，用文本和图像作为全局引导，以线性复杂度联合建模短期和长期依赖；(2) **Direct Forcing**——高效单步近似策略改善 train-inference 对齐，遏制 AR 解码中的误差传播。

### 5.9 TeleWorld (2026.01)
- **论文**: Towards Dynamic Multimodal Synthesis with a 4D World Model
- **arXiv**: 2601.00051 | **引用**: 2 | **机构**: 中国电信（27位作者）
- **核心方法**: 实时多模态 4D 世界建模，"Generation-Reconstruction-Guidance" 闭环范式：生成的视频流持续重建为动态 4D 时空表示，反过来引导后续生成保持空间/时间/物理一致性。Macro-from-Micro Planning (MMPL) 做层次化片段级规划，DMD 实现实时合成。

### 记忆机制技术谱系

```
按记忆类型分类：
├─ 帧级记忆（直接存帧）
│   ├─ Context as Memory (FOV重叠检索)
│   ├─ WorldPack/MemoryPack (可学习检索)
│   └─ Resampling Forcing (top-k history routing)
├─ 3D 几何记忆（surfel/点云索引）
│   ├─ WorldMem (memory bank + 时间戳)
│   ├─ VMem (surfel-indexed, ICCV 2025 Highlight)
│   ├─ SPMem (Stanford, 显式3D存储)
│   ├─ Memory Forcing (point-to-frame retrieval)
│   └─ DeepVerse (4D几何预测+记忆检索)
└─ 特征级对齐
    └─ Geometry Forcing (中间表示→几何特征对齐)
```

---

## 六、场景丰富程度

由基础模型和训练数据决定，无独立技术工作。主要取决于：
- 训练数据多样性（游戏录像、真实视频、合成数据）
- 基础模型容量（Wan 1127引用、HunyuanVideo、CogVideoX）

---

## 七、渲染速度

### CausVid (2024.12) ⭐ 开创性工作
- **论文**: From Slow Bidirectional to Fast Autoregressive Video Diffusion Models
- **arXiv**: 2412.07772 | **引用**: 180 | **录用**: CVPR 2025 | **机构**: MIT CSAIL + Adobe Research
- **核心方法**: 将预训练双向扩散 Transformer 适配为因果 AR 模型，再用 DMD（Distribution Matching Distillation）将 50 步扩散压缩到 4 步。非对称蒸馏策略用双向 teacher 监督因果 student。流式生成 9.4 FPS，初始延迟 1.3s。
- **影响**: 后续 Full Video Generation → AR Video Generation 的大量工作遵循类似框架

**渲染速度相关工作汇总**（从锚点引用网络发现）：

| 引用数 | 论文 | 方向 |
|--------|------|------|
| 180 | CausVid | 双向→因果蒸馏 |
| 81 | SageAttention2 | 异常值平滑高效注意力 |
| 81 | XAttention | 块稀疏注意力 |
| 73 | FastVideo/STA | 滑动瓦片注意力 |
| 53 | FastVideo/VSA | 可训练稀疏注意力 |
| 51 | Sparse VideoGen2 | 语义感知稀疏注意力 |
| 49 | SpargeAttention | 无需训练精确稀疏 |

---

## 八、性能提升类专项工作

交互式世界模型系列，聚焦时序连续性和渲染分辨率：

### 8.1 MAGI-1 (2025.05)
- **论文**: Autoregressive Video Generation at Scale
- **arXiv**: 2505.13211 | **引用**: 136 | **机构**: Sand.ai
- **核心方法**: 24B 参数 AR 模型，逐 chunk 预测视频帧序列，per-chunk 噪声随时间单调递增实现因果时间建模。支持 4M token 上下文长度，推理峰值成本恒定（不随视频长度增长）。

### 8.2 Matrix-Game 系列 (Skywork AI / 昆仑万维)

**Matrix-Game 1.0 (2025.06)**
- **arXiv**: 2506.18701 | **机构**: Skywork AI
- **核心方法**: 17B+ 参数模型，两阶段训练：大规模无标签预训练（2700+ 小时 Minecraft 游戏录像）→ 动作标注训练（1000+ 小时精细键鼠标注）。条件于参考图像、运动上下文和用户动作。

**Matrix-Game 2.0 (2025.08)**
- **arXiv**: 2508.13009 | **引用**: 49
- **核心方法**: 因果架构 + 少步蒸馏实现实时（25 FPS）流式生成。可扩展数据管线（Unreal Engine + GTA5，1200 小时），帧级键鼠动作注入模块，支持分钟级视频生成。

### 8.3 Yume 系列 (上海 AI Lab / 复旦)

**Yume 1.0 (2025.07)**
- **arXiv**: 2507.17744 | **引用**: 26
- **核心方法**: Masked Video Diffusion Transformer (MVDT) + 记忆模块，从图像+键盘输入做无限 AR 视频生成。相机运动量化、Anti-Artifact Mechanism (AAM)、Time Travel Sampling (TTS-SDE)、对抗蒸馏+缓存加速。

**Yume 1.5 (2025.12)**
- **arXiv**: 2512.22096 | **引用**: 8
- **核心方法**: 三大升级：(1) 统一上下文压缩（线性注意力）生成长视频；(2) 双向注意力蒸馏实现实时流式加速；(3) 文本控制世界事件生成。

### 8.4 Hunyuan-GameCraft 系列 (Tencent Hunyuan)

**Hunyuan-GameCraft 1.0 (2025.06)**
- **arXiv**: 2506.17201 | **引用**: 35
- **核心方法**: 键盘鼠标输入统一为共享相机表示空间做精细动作控制 + 混合历史条件训练策略做 AR 序列扩展。100+ 款 3A 游戏的 1M+ 录像训练，模型蒸馏实现实时部署。

**Hunyuan-GameCraft 2.0 (2025.11)**
- **arXiv**: 2511.23429 | **引用**: 9
- **核心方法**: 从固定键盘输入转向 **指令驱动交互**（自然语言 prompt）。基于 14B MoE 图生视频基础模型 + 文本驱动交互注入机制。自动化管线将非结构化文本-视频对转换为因果对齐的交互数据集。

### 性能提升系列对比

| 系列 | 版本 | 日期 | 参数量 | FPS | 核心特色 |
|------|------|------|--------|-----|----------|
| MAGI | 1 | 2025.05 | 24B | — | 4M token 上下文，恒定推理成本 |
| Matrix-Game | 1.0→2.0 | 05→08 | 17B+ | 25 | 开源，Minecraft+UE+GTA5 数据 |
| Yume | 1.0→1.5 | 07→12 | — | — | 文本控制，线性注意力压缩 |
| Hunyuan-GameCraft | 1.0→2.0 | 06→11 | 14B MoE | — | 100+游戏数据，指令驱动 |

---

## 九、总结：技术路线全景图

```
视频世界模型
├─ 三维一致性
│   └─ FantasyWorld (冻结视频模型+几何分支)
├─ 物理合理性
│   └─ (依赖基础模型，无独立方法)
├─ 长时渲染质量 ← Forcing 家族
│   ├─ Self-Forcing (奠基, 189引用)
│   ├─ Self-Forcing++ / Rolling Forcing / Reward Forcing / Resampling Forcing
│   ├─ Infinity-RoPE / UltraViCo (training-free)
│   └─ LongLive / LongVie 1→2 / MagicWorld
├─ 长时一致性 ← Memory 机制
│   ├─ 帧级: Context as Memory, WorldPack
│   ├─ 3D几何: WorldMem, VMem, SPMem, Memory Forcing, DeepVerse
│   └─ 特征对齐: Geometry Forcing
├─ 渲染速度
│   └─ CausVid (双向→因果蒸馏, 180引用)
└─ 性能提升专项 (交互式世界模型)
    ├─ MAGI-1 (Sand.ai, 24B)
    ├─ Matrix-Game 1.0→2.0 (Skywork AI)
    ├─ Yume 1.0→1.5 (上海AI Lab)
    └─ Hunyuan-GameCraft 1.0→2.0 (Tencent)
```

---

## 附录：论文速查表

| # | 论文 | arXiv | 日期 | 引用 | 机构 | 分类 |
|---|------|-------|------|------|------|------|
| 1 | Self-Forcing | 2506.08009 | 2025.06 | 189 | Adobe | 长时渲染 |
| 2 | CausVid | 2412.07772 | 2024.12 | 180 | MIT+Adobe | 渲染速度 |
| 3 | MAGI-1 | 2505.13211 | 2025.05 | 136 | Sand.ai | 性能提升 |
| 4 | LongLive | 2509.22622 | 2025.09 | 65 | HKUST+NVIDIA | 长时渲染 |
| 5 | WorldMem | 2504.12369 | 2025.04 | 61 | NTU | 长时一致 |
| 6 | Context as Memory | 2506.03141 | 2025.06 | 61 | 港大+快手 | 长时一致 |
| 7 | Self-Forcing++ | 2510.02283 | 2025.10 | 59 | UCLA | 长时渲染 |
| 8 | SPMem | 2506.05284 | 2025.06 | 55 | Stanford | 长时一致 |
| 9 | Rolling Forcing | 2509.25161 | 2025.09 | 55 | NTU+Tencent | 长时渲染 |
| 10 | Matrix-Game 2.0 | 2508.13009 | 2025.08 | 49 | Skywork AI | 性能提升 |
| 11 | Hunyuan-GameCraft 1.0 | 2506.17201 | 2025.06 | 35 | Tencent | 性能提升 |
| 12 | VMem | 2506.18903 | 2025.06 | 32 | Oxford | 长时一致 |
| 13 | Yume 1.0 | 2507.17744 | 2025.07 | 26 | 上海AI Lab | 性能提升 |
| 14 | Geometry Forcing | 2507.07982 | 2025.07 | 24 | MSR+清华 | 长时一致 |
| 15 | DeepVerse | 2506.01103 | 2025.06 | 17 | 上海AI Lab | 长时一致 |
| 16 | Memory Forcing | 2510.03198 | 2025.10 | 15 | CUHK-SZ | 长时一致 |
| 17 | Reward Forcing | 2512.04678 | 2025.12 | 14 | 蚂蚁集团 | 长时渲染 |
| 18 | WorldPack | 2510.01784 | 2025.10 | 10 | ShanghaiTech | 长时一致 |
| 19 | Infinity-RoPE | 2511.20649 | 2025.11 | 9 | Virginia Tech | 长时渲染 |
| 20 | Resampling Forcing | 2512.15702 | 2025.12 | 9 | 上海AI Lab | 长时渲染 |
| 21 | Hunyuan-GameCraft 2.0 | 2511.23429 | 2025.11 | 9 | Tencent | 性能提升 |
| 22 | Yume 1.5 | 2512.22096 | 2025.12 | 8 | 上海AI Lab | 性能提升 |
| 23 | FantasyWorld | 2509.21657 | 2025.09 | 3 | Alibaba | 三维一致 |
| 24 | UltraViCo | 2511.20123 | 2025.11 | 3 | 清华 | 长时渲染 |
| 25 | MagicWorld | 2511.18886 | 2025.11 | 3 | vivo | 长时渲染 |
| 26 | LongVie 2 | 2512.13604 | 2025.12 | 3 | 复旦 | 长时渲染 |
| 27 | TeleWorld | 2601.00051 | 2026.01 | 2 | 中国电信 | 长时一致 |
| 28 | LongVie 1 | 2508.03694 | 2025.08 | ~few | 复旦 | 长时渲染 |
| 29 | Matrix-Game 1.0 | 2506.18701 | 2025.06 | — | Skywork AI | 性能提升 |
