# EgoScale: Scaling Dexterous Manipulation with Diverse Egocentric Human Data (2026)

## 基本信息
- 作者: Ruijie Zheng*, Dantong Niu*, Yuqi Xie*, Jing Wang, Mengda Xu, Yunfan Jiang, Fernando Castañeda, Fengyuan Hu, You Liang Tan, Letian Fu, Trevor Darrell, Furong Huang, Yuke Zhu†, Danfei Xu†, Linxi Fan†
- 机构: NVIDIA (主导) + UC Berkeley + University of Maryland
- arXiv: 2602.16710
- 链接: https://research.nvidia.com/labs/gear/egoscale/

## 一句话总结
首次在 20,854 小时大规模 egocentric 人类视频上预训练 flow-based VLA，揭示 human action prediction loss 与数据规模的 log-linear scaling law，并通过"大规模人类预训练 → 轻量对齐 mid-training → 任务 post-training"三阶段配方，在 22-DoF 灵巧手上实现 54% 平均成功率提升和 one-shot 新任务泛化。

## 问题
先前 human-to-robot transfer 工作存在两个核心局限：
1. **数据规模有限**：大多使用十到数百小时的人类数据，无法覆盖长尾操作行为的多样性
2. **聚焦低自由度末端**：多数方法针对夹爪或低 DoF 手，未涉及高 DoF 灵巧手的精细手指控制

**核心问题**：大规模人类数据能否作为高 DoF 灵巧操作的可预测、可扩展的监督信号？如何有效弥合人手与机器人灵巧手之间的具身差距？

## 方法
- **方法线归属**: VLM + Diffusion/Flow Head（基于 GR00T N1 架构）+ Human Data Pretraining（流派 A: Egocentric 视频 + 手部追踪 → 直接训练 Policy）
- **核心 idea**: Human-to-robot transfer 本质是一个 scaling phenomenon。通过在 20K+ 小时 egocentric 人类视频上用 wrist motion + retargeted hand joint actions 作为监督预训练 VLA，再用少量对齐的 human-robot 数据 mid-training，将规模（Stage I）和对齐（Stage II）解耦，高效迁移到灵巧机器人控制。

### 关键技术点:

#### 1. Human Action Representation（人类动作表示）
- **Wrist-level Arm Motion**: 相对 SE(3) 末端执行器运动 ΔW^t = (W^0_w)^{-1} W^t_w，去除全局相机运动依赖，人类与机器人共享同一表示
- **Hand Articulation**: 21 个人手 keypoints 通过基于优化的 retargeting 映射到 22-DoF Sharpa 手关节空间（CasADi + IPOPT），保留人手手指关节信息的同时对齐机器人控制接口
- **关键发现**: Retargeted joint-space actions 远优于 wrist-only（缺失手指信息）和 fingertip-based（小误差导致不合理关节配置）两种替代方案

#### 2. 两阶段数据管线（Scale ↔ Alignment 解耦）
- **Stage I - 大规模 Egocentric 预训练数据**: 
  - 20,854 小时 egocentric 视频（30 FPS），来自 in-the-wild 采集（零售、家庭、工业等），覆盖 9,869 个场景、6,015 个任务、43,237 个物体
  - 用 off-the-shelf SLAM + hand pose estimation 提取相机运动和手部轨迹（有噪声但规模补偿）
  - 补充 829 小时 EgoDex 数据集（Apple Vision Pro 高精度追踪），提供精确运动学锚定
- **Stage II - 对齐 Human-Robot Mid-Training 数据**: 
  - 344 个桌面任务，每任务约 30 条人类轨迹 + 5 条机器人轨迹（共 ~50 小时人类 + ~4 小时机器人）
  - **关键对齐**: 人类演示使用与机器人相同的相机配置（匹配视角和内参），手部动作用 Vive tracker + Manus 手套采集，与遥操作 motion-capture 一致
  - **作用**: 将 Stage I 学到的抽象操作结构锚定到机器人的感知和控制空间

