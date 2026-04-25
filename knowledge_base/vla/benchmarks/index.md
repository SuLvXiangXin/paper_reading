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

### Ego / Human-Data 相关评测 🆕
- **Ego Humanoid Manipulation Benchmark**：EgoVLA 使用的短时/长时双臂灵巧手机器人任务，区分 seen/unseen visual configurations
- **EgoZero Franka tasks**：7 个真机任务（open oven door、put bread on plate、sweep board、erase board、sort fruit、fold towel、insert book in shelf），验证 smart-glasses human demo 的 robot-free zero-shot policy
- **EMMA mobile manipulation tasks**：Table Service、Handover Wine、Grocery Shopping、Push Chair，每设置 50 trials，强调 mobile base + manipulation 的 human-data co-training
- **EgoHumanoid G1 tasks**：Pillow Placement、Trash Disposal、Toy Transfer、Cart Stowing，验证 ego human demos 对 humanoid loco-manipulation 的迁移
- **UniDex tool-use tasks**：Make Coffee、Sweep Objects、Water Flowers、Cut Bags、Use Mouse，评估异构灵巧手统一动作空间和 ego-video pretraining

### Egocentric Perception / Hand Motion Benchmarks 🆕
- **Uni-Hand**：EgoPAT3D-DT、H2O-PT、HOT3D-Clips、CABH/CABH-E，以及 Hand-ALOHA-Transfer 下游验证
- **HaWoR**：DexYCB camera-frame hand pose、HOT3D world-space hand/camera trajectory、EPIC-KITCHENS qualitative
- **MEgoHand**：TACO、HOI4D、H2O、HOT3D、OakInk2 in-domain，ARCTIC/HOLO cross-domain
- **OpenMMEgo**：EgoSchema、EgoPlan、QAEgo4D、EgoTaskVQA、OMEBench，并检查通用视频能力是否损伤

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

### GigaAI / World-Model Data Engine 评测 🆕
- **GigaWorld-0**：PBench Robot Set、DreamGen Bench，重点评估 embodied video/action data generation 质量，而非直接 policy benchmark
- **GigaBrain-0**：G1 与 PiPER 真机，覆盖 laundry folding、paper towel preparation、juice preparation、table bussing、boxes moving、laundry baskets moving 以及外观/摆放/视角泛化
- **GigaBrain-0.5M***：8 个 GigaAI 内部真机任务、RoboChallenge 30 标准任务、RAMP value prediction
- **GigaWorld-Policy**：RoboTwin 2.0 50 任务 clean/randomized、PiPER 真机 Clean Desk / QR Scan / Sweep Trash / Stack Bowls、A100 推理延迟
- **π-StepNFT**：LIBERO 4 suites few-shot、ManiSkill PutOnPlateInScene IND/OOD
- **ViVa**：Box Assembly 真机 RECAP 对比、shirt folding / box packaging / toilet paper organization value analysis、pants folding OOD value generalization

### 官方技术页 / 非公开 Benchmark 🆕
- **Figure Helix 系列**：Helix、Helix Logistics、Scaling Helix Logistics、Project Go-Big、Helix 02 均以官方视频或内部指标为主；可记录为技术路线信号，但不要与 LIBERO/RoboCasa/ALOHA 等可复现 benchmark 等同
- **典型内部指标**：物流 normalized effective throughput、移动输送带包裹秒/件、条码朝向扫描成功率、公开视频任务长度与动作数

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
| RoboTwin 2.0 | GigaWorld-Policy | 0.86 simulation SR | 2026.03 | Action-centered WAM，50 任务 |
| RoboChallenge | GigaBrain-0.5M* | 51.67% avg SR | 2026.02 | World model-conditioned RL 后训练 |
