# Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning (2026)

## 基本信息
- 作者: Moo Jin Kim, Yihuai Gao, Tsung-Yi Lin, Yen-Chen Lin, Yunhao Ge, Grace Lam, Percy Liang, Shuran Song, Ming-Yu Liu, Chelsea Finn, Jinwei Gu
- 机构: NVIDIA + Stanford University
- arXiv: 2601.16163
- 开源: 代码、模型权重、训练数据全部公开

## 一句话总结
将预训练视频生成模型（Cosmos-Predict2-2B）通过 **latent frame injection**（将动作/本体感知/价值编码为 latent frame）无架构修改地单阶段微调为统一的策略+世界模型+价值函数，在 LIBERO (98.5%) 和 RoboCasa (67.1%) 上 SOTA，并支持基于世界模型的 best-of-N 规划进一步提升。

## 问题
1. **如何有效利用视频模型的时空先验**：现有 video-based robot policies 要么需要多阶段训练（先微调视频模型、再训练独立 action module），要么引入新架构组件（IDM、单独 action diffuser），增加复杂性
2. **如何统一策略、世界模型和价值函数**：先前工作使用独立模块分别实现 policy、world model 和 value function，且通常从头训练
3. **如何用有限 rollout 数据实现有效规划**：仅靠 demonstration 数据训练的世界模型难以泛化到 OOD 状态

## 方法
- **方法线归属**: World Model + VLA → **流派B: 视频+动作联合去噪**（同一 latent diffusion 框架内同时处理视频帧和动作/状态/价值）
- **核心 idea**: 不修改预训练视频模型架构，直接将动作、本体感知、价值编码为 latent frames 插入视频 diffusion 序列，通过单阶段微调让视频模型学会生成这些新模态
- **关键技术点**:

### 1. Latent Frame Injection（核心机制）
- 将非图像模态（action chunk、robot proprioception、value）标准化到 [-1,+1] 后 flatten 并 duplicate 填充为 H'×W'×C' 的 latent volume
- 直接插入/覆盖视频 diffusion 的 latent frame 序列中对应位置
- 多相机图像同样通过插入额外 latent frames 支持
- 序列结构：(blank, proprio, wrist_cam, cam1, cam2, action, future_proprio, future_wrist, future_cam1, future_cam2, value) = (s, a, s', V(s'))
- **无需任何架构修改**——完全复用视频模型的 diffusion transformer、VAE tokenizer、cross-attention 等

### 2. 联合训练策略+世界模型+价值函数
- 通过 **conditioning mask** 控制哪部分 latent 是条件、哪部分是生成目标，决定训练的是 policy / world model / value function
  - Policy: 条件 s, 生成 (a, s', V(s'))
  - World model: 条件 (s, a), 生成 (s', V(s'))  
  - Value function: 条件 (s, a, s'), 生成 V(s')
- 训练 batch 分配: 50% demonstrations → policy, 25% rollouts → world model, 25% rollouts → value function
- **辅助目标**: policy 不仅预测 a，还同时预测 s' 和 V(s')，提供额外监督（消融实验验证有效）

### 3. 基于世界模型的规划 (Model-Based Planning)
- **Dual deployment**: 原始 checkpoint 作为 policy model，在 rollout 数据上微调的 checkpoint 作为 planning model
- **Best-of-N sampling**: 从 policy 采样 N 个动作候选 → planning model 预测每个候选的未来状态和价值 → 选择最高价值动作
- **Ensemble robustification**: 每个动作查询 3 次世界模型、5 次价值函数，总计 15 个价值预测，用 "majority mean"（先判断多数预测成功/失败，再在多数组内取均值）
- **V(s') vs Q(s,a)**: 实验表明 model-based V(s') 优于 model-free Q(s,a)，前者利用了学到的环境动力学

### 4. 噪声分布调整（重要工程细节）
- 原始 Cosmos-Predict2 的 log-normal σ 分布偏重低噪声区域，不利于动作精确生成
- 改为 **hybrid log-normal-uniform 分布**（70% log-normal + 30% uniform[1,85]），增加高噪声权重
- 推理时设置更高的 σ_min = 4（而非 0.002），避免低噪声区的不准确去噪

### 5. 并行 vs 自回归解码
- 直接策略评估: 并行解码（速度快，只需 action）
- 规划模式: 自回归解码 action → s' → V(s')（质量更高）

## 实验

### Benchmark 与主要结果
| Benchmark | Cosmos Policy | 次优方法 | 备注 |
|-----------|--------------|---------|------|
| LIBERO (4 suites avg) | **98.5%** | CogVLA 97.4% | 新 SOTA，每套 500 trials × 3 seeds |
| LIBERO-Long | **97.6%** | CogVLA 95.4% | 长时序任务提升最显著 |
| RoboCasa (24 tasks avg) | **67.1%** (50 demos) | FLARE 66.4% (300 demos) | 仅用 50 demo 超越用 300 demo 的方法 |
| ALOHA 4 tasks avg score | **93.6** | π₀.5 88.6 | 双臂真机，4 任务 101 trials |

### ALOHA 真机细节
- 4 个挑战任务: put X on plate (语言跟随)、fold shirt (长时序接触丰富)、put candies in bowl (高多模态)、put candy in ziploc bag (毫米级精度)
- Cosmos Policy 在后两个高难度任务显著领先: candies 89.6 vs π₀.5 95.2, ziploc 85.4 vs π₀.5 61.5
- **关键发现**: π₀.5 在高精度抓取（ziploc bag slider）失败，OpenVLA-OFT+ 的 L1 回归在高多模态任务中在两个目标之间犹豫