#### 3. 模型架构（基于 GR00T N1）
- **VLM backbone**: 预训练视觉语言模型编码图像 + 语言指令为 vision-language embedding φ_t
- **DiT action expert**: Flow-matching 目标预测 action chunk
- **人类数据处理**: 无 proprioception 时用 learnable placeholder token 替代 q_t
- **跨具身适配**: 轻量级 embodiment-conditioned MLP adapters（输入/输出端），用于不同机器人手的关节空间映射；wrist motion、VLM backbone、DiT expert 完全共享

#### 4. 三阶段训练配方
- **Stage I (Human Pretraining)**: 256 GB200 GPUs, batch=8192, lr=5e-5, 100K steps, **全参数解冻**
- **Stage II (Aligned Mid-training)**: batch=2048, lr=3e-5, 50K steps, **冻结 VLM backbone**，仅更新 vision encoder + DiT action expert
- **Stage III (Post-training)**: batch=512, lr=3e-5, 10K steps, 任务特定机器人演示（通常 20-100 条）

## 实验

### 主要评测平台
- **Galaxea R1Pro**: 双臂轮式人形机器人 + 22-DoF Sharpa Wave 灵巧手
- **Unitree G1**: 7-DoF 三指手（验证跨具身迁移）
- **感知**: 头部 ego 相机 + 双腕内侧相机（面向手掌）

### Benchmark: 5 个高灵巧度真机任务
1. **Shirt Rolling**: 协调双手折叠/卷T恤放入篮中（可变形物体）
2. **Card Sorting**: 手指摩擦分离单张卡片并插入对应颜色的卡槽
3. **Tong Fruit Transfer**: 从工具箱抓取夹子→用夹子夹水果→放置
4. **Bottle Cap Unscrewing**: 持续旋转拧开小瓶盖（4 种瓶子）
5. **Syringe Liquid Transfer**: 拿注射器→抽液→注射→丢弃（最难，长时序多步推理）

### 主要结果

#### RQ1: 大规模人类预训练的效果
| 方法 | Avg Task Completion | Avg Success Rate |
|------|-------------------|-----------------|
| No Pretrain | 0.24 | 0.02 |
| Midtrain Only | 0.53 | 0.28 |
| Human Pretrain | 0.71 | 0.38 |
| **Human Pretrain + Midtrain** | **0.83** | **0.56** |

- 人类预训练（无对齐）已超过 midtrain-only 基线
- 两者结合效果最佳：平均成功率 56% vs 无预训练 2%（**+54%**）

#### RQ2: Scaling Law
- 数据规模 1k→2k→4k→10k→20k 小时
- **Log-linear scaling law**: L = 0.024 - 0.003·ln(D), R² = 0.9983
- 任务完成率从 1k 小时的 0.30 单调增至 20k 小时的 0.71，无饱和迹象
- 小数据集（1k-2k 小时）出现过拟合，大数据集（10k-20k）训练过程稳定单调下降

#### RQ3: One-shot 新任务泛化
- **Fold Shirt**: 1 条机器人 demo + 100 条人类 demo → 88% 成功率
- **Unscrewing Water Bottles**: 1 条 demo/瓶 → 55% 成功率
- 缺少大规模预训练或 mid-training 的模型在 one-shot 设定下完全失败

#### RQ4: 跨具身迁移（G1 三指手）
- Pen in Bin / Dish Handover in Rack 两个任务
- 人类预训练 + midtrain 相比无预训练基线在两个任务上均 **>30% 绝对提升**
- 即使 22-DoF → 7-DoF 三指手的巨大运动学差异，人类预训练仍然有效

#### RQ5: 动作表示消融
- Retargeted Joint-space > Fingertip-based > Wrist-only
- Wrist-only 在需要精细手指控制的任务上严重失败
- Fingertip 表示因小误差导致不合理关节配置

### 对比基线
- No Pretrain（从头训练）
- Midtrain Only（仅 mid-training 数据预训练）
- 不同数据规模的人类预训练变体
- 不同动作表示的消融

## 评价

