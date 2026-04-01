# 流派 C: LLM 推理驱动

## 核心思路
利用 LLM/VLM 的语言理解和推理能力，做显式的推理链（chain-of-thought）规划导航。

## 代表工作

### NavGPT (Zhou et al., AAAI 2024) — 328 引用
首个 LLM-based VLN。将场景文本化，GPT 做显式推理。

### NavGPT-2 (Zhou et al., ECCV 2024) — 88 引用
升级为 VLM，直接接收视觉输入，无需文本化中间步骤。

### InstructNav (Long et al., 2024) — 123 引用
零样本指令导航，组合 LLM + 视觉模块，无需任务特定训练。

## 发展趋势
- NavGPT → NavGPT-2：从纯 LLM 到 VLM
- 零样本能力强但效率低（多次 LLM 调用）
- 与 RL 微调结合（VLN-R1）
