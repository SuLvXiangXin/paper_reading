# Video World Model — 视频世界模型

## 领域概述
视频世界模型（Video World Model）旨在构建能够理解和模拟物理世界的视频生成系统，
核心目标是全方位提升性能：三维一致性、物理合理性、长时渲染质量、长时一致性、场景丰富度和渲染速度。

## 子方向
| 子方向 | 核心挑战 | 代表工作数 | 方法文件 |
|--------|----------|-----------|---------|
| [三维一致性](methods/3d_consistency.md) | 相机精准渲染、多视角一致性 | 1 | — |
| [物理合理性](methods/physical_plausibility.md) | 多智能体交互、Actor-场景交互 | — | — |
| [长时渲染质量](methods/long_rendering_quality.md) | 长时间序列渲染稳定性，exposure bias / train-test gap | 11 | ✓ |
| [长时一致性](methods/long_consistency.md) | 场景/角色/逻辑一致性 | 9 | — |
| [渲染速度](methods/rendering_speed.md) | 实时生成 | 2 | ✓ |
| [性能提升专项](methods/performance_enhancement.md) | 时序连续性 + 渲染分辨率 | 5 系列 | — |

## 调研报告
- [视频世界模型全景调研](reports/video_world_model_survey.md) — 2026.03，按彭德刚框架整理

## 论文卡片
- [papers/index.md](papers/index.md) — 全部论文速查表
- [1X World Model](papers/1x_world_model_2025.md) — 2025，1X Technologies，首个全身人形机器人视频世界模型，用于策略离线评估（state value预测+真机相关性验证）
- [Self-Forcing++](papers/self_forcing_plus_plus_2025.md) — 2025.10，UCLA+ByteDance，分钟级高质量视频生成
- [LongLive](papers/longlive_2025.md) — 2025.09，NVIDIA+MIT+HKUST，实时交互式长视频生成（20.7 FPS，240s，KV-recache）
- [Context as Memory](papers/context_as_memory_2025.md) — 2025.06，港大+浙大+快手，FOV检索帧级记忆实现长期场景一致性
- [Sliding Tile Attention](papers/sliding_tile_attention_2025.md) — 2025.02，UCSD+UCB+清华，tile-wise 稀疏注意力使 HunyuanVideo 推理加速 3.53×

## 时间线
- 2024.12: CausVid 开启快速 AR 视频生成（双向→因果蒸馏 + DMD）
- 2025.02: STA 首次将 3D 滑动窗口注意力真正高效实现（ICML 2025），视频 DiT 推理加速 3.53×
- 2025.04-06: 长时一致性记忆方法爆发（WorldMem, Context as Memory, VMem, SPMem）
- 2025.05-06: 交互式世界模型涌现（MAGI-1, Matrix-Game, Hunyuan-GameCraft）
- 2025.06: Self-Forcing 定义长时渲染质量基线（exposure bias 根治）
- 2025.09: LongLive 实现实时交互式长视频生成（20.7 FPS，240s，KV-recache 首次解决流式 prompt 切换）
- 2025.07-12: Forcing 家族快速扩展（Self-Forcing++, Rolling Forcing, LongLive, Reward Forcing, Resampling Forcing）
- 2025.09: FantasyWorld 推进 3D 一致性
- **2025.10: Self-Forcing++ 实现 4 分 15 秒分钟级高质量视频，发现训练预算 scaling law**
- 2026.01: TeleWorld 4D 世界模型

## 关键概念速查
| 概念 | 定义 | 相关方法 |
|------|------|---------|
| Exposure Bias | AR 训练用 GT 条件、推理用自生成条件的分布差异 | Self-Forcing 系列 |
| Distribution Matching Distillation (DMD) | 最小化 student/teacher 输出分布 KL 散度 | CausVid, Self-Forcing, Self-Forcing++, LongLive |
| Rolling KV Cache | 推理时滑动窗口 KV 缓存，支持流式长视频 | Self-Forcing, Self-Forcing++, LongLive |
| Backward Noise Initialization | 对已生成 clean latent 重新加噪作为 student/teacher 评分起点 | CausVid, Self-Forcing, Self-Forcing++ |
| Extended-DMD | 在自生成长视频的均匀采样短窗口上计算 DMD loss | **Self-Forcing++** |
| Visual Stability | 用 Gemini-2.5-Pro 评曝光稳定性（修正 VBench 偏差）| **Self-Forcing++** |
| Frame Sink | 将视频第一帧 latent 作为永久全局 anchor，保持长程一致性；attention sink 需先解决 train-test 失配才能生效 | **LongLive** |
| KV-Recache | Prompt 切换时用已生成帧 + 新 prompt 重建 KV cache，刷新语义同时保持视觉连续 | **LongLive** |
| Streaming Long Tuning | 逐 clip 滚动 DMD（train-long–test-long），历史帧 detach，梯度局部化 | **LongLive** |
| FOV Overlap Retrieval | 根据相机视野（Field of View）的几何重叠关系筛选记忆帧 | **Context as Memory** |
| History Context Comparison | "旋转离开再旋转回来"评测协议，直接测量模型自身记忆一致性 | **Context as Memory** |
| Frame-Dimension Concatenation | 将上下文帧与预测帧沿帧维度拼接输入 DiT，无需额外模块 | **Context as Memory**, ReCamMaster |
| Mixed Block | FlashAttention 中部分被 mask 的 block，是 SWA 效率差根因；STA 从算法上消除 | **STA** |
| Tile（STA） | (T,T,T) token 立方体，T³=FA block size；STA 以 tile 为单位滑动消除 mixed block | **STA** |
| Head Specialization | 不同 attention head 的局部性强度不同但对 prompt 稳定，可离线搜索最优窗口 | **STA** |
| Attention Recall | 局部窗口内注意力得分占总得分比例，量化视频 DiT 的 3D 局部性 | **STA** |
| Kernel Efficiency | 稀疏内核 MFU / 全注意力 MFU，衡量稀疏化实际效率转化率 | **STA** |
