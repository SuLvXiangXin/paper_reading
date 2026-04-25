# RoboDual: Towards Synergistic, Generalized and Efficient Dual-System for Robotic Manipulation (2024)

## 基本信息
- 作者: Qingwen Bu, Hongyang Li, Li Chen, Jisong Cai, Jia Zeng, Heming Cui, Maoqing Yao, Yu Qiao
- 机构: Shanghai Jiao Tong University, The University of Hong Kong, AgiBot, Shanghai AI Lab
- arXiv: 2410.08001
- 链接: https://arxiv.org/abs/2410.08001
- 项目页: https://robodual.github.io

## 一句话总结
RoboDual 把 OpenVLA 类慢速 generalist 和小型 diffusion specialist 组合起来：generalist 提供语义和粗动作计划，specialist 以高频连续 action chunk 执行，从而同时改善泛化、精度和推理频率。

## 问题
Generalist VLA 有跨任务语义和语言泛化，但推理慢、动作离散、控制不够精细；ACT/Diffusion Policy 等 specialist 控制平滑高效，但缺少跨任务和语言泛化能力。

## 方法
- 方法线归属: Dual-system VLA / Generalist-conditioned specialist / Diffusion policy
- 核心 idea: 保留 OpenVLA 的高层能力，用一个 20M 级 DiT specialist 消化 generalist 的 action token 和 hidden latent，并结合多模态观测输出更快、更平滑的连续动作。
- 关键技术点:
  - Generalist: 基于 OpenVLA LoRA fine-tune，并扩展为自回归 action chunk 输出。
  - Specialist: Diffusion Transformer 对连续 action sequence 去噪，可接入 RGB、depth、tactile、proprioception 等观测。
  - Conditioning: specialist 同时使用 generalist 离散动作、generalist latent、视觉/本体等条件。
  - Latency handling: shifted-window conditioning 和 latency-aware augmentation 处理 generalist 与 specialist 异步运行。

## 实验
- Benchmark: CALVIN ABC->D、真实 ALOHA 单指令/多指令任务、位置/背景/干扰物/新物体泛化。
- 主要结果: CALVIN 平均完成长度 3.66，高于 3D Diffuser Actor 3.27；真实任务总体比最强 baseline 高约 20%；相比 OpenVLA 真实场景提升 26.7%，控制频率约 15Hz，对比 OpenVLA 约 3.9Hz。
- 对比基线: ACT、Diffusion Policy、Octo、OpenVLA、RoboFlamingo、GR-1、3D Diffuser Actor、SuSIE 等。

## 评价
- 优势: 击中了 OpenVLA 的两大痛点：离散动作精度和低频推理；小 specialist 训练成本低，且能利用 depth/tactile 等 generalist 不易接入的传感器。
- 局限: 系统复杂度高于单一 VLA；generalist 的错误计划仍可能传递给 specialist；需要为目标机器人训练 specialist，零样本跨具身能力有限。
- 对 VLA 领域的贡献: RoboDual 是“VLA 负责语义/规划，diffusion specialist 负责控制”的代表工作，为后续 VLA 部署提供了比单模型更工程化的折中方案。
