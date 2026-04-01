# NaVILA: Legged Robot VLA for Navigation (2024)

## 基本信息
- **标题**: NaVILA: Legged Robot Vision-Language-Action Model for Navigation
- **作者**: An-Chieh Cheng, Yandong Ji, Zhaojing Yang, Xueyan Zou, Jan Kautz, Erdem Biyik, Hongxu Yin, Sifei Liu, Xiaolong Wang
- **机构**: NVIDIA, UC San Diego
- **arXiv**: 2412.04453
- **年份**: 2024 (RSS 2025)
- **引用数**: 143
- **方法线归属**: **导航基础模型（四足 + 人形）**

## 核心贡献
1. **首个面向四足/人形机器人的 VLA 导航模型**
2. **两层级架构**：VLA 高层规划 + 视觉运动策略低层控制
3. **首次证明人类视频可用于连续环境导航训练**（YouTube → MASt3R 位姿 → 动作标签）
4. **跨机器人泛化**：同一 VLA 无需重训即可部署到 Go2/H1/T1

## 方法架构

### 上层：VLA（8B 参数）
- 基座：**VILA**（NVIDIA 自研 VLM 家族）
- 视觉编码器：每帧 196 tokens，**全参数可训练**
- 投影器：下采样 + MLP，全参数可训练
- LLM：8B 参数，全参数可训练
- 输入：历史帧（均匀采样，首帧必选）+ 当前帧 + 语言指令
- 输出：**中层语言动作**（如 "turn right 30 degrees", "moving forward 75cm"）
  - 正则表达式解析动作类型和参数值
  - 核心创新：不直接预测关节角度，充分利用 LLM 语言推理

### 下层：视觉运动策略
- 将中层语言指令转为固定速度命令执行
- **单阶段 RL（PPO）**，Isaac Lab 训练，60K FPS 吞吐
- 观测：本体感知 + **LiDAR 高度图**（Unitree L1，360×90° FOV）
  - 体素 0.06m，取最低值 + 5 帧最大值滤波
  - 关键优势：可检测透明物体，强光下鲁棒
- 输出：12 维关节目标位置
- 多地形训练：平坦、粗糙、斜坡、障碍物

### 双频运行
- VLA：~1 FPS（低频高层规划）
- 运动策略：实时高频（低层控制）

## 训练数据

| 数据类型 | 来源 | 规模 |
|----------|------|------|
| 真实视频导航 | YouTube 旅游视频 | 2K 视频 → 20K 轨迹 |
| 仿真导航 | R2R-CE + RxR-CE | 最短路径跟随器标注 |
| 辅助数据 | EnvDrop + ScanQA | 轨迹摘要 + 3D QA |
| 通用 VQA | ShareGPT4V, Video-ChatGPT 等 | 保持通用能力 |

**YouTube 视频处理流程**：
视频 → 熵采样 → **MASt3R 度量位姿估计** → 逐步动作标签 → VILA caption + GPT-4o 改写指令

## 训练策略
- 从 VILA Stage 2 开始（已完成视觉-语言预训练）
- **全解冻 SFT**（vision encoder + projector + LLM），1 epoch
- 学习率 1e-4，cosine decay，warm-up 0.03
- 连续动作合并（最多 3 步）+ **stop 标签重平衡**（去掉后 SR 暴跌 20%）
- 训练：4×8 A100 节点，18 小时
- 推理：单张 RTX 4090，~1 FPS；**AWQ W4A16 量化**后延迟降 38%，显存从 18.5GB→8.6GB

## 实验结果

### R2R-CE Val-Unseen

| 方法 | 输入 | SR↑ | SPL↑ | NE↓ |
|------|------|------|------|------|
| **NaVILA** | 单视图 RGB | **54.0** | **49.0** | **5.22** |
| NaVid | 单视图 RGB | 37.0 | 35.9 | 5.47 |
| BEVBert | 全景+Depth+Odom | 59.0 | — | — |

- 单视图 RGB 下超 NaVid **+17% SR**
- 接近全景+深度+里程计方法水平

### RxR-CE 跨数据集零样本
- NaVILA SR **34.3%** vs NaVid 23.8%（**+10.5%**）

### ScanQA 空间理解
- CIDEr **102.7**，超越需要 3D 扫描的 LEO (101.4)

### 真实世界（Go2, 25 指令 ×3）
- 总 SR **88%**，复杂指令 SR **75%**
- 无人类视频时 outdoor SR 0%，有后 SR 83-100%

## 消融实验关键结论

| 消融 | SR 变化 | 结论 |
|------|---------|------|
| 去掉标签重平衡 | **-19.7** | 最关键因素！|
| 去掉人类视频 | -4.3 | 对 outdoor 影响巨大（0%→83%）|
| 8→64 帧 | +0.4 | 导航任务 8 帧够用 |
| FP16→W4A16 量化 | -1.5 | 可接受，速度+40% |

## 局限性
1. **纠错能力不足**：偏离轨迹后无法自我纠正
2. **计算开销大**：~1 FPS
3. **空间理解仍需加强**
4. **缺少显式推理数据**

## 与其他工作的关系
- **NVIDIA 导航线**（Jan Kautz 组）的代表作
- **跨形态**：Go2（四足）→ H1（人形）→ T1（人形），同一 VLA
- **关键技术**：MASt3R 使 YouTube→导航训练数据成为可能
- **中层语言动作**思想被 DualVLN System 2 继承
