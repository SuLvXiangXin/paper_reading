# 流派 D: 导航基础模型

## 核心思路
在大规模多机器人数据上预训练通用导航策略，支持跨机器人形态和跨场景迁移。

## 代表工作

### GNM (Shah et al., ICRA 2023) — 214 引用
三部曲第一作。首个跨机器人通用导航模型，6 种机器人形态。

### ViNT (Shah et al., CoRL 2023) — 277 引用
三部曲第二作。视觉导航基础模型，EfficientNet + Transformer。

### NoMaD (Sridhar et al., ICRA 2024) — 290 引用
三部曲第三作。扩散策略 + Goal masking，统一目标导向和探索。

### NaVILA (Cheng et al., RSS 2025) — 143 引用
四足机器人 VLA 导航模型（NVIDIA 出品），扩展到非轮式机器人。

## 关键人物
- **Dhruv Shah / Sergey Levine** (UC Berkeley)：GNM → ViNT → NoMaD 系列
- 这三篇加起来 781 引用，是导航基础模型方向的绝对核心
