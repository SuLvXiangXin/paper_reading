# UniDex: A Robot Foundation Suite for Universal Dexterous Hand Control from Egocentric Human Videos (2026)

## 基本信息
- 作者: Gu Zhang, Qicheng Xu, Haozhe Zhang, Jianhan Ma, Long He, Yiming Bao, Zeyu Ping, Zhecheng Yuan, Chenhao Lu, Chengbo Yuan, Tianhai Liang, Xiaoyu Tian, Maanping Shao, Feihong Zhang, Mingyu Ding, Yang Gao, Hao Zhao, Hang Zhao, Huazhe Xu
- 机构: Tsinghua University, Shanghai Qizhi Institute, Sun Yat-sen University, University of North Carolina at Chapel Hill
- arXiv: 2603.22264
- 项目: https://unidex-ai.github.io/

## 一句话总结
UniDex 是面向异构灵巧手的 robot foundation suite：从 ego 人类视频中 retarget 出 8 种灵巧手、50K+ 轨迹的 robot-centric 预训练数据，提出 82D Function-Actuator-Aligned Space (FAAS) 统一动作空间，并训练 3D flow VLA，在 5 个真实工具使用任务上达到 81% 平均 task progress，显著超过 π0/DP/DP3。

## 问题
灵巧手 foundation policy 同时缺数据、缺跨手迁移接口、动作维度高；直接复用 gripper-centric VLA 会忽略手指功能结构，而针对单个灵巧手收集遥操作数据成本很高，无法覆盖剪刀、喷壶、鼠标等需要精细手指协调的日常工具使用。

## 方法
- 方法线归属: Human Data Pretraining for VLA + 3D VLA + cross-hand unified action space。
- 核心 idea: 先把 ego 人手视频转换成多种机器人灵巧手可执行的 robot-centric 轨迹，再用按功能对齐的统一动作空间训练单一 3D VLA，从而把人手数据规模化优势转成跨灵巧手控制能力。
- 关键技术点:
  - UniDex-Dataset: 从 H2O、HOI4D、TACO、OakInk2 等 RGB-D ego human datasets 派生，human-in-the-loop retargeting 对齐 fingertip trajectories 并保持合理 hand-object contacts。
  - 数据规模: 9M paired frames、50K+ trajectories、8 种灵巧手（6-24 DoF），训练时 mask human hands 并使用 pointcloud 以缩小视觉/运动学 gap。
  - FAAS: 82D Function-Actuator-Aligned Space，将功能相似的手指/actuator 映射到共享坐标，支持 cross-hand skill transfer。
  - UniDex-VLA: 单视角 colored pointcloud + language + proprioception，Uni3D 编码，conditional flow-matching 预测 FAAS action chunk，架构整体继承 π0 的 flow VLA 思路。
  - UniDex-Cap: Apple Vision Pro + RealSense L515 + 3D mount，采集同步 RGB-D 和人手/头部 pose，再转换成 robot-executable trajectories 支持 human-robot co-training。

## 实验
- Benchmark: Franka arm + Inspire/Wuji/Oymotion hands；5 个真实工具任务 Make Coffee、Sweep Objects、Water Flowers、Cut Bags、Use Mouse；每任务只用 50 条 robot demos fine-tune。
- 主要结果: 5 任务平均 task progress 81.0 +/- 12.1%，final success rate 76.0 +/- 17.8%；对比 DP 29.0/22.0、DP3 35.0/30.0、π0 38.0/35.0、UniDex-VLA No Pretrain 32.5/23.0。Zero-shot cross-hand coffee transfer 中 Oymotion 60%、Wuji 40%，π0 为 10%/0%。
- 对比基线: Diffusion Policy, 3D Diffusion Policy, π0, UniDex-VLA without pretraining；另有空间/物体泛化和 UniDex-Cap co-training 消融。

## 评价
- 优势: 是该子集中最直接的 robot policy 论文；FAAS 比简单 zero-padding 更贴近灵巧手功能结构，UniDex-Dataset 把人类 ego 数据变成 robot-centric 多手数据，真实工具任务比常见 pick-and-place 更考验手指控制。
- 局限: retargeting 仍有 human-in-the-loop，规模化自动化程度不如纯视频预训练；评测集中在 5 个桌面工具任务，尚未覆盖通用移动操作/长时序家庭任务；论文也指出 human data 有帮助但 robot data 仍不可替代。
- 对 VLA 领域的贡献: 为“人手视频 -> 灵巧手 VLA”提供了比 EgoScale/Being-H0.5 更偏 robot-centric 的实现路线，建议作为 Human Data Pretraining 支线下的“FAAS/功能对齐灵巧手动作空间”代表工作。
