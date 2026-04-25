# WholeBodyVLA: Towards Unified Latent VLA for Whole-Body Loco-Manipulation Control (2025)

## 基本信息
- 作者: Haoran Jiang*, Jin Chen*, Qingwen Bu, Li Chen, Modi Shi, Yanjie Zhang, Delong Li, Chuanzhe Suo, Chuang Wang, Zhihui Peng, Hongyang Li
- 机构: Fudan University, OpenDriveLab & MMLab at The University of Hong Kong, AgiBot, SII
- arXiv: 2512.11047
- 链接: https://arxiv.org/abs/2512.11047, https://opendrivelab.com/WholeBodyVLA

## 一句话总结
WholeBodyVLA 用 action-free egocentric videos 学 unified latent actions，再用 LMO RL 低层控制器执行离散移动/蹲起命令，在 AgiBot X2 上实现大空间 humanoid loco-manipulation。

## 问题
Humanoid loco-manipulation 需要移动先创造可操作姿态，再稳定完成双臂操作。模块化导航+操作容易在阶段切换处累积误差，端到端 VLA 又缺少大规模 humanoid teleop 数据；同时普通 velocity-tracking RL controller 对侧移、转身、蹲起等操作前置动作不够精确稳定。

## 方法
- 方法线归属: VLA-guided WBC / Foundation-model humanoid loco-manipulation
- 核心 idea: 把 action-free 人类 ego 视频转成离散 latent supervision，预训练高层 VLA 的 locomotion/manipulation 意图；再用少量 teleop grounding 到双臂关节动作和离散 locomotion command，由 LMO RL controller 负责低层稳定执行
- 关键技术点:
  - Unified latent learning: 训练 locomotion LAM 与 manipulation LAM，把 frame-to-frame inverse dynamics 编码成离散 latent action
  - 数据来源: 自采 manipulation-aware locomotion egocentric videos + AgiBot World manipulation data + AgiBot X2 teleop trajectories
  - Action grounding: VLA 约 10Hz 输出双臂 joint actions 和下肢 locomotion command
  - LMO RL: 面向 advancing、turning、squatting、lateral stepping 的离散命令接口，减少 velocity-based controller 的决策-执行错配
  - 系统任务: bag packing、box loading、cart pushing，以及不平地面、长序列、地面标记跟随、擦桌/吸尘等扩展场景

## 实验
- Benchmark: AgiBot X2 真实机器人，3 个主任务、每任务两个 subgoal；每个 subgoal 25 trials
- 主要结果:
  - WholeBodyVLA 平均 78.0%，高于 Modular Design 64.0%、GR00T w/ LMO 42.0%、OpenVLA-OFT w/ LMO 56.7%
  - 去掉 latent pretraining 后平均 39.3%，说明 action-free video latent learning 贡献很大
  - 只用 manipulation LAM 为 63.3%，完整 locomotion+manipulation latent learning 为 78.0%，主要收益来自需要先移动再操作的任务
  - velocity-based RL 替代 LMO 后平均 54.0%，且差距主要来自第二阶段移动/蹲起/转身子目标
  - LMO ablation 显示两阶段 curriculum、方向精度奖励和结构化扰动都影响轨迹精度与蹲起稳定性
- 对比基线: Modular Design、GR00T N1.5 w/ LMO、OpenVLA-OFT w/ LMO、w/o LAM、manip-only LAM、shared LAM、velocity-based RL

## 评价
- 优势: 把 VLA 预训练从桌面操作推进到 humanoid large-space loco-manipulation；action-free video 作为 latent supervision 缓解 teleop 稀缺；低层 LMO 明确针对操作前置移动动作，而不是泛化速度跟踪
- 局限: 高层仍需 teleop fine-tuning grounding；任务主要是粗粒度双臂搬运/推车，长时记忆、主动感知和灵巧操作仍未解决；低层 controller 与 VLA 仍是分层耦合，不是完全端到端动态闭环
- 对 Whole-Body Control 的贡献: WholeBodyVLA 是语言/VLA 引导 WBC 主线的代表工作，定位在 HOVER/SONIC 式低层控制与 VLA policy 之间，强调“高层 latent VLA + 任务化低层 RL”解决大空间移动操作
