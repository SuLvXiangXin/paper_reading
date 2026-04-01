# NoMaD: Goal Masked Diffusion Policies (2023)

## 基本信息
- **标题**: NoMaD: Goal Masked Diffusion Policies for Navigation and Exploration
- **作者**: Ajay Sridhar, Dhruv Shah, Catherine Glossop, Sergey Levine
- **机构**: UC Berkeley
- **arXiv**: 2310.07896
- **年份**: 2023 (ICRA 2024)
- **引用数**: 290
- **方法线归属**: **导航基础模型**

## 核心贡献
1. **首次将扩散策略用于目标条件导航**
2. **Goal Masking**：统一目标导向导航和无方向探索，单模型切换
3. **多模态动作分布**：天然处理岔路口等歧义场景
4. **19M 参数**超越 335M 参数的 Subgoal Diffusion

## 方法架构

### 三大组件
1. **视觉编码器**：两个 EfficientNet-B0
   - 观测编码器 ψ(o_i)：独立编码每帧 RGB (96×96)
   - 目标融合编码器 ϕ(o_t, o_g)：编码当前观测与目标图像的联合表征
   - 输出：256 维 token
2. **Transformer 解码器**：4 层 4 头，处理 7 个 token（5 历史 + 1 当前 + 1 目标）
   - 输出：上下文向量 c_t（average pooled）
3. **扩散策略解码器**：1D 条件 U-Net（15 层卷积）
   - 以 c_t 为条件，K=10 步去噪
   - 生成 **8 步未来动作序列**

### Goal Masking 机制
- 二值掩码 m：c_t = f(ψ(o_i), ϕ(o_t, o_g), m)
- m=1：屏蔽目标 token → **无方向探索**
- m=0：目标 token 正常参与 → **目标导向导航**
- 训练时 m ~ Bernoulli(0.5)，50% 有目标 50% 无目标

### 与 ViNT/GNM 的演进

| 维度 | GNM | ViNT | NoMaD |
|------|-----|------|-------|
| 视觉 | CNN | EfficientNet+Transformer | 同 ViNT |
| 动作预测 | MLP 回归 | MLP 回归 | **扩散模型** |
| 目标 | 必须有 | 必须有 | **可选（goal masking）** |
| 探索 | 无 | 需外挂 300M 扩散模型 | **内置** |
| 多模态 | 无 | 无 | **有** |
| 参数 | — | 16M+300M=316M | **19M** |

## 训练数据
- **GNM 数据集 + SACSoN 数据集**
- 跨多种地面机器人平台，100+ 小时真实世界轨迹
- 仅 RGB（无深度/LiDAR）

## 训练策略
- 端到端监督学习
- Loss = 扩散去噪 MSE + λ·时间距离预测 MSE（λ=10⁻⁴）
- AdamW, lr=10⁻⁴, 30 epochs, batch 256
- Square Cosine Noise Scheduler, K=10 去噪步

## 实验结果（真实世界 LoCoBot, 6 个环境）

### 探索任务
| 方法 | 参数 | 成功率 | 碰撞 |
|------|------|--------|------|
| Subgoal Diffusion | 335M | 77% | 1.7 |
| **NoMaD** | **19M** | **98%** | **0.2** |

### 导航任务
- NoMaD **90%** 成功率，与最强基线持平
- 参数量仅为 Subgoal Diffusion 的 **1/15**

## 消融实验关键结论
- 统一训练（探索+导航）**不损失**任何单项性能
- EfficientNet + Transformer + attention masking 是最优编码组合
- ViT 端到端训练扩散策略时优化困难（仅 32% 成功率）
- 扩散模型在岔路口稳定输出多模态分布，条件于目标后正确收敛

## 局限性
1. **仅支持目标图像**：不支持语言指令、GPS 等
2. **高层规划简单**：标准 frontier-based 探索，无语义引导
3. **仅地面机器人验证**
4. **开环 8 步执行**：无闭环反馈修正

## 关键技术细节
- 输入：96×96 RGB，过去 5 步 + 当前 + 可选目标
- 输出：8 步动作（10 步去噪）
- 总参数：19M（Transformer ~5M + EfficientNet + U-Net）
- 可在 NVIDIA Jetson Orin 上边缘部署
- 时间距离预测用于拓扑图边权重
- **DualVLN 的 System 1 直接借鉴了 NoMaD 的扩散策略导航思想**