### 优势
1. **首个 scaling law for human-to-robot transfer**: L = 0.024 - 0.003·ln(D) 的 log-linear 关系（R²=0.9983）是该领域最干净的 scaling 结果，且验证了 offline loss 与真机性能的强相关性
2. **数据规模前所未有**: 20,854 小时人类数据，比 prior work（EgoMimic ~数百小时, EgoDex 829 小时）大 20x+，真正展示了"量变引发质变"
3. **简洁有效的 recipe**: Scale → Align → Post-train 三阶段清晰解耦，设计简单但效果显著（+54%），实用价值高
4. **灵巧操作的复杂度新标杆**: Syringe Liquid Transfer 等任务需要长时序推理 + 精密空间对齐 + 灵巧工具使用，是 VLA 领域少见的高难度评测
5. **one-shot 泛化能力涌现**: 仅 1 条机器人 demo 即可完成新任务（88% shirt folding），说明人类预训练提供了强大的 motor prior
6. **跨具身泛化**: 22-DoF → 7-DoF 三指手的成功迁移证明人类运动先验具有 embodiment-agnostic 特性

### 局限
1. **计算资源极高**: 256 GB200 GPUs 进行 Stage I 训练，工业级资源门槛
2. **未开源**: 模型、数据、训练代码均未公开（NVIDIA 闭源），可复现性差
3. **对齐数据仍需精心采集**: Stage II 的 50 小时人类 + 4 小时机器人数据需要匹配相机配置和 mocap 设备，采集成本不低
4. **评测任务有限**: 仅 5 个核心任务（+ 2 个 one-shot + 2 个 G1），缺乏标准化 benchmark 的可比性
5. **Scaling law 的适用范围**: 仅在 1k-20k 小时范围内验证，是否在更大规模上继续成立未知
6. **Stage I 数据的手部追踪质量**: off-the-shelf SLAM + hand pose 在 in-the-wild 场景中噪声较大，论文虽称"规模补偿"但未量化噪声影响
7. **与 GR00T N1 的关系不明**: 架构直接复用 GR00T N1，但未清晰说明 EgoScale 的独立贡献 vs 基础架构的贡献

### 对 VLA 领域的贡献
1. **确立人类数据作为灵巧操作的可扩展监督源**: 不同于 prior work 的小规模验证，EgoScale 在真正大规模上证明了 human data scaling 的有效性和可预测性
2. **提出实用的三阶段 human-to-robot recipe**: Scale（人类数据）→ Align（对齐数据）→ Specialize（任务数据），为后续工作提供了清晰的方法论模板
3. **揭示 scaling law**: 为"需要多少人类数据"提供了定量预测工具，类似 LLM 领域的 Chinchilla scaling law 之于模型训练
4. **证明 retargeted joint-space 是最优的人类动作表示**: 为 egocentric human data → dexterous manipulation 的 pipeline 中的动作表示选择提供了明确的实验指导

### 与相关工作的对比

| 维度 | EgoScale | EgoMimic (2024) | EgoVLA (2025) | Being-H0/H0.5 | Emergence of H2R (PI) |
|------|----------|-----------------|---------------|----------------|----------------------|
| 人类数据规模 | 20,854 h | ~数百 h | ~数百 h | 35K+ h (H0.5) | 大规模跨具身 |
| 灵巧手 DoF | 22-DoF | 低 DoF | 低 DoF | 多种 | 低 DoF 为主 |
| Scaling Law | ✅ 定量 | ❌ | ❌ | ❌ | 定性 |
| One-shot 迁移 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 跨具身迁移 | ✅ (22→7 DoF) | ❌ | 有限 | ✅ | ✅ |
| 对齐策略 | Mid-training (50h+4h) | Co-training | IK+retargeting | Post-training | Co-training |
| 架构 | GR00T N1 (flow VLA) | ACT-style | VLA | MoT VLA | π 系列 |

### 关键洞察
- **EgoScale vs Being-H0.5**: 两者几乎同期（2026初），思路高度相似（大规模 ego 人类视频 VLA 预训练），但 EgoScale 聚焦 scaling law 和高 DoF 灵巧手，Being-H0.5 聚焦 MoT 架构和更广泛的跨具身适配
- **EgoScale vs Emergence of H2R (PI)**: PI 的发现是"transfer 在 VLA scale up 后自然涌现，不需要特殊设计"，EgoScale 则提出了显式的 alignment mid-training 阶段，认为少量精确对齐是关键——两者观点互补
- **本质贡献**: 将 "human data for robot learning" 从 "有效但小规模" 推向 "可预测、可扩展"，类似 NLP 中从 Word2Vec 到 GPT-3 的跨越
