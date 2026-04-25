# EgoHumanoid: Unlocking In-the-Wild Loco-Manipulation with Robot-Free Egocentric Demonstration (2026)

## 基本信息
- 作者: Modi Shi*, Shijia Peng*, Jin Chen*, Haoran Jiang, Yinghui Li, Di Huang, Ping Luo, Hongyang Li, Li Chen
- 机构: The University of Hong Kong, Shanghai Innovation Institute, Beihang University, Kinetix AI
- arXiv: 2602.10106
- 链接: https://arxiv.org/abs/2602.10106, https://opendrivelab.com/EgoHumanoid/
- 来源/验证状态: 已核对 arXiv v1 PDF 和项目页；论文称 code/models will be released，当前卡片只依据论文和项目页信息

## 一句话总结
EgoHumanoid 首次系统验证 egocentric human demos 对 humanoid whole-body loco-manipulation 的迁移价值：通过 view alignment 和 unified action alignment，把 in-the-wild 人类示范与少量 Unitree G1 robot teleop co-train 到 π0.5 policy，在未采集机器人数据的新场景中相对 robot-only 提升 51pp。

## 问题
人形机器人 loco-manipulation 同时涉及移动、姿态调整和操作，数据需求远高于固定机械臂。机器人遥操作受实验室、安全和硬件限制，难覆盖家庭、商店、户外等真实场景；但人类 ego 示范和机器人之间有更大的视角、身高、形态、运动学和动态平衡 gap。

## 方法
- 方法线归属: Human Data Pretraining for VLA / Humanoid loco-manipulation co-training；基于 π0.5 finetuning，加入 view/action alignment
- 核心 idea: 低层动作具身相关，但导航路线、接近物体、任务分解等高层行为结构可迁移；通过把 human ego view 变换到机器人视角、把 human motion 离散/连续映射到机器人 action space，让同一 VLA policy 从 human diversity 和 robot embodiment-correct demos 中共同学习
- 关键技术点:
  - 采集系统: PICO VR headset + 5 个 PICO trackers + head-mounted ZED X Mini；人类数据可在室内/户外自由采集，机器人数据通过 VR teleoperation 控制 Unitree G1 + Dex3 hands
  - View alignment: MoGe 估计 depth/point map，把人类 ego image 重投影到机器人相机高度，再用 latent diffusion inpainting 补全 disocclusion 区域
  - Action alignment: 上半身用双臂 6-DoF delta end-effector pose；下半身把 pelvis trajectory 量化为离散速度/转向/蹲站命令；手部用曲率估计 binary open/close
  - Policy: finetune π0.5，输入 egocentric RGB + language instruction，不输入 proprioception；18D action = 双臂 12D delta pose + 3D discrete locomotion + 2D gripper + 1D delta height，action chunk size 50
  - Sampling: 分析 robot:human batch ratio，精细操作任务更依赖 robot ratio，导航/粗操作更受益于 human ratio

## 实验
- Benchmark: Unitree G1 真实人形机器人，4 个 loco-manipulation 任务：Pillow Placement、Trash Disposal、Toy Transfer、Cart Stowing；每设置 20 trials
- 主要结果:
  - In-domain: co-training 平均 score 78%，robot-only 59%
  - Generalization: co-training 82%，robot-only 31%，提升 51pp；新场景只在人类数据中出现，无 in-the-wild robot data
  - Subskill: Human-only 在导航主导阶段多为 100%，说明导航和接近策略强可迁移；精细操作阶段明显弱于 co-training，说明 robot demos 对 contact/rotation 仍关键
  - Scaling: human demos 从 0 增至 300 时表现持续提升；导航/粗抓取偏好更高 human ratio，精细操作偏好更高 robot ratio
  - 数据效率: 人类示范平均 39.7s/episode，机器人 teleop 62.1s/episode，约 2x 更高效
- 对比基线: Robot-only, Human-only, Co-training; view alignment ablation; 不同 human demo 数量和 robot:human sampling ratio

## 评价
- 优势: 把 egocentric human data 的迁移从桌面/移动底盘推进到 humanoid whole-body loco-manipulation；view alignment + action alignment 覆盖视觉和运动学两个核心 gap；真实 G1 场景评测显示 human data 对 scene generalization 的贡献很强；subskill 分析清楚地区分了“人类数据擅长导航/粗操作、机器人数据补精细操作”
- 局限: 不是完全 robot-free，仍需 robot teleop 数据提供 embodiment-correct manipulation supervision；delta end-effector pose 在无 proprioception 时存在旋转歧义，限制细粒度转动控制；loco-manipulation 视角变化导致数据需求约为固定操作的 2-3x；离散 locomotion command 限制运动表达；人类示范仍需遵循手腕姿态一致、躯干稳定、手部可见等采集规范
- 对 VLA 领域的贡献: EgoHumanoid 是 EMMA 之后 human egocentric data 走向 humanoid 的关键扩展，说明 human data 对开放环境泛化的价值在更复杂具身上仍成立；它也提示 taxonomy 中应把 Human Data Pretraining 进一步拆成 tabletop hand policy、mobile manipulation co-training、humanoid loco-manipulation co-training 三个子线
