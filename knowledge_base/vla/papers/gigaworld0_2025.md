# GigaWorld-0: World Models as Data Engine to Empower Embodied AI (2025)

## 基本信息
- 作者: GigaWorld Team（Angen Ye, Boyuan Wang, Chaojun Ni, Guan Huang, Guosheng Zhao, Haoyun Li, Jiagang Zhu, Kerui Li, Mengyuan Xu, Qiuping Deng, Siting Wang, Wenkang Qin, Xinze Chen, Xiaofeng Wang, Yankai Wang, Yu Cao, Yifan Chang, Yuan Xu, Yun Ye, Yang Wang, Yukun Zhou, Zhengyuan Zhang, Zhehao Dong, Zheng Zhu 等）
- 机构: GigaAI
- arXiv: 2511.19861
- 项目: https://giga-world-0.github.io/
- 代码: https://github.com/open-gigaai/giga-world-0
- 模型: https://huggingface.co/open-gigaai

## 一句话总结
GigaWorld-0 将 world model 明确定位为 VLA 数据引擎：用 GigaWorld-0-Video 生成 appearance/view/mimic/action-semantics 可控的 embodied videos，用 GigaWorld-0-3D 保证几何一致与物理可执行，再通过 IDM/3D planning 产出 paired video-action 数据，训练 GigaBrain-0 等 VLA 在无额外真实交互下提升真实机器人泛化。

## 问题
VLA 数据瓶颈不仅是数量不足，还包括 texture/material/light、camera viewpoint、human-to-robot embodiment、3D geometry 和 contact dynamics 的覆盖不足。单一视频生成、单一 sim2real 外观增强或单一 3D 仿真都只能覆盖一个维度，难以同时提供视觉真实、几何一致、物理合理、指令对齐并带动作监督的数据。

## 方法
- 方法线归属: World Model + VLA → data engine / synthetic embodied data generation；与 DreamZero/Cosmos Policy 不同，它不是直接把 world model 作为 policy，而是用 world model 批量生产 VLA 训练数据。
- 核心 idea: 将 GigaAI 之前的 EmbodieDreamer、MimicDreamer、EgoDemoGen 等能力统一成一个模型套件：2D 视频模型负责大规模真实感和可控编辑，3D 模块负责物理/几何约束，IDM 和 motion planning 负责把生成视频转为可训练动作标签。
- 关键技术点:
  - GigaWorld-0-Video-Dreamer: 2B activated parameter 的 IT2V embodied video foundation model，3D-VAE latent、flow matching、3D-RoPE、sparse attention、4 routed MoE experts / top-2 routing。
  - Video adaptations: AppearanceTransfer 改 texture/material/light；ViewTransfer 生成 novel egocentric view 并同步变换动作；MimicTransfer 将第一人称人手视频转为机器人臂视频。
  - GigaWorld-0-IDM: 对生成视频预测 12 个 arm joints + 2 个 gripper DoF，训练时只输入分割出的机器人臂区域以减少背景干扰。
  - GigaWorld-0-3D: FG 生成可操作物体资产，BG 用 3D Gaussian Splatting 重建场景，Phys 做可微系统辨识，Act 生成可执行物理一致机械臂动作。
  - GigaTrain: FP8、sparse attention、FSDP/DeepSpeed、activation checkpoint 等训练框架；视频生成支持 denoising-step distillation + FP8 inference，论文称可超过 50x 加速。

## 实验
- Benchmark: PBench Robot Set、DreamGen Bench；下游通过 GigaBrain-0 在真实机器人任务中定性展示 Laundry Folding、Paper Towel Preparation、Juice Preparation、Table Bussing、Boxes Moving 等。
- 主要结果: PBench Robot Set overall score 82.07，超过 Cosmos-Predict2-14B 79.88、Cosmos-Predict2.5-2B 79.95、Wan2.2-14B 78.85；DreamGen Bench 上 2B activated GigaWorld-0-Video-Dreamer 在 GR1-Env/Object/Behavior 的 instruction following 上整体优于 Cosmos-Predict2.5-2B。论文将完整 VLA 成功率分析指向 GigaBrain-0。
- 对比基线: Cosmos-Predict2/2.5、Wan2.2 5B/14B；训练效率对比 DeepSpeed ZeRO0/2、FSDP-2、FP8、sparse attention、MoE 配置。

## 评价
- 优势: 不是单点数据增强，而是把 appearance、view、mimic、3D asset、physics、action synthesis 组织成统一数据工厂；2B activated MoE 以较低激活参数达到强 embodied video 质量；与 GigaBrain-0/GigaWorld-Policy 构成“数据引擎 → policy → action-centered WAM”的完整产品线。
- 局限: 论文下游 policy 结果主要定性，定量成功率需结合 GigaBrain-0 论文；生成数据质量依赖过滤器，hallucination/artifact 对 policy 的影响仍未系统量化；GigaWorld-0-IDM/action labels 的精度和泛化范围仍是潜在瓶颈；相比 DreamZero/Cosmos Policy，它本身不直接闭环控制或规划。
- 对 VLA 领域的贡献: 明确提出“World Models as Data Engine”作为区别于 WAM-as-policy 的路线：world model 不一定直接输出动作，也可以作为可控、可扩展、可筛选的 synthetic data pipeline，系统性补齐 VLA 在外观、视角、人类示范和物理一致性上的长尾数据。
