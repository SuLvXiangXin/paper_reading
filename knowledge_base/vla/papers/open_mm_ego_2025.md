# OpenMMEgo: Enhancing Egocentric Understanding for LMMs with Open Weights and Data (2025)

## 基本信息
- 作者: Hao Luo, Zihao Yue, Wanpeng Zhang, Yicheng Feng, Sipeng Zheng, Deheng Ye, Zongqing Lu
- 机构: Peking University, BeingBeyond, Renmin University of China, Tencent
- 发表: NeurIPS 2025
- 论文/页面: https://neurips.cc/virtual/2025/loc/san-diego/poster/119544
- 代码/数据: https://github.com/BeingBeyond/OpenMMEgo

## 一句话总结
OpenMMEgo 不是动作模型，而是面向 egocentric video 的 LMM 训练数据和开放权重路线：构建 OME10M（8.2M ego video QA + 约 1M general QA）和 OMEBench，用 semantic-aware visual token compression 与 dual curriculum 让 Qwen2.5-VL/LLaVA-Video 显著提升第一人称视频理解且基本不损伤通用视频能力。

## 问题
通用视频 LMM 往往擅长第三人称、剪辑稳定的视频，但第一人称视频存在视角快速变化、自运动、手-物交互细节和长期事件记忆，现有 ego QA 数据又常不可访问、粒度粗或只覆盖短片段，难以支撑 embodied intelligence 所需的细粒度理解。

## 方法
- 方法线归属: Egocentric perception / LMM instruction tuning；是 VLA 的感知与语义理解组件，不是 VLA policy。
- 核心 idea: 用大规模合成 QA 把 Ego4D/Ego-Exo4D 的第一人称交互视频转成可训练的 LMM 指令数据，同时通过 token compression 和 curriculum 处理长 ego 视频的计算与难度问题。
- 关键技术点:
  - OME10M: 从 Ego4D、Ego-Exo4D、Ego4D-GoalStep 合成多层 QA，包含 behavior-based QAs、vision-centric QAs 和 general video QAs。
  - OMEBench: 372 个 hold-out videos、约 4K multiple-choice questions，分 behavior 和 vision-centric 子集。
  - semantic-aware token compression: STM + TTP 组合，在固定视觉 token budget 下选择关键时空/实体信息，支持更长视频。
  - dual curriculum learning: offline difficulty 预估 + online learning dynamics，按样本复杂度逐步训练。

## 实验
- Benchmark: EgoSchema、EgoPlan、QAEgo4D、EgoTaskVQA、OMEBench；通用视频 Video-MME、MVBench、PerceptionTest；补充 HD-EPIC、OpenEQA、EPIC-Kitchens-100 MIR。
- 主要结果: OpenMMEgo-Qwen2.5-VL 相比 Qwen2.5-VL 在 EgoSchema 69.3(+4.3)、EgoPlan 50.2(+5.0)、QAEgo4D 65.6(+6.2)、EgoTaskVQA 56.2(+2.5)、OMEBench-beh 65.7(+10.4)、OMEBench-vis 63.2(+13.8)；通用视频基本稳定（Video-MME 65.0 -0.1，MVBench 70.8 +1.2，PerceptionTest 71.2 +0.7）；STM+TTP 支持 192 frames，推理成本约 1.47x。
- 对比基线: Qwen2.5-VL, LLaVA-Video, Qwen2-VL, LLaVA-OneVision, VideoChat-Flash, MM-EGO, Gemini-2.0-Flash 等。

## 评价
- 优势: 明确补齐了 ego 视频中“自运动 + 物体细节 + 交互事件”的 LMM 短板，对 VLA 的高层感知、数据标注和长视频理解有直接支撑。
- 局限: QA 多由 Gemini 合成，可能继承 teacher bias；没有动作监督或机器人控制实验；对 VLA 性能的收益仍是间接推断；仓库 README 当前仍提示代码和数据将发布。
- 对 VLA 领域的贡献: 为 Being-H/ego VLA 体系提供可复用的 egocentric semantic backbone 和数据生成范式，适合作为人手视频预训练前的自动标注、过滤和任务理解模块。
