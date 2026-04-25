# EgoHumanoid: Unlocking In-the-Wild Loco-Manipulation with Robot-Free Egocentric Demonstration (2026)

## 基本信息
- 作者: Modi Shi*, Shijia Peng*, Jin Chen*, Haoran Jiang, Yinghui Li, Di Huang, Ping Luo, Hongyang Li, Li Chen
- 机构: The University of Hong Kong, Shanghai Innovation Institute, Beihang University, Kinetix AI
- arXiv: 2602.10106
- 链接: https://arxiv.org/abs/2602.10106, https://opendrivelab.com/EgoHumanoid/
- 相关卡片: `knowledge_base/vla/papers/egohumanoid_2026.md`

## 一句话总结
EgoHumanoid 从 whole-body 视角看，是用低成本人类 ego 示范补齐 humanoid loco-manipulation 场景分布，并与少量机器人遥操作共同训练 VLA policy。

## 问题
Humanoid loco-manipulation 的数据瓶颈比固定机械臂更严重：机器人需要先导航、接近、调整身体和完成操作。真实机器人遥操作成本高、场景覆盖窄；人类 ego 示范虽然易采，但存在视角、身高、运动学、手部和下肢控制空间差异。

## 方法
- 方法线归属: VLA-guided Loco-Manipulation / Human Data Pretraining for Humanoids
- 核心 idea: 高层行为结构（接近目标、绕行、任务分解）可从人类 ego demos 迁移，低层 embodiment-correct manipulation 由机器人 teleop 数据补足
- 关键技术点:
  - View alignment: 将人类 ego image 重投影到机器人相机高度，并补全遮挡区域
  - Action alignment: 上身映射到双臂 delta end-effector pose，下身用离散速度/转向/蹲站命令，手部简化为 open/close
  - Policy: finetune π0.5，输入 ego RGB + language，输出双臂、下肢和夹爪/手部动作
  - 数据策略: 比较 human-only、robot-only、co-training 和不同 robot:human sampling ratio

## 实验
- Benchmark: Unitree G1 真实机器人，Pillow Placement、Trash Disposal、Toy Transfer、Cart Stowing
- 主要结果:
  - In-domain 平均 score: co-training 78%，robot-only 59%
  - Generalization: co-training 82%，robot-only 31%，新场景主要来自人类数据覆盖
  - Subskill 分析显示人类数据对导航/接近/粗操作最有帮助，精细接触和旋转仍依赖机器人数据
- 对比基线: Robot-only、Human-only、Co-training、view/action alignment ablations

## 评价
- 优势: 对 WBC 的意义不在低层控制算法，而在证明 human egocentric data 能显著扩展 humanoid loco-manipulation 场景覆盖；与 WholeBodyVLA 共同构成 OpenDriveLab 的“人类视频/示范 -> humanoid VLA”路线
- 局限: 仍不是 robot-free，精细操作依赖机器人遥操作；离散 locomotion command 限制全身运动表达；不解决低层动态稳定控制本身
- 对 Whole-Body Control 的贡献: 作为交叉卡片保留，定位在 VLA 与 WBC 的数据层接口，提醒 whole-body_control taxonomy 中 loco-manipulation 不只依赖控制器，也依赖可迁移的人类场景数据
