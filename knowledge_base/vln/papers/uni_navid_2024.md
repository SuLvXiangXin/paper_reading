# Uni-NaVid: Unified Video-based VLA for Navigation (2024)

## 基本信息
- **标题**: Uni-NaVid: A Video-based Vision-Language-Action Model for Unifying Embodied Navigation Tasks
- **作者**: Jiazhao Zhang, Kunyu Wang, Shaoan Wang, Minghan Li, Haoran Liu, Songlin Wei, Zhongyuan Wang, Zhizheng Zhang, He Wang
- **机构**: 北京大学 (He Wang 组)
- **arXiv**: 2412.06224
- **年份**: 2024 (RSS 2025)
- **引用数**: 93
- **方法线归属**: **视频流 VLM 导航**

## 核心贡献
1. **首个统一 4 种导航任务的视频 VLA 模型**（VLN/ObjNav/EQA/Following）
2. **在线三级记忆 Token 合并**：当前帧(64 tokens) / 短期(4/帧) / 长期(1/帧)，推理 5Hz
3. **5.9M 训练样本**（3.6M 导航 + 2.3M 视频理解）
4. **4 步前瞻预测**：支持异步非阻塞部署

## 方法架构

### 基座：EVA-CLIP + Vicuna-7B
- 视觉编码器 EVA-CLIP（冻结），每帧 256 patch tokens
- 两层 MLP 投影器对齐视觉-语言空间
- LLM：Vicuna-7B（Stage 2 微调）

### 在线三级 Token 合并（核心创新）
受 Atkinson-Shiffrin 记忆模型启发：
- **当前帧**：Grid Pooling α=2 → **64 tokens**（精细几何）
- **短期记忆**（最近 B=64 帧）：Grid Pooling α=8 → **4 tokens/帧**
- **长期记忆**（>64 帧）：Grid Pooling α=16 → **1 token/帧**
- **长期 Token 合并**：余弦相似度 > τ=0.95 的 token 加权平均合并，防线性增长
- **在线更新**：新帧到来时仅对边界帧做 grid pooling，无需全量重算

### 统一多任务设计
- `<NAV>` 指示符区分导航/问答模式
- VLN/ObjNav/Following → 输出动作序列
- EQA → 先导航（带`<NAV>`），stop 后移除`<NAV>`回答问题
- 目标信息通过前缀统一（"Search for"/"Follow"）

### 动作空间
- FORWARD(25cm), TURN-LEFT(30°), TURN-RIGHT(30°), STOP
- 每步预测 4 个动作（异步执行）

## 训练数据

| 类型 | 数据量 | 占比 |
|------|--------|------|
| VLN（R2R+RxR, HM3D/MP3D）| 2.4M | 40% |
| ObjNav（HM3D）| 483K | 8% |
| Human Following（自建, Habitat 3.0）| 544K | 9% |
| EQA（MP3D）| 250K | 4% |
| Video Caption（Panda-70M 等）| 30% | 30% |
| Video QA | 9% | 9% |
| **总计** | **5.9M** | |

## 训练策略
- 两阶段：(1) 对齐投影器 (2) 微调投影器+LLM
- 40×H800 GPU，35 小时（1400 GPU-hours），仅 1 epoch
- 视频 1 FPS 采样

## 实验结果

### R2R-CE Val-Unseen
- SR **47.0%**, SPL **42.7%** — 比 NaVid +25.7% SR

### RxR-CE Val-Unseen
- SR **48.7%**, SPL **40.9%** — 比 NaVid +104.6% SR

### HM3D ObjectNav
- SR **73.7%**, SPL **37.1%** — **SOTA**（仅 RGB，超过用深度的方法）

### ScanQA
- CIDEr **94.72** — 多项 SOTA

### Human Following
- SR **61.2%**, FR **71.9%** — 超 IBVS +21% SR

## 消融实验关键结论

| 消融 | 影响 | 结论 |
|------|------|------|
| 去掉多任务联合训练 | 所有任务下降 | 多任务协同增益 |
| 去掉 `<NAV>` 指示符 | VLN -11.8, EQA -26.9 | EQA 最依赖模式切换 |
| 去掉 VQA 数据 | EQA 崩至 1.19 | 防灾难性遗忘必需 |
| 仅当前帧（无记忆）| VLN -80.3% | VLN 最依赖历史 |
| 数据 3M→6M | 增益递减 | 受限于模拟器多样性 |

## 与 NaVid 的核心差异
- 从单任务 → 4 任务统一
- Token 从平铺 → 三级分层记忆 + 在线合并
- 推理从 1-2s/步 → 0.2s/步（5Hz）
- 动作从单步 → 4 步前瞻（异步部署）

## 局限性
1. 仅 4 种导航任务，覆盖有限
2. 离散动作空间（25cm/30°），无法精细控制
3. 数据规模瓶颈（模拟器多样性）
4. 仅仿真验证，4 步短视界规划
