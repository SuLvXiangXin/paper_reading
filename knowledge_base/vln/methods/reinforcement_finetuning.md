# 流派 F: 强化微调

## 核心思路
在 SFT 后用强化学习进一步优化 VLN 策略，类似 DeepSeek-R1 的 post-training 范式。

## 代表工作

### VLN-R1 (Qi et al., 2025) — 43 引用
GRPO 训练 + Time-Decayed Reward。首个将 RL 后训练引入 VLN。

### EvolveNav (Lin et al., 2025) — 15 引用
自改进 embodied reasoning，通过迭代 RL 提升导航性能。

## 发展趋势
- DeepSeek-R1 的成功催生了 VLN 领域的 RL 后训练浪潮
- GRPO 无需价值网络，适合大模型
- 预期 2026 年会有更多 RL-based VLN 工作
