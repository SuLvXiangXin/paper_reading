# VLN 技术组件索引

## 视觉表征
- **全景图**: 360° 全景观测（R2R 标准）
- **视频流**: 连续 RGB 帧序列（NaVid, StreamVLN）
- **BEV 鸟瞰图**: 俯视视角的空间表征（BEVBert）

## 空间记忆
- **拓扑图**: 节点=位置，边=可达关系（DUET, ETPNav）
- **网格地图**: 结构化空间网格（GridMM）
- **语义地图**: 带标注的 2D 地图（MapNav）
- **隐式记忆**: 神经网络内部的隐状态（JanusVLN）
- **视频记忆**: 视频历史作为记忆（NaVid）

## 动作生成
- **离散选择**: 从候选 viewpoint 中选择（DUET）
- **Waypoint 预测**: 预测中间路径点（ETPNav, DualVLN System 2）
- **扩散策略**: 扩散模型生成连续轨迹（NoMaD, NavDP, DualVLN System 1）
- **直接回归**: 直接输出动作值（NaVid）
