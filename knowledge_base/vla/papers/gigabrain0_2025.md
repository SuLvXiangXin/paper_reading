# GigaBrain-0: A World Model-Powered Vision-Language-Action Model (2025)

## 基本信息
- 作者: GigaBrain Team (Angen Ye, Boyuan Wang, Chaojun Ni, Guan Huang, Guosheng Zhao, Haoyun Li, Jie Li, Xiaofeng Wang, Zheng Zhu 等)
- 机构: GigaAI
- arXiv: 2510.19430
- 项目/代码: https://gigabrain0.github.io/ / https://github.com/open-gigaai/giga-brain-0

## 一句话总结
GigaBrain-0 不是把视频模型直接作为策略，而是把 GigaWorld 作为数据引擎，通过 Real2Real、View Transfer、Sim2Real、人类视频转机器人、多视角视频生成和 IDM 合成数据扩展 VLA 训练；结合 RGB-D 输入和 Embodied CoT，在 G1/PiPER 真机的灵巧、长时序、移动操作上稳定优于 π0，并推出 402M 的 GigaBrain-0-Small。

## 问题
通用 VLA 依赖昂贵真机数据，真实场景覆盖的外观、摆放、视角和长尾任务有限；纯 BC 数据越多越贵，且小规模真实示教很难覆盖桌面杂乱、移动操作和变形物动态。

## 方法
- 方法线归属: VLM + Flow Head / World Model as Data Engine / Embodied CoT
- 核心 idea: 用世界模型批量生成保持几何和动作语义的数据变体，以数据多样性补齐真实机器人采集瓶颈，再用 RGB-D + CoT + flow action expert 训练 VLA。
- 关键技术点:
  - 架构: PaliGemma2 + SigLIP RGB-D 输入 + Mixture-of-Transformers + DiT flow matching action chunk。
  - Knowledge Insulation 减少连续动作学习对 VLM 语义空间的干扰；离散 action token 加速预训练收敛。
  - Embodied CoT 包含 10 个 2D 末端轨迹关键点、subgoal language 和离散动作 token。
  - GigaWorld 数据: Real2Real appearance transfer、view transfer、Sim2Real transfer、egocentric human video transfer、text-to-video + IDM、多视角视频生成，并通过质量评估过滤。
  - 真实数据: 1182 小时自采，覆盖 Agilex Cobot Magic 和 AgiBot G1 的 14 类真实场景。

## 实验
- Benchmark: G1 与 PiPER 真机，任务覆盖 laundry folding、paper towel preparation、juice preparation、table bussing、boxes moving、laundry baskets moving，以及外观/摆放/视角泛化。
- 主要结果: 六类真机任务均优于 π0，其中 dexterous/mobile 任务约 +10%~30%；生成数据混入比例提升后，外观泛化超过 80%，摆放泛化超过 90%，视角泛化超过 80%；GigaBrain-0-Small 在 Orin 上 0.13s、1.9GB、80% SR，与 π0 80% 持平但延迟/显存大幅降低。
- 对比基线: π0，同任务同配置微调；轻量部署对比 π0 on Jetson AGX Orin。

## 评价
- 优势: 把 world model 的价值从"推理时想象"转为"训练数据放大器"，更接近可规模化的数据工程；RGB-D 和 CoT 对空间与长程结构有直接帮助。
- 局限: 结果大量依赖 GigaWorld 私有生成与质量过滤管线，标准 benchmark 数值较少；主模型仍是任务后训练范式，跨具身统一能力不如 Being-H0.5 这类显式统一动作空间工作清晰。
- 对 VLA 领域的贡献: 与 Cosmos Policy/DreamZero 的 WAM 路线互补，证明世界模型也可以作为 VLA 数据引擎来提高泛化；应在方法线中单独标注为 "World Model as Data Engine"。
