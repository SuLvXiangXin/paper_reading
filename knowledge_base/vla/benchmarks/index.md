# Benchmark 概览

## 仿真 Benchmark

### LIBERO
- 桌面操作任务集，多个子集（LIBERO-Spatial, LIBERO-Object, LIBERO-Goal, LIBERO-Long 等）
- **当前 SOTA**：Cosmos Policy 98.5% (avg), Being-H0.5 98.9% (LIBERO-Long 单项)
- 注意：已高度饱和（98%+），区分度显著降低

### SimplerEnv
- 基于 Google Robot 和 WidowX 的仿真评测
- OpenVLA 等在此评测

### RoboCasa
- 家庭场景仿真 benchmark，24 个厨房操作任务
- **当前 SOTA**：Cosmos Policy 67.1% (仅 50 demos/task)，FLARE/GR00T-N1.5+HAMLET 66.4% (300 demos)
- 注意：Cosmos Policy 用远少于其他方法的 demo 数据达到 SOTA，验证视频预训练先验的数据效率优势
- 绝对值仍不高，有较大提升空间

### CALVIN
- 长时序桌面操作

### RLBench
- 丰富的桌面操作任务集

### Language Table
- 语言条件桌面操作

### Franka Kitchen
- 厨房操作场景

### Push-T, Block Pushing, RoboMimic
- Diffusion Policy 的评测基准（2D/3D 操作）

## 真机 Benchmark

### BridgeV2 (WidowX)
- 最常用的开源真机评测平台
- OpenVLA 在此建立了 7B 超越 55B 的标杆

### Google Robot (Everyday Robots)
- RT-2 的原始评测平台，已停产
- 6k 次评测，最大规模真机评测之一

### ALOHA 双臂操作平台 🆕
- 两个 ViperX 300 S 臂 + 三相机（顶部+双腕部）
- Cosmos Policy 在此平台进行了全面评测，4 个挑战任务 101 trials
- **当前最佳**: Cosmos Policy 93.6 avg score，超越 π₀.5 (88.6), π₀ (77.9), OpenVLA-OFT+ (62.0)
- 关键发现: 视频模型预训练在高多模态（candies）和高精度（ziploc bag）任务上优势显著

### 多平台真机评测
- π₀：7 种构型（UR5e、Franka、ARX、Trossen、移动平台等）
- π₀.5：移动操作平台，真实家庭评测
- **Being-H0.5**：5 种异构平台跨具身评测
  - PND Adam-U（灵巧手半人形）
  - Franka+Inspire（灵巧手臂）
  - Unitree G1（人形机器人）
  - BeingBeyond D1（教育臂）
  - SO-101（便携臂）
  - 涵盖单臂、灵巧手、半人形、全人形等形态
  - 首次展示单一检查点跨具身 zero-shot 迁移信号

### Open-world 真机评测
- π₀.5 首创：mock homes + real homes，10-15 分钟长时序任务

## SOTA 追踪
| Benchmark | SOTA 模型 | SOTA 分数 | 时间 | 备注 |
|-----------|----------|-----------|------|------|
| LIBERO (avg) | Cosmos Policy | 98.5% | 2026.01 | Being-H0.5 LIBERO-Long 单项 98.9% |
| RoboCasa (avg) | Cosmos Policy | 67.1% | 2026.01 | 仅 50 demos/task |
| ALOHA 双臂 (avg score) | Cosmos Policy | 93.6 | 2026.01 | 4 任务 101 trials |
| BridgeV2 (真机) | OpenVLA | — | 2024.06 | |
| 跨具身真机 (5平台) | Being-H0.5 | 显著优于 π₀.5 | 2026.01 | |
| Open-world 家庭 | π₀.5 | 60-90% 进度 | 2025 | |
