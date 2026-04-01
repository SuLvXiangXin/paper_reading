# StreamVLN: Streaming VLN via SlowFast Context Modeling (2025)

## 基本信息
- **标题**: StreamVLN: Streaming Vision-and-Language Navigation via SlowFast Context Modeling
- **作者**: Meng Wei, Chenyang Wan, Xiqian Yu, Tai Wang, Yuqiang Yang, Xiaohan Mao, Chenming Zhu, Wenzhe Cai, Hanqing Wang, Yilun Chen, Xihui Liu, Jiangmiao Pang
- **机构**: 上海 AI Lab, 香港大学
- **arXiv**: 2507.05240
- **年份**: 2025
- **引用数**: 52
- **方法线归属**: **流式 VLN**

## 核心贡献
1. **首个流式 VLN 框架**：解决传统 VLN 方法延迟高、无法实时响应的问题
2. **SlowFast 双通道上下文建模**
3. **3D-aware Voxel Token Pruning**：仅推理时使用，减少 ~20% token 且性能提升
4. **交错式 VLA**：多轮对话格式，每轮 8 轮 × 4 动作 = 32 个连续动作

## 方法架构

### 基座模型：LLaVA-Video 7B（Qwen2-7B 语言模型）

### Fast 通道（快速流式对话上下文）
- **滑动窗口 KV cache**：保留最近 N=8 轮对话的 KV 状态
- 窗口满时：观测 token KV offload（可供 Slow 通道使用），非观测 token（prompt/动作）直接丢弃
- **消除 99%+ 重复 prefill 计算**
- 延迟在长导航中保持稳定（不随轮数线性增长）

### Slow 通道（慢更新记忆上下文）
- 每个会话结束时均匀采样 8 帧存入记忆
- 每帧 196 tokens（14×14 patch grid）
- 记忆容量：8帧 × 196 tokens = 1568 tokens → 剪枝后 ~1250 tokens

### 3D-aware Voxel Token Pruning
- 利用深度信息将 2D patch 反投影到共享 3D 空间
- 离散化为均匀体素（voxel）
- 多帧中投影到同一体素的 token → 仅保留最新观测
- 阈值机制：若某帧剪枝后保留 token 数低于 θ·H·W，整帧丢弃
- **仅推理时使用**（训练时剪枝损害性能）
- 效果：减少 ~20% token，SR 反而提升 +1.2（聚焦有效 token）

### 动作 token 设计
- 使用罕见符号 ↑←→ 作为动作 token（1 token/动作）
- 对比：NaVILA 自然语言 ~10 token/动作，UniNaVid 文本词汇 1 token/动作
- 单次推理 4 动作仅需 **0.27s**

## 训练数据

| 数据源 | 规模 | 说明 |
|--------|------|------|
| R2R + R2R-EnvDrop + RxR (MP3D) | 450K 视频片段 | 60 个场景 |
| ScaleVLN 子集 (HM3D) | 300K（~150K 轨迹）| 700 个场景 |
| DAgger 矫正数据 | 240K | 模型 rollout + 专家纠正 |
| LLaVA-Video-178K + ScanQA | 248K | 视频 VQA + 3D 理解 |
| MMC4 | 230K | 交错图文多轮对话 |
| **总计** | **~1.47M** | VLA 67% + 通用 33% |

## 训练策略
- **两阶段训练**：
  1. 仅 oracle VLN 轨迹微调 1 epoch
  2. 混合 VLN + DAgger + 通用多模态数据，再训练 1 epoch
- 学习率：LLM 2e-5，视觉编码器 5e-6
- Batch size：128 视频片段
- 训练成本：**~1500 A100 GPU-hours**

## 实验结果

### R2R-CE Val-Unseen

| 方法 | SR↑ | SPL↑ | NE↓ |
|------|------|------|------|
| **StreamVLN†** | **56.9** | **51.9** | **4.98** |
| NaVILA† | 54.0 | 49.0 | 5.22 |
| UniNaVid† | 47.0 | 42.7 | 5.58 |
| NaVid | 37.4 | 35.9 | 5.47 |
| ETPNav（全景+Depth+Odom）| 57.0 | 49.0 | 4.71 |

- RGB-only 方法中 **SOTA**
- 接近全景+多传感器方法 ETPNav（SR 56.9 vs 57.0）

### RxR-CE Val-Unseen
- StreamVLN† SR **52.9**, SPL **46.0**, nDTW **61.9** — 全面 SOTA

### 推理延迟
- 单次推理（4 动作）：**0.27s**（RTX 4090）
- KV cache 使延迟不随导航长度增长
- 24 轮时仍保持 ~0.15s，而无 cache 方法已增至 0.50s+

## 消融实验关键结论

| 消融 | SR 变化 | 结论 |
|------|---------|------|
| 去掉 RxR 数据 | -7.8 | RxR 贡献最大 |
| 去掉 DAgger | -5.5 | DAgger 至关重要 |
| 去掉 MMC4 | -2.0 | 交错图文对多轮交互有帮助 |
| 记忆 2×196→8×196 | +8.2 | 更多记忆帧显著提升 |
| 使用全部上下文 | -5.5 vs 8×196 | **过长上下文反而有害** |
| Voxel pruning | +1.2 | 剪枝去噪，反而提升 |
| 符号 token vs 自然语言 | -1.7 SR, 3.7x 更快 | 符号是延迟-性能最优折衷 |

## 局限性
1. **低级动作鲁棒性不足**：对视角变化和遮挡不够鲁棒
2. **超长导航仍有挑战**：混合上下文在极长导航中推理一致性有限
3. **异步部署复杂**：需同步历史动作以保持对话一致性

## 与其他工作的关系
- **前序**: NaVid（视频 VLM 思路）
- **后续**: DualVLN（双系统升级，SR +7.4）
- **关键洞察**: 过长上下文有害 → SlowFast 分离是正确方向；体素剪枝去噪提升性能
