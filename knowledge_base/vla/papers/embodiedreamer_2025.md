# EmbodieDreamer: Advancing Real2Sim2Real Transfer for Policy Training via Embodied World Modeling (2025)

## 基本信息
- 作者: Boyuan Wang*, Xinpan Meng*, Xiaofeng Wang*, Zheng Zhu*†, Angen Ye, Yang Wang, Zhiqin Yang, Chaojun Ni, Guan Huang, Xingang Wang†
- 机构: GigaAI, Institute of Automation CAS, Peking University
- arXiv: 2507.05198
- 项目: https://embodiedreamer.github.io/
- 代码: https://github.com/GigaAI-research/EmbodieDreamer

## 一句话总结
EmbodieDreamer 将 embodied world modeling 用作 Real2Sim2Real policy 训练环境，通过 PhysAligner 对齐仿真动力学、VisAligner 将低保真仿真渲染转为真实感视频，使 ACT/π0 可在生成的高保真仿真轨迹上做 RL/IL 增强，真机平均成功率较单纯真实数据微调提升约 29.17%。

## 问题
真实机器人数据昂贵，仿真训练又同时受物理动力学 gap 和视觉外观 gap 限制。现有 Real2Sim2Real 方法往往只做参数搜索或视觉随机化，难以同时保证控制轨迹真实、视觉输入真实，并支撑闭环 RL 或大规模 IL 数据增强。

## 方法
- 方法线归属: World Model + VLA / Embodied world model data engine；更接近 GigaWorld-0 之前的 Real2Sim2Real 子系统，而非直接的 VLA policy 架构。
- 核心 idea: 先把仿真变成可训练 policy 的“近真实世界”：物理层用可微 surrogate 做系统辨识，视觉层用条件视频扩散把仿真状态翻译成真实感观测，再在该环境中生成偏好排序 RL 轨迹或外观增强 IL 数据。
- 关键技术点:
  - PhysAligner: 对摩擦、刚度、阻尼/PD 控制参数采样建 simulator surrogate，再固定网络用梯度下降匹配真实轨迹；相比 SimplerEnv 的模拟退火更快、更稳定。
  - VisAligner: 基于 latent video diffusion，使用 reference image、机器人 URDF 回放、前景物体 mask 三类条件，显式解耦背景、机器人和操作物体。
  - RL 用法: ACT 单目策略在仿真中 rollout，VisAligner 渲染为 photorealistic observation，以末端到目标距离做 preference ranking，选择 top/bottom 轨迹继续微调。
  - IL 用法: 改变前景/背景后回放原动作，生成新视觉条件下的真实感 demonstrations，用于训练 ACT 或 post-train π0。

## 实验
- Benchmark: Cobot Mobile ALOHA 真机；RT-1 数据用于 PhysAligner/VisAligner 评测；4 个真机操作任务（Grab Paper Cup, Put Pen in Cup, Put Remote in Box, Put Cup on Mat）。
- 主要结果: PhysAligner 轨迹误差 0.2161 vs SimplerEnv 0.2245，时间 1299.92s vs 12888.43s；VisAligner FVD 176.27 vs w/o object segmentation 422.73；RL with EmbodieDreamer 平均成功率 0.77 vs 三视角 SFT 0.60、单视角 SFT 0.49。
- 对比基线: SimplerEnv system identification、无物体分割的 VisAligner、ACT SFT（三视角/单视角）、真实数据 vs 生成数据训练的 ACT/π0。

## 评价
- 优势: 同时处理物理和视觉两个 reality gap；生成环境不仅做数据增强，还能闭环 rollout 做 preference-style RL；对后续 GigaWorld-0 的 Phys/View/Appearance/Mimic 数据引擎模块有明显前身关系。
- 局限: 实验规模仍是少量 Mobile ALOHA 桌面任务；VisAligner 依赖 calibrated simulator、URDF 和分割条件；RL reward 主要是末端距离，未覆盖长时序语义成功；代码/模型状态在项目页仍偏“coming soon/初始化”。
- 对 VLA 领域的贡献: 将“视频生成式 world model”从单纯观测增强推进到可训练 policy 的 Real2Sim2Real 环境，证明 world model 可以作为 RL/IL 数据引擎补足真实机器人数据，而不是只作为显式规划器或未来帧预测器。
