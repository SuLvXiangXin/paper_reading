# HoloMotion-1 Technical Report (2026)

## 基本信息
- 作者: Maiyue Chen, Kaihui Wang, Bo Zhang, Xihan Ma, Zhiyuan Yang, Yi Ren, Qijun Huang, Zihao Zhu, Yucheng Wang, Zhizhong Su
- 机构: Horizon Robotics
- arXiv: 2605.15336
- 链接: https://github.com/HorizonRobotics/HoloMotion, https://horizonrobotics.github.io/robot_lab/holomotion

## 标签
- domain: whole_body_control
- method_tags: [Motion Imitation, Foundation Models, Sparse MoE Transformer, Sequence-Level PPO]
- task_tags: [运动跟踪, 全身遥操作, 表达性动作]
- component_tags: [大规模预训练, 运动重定向, Sim-to-Real 迁移, KV-cache]
- benchmark_tags: [MuJoCo, IsaacLab, OMOMO, HumanAct12, TWIST2]
- data_tags: [MotionMillion, AMASS, LAFAN1, in-house teleoperation]
- robot_tags: [Unitree G1]
- application_tags: [zero-shot whole-body motion tracking, real-time teleoperation]

## 一句话总结
HoloMotion-1 用 2000+ 小时视频重建运动为主、MoCap 和自采遥操作数据为辅，训练稀疏 MoE Transformer 全身跟踪策略，在未见动作集和真实 Unitree G1 上零样本跟踪。

## 问题
传统 humanoid motion tracking 多依赖 AMASS/LAFAN1 等 MoCap 数据和中等规模 MLP policy，动作覆盖有限；直接使用大规模野外视频重建动作又会引入重建噪声、来源域差异和质量不均。HoloMotion-1 试图回答：能否把视频级运动多样性、Transformer 序列建模和实时闭环控制结合起来，形成可部署的 WBC motion foundation model。

## 方法
- 方法线归属: Motion Imitation / Foundation Model WBC
- 核心 idea: 以 video-reconstructed motions 作为运动多样性的主来源，用 MoCap 和 in-house 遥操作/惯性动捕数据补充高保真与部署相关覆盖；策略端用稀疏 MoE Transformer 扩大总容量，同时通过参考运动路由、KV-cache 和 sequence-level PPO 控制训练与推理成本。
- 关键技术点:
  - Hybrid motion corpus: MotionMillion 提供 2000+ 小时野外视频重建动作，AMASS/LAFAN1 提供干净 MoCap，自采 PICO VR/MR 与 Noitom 惯性动捕补齐遥操作和高动态部署数据。
  - Sparse MoE Transformer: decoder-only causal Transformer，context window 32，400M total parameters，但每步只激活约 7M 参数；MoE router 仅看 reference motion，降低真实机器人状态误差导致的路由抖动。
  - Sequence-level PPO: 保留连续 rollout segment，一次前向计算整段 log-prob，避免 step-level PPO 对重叠历史窗口的重复计算，报告训练吞吐最高提升 22x。
  - KV-cache real-time inference: 对每个环境/机器人维护 Transformer key-value ring buffer，rollout 和实机部署时每步只处理新 token，报告嵌入式推理最高 4x/11x 加速，实机策略推理约 200-300 Hz。
  - Deployment-oriented tracking: actor 使用带噪观测，critic 使用特权仿真状态；结合动作延迟、摩擦、质量/COM、PD gain、外部 push 和粗糙地形随机化，输出关节位置目标由底层 PD 控制。

## 实验
- Benchmark: Unitree G1 29-DoF；IsaacLab 训练，MuJoCo 统一评测；OOD 评测集包含 OMOMO、HumanAct12、TWIST2、TikTokDance、InertialTeleop。
- 主要结果: 相比最强基线 SONIC，HoloMotion 的 macro-average EMPKPE 为 124.57 mm vs 227.95 mm，约 40%+ 降低；EMPJPE 0.0979 rad、root velocity error 3.9 mm/frame、success rate 97.55%，均优于 GMT、Any2Track、SONIC。真实 G1 无任务微调即可跟踪野外视频舞蹈、武术/爬行/坐下等接触丰富动作，并支持 VR/惯性动捕实时遥操作。
- 对比基线: GMT, Any2Track, SONIC；效率对比包括 dense Transformer + sliding-window PPO。

## 评价
- 优势: 把 WBC scaling 的数据轴从高质量 MoCap 扩展到视频重建动作，显著提高动作风格和采集条件覆盖；稀疏 MoE Transformer 让 400M 级总容量能落到实时控制；sequence-level PPO 和 KV-cache 针对序列策略的训练/部署瓶颈给出工程闭环。
- 局限: 仍以完整参考运动跟踪为主，尚未解决 Follow Any Command、Move on Any Terrain、Control Any Embodiment；视频重建数据质量依赖上游人体运动估计与 retargeting，跨机器人泛化仍需新架构；与 SONIC 等系统的比较受训练数据来源和公开实现差异影响。
- 对 Whole-Body Control 的贡献: HoloMotion-1 是 SONIC 之后另一条 WBC foundation model scaling 路线：SONIC 强调高质量 MoCap + MLP/统一 token，HoloMotion 强调视频重建大数据 + 稀疏 MoE Transformer + 序列级 RL，可作为“野外视频运动数据驱动的全身跟踪基础模型”锚点。
