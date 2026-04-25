# TAMEn: Tactile-Aware Manipulation Engine for Closed-Loop Data Collection in Contact-Rich Tasks (2026)

## 基本信息
- 作者: Longyan Wu, Jieji Ren, Chenghang Jiang, Junxi Zhou, Shijia Peng, Ran Huang, Guoying Gu, Li Chen, Hongyang Li
- 机构: OpenDriveLab / The University of Hong Kong / Shanghai Jiao Tong University 等
- arXiv: 2604.07335
- 项目页: https://opendrivelab.com/TAMEn
- 代码: https://github.com/OpenDriveLab/TAMEn

## 一句话总结
TAMEn 是一个面向接触丰富双臂任务的触觉感知闭环数据采集系统：用跨夹爪形态的 wearable interface、mocap/VR 双模式采集、可行性检查和 tactile-visualized recovery teleoperation，把 UMI 式手持示范扩展到可回放、可纠错、可微调的触觉数据飞轮。

## 问题
手持式示范采集比机器人遥操作更高效，但在 contact-rich bimanual manipulation 中仍有三类瓶颈：
- 硬件通常绑定特定 gripper，难以快速适配异构夹爪；
- 高精度 tracking 与便携野外采集难以兼得；
- 离线示范缺少在线可行性检查和真实触觉恢复数据，导致回放失败和策略 refinement 数据不足。

## 方法
- 方法线归属: 交互式/闭环数据收集；robot-free / handheld visuo-tactile demonstration；contact-rich manipulation
- 核心 idea: 采集阶段不仅记录成功示范，还要在线检查可回放性，并在策略执行失败时用带触觉反馈的人类恢复数据闭环修正。
- 关键技术点:
  - **Cross-morphology wearable interface**: 快速适配不同夹爪/末端执行器，减少硬件形态绑定。
  - **Dual-modal acquisition pipeline**:
    - precision mode: 利用 motion capture 采集高保真示范；
    - portable mode: 利用 VR tracking 做 in-the-wild 采集，并支持 tactile-visualized recovery teleoperation。
  - **Feasibility-aware demonstration pipeline**: 采集时检查示范是否可被机器人回放，减少不可执行轨迹。
  - **Pyramid data regime**: 统一 large-scale tactile pretraining、task-specific bimanual demonstrations 和 human-in-the-loop recovery data。
  - **Visuo-tactile policy learning**: 用触觉和视觉共同训练策略，面向接触丰富任务的精细纠偏。

## 实验
- Benchmark: 多个真实双臂 contact-rich manipulation tasks。
- 主要结果:
  - feasibility-aware pipeline 显著提高 demonstration replayability；
  - visuo-tactile learning framework 将 diverse bimanual tasks 的成功率从 34% 提升到 75%；
  - 系统开源硬件和数据集，支持复现和扩展。
- 对比基线: 常规 handheld data collection、无 feasibility checking、无触觉/无 recovery data 的策略训练设置。

## 评价
- 优势: 把数据采集、回放可行性、失败恢复和触觉反馈放进同一闭环，比单纯离线示范更贴近真实部署；双模式采集兼顾精度与可扩展性。
- 局限: 仍需专用 wearable interface 和传感器标定；主要面向夹爪/双臂接触任务，对多指灵巧手和长时序开放任务的适配还需验证。
- 对 VLA 领域的贡献: TAMEn 与 RoboCopilot/GCENT/FreeTacMan 同属数据收集效率路线，但它把 tactile-aware recovery data 明确纳入闭环，为 contact-rich VLA 后训练提供更高价值数据。
