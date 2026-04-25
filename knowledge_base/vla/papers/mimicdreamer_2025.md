# MimicDreamer: Aligning Human and Robot Demonstrations for Scalable VLA Training (2025)

## 基本信息
- 作者: Haoyun Li*, Ivan Zhang*, Runqi Ouyang*, Xiaofeng Wang, Zheng Zhu†, Zhiqin Yang, Zhentao Zhang, Boyuan Wang, Chaojun Ni, Wenkang Qin, Xinze Chen, Yun Ye, Guan Huang, Zhenbo Song†, Xingang Wang†
- 机构: GigaAI, CASIA, NJUST, Tsinghua University
- arXiv: 2509.22199
- 项目: https://mimicdreamer.github.io/
- 代码: https://github.com/GigaAI-research/MimicDreamer

## 一句话总结
MimicDreamer 将低成本 egocentric 人类示范转成机器人可用的 VLA 训练监督：EgoStabilizer 稳定第一人称视角，IK 将人手轨迹转为可执行关节动作，H2R Aligner 用视频扩散把人手视频翻译成机器人视频；在 6 个真机任务上，20 条人类转机器人数据 + 20 条机器人数据使 π0 类策略平均成功率从 65.8% 提升到 85.0%。

## 问题
人类示范比机器人遥操作便宜且可扩展，但直接用于 VLA 训练会遇到三重 gap：ego 相机抖动/视角漂移，人手轨迹到机器人关节控制不可直接执行，人手外观与机器人臂外观差异导致视觉域错配。EgoMimic/EgoVLA 等工作多只处理其中一部分，尚未把人类视频完整转成“机器人可执行且视觉一致”的训练样本。

## 方法
- 方法线归属: Human Data Pretraining for VLA / 人类 egocentric 数据到机器人监督；同时属于 world-model/data-engine 式视频生成增强。
- 核心 idea: 不把人类视频作为辅助表征，而是通过 viewpoint、action、vision 三维对齐，生成配对的机器人视频 + 机器人动作，让 VLA 可以像用真实遥操作数据一样训练。
- 关键技术点:
  - EgoStabilizer: 基于 homography 将移动 ego 视频 canonicalize 到任务参考视角，并 inpaint warp 带来的遮挡和空洞，降低跨序列视角漂移。
  - 动作对齐: 将人体 3D hand keypoints 转到 robot frame，保留 wrist 的 pitch/yaw，弱化 roll；用带平滑项、关节/速度限制的 IK 求解低抖动关节轨迹，gripper 由手部张开度分类得到。
  - H2R Aligner: 基于 CogVideoX-5B-I2V 的条件视频扩散；训练时用真实机器人视频作为目标，背景去除机器人、仿真机器人前景作为条件；推理时用 masked human background + IK replay simulation 合成机器人域视频。
  - VLA 训练: 以 π0 预训练权重初始化，在合成人类转机器人数据与少量真实机器人数据上用 conditional flow matching post-training。

## 实验
- Benchmark: EgoDex 风格的 6 个真机任务（Pick Bag, Clean Surface, Stack Bowls, Dry Hands, Insert Tennis, Stack Cups），PiPER/双臂机器人设置；指标为 Success Rate 和 Progress Success Rate。
- 主要结果: Robot Only（20 条机器人数据）平均 65.8% SR / 76.3% PSR；Minimal Robot（20 human-to-robot + 3 robot）达 70.0% / 81.0%；Equal Data（20 human-to-robot + 20 robot）达 85.0% / 91.0%。随 human-to-robot 数据从 5 增至 30 条，6 个任务 SR/PSR 单调上升，Insert Tennis 从 25% SR 提升到 50%。
- 对比基线: 仅机器人数据、少量机器人数据 + 合成数据、等量机器人 + 合成数据；同时报告 H2R Aligner 和 EgoStabilizer 的视觉/稳定性定性结果。

## 评价
- 优势: 相比 EgoMimic 的 mask/line co-training，MimicDreamer 更彻底地把人类视频转换为机器人域演示；相比 EgoScale/Being-H0.5 的大规模直接预训练，它强调“数据转换器”而非“更大模型”，对少量机器人数据场景更实用。
- 局限: 仍需人手 3D 关键点、机器人 URDF、相机标定和 IK，可扩展性受感知/标定质量限制；实验任务数和机器人形态有限；合成数据在 20 条后出现 ceiling/diminishing return，说明视觉对齐后瓶颈转向精细抓取和接触动作。
- 对 VLA 领域的贡献: 提供了从 human video 到 robot supervision 的完整工程闭环，使人类数据路线从“co-training 辅助”进一步走向“可替代遥操作的数据生产管线”，也成为 GigaWorld-0 MimicTransfer 模块的直接前身。
