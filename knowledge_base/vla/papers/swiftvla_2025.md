# SwiftVLA: Unlocking Spatiotemporal Dynamics for Lightweight VLA Models at Minimal Overhead (2025)

## 基本信息
- 作者: Chaojun Ni, Cheng Chen, Xiaofeng Wang, Zheng Zhu, Wenzhao Zheng, Boyuan Wang, Tianrun Chen, Guosheng Zhao 等
- 机构: GigaAI, Peking University, Moxin Technology, Tsinghua University, X-Humanoid
- arXiv: 2512.00903
- 项目/代码: https://swiftvla.github.io/ / https://github.com/GigaAI-research/SwiftVLA

## 一句话总结
SwiftVLA 是 0.45B 轻量 VLA，通过冻结 4D visual geometry transformer + temporal cache、Fusion Tokens 和 mask-and-reconstruct，把 4D 时空几何蒸馏进小 VLM；推理时可移除 4D 分支，在 Jetson Orin 上接近 SmolVLA 延迟但平均 SR 0.76，较 π0 快 18x、显存少 12x。

## 问题
轻量 VLA（TinyVLA/SmolVLA）虽然适合边缘部署，但小 VLM 空间/时间理解弱，复杂抓取、长时序和变形物任务成功率显著低于 π0；直接融合 3D/4D 特征又常依赖大 VLM 或额外分支，推理开销抵消轻量化收益。

## 方法
- 方法线归属: 轻量化 VLA / 4D 时空几何蒸馏
- 核心 idea: 训练期用 4D 几何特征教小 VLM 学会时空动态，推理期只保留 2D VLM + action expert，从而把 4D 作为监督而非部署负担。
- 关键技术点:
  - 预训练 4D visual geometry transformer 从 2D 图像增量抽取 4D 特征，temporal cache 复用历史帧特征。
  - Fusion Tokens 在小 VLM 内融合 2D/4D 特征，并用未来末端轨迹预测约束其任务相关性。
  - mask-and-reconstruct 随机遮蔽 2D 或 4D 输入，让 action expert 重建被遮蔽特征，降低对 4D 分支的推理依赖。
  - 推理阶段移除 4D extractor、trajectory head 和 reconstruction head，仅保留紧凑 VLA。

## 实验
- Benchmark: RoboTwin 2.0、LIBERO、真实 PiPER/Jetson Orin、Fold the Cloth 长时序变形物任务。
- 主要结果: RoboTwin 平均 SR 0.53（with 4D input 0.55），比 SmolVLA 0.29 高 82.76%；LIBERO 平均 94.7（with 4D input 95.1），接近/超过多种 3B+ VLA；Jetson Orin 上 0.167s、1398MB、SR 0.76（π0: 2.966s、16236MB、SR 0.48）。
- 对比基线: π0、GO-1、TinyVLA、SmolVLA/SmolVLA 同配方、SpatialVLA、4D-VLA、QDepth-VLA、OpenVLA-OFT、GR00T-N1。

## 评价
- 优势: 与 Evo-1 的"语义保护轻量化"不同，SwiftVLA 抓住小模型缺几何/动态先验的问题；4D 分支训练期强监督、推理期可丢弃，部署代价很低。
- 局限: 主要实验仍是单/双臂操作与标准仿真，未证明跨具身统一训练；4D 特征质量依赖冻结几何模型，且训练期计算并不轻。
- 对 VLA 领域的贡献: 为轻量 VLA 提供了"训练期时空蒸馏、推理期纯 2D"路径，可与 Evo-1 的语义保护、Evo-0 的隐式 3D 增强共同构成轻量部署方法线。
