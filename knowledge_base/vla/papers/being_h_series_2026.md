# Being-H Series: H0 / H0.5 / H0.7 (2025-2026)

## 基本信息
- 作者: BeingBeyond Team；H0/H0.5 论文作者包括 Hao Luo, Yicheng Feng, Wanpeng Zhang, Sipeng Zheng, Ye Wang, Zongqing Lu 等
- 机构: BeingBeyond, Peking University, Renmin University of China
- arXiv: H0 2507.15597；H0.5 2601.12993；H0.7 为 2026-04-14 官方 release/paper
- 代码/模型: https://github.com/BeingBeyond/Being-H
- 相关卡片: [being_h0_2025.md](being_h0_2025.md), [being_h05_2026.md](being_h05_2026.md), [being_h07_2026.md](being_h07_2026.md)

## 一句话总结
Being-H 系列从 H0 的“人手视频 VLA 预训练”起步，经 H0.5 扩展为 35K+ 小时/30 具身/统一动作空间的跨具身 VLA，再到 H0.7 用 200K 小时 ego 视频和 15K 小时机器人数据训练 latent world-action model，形成 BeingBeyond 人类中心机器人基础模型路线。

## 问题
VLA 需要同时解决三类瓶颈：机器人示范规模远小于互联网视觉语言数据，灵巧手/人形等高 DoF 具身数据更稀缺，直接从当前观测映射动作又缺少对未来物理演化的显式建模。Being-H 系列试图用大规模人类 ego 视频作为可扩展物理数据源，并逐步把动作、跨具身和世界建模统一起来。

## 方法
- 方法线归属: Human Data Pretraining for VLA；H0/H0.5 属于 VLM + Diffusion/Flow Head + 人类中心学习，H0.7 转向 Latent World-Action Model。
- 核心 idea: 把人手运动视为“foundation manipulator”或物理母语，让模型先从大规模人类视频学习可迁移的操作先验，再通过统一动作空间/后训练/latent future alignment 落到机器人控制。
- 关键技术点:
  - **Being-H0**: 详见 [being_h0_2025.md](being_h0_2025.md)；physical instruction tuning = 人手视频 VLA pretraining + physical space alignment + robot post-training；part-level motion tokenization 用 grouped residual quantization 表示 MANO hand motion；UniHand 聚合 motion capture、VR 和 RGB-only 视频，论文报告超过 150M instruction-following samples，训练子集 UniHand-2.5M。
  - **Being-H0.5**: 已在 [being_h05_2026.md](being_h05_2026.md) 详细记录；核心是 UniHand-2.0（35K+ 小时、30 具身、120B token）、统一物理语义动作空间、MoT/MoF、MPG、UAC 和 ESA。
  - **Being-H0.7**: 详见 [being_h07_2026.md](being_h07_2026.md)；在 VLA 与 pixel-space WAM 之间加入 latent reasoning space；prior branch 用 learnable latent queries，posterior branch 训练时看未来观测并替换为 future embeddings，通过 latent hidden-state alignment 把未来信息注入可部署分支，推理时不做未来像素 rollout。
  - H0.7 数据规模: 官方 release 报告 200,000 小时 egocentric human videos + 15,000 小时 robot demonstrations。

## 实验
- Benchmark: H0 在真实灵巧手任务上评估 Pick-Place-Toy、Close-Toolbox、Close-Lid、Pour-Cup、Unfold-Clothes；H0.5 见独立卡片；H0.7 在 LIBERO、LIBERO-plus、GR1、CALVIN、RoboCasa、RoboTwin2.0，以及 3 个真机平台 12 个任务/5 个能力套件评估。
- 主要结果: H0 在 real-world dexterous tasks 上整体优于 GR00T N1.5 和无 physical instruction tuning 的 InternVL3，例如 Pour-Cup 100%、Unfold-Clothes 75%；H0.7 报告 LIBERO 99.2%、RoboCasa 62.1%、LIBERO-plus zero-shot 82.1%/finetune 84.8%、GR1 49.2%、RoboTwin2.0 clean 90.2%/randomized 89.6%、CALVIN ABCD->D 4.67/5；真机五个 suite 中 H0.7 全部领先 H0.5、π0.5 和 Fast-WAM。
- 对比基线: H0 对比 GR00T N1.5、InternVL3；H0.5 对比 π0.5、GR00T-N1、InternVLA-M1 等；H0.7 对比 H0.5、π0.5、Fast-WAM 和各 benchmark SOTA。

## 评价
- 优势: 路线连续清晰：H0 证明人手 motion token 可迁移到机器人，H0.5 规模化到跨具身统一动作空间，H0.7 进一步把 ego video 的未来物理结构压缩到 latent action prior；同时维持较强开源/工程部署导向。
- 局限: H0.7 当前是官方 release/paper 而非 arXiv 条目；H0/H0.5/H0.7 的数据和评测协议逐步变化，横向归因不完全干净；H0.7 的 latent world modeling 虽避免像素 rollout，但未来监督如何跨更复杂开放世界任务扩展仍需第三方复现。
- 对 VLA 领域的贡献: Being-H 系列是 EgoScale 之外最系统的人类 ego 视频 -> VLA/WAM scaling 路线，建议在主索引中把它从单篇 Being-H0.5 扩展为“Being-H family: H0 human-video VLA pretraining -> H0.5 cross-embodiment VLA -> H0.7 latent WAM”。
