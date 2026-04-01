# HG-DAgger: Interactive Imitation Learning with Human Experts (2019)

## 基本信息
- 作者: Michael Kelly, Chelsea Sidrane, Katherine Driggs-Campbell, Mykel J. Kochenderfer
- 机构: Stanford University, UIUC
- arXiv: 1810.02890
- 发表: ICRA 2019
- 开源: 无公开代码

## 一句话总结
通过让人类专家保持完整控制权（而非 DAgger 的随机切换），解决 human-in-the-loop 模仿学习中 RC 采样造成的 actuator lag 和标签质量下降问题，同时用集成神经网络的 "doubt" 指标学习数据驱动的安全阈值。

## 问题

### 背景：DAgger 的局限
DAgger（Ross & Bagnell, 2010）通过让 Novice 影响采样分布（Robot-Centric Sampling, RC Sampling）来解决 Behavioral Cloning 的 distribution shift 问题：训练时以概率 β 执行人类动作、(1-β) 执行 Novice 动作，人类在 Novice 采样的状态上提供矫正标签。

### 核心问题：人类作为专家时 RC Sampling 的问题
1. **感知 actuator lag**: DAgger 随机切换 Novice/Human 控制权 → 人类感受到控制时延 → 标签质量下降，行为发生偏移
2. **安全性降低**: 部分由未训练完成的 Novice 控制系统 → 物理系统存在安全隐患
3. **β 调参困难**: β 过高 → 退化为 Behavioral Cloning（compounding error）；β 过低 → 人类失去反馈、标签质量差；且物理系统上调参代价昂贵
4. **人类适应偏移**: 人类察觉到控制权被分享 → 过度补偿 → 学到与无干扰时不同的行为

**根本问题**: RC Sampling 对人类专家的假设是不合理的——人类需要连续、完整的控制反馈才能给出高质量示教。

## 方法

- **方法线归属**: **Human-in-the-Loop 模仿学习 / 交互式数据采集**——这是 DAgger 系列变体的一个分支，专门针对人类专家的心理/认知局限设计数据采集策略。与 EnsembleDAgger 同系列，但更强调人类控制权。

### 核心 Idea：Human-Gated DAgger

让**人类决定何时接管**，而不是算法随机切换控制权：

1. Novice 正常运行，人类观察
2. 人类判断 Novice 进入危险状态 → 人类**主动接管**（完整控制权）
3. 人类将系统引导回安全状态后，手动交还控制权给 Novice
4. **标签只在人类控制期间收集**（含 BC 初始化阶段），此时人类有完整控制反馈

```
Gating function: g(x_t) = 1[x_t not in P]  (P = 人类判断的安全状态集)
Rollout policy:  pi_i(x_t) = g(x_t)*pi_H(x_t) + (1-g(x_t))*pi_N_i(o_t)
Data collected:  D_i = {(O(x_t), pi_H(x_t)) | g(x_t)=1, x_t in rollout_i}
```

**关键优势**: 人类始终在完整控制状态下提供示教，无 actuator lag，高质量标签；Novice 在安全区域自主运行，样本效率提高。

### 不确定性驱动的风险度量：Doubt Metric

使用**集成神经网络**表示 Novice（近似 Gaussian Process）：

- Doubt 度量: `d_N(o_t) = ||diag(C_t)||_2`（C_t 为集成输出的协方差矩阵主对角线 L2 范数）
- **语义**: doubt 高 → 训练数据稀疏的区域 → 可能高风险（人类会避开高风险区域，导致这些区域欠采样）

### 数据驱动的安全阈值学习

不需要手动设置 doubt 阈值，从**人类干预数据**中学习：

```
I = 人类接管瞬间的 doubt 记录（intervention logfile）
tau = mean(I[0.75N:N])  // 取最后 25% 干预记录的均值
```

**设计理由**: 训练后期的干预更具代表性（Novice 更成熟，干预对应真正的边界情况）；取 25% 而非最后一个是为了平滑噪声。

最终用 `P_hat = {x_t | d_N(O(x_t)) <= tau}` 近似"安全集"，可用于评估训练好策略在不同区域的风险。

## 实验

