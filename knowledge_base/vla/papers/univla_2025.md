# UniVLA: Learning to Act Anywhere with Task-centric Latent Actions (2025)

## 基本信息
- 作者: Qingwen Bu, Yanting Yang, Jisong Cai, Shenyuan Gao, Guanghui Ren, Maoqing Yao, Ping Luo, Hongyang Li
- 机构: The University of Hong Kong, OpenDriveLab, AgiBot
- arXiv: 2505.06111
- 链接: https://arxiv.org/abs/2505.06111
- 代码: https://github.com/OpenDriveLab/UniVLA

## 一句话总结
UniVLA 用 task-centric latent action 把 action-free video、跨具身机器人数据和导航数据统一到离散潜动作空间，避免直接对齐低层动作标签，在少得多的预训练算力和下游数据下显著超过 OpenVLA。

## 问题
OpenVLA/RT-2 类 VLA 依赖动作标注和具身特定动作空间，难以利用大量人类视频、导航视频或不同机器人数据；直接把低层动作 token 作为统一语言会受到 embodiment mismatch 限制。

## 方法
- 方法线归属: VLM + Latent Action Token / Action-label-free pretraining
- 核心 idea: 先从视频中无监督学习“任务中心”的潜动作 token，再让 VLM 预测这些潜动作，部署时只需学习小型 action decoder 将潜动作转成目标机器人的低层动作。
- 关键技术点:
  - Latent Action Model: 用 inverse dynamics encoder + forward dynamics decoder，从帧对中学习离散 latent action；预测目标不是像素而是 DINOv2 feature。
  - Task-centric decoupling: 两阶段训练先用语言吸收任务无关视觉变化，再冻结 task-irrelevant codebook，学习新的 task-centric codebook。
  - Generalist policy: 基于 Prismatic-7B，扩展 ACT token 词表，自回归预测 4 个 latent action token。
  - Efficient adaptation: 下游通过 LoRA + 约 12.6M 参数 action decoder 将 latent action 解码为 action chunk；还可把历史 latent action 输出放入 prompt，近似低成本历史记忆。

## 实验
- Benchmark: LIBERO、CALVIN、SimplerEnv、Room-to-Room navigation、真实机器人部署。
- 主要结果: LIBERO 平均成功率 95.2%，高于 OpenVLA 76.5；论文还报告在 Real-world、Room2Room、SimplerEnv、CALVIN 上均明显超过 OpenVLA，并称预训练算力少于 OpenVLA 的 1/20、下游数据少于 1/10。
- 对比基线: OpenVLA、LAPA、Diffusion Policy、Octo、MDT、MaIL 等。

## 评价
- 优势: 用潜动作绕开跨具身低层动作对齐，是利用 action-free human videos 的务实方案；压缩动作空间使预训练更省算力；同一框架覆盖 manipulation 和 navigation。
- 局限: 潜动作仍需要下游 decoder 学到目标 embodiment 的控制细节；VLM 自回归 latent token 仍可能受推理延迟影响；action-free video 的质量和任务相关性决定上限。
- 对 VLA 领域的贡献: UniVLA 是 OpenVLA 动作 token 路线的一个重要变体：从“离散化真实动作”转向“学习可迁移潜动作”，与 π0 的 continuous flow head 形成另一条解决动作空间问题的路线。
