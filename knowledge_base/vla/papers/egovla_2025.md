# EgoVLA: Learning Vision-Language-Action Models from Egocentric Human Videos (2025)

## 基本信息
- 作者: Ruihan Yang*, Qinxi Yu*, Yecheng Wu, Rui Yan, Borui Li, An-Chieh Cheng, Xueyan Zou, Yunhao Fang, Xuxin Cheng, Ri-Zhao Qiu, Hongxu Yin, Sifei Liu, Song Han, Yao Lu, Xiaolong Wang
- 机构: UC San Diego, UIUC, MIT, NVIDIA
- arXiv: 2507.12440
- 链接: https://arxiv.org/abs/2507.12440, https://rchalyang.github.io/EgoVLA
- 来源/验证状态: 已核对 arXiv v3 PDF 和项目页；结果来自论文的 Ego Humanoid Manipulation Benchmark 仿真评测

## 一句话总结
EgoVLA 用带手腕/手姿态标注的 egocentric 人类视频预训练 VLM-action 模型，再用少量 humanoid robot demos 后训练，通过 MANO 统一动作空间、IK 和 retargeting 迁移到双臂灵巧手机器人；它证明 human-video pretraining 能显著提升机器人后训练效果，但还不是 robot-free zero-shot policy。

## 问题
机器人 VLA 依赖大规模遥操作数据，硬件与专家操作限制了数据规模和任务/场景多样性。人类第一视角视频更丰富，但直接用于机器人控制存在三类 gap：
- 人手动作与机器人手/机械臂动作空间不同
- ego 人类视频与机器人视觉外观不同
- 仅靠人类数据预测的动作无法直接稳定部署到机器人

## 方法
- 方法线归属: Human Data Pretraining for VLA / Egocentric 视频 + 手部追踪 → 机器人策略；架构上是 VLM + transformer action regression head，而非 diffusion/flow head
- 核心 idea: 把人类手腕位姿和 MANO 手参数当作可迁移动作空间，在人类视频上学习通用操作先验，再把机器人 demonstrations retarget 到同一空间做后训练，推理时用 IK + 手部 retargeting 转回机器人控制
- 关键技术点:
  - 数据: HOI4D、HOT3D、HoloAssist、TACO 混合，约 500K image-action pairs，包含 RGB、wrist pose、hand pose、camera pose
  - 模型: NVILA-2B backbone + 300M transformer action head，输入 1 秒视觉历史、语言指令、action query token 和 proprioception
  - 动作: 预测未来 1 秒、30Hz 的双手 wrist translation/rotation(rot6D) + MANO top-15 PCA hand parameters
  - 统一动作空间: 机器人 demos 通过 3D 坐标变换、MANO fingertip optimization 映射成人手表示；推理时 wrist pose 走 IK，MANO keypoints 经轻量 MLP 映射到机器人手关节
  - Benchmark: 提出 Ego Humanoid Manipulation Benchmark，Isaac Lab + Unitree H1 + Inspire hands，12 个双臂灵巧操作任务，每任务 100 demos

## 实验
- Benchmark: Ego Humanoid Manipulation Benchmark；短时任务 7 个，长时任务 5 个，seen/unseen visual configurations；基线为 ACT specialist 和 EgoVLA-NoPretrain
- 主要结果:
  - 短时 seen: EgoVLA mean SR 77.78 / PSR 84.92，高于 NoPretrain 64.55 / 71.87 和 ACT 24.87 / 59.79
  - 短时 unseen: EgoVLA mean SR 69.11 / PSR 76.26，高于 NoPretrain 51.28 / 62.63
  - 长时 seen: EgoVLA mean SR 45.93 / PSR 80.78，高于 NoPretrain 26.67 / 54.93
  - 长时 unseen: EgoVLA mean SR 28.79 / PSR 69.11，高于 NoPretrain 11.21 / 36.20
  - Zero-shot robot deployment without robot post-training 为 0% success，说明 human pretraining 需要目标机器人后训练激活
- 对比基线: ACT, EgoVLA-NoPretrain, EgoVLA(50% robot demos)

## 评价
- 优势: 将 egocentric human video 从表征预训练推进到直接动作监督；MANO 统一空间给人手→humanoid hand 提供了清晰桥；新 benchmark 覆盖双臂、灵巧手和长时序仿真任务；数据混合消融显示 human data 多样性越高泛化越好
- 局限: 依赖手腕/手姿态标注，不能无机器人数据 zero-shot 部署；主要是仿真评测而非真实 humanoid；语言指令偏短技能执行，不解决高层长程规划；retargeting 仍是 embodiment-specific 工程
- 对 VLA 领域的贡献: EgoVLA 是 Human Data Pretraining for VLA 路线的早期清晰实例，定位介于 EgoMimic/EgoZero 的小规模 robot-free/point policy 和 Being-H0.5/EgoScale 的大规模 human-centric VLA scaling 之间：它证明人类手部动作监督能提升机器人后训练，但也暴露了 embodiment alignment 仍需 robot data 的现实瓶颈