### 任务设置
- **任务**: 自动驾驶——在两车道路上绕过静止障碍物（无碰撞、不出界）
- **观测**: 距路中线距离 y、朝向角 θ、速度 s、到车道边缘距离 (l_l, l_r)、到最近障碍距离 (d_l, d_r)
- **动作**: 方向盘角度 + 速度指令
- **数据量**: BC 预训练 10,000 标签 + 每 epoch 2,000 标签 × 5 epochs
- **对比方法**: Behavioral Cloning、DAgger（β=0.85 初始，每 epoch × 0.85 衰减）

### 仿真结果（学习曲线）
- HG-DAgger：更快收敛、更稳定（road departure rate 和 collision rate 均最低）
- DAgger：后期训练不稳定——β 减小时 Novice 控制比例增加 → actuator lag 加剧 → 标签质量下降

### 安全阈值验证（仿真）
在学到的安全集内 P_hat vs 外 P_hat' 初始化，评估 Novice 性能：

| 初始化区域 | 碰撞率 | 出界率 | 出界时长 |
|-----------|--------|--------|---------|
| P_hat（安全集内） | 0.607e-3 | 0.607e-3 | 1.63s |
| P_hat'（安全集外）| 7.533e-3 | 12.092e-3 | 3.74s |

碰撞率差 12x，出界率差 20x，验证了 doubt 阈值的有效性。

### 真实车辆结果
在 MG-GS 实车上测试（LiDAR + 高精定位，5 个随机障碍物配置）：

| 方法 | 碰撞次数 | 出界次数 | Bhattacharyya 距离（vs 人类） |
|------|---------|---------|-------------------------------|
| Behavioral Cloning | 1 | 6 | 0.1173 |
| DAgger | 1 | 1 | 0.1057 |
| HG-DAgger | 0 | 0 | 0.0834 |

- 唯一零碰撞、零出界的方法
- 方向盘分布比 DAgger 更接近人类（21.1% 提升，Bhattacharyya 距离）

## 评价

### 优势
1. **直觉清晰，实用性强**: "人类保持完整控制权" 这一核心 idea 在物理机器人上易于实现，无需复杂的切换机制
2. **数据驱动阈值学习**: 避免了手动设置风险阈值的困难，从人类干预行为中自动学习，是一个 elegant 的设计
3. **同时解决安全和标签质量**: 单一机制（人类门控）同时改善了训练安全性和标签质量
4. **在真实车辆上验证**: 许多模仿学习论文只在仿真中验证，这篇在真实汽车上展示了零事故

### 局限
1. **依赖人类反应速度**: HG-DAgger 在人类无法快速识别/响应危险的场景下不适用（论文自己承认）
2. **仅限于行为克隆框架**: 无语言条件、无跨具身泛化，数据规模小（百级示教），不具备现代 VLA 的泛化能力
3. **评估规模有限**: 真实车辆只测了 5 个配置，统计显著性有限
4. **未解决 test-time 安全**: 学到的 τ 目前只用于分析，未来才计划用于自动切换控制器

### 对 VLA / 机器人学习的贡献
1. **人类数据采集范式**: HG-DAgger 的思想直接影响了现代机器人遥操作数据采集——让专家保持完整控制（如 EgoMimic、EgoScale 中人类演示的全程主导权），而非被算法打断
2. **模型不确定性用于安全边界**: 集成方法估计 doubt + 数据驱动阈值的思想在后续工作中有回响（uncertainty-based gating in deployment）
3. **RC Sampling 问题的系统分析**: 首次明确指出 DAgger 在人类专家设定下的不适用性，为人类数据采集提供了理论基础

### 与相关工作的关系
- **DAgger (Ross & Bagnell 2010)**: 解决了 DAgger 在人类专家设定下的核心缺陷（RC Sampling + actuator lag）
- **EnsembleDAgger (Menda 2018)**: HG-DAgger 借鉴了其集成 doubt 度量，但区别是：EnsembleDAgger 用 doubt 自动门控、HG-DAgger 由人类门控 + doubt 只用于阈值学习
- **Confidence-Based Autonomy (Chernova & Veloso 2009)**: 最相近的方法——允许专家随时干预，也允许 Novice 主动请求演示。HG-DAgger 的区别：不允许 Novice 主动请求（避免切换行为）+ 用集成 NN 而非 GMM
- **EgoMimic / EgoScale (2024-2026)**: 现代人形机器人数据采集中的"人类主导全程"思想的远亲——核心精神一脉相承
