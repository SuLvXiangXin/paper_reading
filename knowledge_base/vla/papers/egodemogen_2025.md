# EgoDemoGen: Egocentric Demonstration Generation for Viewpoint Generalization in Robotic Manipulation (2025)

## 基本信息
- 作者: Yuan Xu*, Jiabing Yang*, Xiaofeng Wang, Yixiang Chen, Zheng Zhu†, Bowen Fang, Guan Huang, Xinze Chen, Yun Ye, Qiang Zhang, Peiyan Li, Xiangnan Wu, Kai Wang, Bing Zhan, Shuo Lu, Jing Liu, Nianfeng Liu, Yan Huang†, Liang Wang†
- 机构: UCAS, CASIA, GigaAI, Tsinghua University, X-Humanoid, FiveAges
- arXiv: 2509.22578
- 项目: https://egodemogen.github.io/
- 代码: https://github.com/GigaAI-research/EgoDemoGen

## 一句话总结
EgoDemoGen 专门解决 egocentric viewpoint shift 下的 demonstration augmentation：它同时迁移动作坐标系和生成新视角观测，通过 EgoTrajTransfer + EgoViewTransfer 生成配对 observation-action 数据，使 RoboTwin 2.0 novel-view 成功率从 11.0% 提升到 27.9%，Mobile ALOHA novel-view 从 37.0% 提升到 60.0%。

## 问题
第三人称视角增强只移动相机，但第一人称/头戴相机视角变化会同时改变相机位姿和机器人 base/action coordinate frame。若只做 novel-view synthesis 而不转动作，视觉与动作不一致；若只转动作而不生成对应观测，也无法训练视觉策略。因此需要生成成对的新 egocentric viewpoint observation-action demonstrations。

## 方法
- 方法线归属: World Model + VLA data generation / egocentric viewpoint augmentation；与 GigaWorld-0 ViewTransfer 同源。
- 核心 idea: 将“新 ego 视角”看成机器人 base 的 SE(3)/平面位移，先生成在新 base frame 下可执行的动作轨迹，再用视频扩散合成与该轨迹对齐的新视角观测。
- 关键技术点:
  - EgoTrajTransfer: 依据 gripper state 将轨迹分成 free-space motion 和 contact-rich skill segment；motion segment 做 endpoint 对齐、缩放和插值，skill segment 做刚体变换以保留物体相对运动。
  - IK feasibility filtering: 用 CuRobo 分别求双臂 IK，以原关节角为 seed；失败帧插值，并按 IK 成功率与最大关节跳变过滤不可行视角。
  - EgoViewTransfer: 基于 CogVideoX-5B-I2V，双条件输入为 novel-view reprojected/inpainted scene video 与 transferred trajectory 渲染出的 robot motion video。
  - Double reprojection self-supervision: 只需要单一源视角数据，先把源视频投到随机视角再投回源视角，让模型学习修复重投影伪影，无需真实多视角 demonstration。

## 实验
- Benchmark: RoboTwin 2.0 仿真 7 任务（ACT policy，100 trials/task），Mobile ALOHA 真机 5 任务（π0 policy，标准视角和 4 个 novel viewpoints，各 20 trials/task）。
- 主要结果: 仿真平均标准/novel 成功率从 Standard Viewpoint 的 29.0/11.0 提升到 EgoDemoGen 的 53.6/27.9；真机从 60.0/37.0 提升到 76.0/60.0。EgoViewTransfer 视频质量显著优于 Direct Reprojection/TrajectoryCrafter/Phantom/VISTA，仿真 FVD 133.5、真实 double reprojection FVD 148.6。
- 对比基线: Standard Viewpoint、Direct Reprojection、TrajectoryCrafter、Phantom、VISTA；消融包括去掉 double reprojection、mask & inpaint、trajectory transfer。

## 评价
- 优势: 清楚地区分 third-person view augmentation 与 egocentric viewpoint augmentation，并证明动作 frame 转换是 novel ego view 数据生成的关键；self-supervised double reprojection 降低了多视角采集成本；在仿真和真机都验证了 novel-view robustness。
- 局限: 主要处理平面 base motion 范围内的 viewpoint shift，大范围位姿变化会受 IK 可行域和视频生成质量限制；需要深度/相机参数/URDF/机器人 mask；生成数据不能完全替代真实数据，固定总数据量时合成比例约 0.4-0.5 最优。
- 对 VLA 领域的贡献: 把“生成更多视角”从纯视觉增强推进到配对 observation-action demonstration generation，为头戴/移动平台 VLA 的视角鲁棒性提供了可复用的数据引擎组件。
