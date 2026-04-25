# EgoZero: Robot Learning from Smart Glasses (2025)

## 基本信息
- 作者: Vincent Liu*, Ademi Adeniji*, Haotian Zhan*, Siddhant Haldar, Raunaq Bhirangi, Pieter Abbeel, Lerrel Pinto
- 机构: New York University, UC Berkeley
- arXiv: 2505.20290
- 链接: https://arxiv.org/abs/2505.20290, https://egozero-robot.github.io
- 来源/验证状态: 已核对 arXiv v2 PDF 和项目页；论文声称 zero robot data，实验为 Franka Panda gripper 真机

## 一句话总结
EgoZero 用 Project Aria smart glasses 采集 in-the-wild 人类示范，把视觉和手部动作压缩成 egocentric 3D point state-action，再训练闭环 Transformer policy；它在 7 个 Franka 任务上用每任务约 20 分钟人类数据、无机器人训练数据达到约 70% zero-shot 成功率，是 human-video → robot policy 路线中最激进的 robot-free 方案之一。

## 问题
人类日常操作数据天然丰富，但传统 robot learning 很难直接使用，因为：
- 视频像素分布在 human/robot/camera 间差异巨大
- 只从 smart glasses 获取的深度和手部动作不完整
- 人手和夹爪机器人动作空间不同
- 许多从视频学 affordance 的方法是开环轨迹，难以处理复杂非线性操作

## 方法
- 方法线归属: Human Data Pretraining for VLA / Egocentric human data → robot policy；更准确说是 point-based morphology-agnostic imitation learning，不是标准 VLM/VLA
- 核心 idea: 不直接从 RGB 学策略，而是用 3D 点集统一 human 和 robot 的状态/动作空间；让 policy 学习相机无关、形态弱相关的几何闭环控制
- 关键技术点:
  - 采集: 仅用 Project Aria 的 RGB、SLAM camera、MPS 6DoF hand pose/camera pose，无手套、无外部多相机、无机器人数据
  - 动作空间: 用 HaMeR hand keypoints + Aria palm pose 估计 thumb/index 3D 坐标和 gripper closure，形成 robot-executable end-effector point action
  - 状态空间: 用 Grounding DINO/DIFT 初始化对应点，CoTracker3 跨帧跟踪，再基于 Aria SLAM 轨迹三角化静态物体 3D points
  - 策略: 闭环 Transformer policy，输入 3D object points + end-effector history，输出 action chunk；训练时加入 3D rotation/translation augmentation
  - 推理: 用 iPhone depth unprojection 得到机器人侧 3D points，单次 Aruco 标定 iPhone-to-robot transform 后在 Franka 上执行

## 实验
- Benchmark: 7 个 Franka Panda 真机任务：open oven door、put bread on plate、sweep board、erase board、sort fruit、fold towel、insert book in shelf
- 主要结果:
  - 每任务 100 human demos，约 20 分钟采集；zero robot data
  - EgoZero 总计 74/105 成功，平均约 70.5%
  - From vision baseline 为 0/105；affordance/open-loop baseline 只在简单任务部分成功；去掉 3D augmentation 或使用 monocular depth 替代三角化均为 0/105
  - 展示 object pose、object semantic、camera 和 human-scale generalization，训练用 Aria fisheye，推理可换 iPhone pinhole
- 对比基线: image-based Baku-style policy、affordance/open-loop policy、EgoZero without 3D augmentations、EgoZero with monocular depth

## 评价
- 优势: 真正把“只戴眼镜做人类示范”推进到 robot-free 真机闭环控制；3D point representation 有强 camera/morphology abstraction；数据效率高，每任务约 20 分钟即可迁移；baseline/ablation 清楚说明闭环策略、三角化和 3D augmentation 缺一不可
- 局限: 点表示上限受 DIFT/CoTracker/hand pose 误差限制，无法自我纠正 3D measurement error；三角化假设物体 pre-grasp 静止且相机有足够运动，难处理随机/动态对象；hand action label 有约 1-2cm 误差，限制高精度任务；目前是单臂夹爪任务，不是语言条件的大规模 VLA
- 对 VLA 领域的贡献: EgoZero 给 Human Data Pretraining 路线提供了一个重要反例/补充：不一定先做大 VLM 或大规模 robot co-training，几何中间表示也能跨越 human→robot gap；它适合成为 EgoVLA/Being-H0.5 这类端到端 VLA 的数据表示和对齐模块参考
