# NaVid: Video-based VLM Plans the Next Step (2024)

## 基本信息
- **标题**: NaVid: Video-based VLM Plans the Next Step for Vision-and-Language Navigation
- **作者**: Jiazhao Zhang, Kunyu Wang, Rongtao Xu, Gengze Zhou, Yicong Hong, Xiaomeng Fang, Qi Wu, Zhizheng Zhang, Wanggui He
- **机构**: 北京大学 (He Wang 组), 阿德莱德大学
- **arXiv**: 2402.15852
- **年份**: 2024 (RSS 2024)
- **引用数**: 198
- **方法线归属**: **视频流 VLM 导航**

## 核心贡献
1. **首个基于视频的 VLM 导航方法**：将导航历史建模为视频流，VLM 直接从视频理解环境
2. **无需地图/里程计/深度**：仅需单目 RGB 视频流即可导航，极简输入
3. **510K 导航样本 + 763K 网络数据**训练
4. **出色的跨数据集和 Sim2Real 迁移能力**

## 方法架构

### 基座模型：LLaMA-VID
四个核心模块协同工作：

**视觉编码器：EVA-CLIP**
- 每帧编码为 256 个 patch token（维度 C）
- 冻结加载预训练权重

**Q-Former + BERT 文本编码器**
- 每帧生成两类 token：
  - **Instruction-queried token**（1个/帧）：Q-Former 做指令-视觉交叉注意力 → mean pool
  - **Instruction-agnostic tokens**：Grid Pooling 压缩视觉特征，保留几何信息
- **非对称 token 编码**（关键设计）：
  - 历史帧：5 tokens（1 queried + 4 agnostic）— 主要提供上下文
  - 当前帧：65 tokens（1 queried + 64 agnostic）— 需要精细几何信息

**跨模态投影器**
- 两个独立线性层（PQ, PV），分别投射 queried 和 agnostic tokens 到 LLM 空间

**LLM：Vicuna-7B**
- 输入格式：`<HIS> {历史帧tokens} </HIS> <OBS> {当前帧tokens} </OBS> <NAV> {指令文本}`
- 输出：自然语言动作 {FORWARD, TURN-LEFT, TURN-RIGHT, STOP} + 量化参数（cm/degree）
- 正则表达式解析，100% 成功率
- **连续 waypoint 预测完全失败（0% SR）**，说明 VLM 难以回归连续坐标

## 训练数据

| 数据来源 | 数量 | 用途 |
|----------|------|------|
| Oracle 导航轨迹（R2R train, 61 个 MP3D 场景）| 320K | 主要动作规划 |
| DAgger 非 oracle 轨迹 | 180K | 提升鲁棒性 |
| Instruction Reasoning 辅助任务 | 10K 轨迹 | 视频→指令反推 |
| Web-scale 视频问答 | 763K | 保持通用能力 |
| **合计** | **~1.27M** | |

## 训练策略
- **混合训练**：动作规划 + 指令推理 + 视频 QA 三任务联合
- **DAgger**：两阶段离线收集（先 oracle 训练→部署收集失败轨迹→混合再训练）
- **仅训练 1 epoch**，24×A100，约 28 小时
- Loss：标准 next-token prediction

## 实验结果

### VLN-CE R2R Val-Unseen

| 方法 | 输入 | SR↑ | SPL↑ | NE↓ |
|------|------|------|------|------|
| ETPNav* | 全景+Depth+Odom | 57.0 | 49.0 | 4.71 |
| WS-MGMap | RGB+Depth+Odom | 38.9 | 34.3 | 6.28 |
| **NaVid** | **RGB only** | **37.4** | **35.9** | **5.47** |
| RGB-CMA | RGB only | 5.0 | 4.43 | 9.55 |

- RGB-only 设定下大幅领先（SR: 5.0→37.4）
- SPL 超过使用 Depth+Odom 的 WS-MGMap

### 跨数据集零样本（RxR Val-Unseen）
- NaVid SR **23.8%**, SPL **21.2%** vs A2Nav SR 16.8%, SPL 6.3%

### 真实世界（Turtlebot4, 200 cases）
- 简单指令 SR ~85%, 复杂指令 SR ~47%
- 远超所有 baseline（WS-MGMap 简单 ~52%）

## 消融实验关键结论

| 消融 | SR 变化 | 结论 |
|------|---------|------|
| 去掉 co-training | -12.7 | 辅助任务对泛化至关重要 |
| 去掉 instruction reasoning | -6.3 | 指令推理有效 |
| 去掉 DAgger | -3.2 | DAgger 提升鲁棒性 |
| 文本历史（NavGPT 风格）| 0.0 SR | 文本完全无法编码导航历史 |
| 视频历史 | 37.4 SR | 视频是最佳历史表征 |
| 1 token/历史帧 | -13.5 SR | token 数影响巨大 |
| 4 tokens/历史帧（默认）| 37.4 SR | 最优性价比 |
| 16 tokens/历史帧 | +0.6 SR | 收益递减，时间翻倍 |

## 局限性
1. **推理延迟高**：每步 1.2-1.5s，可通过 action chunking 或量化缓解
2. **长 horizon 指令性能下降**：长上下文 token 问题，缺乏长视频标注数据

## 与其他工作的关系
- **后续**: Uni-NaVid（统一多任务）, NaVid-4D（加入深度）
- **影响**: 开创视频-based VLN 路线，被 StreamVLN、DualVLN 等继承
- **关键洞察**: 视频是导航的自然表征；去掉中间表征反而提高泛化性
