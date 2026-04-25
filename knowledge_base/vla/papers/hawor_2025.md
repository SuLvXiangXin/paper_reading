# HaWoR: World-Space Hand Motion Reconstruction from Egocentric Videos (2025)

## 基本信息
- 作者: Jinglei Zhang, Jiankang Deng, Chao Ma, Rolandos Alexandros Potamias
- 机构: Shanghai Jiao Tong University, Imperial College London
- arXiv: 2501.02973
- 发表: CVPR 2025

## 一句话总结
HaWoR 将 egocentric hand reconstruction 从相机坐标系提升到世界坐标系：先估计 camera-frame hand motion，再用 adaptive egocentric SLAM + metric scale 对齐到 world space，并用 motion infiller 补全手离开视野时的轨迹。

## 问题
大多数 3D 手部重建方法只输出 camera-frame pose，无法直接表达人在真实世界中的手部轨迹；而 ego 视频中相机和手同时运动，且手常被遮挡或离开视野，直接把单帧手部估计和普通 SLAM 拼接会产生尺度漂移和不连续轨迹。

## 方法
- 方法线归属: Human Data Pretraining for VLA 的手部追踪/数据标注基础设施；不是 policy 模型。
- 核心 idea: 将世界坐标手部运动估计解耦为“相机坐标手部重建 + 世界坐标相机轨迹估计 + 缺失片段补全”，从而把 in-the-wild ego 视频转成可用于机器人学习的 3D motion supervision。
- 关键技术点:
  - transformer-based camera-frame hand motion reconstruction，增强遮挡下的手部估计。
  - adaptive egocentric SLAM，针对 ego 视频中手占据大视野、动态遮挡和快速头动调整 DROID-SLAM 式优化。
  - 使用 Metric3D/metric depth 估计为单目 SLAM 恢复真实尺度。
  - motion infiller network 处理手离开视野或严重遮挡的帧，比 last-pose 和线性插值更稳定。

## 实验
- Benchmark: DexYCB camera-frame hand pose；HOT3D world-space hand/camera trajectory；补充 EPIC-KITCHENS in-the-wild qualitative。
- 主要结果: HOT3D world-space 上 W-MPJPE 33.20mm，显著低于 HMP-SLAM 119.41mm、WiLoR-SLAM 151.67mm；RTE 0.78 vs HMP-SLAM 2.79；adaptive SLAM 的 ATE-S 14.61mm，优于 DROID+Metric3D 21.07mm；推理约 40ms/frame，比 HMP-SLAM 的 160ms/frame 快约 75%。
- 对比基线: HaMeR-SLAM, HandDGP-SLAM, WiLoR-SLAM, HMP-SLAM, DROID-SLAM + ZoeDepth/DepthAnythingV2/Metric3D。

## 评价
- 优势: 解决了 ego 人手数据用于机器人学习时最关键的参考系问题，输出 world-space wrist/hand trajectory，比 camera-frame pose 更适合 retargeting、policy pretraining 和跨场景标注。
- 局限: 仍是离线重建工具，不直接学习 robot policy；依赖 monocular SLAM 和 metric depth，低纹理、强动态或长序列场景仍可能漂移；infiller 的泛化受 HOT3D 训练分布限制。
- 对 VLA 领域的贡献: 是 EgoScale/Being-H0.5/JALA 等人手数据路线的关键底层能力之一，提供从普通 ego 视频到可训练 3D 手部动作监督的高质量标注路径。