### 规划实验
- 在 ALOHA 最后两个困难任务上，model-based planning (V(s')) 比无规划基线 **平均提升 12.5 分**
- Model-based V(s') > Model-free Q(s,a)，归因于 V(s') 利用了学到的环境动力学，数据效率更高
- 世界模型在 rollout 数据微调后能更准确预测失败状态（如 ziploc bag 滑落）

### 消融实验
| 消融 | LIBERO Avg SR | 变化 |
|------|--------------|------|
| Full Cosmos Policy | 98.5% | — |
| w/o auxiliary losses | 97.0% | -1.5% |
| w/o pretrained model (from scratch) | 94.6% | -3.9% |
| w/o future state supervision (RoboCasa) | 44.4% | -22.7% |

- **预训练很重要**: 从头训练降 3.9%，且真机上动作抖动可能损坏机器人
- **辅助目标很重要**: 去掉辅助 loss 降 1.5%
- **未来状态预测是关键**: RoboCasa 上去掉所有未来状态监督直接从 67.1% 暴降至 44.4%

### 对比基线
- Diffusion Policy (从头训练的 diffusion), Dita, UVA, UWM, Video Policy
- Fine-tuned VLAs: π₀, π₀.5, OpenVLA-OFT, OpenVLA-OFT+, CogVLA, UniVLA, DP-VLA, GR00T-N1.5
- FLARE, GR00T-N1.5+HAMLET, GR00T-N1+DreamGen 等 world model 增强方法

### 推理延迟
- 并行生成 (5 steps): 0.61s / action chunk on 1 H100
- 并行生成 (10 steps): 0.95s on 1 H100
- 并行生成 (1 step): 0.16s on 1 H100（RoboCasa 仅损失 0.7%）
- Model-based planning (N=8): ~4.9s on 8 parallel H100s

## 评价

### 优势
1. **极致简洁**: 无架构修改、无新模块、单阶段微调——将复杂的 video→policy 适配简化为 latent frame injection + conditioning mask
2. **统一三合一**: 同一模型同时是 policy + world model + value function，通过 conditioning mask 切换功能，优雅利用视频 diffusion 的 native 能力
3. **数据高效**: RoboCasa 仅用 50 demos 超越用 300-3000 demos 的方法（FLARE、UWM、GR00T-N1.5 等），说明视频预训练先验的强大价值
4. **多模态动作分布建模优势**: 在高多模态任务（candies）和高精度任务（ziploc bag）上显著优于 VLA（π₀.5、OpenVLA-OFT+），验证了 latent diffusion 建模动作分布的天然优势
5. **规划能力**: 从 demonstration-only 到 rollout-enhanced planning 的渐进提升路径设计合理

### 局限
1. **推理延迟**: 规划模式需 ~5 秒/chunk on 8 GPU，不适合动态任务
2. **规划依赖大量 rollout 数据**: 648 条 rollout 才获得有效规划，数据获取成本高
3. **单层搜索树**: 仅 best-of-N 一步前瞻，缺乏深度规划能力
4. **模型规模与计算**: 2B 参数 + latent diffusion，训练需 32-64 H100 48 小时
5. **未验证跨具身泛化**: 所有实验都是 per-platform training，未展示跨具身迁移能力
6. **LIBERO 接近饱和**: 98.5% 的 LIBERO 区分度已很低

### 对 VLA 领域的贡献
1. **确立 "视频模型 → 策略" 的最简适配范式**: latent frame injection 证明预训练视频 diffusion model 无需架构修改即可成为强 policy，为社区提供了比 Video Policy（多阶段）、UVA/UWM（自定义架构）更简洁的替代
2. **刷新 World Model + VLA 流派B 的 SOTA**: 统一的策略/世界模型/价值函数设计让联合去噪范式从概念验证走向实际效用
3. **验证视频预训练 > VLM 预训练（在低层控制场景）**: 在 ALOHA 真机上超越经过大规模动作数据预训练的 π₀.5 和 OpenVLA-OFT+，支持"时空动力学先验比静态图文语义先验更适合低层控制"的假说
4. **planning-from-experience 路径**: 展示了从 BC 出发、通过 rollout 收集逐步提升的实用路径，弥合了纯 BC 和 RL 之间的鸿沟

## 与已有工作的关系

### vs Video Policy / UVA (多阶段 video→policy 方法)
- Video Policy: 先微调视频模型，再训练独立 action module → 两阶段
- UVA: 联合视频+动作但从头训练 → 无视频预训练先验
- Cosmos Policy: 单阶段微调 + 无架构修改 + 预训练先验 → 更简洁更强

### vs π₀ / π₀.5 (VLM + Flow Head)
- π₀/π₀.5 的预训练基座是 VLM (PaliGemma)，学的是静态图文语义
- Cosmos Policy 的预训练基座是视频生成模型，学的是时空动力学
- 两者代表了不同的预训练先验假设：**语义知识 vs 物理动力学**
- Cosmos Policy 在需要精确低层控制的任务（ziploc bag, candies）上优势更大

### vs FLARE / GR00T-N1.5 (流派A: 隐式世界模型)
- FLARE 用 future token 做隐式前瞻，不生成显式未来帧
- Cosmos Policy 生成显式未来状态图像 + value，支持 best-of-N planning
- 两者都来自 NVIDIA，代表 NVIDIA 在 world model + VLA 方向的两条平行探索

### vs DreamZero (同为流派B 联合去噪)
- DreamZero 14B 基于 Wan2.1，强调零样本泛化
- Cosmos Policy 2B 基于 Cosmos-Predict2，强调单平台微调 + planning
- 互补的规模和功能定位

### vs Diffusion Policy (从头训练)
- Cosmos Policy 可视为 "Diffusion Policy + 视频预训练先验 + 世界模型 + 价值函数" 的升级
- LIBERO: 98.5% vs 72.4%, 巨大提升
