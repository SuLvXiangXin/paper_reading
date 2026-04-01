# DualVLN: Ground Slow, Move Fast (2025) — 锚点论文

## 基本信息
- **标题**: Ground Slow, Move Fast: A Dual-System Foundation Model for Generalizable Vision-and-Language Navigation
- **作者**: Meng Wei, Chenyang Wan, Jiaqi Peng, Xiqian Yu, Yuqiang Yang, Delin Feng, Wenzhe Cai, Chenming Zhu, Tai Wang, Jiangmiao Pang, Xihui Liu
- **机构**: 上海 AI Lab, 香港大学, 浙江大学, 清华大学
- **arXiv**: 2512.08186
- **年份**: 2025
- **引用数**: 10（截至 2026-03）
- **方法线归属**: **双系统基础模型**

## 核心贡献
1. **首个双系统 VLN 基础模型**：System 2（VLM 全局规划 2Hz）+ System 1（DiT 局部执行 30Hz）
2. **解耦训练**：VLM 保持泛化，DiT 专注运动质量，联合训练 SR 掉 9.1 个点
3. **Pixel Goal + Latent Goal 双通道条件**
4. **Social-VLN Benchmark**：首个动态障碍物 VLN 评测

## 方法架构

### System 2（慢系统，2 Hz）
- 基座：**Qwen-VL-2.5 (7B)**，像素级空间 grounding
- 输入：自我中心 RGB 序列 + 历史观测 + 语言指令
- 输出三种类型：
  - **Pixel Goal**：2D 像素坐标，最远可见 waypoint
  - **View Adjustment**：离散视角调整（左/右/上/下 15°），最多 4 个连续调整
  - **STOP**：任务完成
- **Farthest Pixel Goal Grounding**：3D 轨迹投影到 2D，深度图+相机距离做遮挡检测
- **Self-Directed View Adjustment**：当 waypoint 不在视野内，模型自主调整视角

### System 1（快系统，30 Hz）
- **Diffusion Transformer (DiT)**：
  - Hidden dim: 384, Layers: 12, Heads: 6
  - 输出：32 个密集 waypoint 的连续轨迹
- RGB 编码器：**DepthAnythingV2-Small ViT backbone**
- 条件信号双通道：
  1. **Latent Goal**：4 个可学习 `<TRAJ>` queries 插入冻结的 QwenVL → 取最后层 hidden states → 线性投影 3584→768 维 → cross-attention
  2. **高频 RGB**：编码 System 2 最后一帧(t) + 当前帧(t+k) → ViT → self-attention → **Q-Former 压缩为 32 tokens**
- 生成方式：**Flow Matching**，MSE velocity loss

### 异步推理
- System 2: 2 Hz（0.7s with KV-cache）
- System 1: 30 Hz（0.03s, TensorRT）
- 底层控制器: 200 Hz
- System 2 latent goal 在两次更新间保持不变

## 训练数据

| 来源 | 用途 |
|------|------|
| VLN-CE 轨迹 → pixel goal grounding | System 2 训练 |
| 同上（1% 即可） | System 1 训练 |
| Social-VLN（60 MP3D 场景, 763K episodes）| 动态避障训练 |

- **System 1 数据极少**：1% 数据即竞争性能，10% 接近饱和

## 训练策略

### Stage 1: 训练 System 2
- QwenVL-2.5 全参数微调（vision encoder + LLM 全解冻）
- AdamW, lr=2e-5, batch=128, 14000 steps, 1 epoch

### Stage 2: 训练 System 1
- **冻结 QwenVL**，仅训练：
  - 4 个 Latent Queries
  - DiT 全部（ViT encoder + Q-Former + DiT blocks）
- AdamW, lr=1e-4, batch=128, 15000 steps
- Flow Matching velocity MSE loss

### 为何解耦
联合训练导致：(1) DiT 收敛显著变慢；(2) System 2 泛化下降（SR -9.1）

## 实验结果

### R2R-CE Val-Unseen（单视角 RGB）

| 方法 | SR↑ | SPL↑ | NE↓ |
|------|------|------|------|
| **DualVLN** | **64.3** | **58.5** | **4.05** |
| StreamVLN† | 56.9 | 51.9 | 4.98 |
| NaVILA† | 54.0 | 49.0 | 5.22 |
| ETPNav（全景+Depth+Odom）| 57.0 | 49.0 | 4.71 |
| NaVid | 37.4 | 35.9 | 5.47 |

- **超越 StreamVLN +7.4 SR, +6.6 SPL**
- **首次 RGB-only 大幅超过全景+多传感器方法**

### RxR-CE Val-Unseen
- DualVLN SR **61.4**, SPL **51.8**, nDTW **70.0** — 全面 SOTA

### VLN-PE 零样本迁移
- DualVLN SR **51.6%** vs NaVid 22.4%（**2.3 倍**）

### Social-VLN（动态障碍物）
- DualVLN SR 37.2 vs StreamVLN 31.4（+5.8）
- 但相比静态场景 64.3 降至 37.2（-27.1），仍有很大提升空间

### 真实世界（Turtlebot4 / Go2 / G1）
- Easy(走廊): SR **100%**, NE 0.2m
- Medium(卧室): SR **95%**, NE 0.3m
- Hard(办公室): SR **70%**, NE 0.4m
- 所有场景超过 NaVid, NaVILA, StreamVLN

### 推理速度
- System 2: 0.7s（KV-cache 复用）
- System 1: 0.03s（TensorRT，32 条轨迹）
- 部署：RTX 4090，20GB 显存

## 消融实验关键结论

| 消融 | SR | SR 变化 | 结论 |
|------|-----|---------|------|
| 完整 DualVLN | 64.3 | — | — |
| 联合训练（w/o Sys.2 Train）| 55.2 | **-9.1** | 解耦训练至关重要 |
| 去掉 Pixel Goal | 62.2 | -2.1 | Pixel Goal 有效 |
| 去掉 Latent Goal | 60.9 | -3.4 | Latent Goal 贡献更大 |
| System 1 vs NavDP | 63.6 vs 58.7 | +4.9 | DiT 优于专用 planner |
| System 1 vs iPlanner | 63.6 vs 47.1 | +16.6 | 远超传统 planner |
| System 1 数据 1% | 竞争性能 | — | 数据需求极小 |
| System 1 数据 10% | 接近饱和 | — | 瓶颈在 System 2 |

## 局限性
1. **Social-VLN 性能降幅大**：静态 64.3→动态 37.2（-27.1）
2. **System 1 对大幅 pixel goal 偏差不鲁棒**：靠近障碍物时 pixel goal 严重偏离，System 1 无法修正
3. **瓶颈在 System 2**：System 1 数据饱和快，说明性能上限取决于 pixel goal 质量
4. **Fall Rate 偏高**：VLN-PE 上 12.32%

## 与其他工作的关系
- **前序**: StreamVLN（同组，数据配方共享）
- **System 1 技术来源**: NavDP（同组，扩散策略导航）
- **被引**: AgentVLN, DecoVLN, HaltNav, ABot-N0, TIC-VLA 等
- **跨平台**：轮式（Turtlebot4）+ 四足（Go2）+ 人形（G1），共用同一模型
- **关键洞察**: 双系统解耦是正确方向；System 1 数据需求极少说明运动策略是低维问题；瓶颈在高层语义理解
