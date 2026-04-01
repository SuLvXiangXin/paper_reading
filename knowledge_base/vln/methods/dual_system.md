# 流派 E: 双系统/层级式

## 核心思路
将导航解耦为高层规划（System 2）和低层执行（System 1），各司其职。

## 代表工作

### DualVLN (Wei et al., 2025) — 10 引用（锚点论文）
首个双系统 VLN 基础模型。System 2 = VLM 全局规划器，System 1 = DiT 局部执行器。

### NavDP (Cai et al., 2025) — 35 引用
Sim-to-Real 扩散策略导航，DualVLN System 1 的核心技术。

### Hi Robot (Shi et al., ICML 2025) — 147 引用
层级式 VLA 模型（Stanford Chelsea Finn 组），高层语言规划 + 低层动作执行。

## 设计哲学
- 认知科学启发：快思考（直觉执行）vs 慢思考（深度推理）
- 解耦训练：高层保持语言泛化，低层专注运动质量
- 适合真实世界部署（低层可实时，高层可离线）
