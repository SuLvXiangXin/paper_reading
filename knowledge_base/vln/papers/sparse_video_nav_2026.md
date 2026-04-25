# SparseVideoNav: Sparse Video Generation for Beyond-the-View VLN (2026)

## 基本信息
- **标题**: Sparse Video Generation Propels Real-World Beyond-the-View Vision-Language Navigation
- **页面名/别名**: MM-VideoNav / SparseVideoNav
- **作者**: Hai Zhang, Siqi Liang, Li Chen, Yuxian Li, Yukuan Xu, Yichao Zhong, Fu Zhang, Hongyang Li
- **机构**: The University of Hong Kong / OpenDriveLab
- **arXiv**: 2602.05827
- **年份**: 2026
- **代码/项目**: https://github.com/OpenDriveLab/SparseVideoNav
- **方法线归属**: **视频生成式 beyond-the-view VLN / sparse future world expansion**

## 核心贡献
1. **首次将视频生成模型引入真实世界 beyond-the-view navigation (BVN)**：目标可能在当前视野外，且语言只给高层意图而非逐步指令。
2. **Sparse future 监督**：生成稀疏未来帧而非连续长视频，用 20 秒预测 horizon 缓解 LLM/VLM 导航的短视问题。
3. **四阶段训练管线**：T2V→I2V、历史注入、扩散蒸馏、基于生成未来的动作学习。
4. **真实 Go2 零样本验证**：在室内、室外、夜间 6 个真实场景中显著优于 Uni-NaVid、StreamVLN、InternVLA-N1。

## 方法架构

### Sparse future video as world expansion
- 核心假设：BVN 的难点不是下一步视觉理解，而是对当前视野外目标和路径的长程想象。
- 使用 Wan2.1 T2V-1.3B 作为 VGM backbone，并改造成 I2V/历史条件模型。
- 未来预测 timestep: `T+1, T+2, T+5, T+8, T+11, T+14, T+17, T+20`
  - 前两个 chunk 保持连续，保证短期控制精度。
  - 后续固定间隔稀疏采样，覆盖 20s horizon，避免连续视频生成的高开销。

### 历史注入与动作头
- 历史观测通过 **Q-Former + Video-Former** 压缩后注入 VGM cross-attention。
- Stage 3 使用 PCM 风格蒸馏，将 denoising 从 50 steps 降到 4 steps。
- Stage 4 冻结生成模型，用 inverse dynamics 训练 DiT action head：
  - 输入：生成的 sparse future latent + 语言指令
  - 输出：连续 8-step action trajectory
  - 为解决生成帧与真实轨迹不对齐，用 Depth Anything 3 对生成未来重新估计动作标签。

## 训练数据

| 数据 | 规模 | 说明 |
|------|------|------|
| 真实世界导航视频 | 140 小时 | 手持 DJI Osmo Action 4 采集，覆盖多样真实环境 |
| 轨迹片段 | ~13K trajectories | 4 FPS 均匀采样，平均 140 帧 |
| 动作标签 | DA3 位姿估计 | 从 6-DoF camera pose 提取局部平面连续动作 |
| 语言指令 | 人工标注 | 面向高层目标/意图，而非逐步导航脚本 |

## 训练策略
- **Stage 1: T2V → I2V**：让 text-to-video backbone 对当前观测保持一致性。
- **Stage 2: History Injection**：加入历史压缩模块，解决 VGM 无法直接吃长历史的问题。
- **Stage 3: Diffusion Distillation**：50-step teacher 蒸馏到 4-step student，支撑真实部署。
- **Stage 4: Action Learning**：基于生成 sparse future 学连续动作，action head 仅 23.4M trainable params。
- 全流程训练约 64 小时，32×H200。

## 实验结果

### 真实世界零样本导航（Unitree Go2）

| 方法 | IFN Avg SR↑ | BVN Avg SR↑ |
|------|-------------|-------------|
| Uni-NaVid | 10.0 | 2.5 |
| StreamVLN | 35.0 | 10.0 |
| InternVLA-N1 | 17.5 | 8.3 |
| **SparseVideoNav** | **50.0** | **25.0** |

- 6 个真实场景：Room、Lab Building、Yard、Park、Square、Mountain。
- 每个场景 2 个 IFN + 2 个 BVN task，每个模型 240 次 trial。
- 相比最强 baseline StreamVLN：IFN +15.0%，BVN +15.0%。
- 夜间 BVN 中 baseline 基本失败，SparseVideoNav 仍有 17.5% 平均成功率。

### 效率与消融

| 设计 | 结果 | 结论 |
|------|------|------|
| Sparse generation vs continuous | 0.79s vs 1.35s | sparse 设计带来 1.7× inference speedup |
| 4-step distillation vs 50-step | 0.79s vs 7.56s | 蒸馏带来 ~9.6× speedup |
| Full optimized vs unoptimized | ~27× speedup | 使 20s future guidance 可真实部署 |
| 去掉 Former | IFN 45.0 / BVN 22.5 | 历史压缩既提速也略提性能 |
| 数据规模 8h→50h→140h | FVD 持续下降 | VGM 路线可从真实视频规模化收益 |

## 局限性
1. **成功率仍不高**：BVN 平均 SR 25%，说明真实开放环境的视野外导航仍很难。
2. **存在 video generation mode collapse**：复杂场景下未来想象可能崩溃，直接导致导航失败。
3. **数据规模仍小于 web-scale**：140 小时已是大规模真实 VLN 数据，但相对通用视频生成预训练仍不足。
4. **延迟仍略慢于 LLM/VLM 导航路线**：虽已 sub-second，但作者认为还需蒸馏和量化继续加速。

## 与其他工作的关系
- **相对 NaVid / Uni-NaVid / StreamVLN**：不只把历史视频交给 VLM 做下一步决策，而是显式生成 sparse future，提供视野外长程引导。
- **相对 InternVLA-N1**：从当前视野内 point/pixel goal 扩展到可想象的未来路径，因此更适合 dead end、坡道、夜间等 BVN 场景。
- **方法图谱位置**：可视为 VLN 中从“视频流理解”走向“视频生成世界模型/未来扩展”的新分支，核心关键词是 **beyond-the-view real-world VLN + sparse video generation**。
