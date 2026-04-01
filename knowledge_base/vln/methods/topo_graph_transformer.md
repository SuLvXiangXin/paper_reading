# 流派 A: 拓扑图 + Transformer

## 核心思路
在导航过程中构建显式拓扑图（或网格地图、BEV 地图），用 Transformer 在图上做全局-局部推理。

## 优势
- 显式空间表征，可解释性强
- 全局规划能力好（避免局部最优）
- 可以利用历史信息（回溯、重访）

## 局限
- 依赖准确的定位和建图
- 图的构建和维护有计算开销
- 离散→连续环境的迁移需要额外的 waypoint 预测

## 代表工作

### DUET (Chen et al., CVPR 2022) — 231 引用
双尺度图 Transformer，同时在全局拓扑图和局部子图上推理。开创了图 Transformer 做 VLN 的范式。

### ETPNav (An et al., 2023) — 171 引用
将 DUET 扩展到连续环境，进化拓扑地图 + waypoint 预测。VLN-CE 上的强基线。

### GridMM (Wang et al., ICCV 2023) — 125 引用
网格记忆地图，将拓扑图替换为结构化的网格表征，更好地编码空间关系。

### BEVBert (An et al., 2022) — 125 引用
BEV 鸟瞰图预训练，融合拓扑图和度量地图的优势。

## 发展趋势
- 从离散导航图 → 连续环境（ETPNav）
- 从纯拓扑 → 融合度量信息（BEVBert, GridMM）
- 逐渐被视频流方法（NaVid）和 LLM 方法（NavGPT）超越/替代
