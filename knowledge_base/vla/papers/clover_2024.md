# CLOVER: Closed-Loop Visuomotor Control with Generative Expectation for Robotic Manipulation (2024)

## 基本信息
- 作者: Qingwen Bu, Jia Zeng, Li Chen, Yanchao Yang, Guyue Zhou, Junchi Yan, Ping Luo, Heming Cui, Yi Ma, Hongyang Li
- 机构: Shanghai AI Lab, Shanghai Jiao Tong University, The University of Hong Kong, Tsinghua University
- arXiv: 2409.09016
- 链接: https://arxiv.org/abs/2409.09016
- 代码: https://github.com/OpenDriveLab/CLOVER

## 一句话总结
CLOVER 将生成式视觉规划从 open-loop 子目标执行改成 closed-loop 控制：视频 diffusion 生成 RGB-D 子目标，policy 学到可度量 state embedding，通过当前-目标误差决定动作、子目标切换和 replanning。

## 问题
SuSIE/UniPi 类“生成视觉计划 + executor”方法通常开环执行固定子目标序列，无法检测当前状态是否真的到达计划，也无法在视觉计划不可达或动态扰动时及时重规划。

## 方法
- 方法线归属: Generative visual planning / Closed-loop visuomotor control
- 核心 idea: 让 executor 的 state embedding 具备误差度量能力，使视觉计划不只是目标图像，而是闭环控制中的 reference signal。
- 关键技术点:
  - Visual Planner: text-conditioned RGB-D video diffusion，生成 8 个未来子目标；引入 depth 和 optical-flow regularization 提升几何一致性和时序连贯性。
  - Feedback-driven policy: 共享 RGB-D encoder 提取 current/goal embedding，用二者差值作为 error，再用 MLP 解码 7-DoF 动作。
  - Closed-loop execution: 根据 embedding distance 自动判断子目标达到、切换和 replan；不依赖真实环境中的任务完成信号。
  - 表征对比: CLIP/LIV 等预训练 embedding 的距离范围小且噪声大，CLOVER 的 IDM-style embedding 更适合控制误差度量。

## 实验
- Benchmark: CALVIN ABC->D、AIRBOT Play 真实长时序任务和单任务，含视觉干扰与动态场景泛化。
- 主要结果: CALVIN 平均完成长度 3.53，超过 3D Diffuser Actor 3.27、SuSIE 2.69；真实长时序任务平均完成长度 2.1，高于 RT-1 的 1.1；closed-loop 比 open-loop 提升约 0.44 average length。
- 对比基线: MCIL、HULC、RT-1、RoboFlamingo、GR-1、3D Diffuser Actor、UniPi、SuSIE、ACT、R3M。

## 评价
- 优势: 把生成式子目标纳入可测量的反馈控制回路，显著缓解视觉计划开环误差累积；RGB-D 和 optical flow 设计贴近机器人几何需求。
- 局限: 仍需要在目标 benchmark/真实任务上训练 visual planner 和 policy；生成式计划的 OOD 可靠性仍是瓶颈；实验机器人和任务规模有限。
- 对 VLA 领域的贡献: CLOVER 是 VLA/具身智能中“视觉世界模型/生成式计划 + 闭环执行”的早期强基线，为后续 RISE 类 world-model self-improvement 提供了规划与反馈控制基础。
