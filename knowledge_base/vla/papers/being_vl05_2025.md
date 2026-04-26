# Being-VL-0.5: Unified Multimodal Understanding via Byte-Pair Visual Encoding (2025)

## 基本信息
- 作者: Wanpeng Zhang, Yicheng Feng, Hao Luo, Yijiang Li, Zihao Yue, Sipeng Zheng, Zongqing Lu
- 机构: Peking University, UC San Diego, Renmin University of China, BeingBeyond
- arXiv: 2506.23639
- 项目: https://research.beingbeyond.com/being-vl05
- 会议: ICCV 2025 Highlight

## 一句话总结
Being-VL-0.5 是 Being-VL-0 的工程化升级：用频率 + 空间一致性构造 priority-guided visual BPE 词表，并配合 curriculum data composition 与 progressive unfreezing，把离散视觉 token MLLM 从概念验证推进到接近连续视觉 encoder 模型的通用 multimodal understanding 性能。

## 问题
Being-VL-0 证明了视觉 BPE 的价值，但早期实现主要依赖频率统计，训练 recipe 也较粗。实际 MLLM/VLA backbone 需要的不只是“能离散化图像”，还要让视觉 token 在 LLM 内部形成稳定语义空间，并在感知、推理、指令跟随任务上可扩展。

## 方法
- 方法线归属: VLM/MLLM backbone；priority-guided BPE visual encoding；可作为 VLA 的视觉语言 backbone 候选，不是 VLA policy。
- 核心 idea: 在 VQ-GAN token 之上构造统一视觉词表，让 VQ token 保留细粒度局部信息，让 BPE token 捕获更大尺度/更稳定的视觉结构；再用分阶段训练让新增视觉 token 逐步对齐语言模型。
- 关键技术点:
  - **Priority-guided encoding**: 候选 token pair 不只按共现频率排序，还加入 spatial consistency，优先合并在不同图像中保持稳定相对位置的视觉 pattern。
  - **统一序列建模**: 图像先经 VQ-GAN 量化，再经 visual BPE 编码，最终 VQ/BPE 视觉 token 与文本 token 进入同一个 autoregressive transformer。
  - **Model expansion**: 默认扩展 8K VQ token + 8K BPE token；16K BPE 版本有更大容量但部分 token 激活不足，效率不如 8K 稳定。
  - **Multi-stage training**: Stage 1 只训练新增视觉 embedding；Stage 2 解冻早期 transformer 层；Stage 3 全参微调。
  - **Curriculum data composition**: 从 Foundation Data/image-caption 到 Perception、Reasoning、Instruction 数据逐步加重，匹配 BPE token 从低层结构到高层语义的学习过程。
  - 与 VLA/VLM backbone 的关系：Being-VL-0.5 解决的是“视觉语义如何更自然地嵌入 LLM”，可增强 VLA 的目标识别、空间 grounding、指令理解和 planner/Connector；低层动作仍需要 action token、flow head、diffusion head 或模块化 skill policy 另行建模。

## 实验
- Benchmark: VQAv2, MMBench, MME-P, SciQA-IMG, POPE, VizWiz。
- 主要结果:
  - Being-VL-0.5: VQAv2 80.2、MMBench 71.8、MME-P 1525.8、SciQA-IMG 70.3、POPE 84.3、VizWiz 57.4。
  - Being-VL-0.5+: VQAv2 80.6、MMBench 72.1、MME-P 1536.3、SciQA-IMG 69.0、POPE 86.0、VizWiz 57.8。
  - w/o BPE 仅 54.3/38.2/1301.2/57.8/76.1/45.0，说明性能不是来自 VQ 离散化本身，而是来自 BPE 视觉词表和训练策略。
  - 标准三阶段训练在 perception/reasoning 平均分 80.3/71.1，高于 single-stage 的 71.2/62.3。
- 对比基线: 连续 embedding 模型（LLaVA-1.5/Next, VILA-1.5, ShareGPT4V 等）和离散 token 模型（Chameleon, Unified-IO-2, Being-VL-0）。Being-VL-0.5 显著超过 Being-VL-0，并把离散 token 路线拉近到连续视觉 encoder 路线。

## 评价
- 优势: 从 tokenizer、embedding expansion、数据 curriculum 到解冻策略形成完整 recipe；证明离散视觉 token 不必只服务生成，也能支撑强 multimodal understanding。
- 局限: 仍是图文理解模型，没有机器人动作、本体感知或实时控制评测；VQ/BPE 编码对高精度几何、接触状态和时序视频的支持还需结合机器人数据验证。
- 对 VLA 领域的贡献: Being-VL-0.5 对 VLA 的意义主要在 backbone 层：相比 OpenVLA/π0/Being-H 依赖的连续视觉 encoder，它提供了一条“视觉也 tokenized、与语言同序列建模”的路线。若接入 VLA，需要再加动作表示与控制头；它本身不是 VLA，但可能改善 VLA 上游 perception/grounding 的 token quality。
