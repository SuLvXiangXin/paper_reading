# 流派 B: 视频流 VLM

## 核心思路
将导航建模为视频理解问题：VLM 直接从实时 RGB 视频流 + 语言指令推理下一步动作。无需显式建图。

## 优势
- 极简输入（仅需 RGB 视频 + 语言）
- 利用 VLM 的强泛化能力
- 自然适配流式处理和实时部署

## 局限
- 长序列视频的上下文窗口压力
- 缺少显式空间记忆，长程导航可能迷路
- 计算量大（VLM 推理延迟）

## 代表工作

### NaVid (Zhang et al., RSS 2024) — 198 引用
开创性工作。首个基于视频的 VLM 导航方法，无需地图/里程计/深度。510K 导航样本训练。

### Uni-NaVid (Zhang et al., RSS 2025) — 93 引用
统一 4 种导航子任务（指令跟随、目标搜索、QA、人物跟踪），3.6M 样本训练。

### StreamVLN (Wei et al., 2025) — 52 引用
SlowFast 双通道上下文建模：Fast 滑窗做实时响应，Slow 压缩历史做长程记忆。3D-aware token pruning。

### SparseVideoNav / MM-VideoNav (Zhang et al., 2026)
首次把视频生成模型引入真实 beyond-the-view VLN。基于 Wan2.1 T2V 改造为历史条件 I2V，生成稀疏未来帧（覆盖 20s horizon），再用生成未来指导连续动作。它不是单纯“看历史视频做下一步”，而是显式想象当前视野外的可行路径。

## 发展趋势
- 从离线处理 → 流式实时（StreamVLN）
- 从单任务 → 多任务统一（Uni-NaVid）
- 从视频理解 → 视频生成式未来扩展（SparseVideoNav）
- 下一步：与双系统结合（DualVLN = VLM + DiT）并压缩生成式未来模型的延迟
