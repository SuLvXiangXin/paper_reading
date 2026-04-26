# Being-VL-0: From Pixels to Tokens (2024)

## 基本信息
- 作者: Wanpeng Zhang, Zilong Xie, Yicheng Feng, Yijiang Li, Xingrun Xing, Sipeng Zheng, Zongqing Lu
- 机构: Peking University, CUHK, UC San Diego, BAAI, CASIA
- arXiv: 2410.02155
- 项目: https://research.beingbeyond.com/being-vl0
- 会议: ICLR 2025

## 一句话总结
Being-VL-0 是 BeingBeyond 的视觉 tokenization 原型：先用 VQ-GAN 把图像量化成离散 token，再像文本 BPE 一样合并水平/垂直相邻的高频视觉 token，使 Llama-3.1-8B 能以统一 token 序列学习图文理解；它是 VLM/MLLM backbone 研究，不是直接输出机器人动作的 VLA。

## 问题
现有 MLLM/VLA backbone 多依赖 CLIP/SigLIP 等连续视觉编码器加 projector，把视觉 embedding 对齐到 LLM。这会保留一个明显的 modality gap：LLM 原本擅长处理离散语言 token，却需要重新解释外部视觉 encoder 输出的连续向量。Being-VL-0 问的是：能否像文本一样给视觉也学习 tokenizer，让视觉 token 本身带有结构先验，从而降低图文对齐难度?

## 方法
- 方法线归属: VLM/MLLM backbone；离散视觉 token + BPE visual encoding；对 VLA 是可复用感知/语义 backbone，而非 action policy。
- 核心 idea: 把图像 patch 的 VQ token 当作视觉“字符”，用 2D BPE 合并频繁共现的水平/垂直 token 对，得到表示局部结构或高层形状的组合视觉 token，再与文本 token 拼成同一个自回归序列。
- 关键技术点:
  - 理论分析指出，Transformer 直接学习某些二维 Markov 结构时可能退化到 unigram 行为；合适 tokenizer 能注入结构先验，使学习问题更接近可解。
  - BPE Image Tokenizer 在 VQ-GAN 8192 codebook 之上扩展视觉词表，支持迭代合并出任意形状的视觉 pattern；论文比较 1K-16K 词表，经验上 8K 附近最好。
  - MLLM 基于 Llama-3.1-8B 扩展 embedding，新增 VQ/BPE 视觉 token 和图像边界 token。
  - 两阶段训练：PT 阶段冻结文本 embedding、用 caption 数据学习新增视觉 embedding；SFT 阶段全参微调多轮图文指令数据。
  - 数据：tokenizer 用 ImageNet/CC/LAION/SBU 共 2.78M 图像；PT 用 CC-3M 595K + LCS 558K；SFT 用 LLaVA-OneVision 1.27M。
  - 与 VLA/VLM backbone 的关系：它提供的是“视觉输入如何进入 LLM”的替代方案，可增强未来 VLA 的识别、grounding、空间语义理解；但它没有 proprioception、action head、flow/diffusion expert 或闭环控制接口。视觉 BPE token 也不等同于 RT-2/OpenVLA 的 action token。

## 实验
- Benchmark: VQAv2, MMBench, MME-P/MME-C, POPE, VizWiz。
- 主要结果: BPE consistently 优于 VQ-only。最佳 scaled 版本达到 VQAv2 60.6、MMBench 44.0、MME-P 1316.2、MME-C 331.0、POPE 81.3、VizWiz 48.2；未加额外 scaling 的 LLM+VQ+BPE PT(freeze)+SFT 为 57.1/40.9/1223.5/307.1/79.0/46.0。
- 对比基线: LLM+VQ、不同 PT 策略、不同视觉词表规模；BPE + 冻结文本 embedding 的 PT 最稳定，说明先保护语言空间、再学习视觉 embedding 有利于对齐。

## 评价
- 优势: 把“tokenizer 是模型能力的一部分”从文本推广到视觉，给离散视觉 MLLM 一个清晰可复现的起点；对 VLA 来说，价值在于可能替代连续视觉 encoder + projector，减少感知 backbone 与 LLM 的表示断层。
- 局限: 结果仍弱于当时强连续视觉 encoder MLLM，实验重点是理解 benchmark 而非机器人控制；VQ-GAN 量化本身会损失细节，BPE 合并也可能牺牲小物体/精细状态。
- 对 VLA 领域的贡献: Being-VL-0 不应归入 VLM+Action Token 或 VLM+Flow Head，而应视作 VLA backbone 的上游基础设施：它改善“图像如何变成可被 LLM/VLM 使用的 token”，为后续把更强视觉理解接入 VLA action expert、Connector 或 planner 提供候选路线。
