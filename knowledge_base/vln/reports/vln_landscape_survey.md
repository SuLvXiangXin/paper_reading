# VLN 领域全景调研报告

> 锚点论文: DualVLN (arXiv: 2512.08186)
> 调研日期: 2026-03-20
> 调研方法: 锚点引用/被引 + 关键作者追踪 + Semantic Scholar 检索

## 1. 领域概览

Vision-Language Navigation (VLN) 是 Embodied AI 的核心任务之一：智能体根据自然语言指令在视觉环境中导航。从 2018 年 R2R 定义任务以来，领域经历了四个阶段的快速发展。

**核心数据**：本次调研覆盖 **22 篇重要论文**，总引用 > 5000 次，涉及 8 个核心研究团队。

## 2. 时间线与里程碑

```
2018  R2R (1653引用) ──────── VLN 任务定义
  │
2020  VLN-CE (454引用) ────── 连续环境
  │   R×R (467引用) ────────── 多语言
  │
2022  DUET (231引用) ──────── 图 Transformer
  │   GNM (214引用) ────────── 通用导航模型
  │   BEVBert (125引用) ────── BEV 预训练
  │
2023  NavGPT (328引用) ────── LLM 推理 VLN ◄ 最高引用的方法论文
  │   ViNT (277引用) ──────── 导航基础模型
  │   NoMaD (290引用) ─────── 扩散策略导航
  │   ETPNav (171引用) ────── 连续环境拓扑规划
  │   GridMM (125引用) ────── 网格记忆地图
  │   Dreamwalker (91引用) ── 心理规划
  │
2024  NaVid (198引用) ─────── 视频 VLM 导航 ◄ 视频流 VLN 开创
  │   NaVILA (143引用) ────── 四足导航 VLA
  │   InstructNav (123引用) ── 零样本 VLN
  │   Uni-NaVid (93引用) ──── 统一视频 VLA
  │   NavGPT-2 (88引用) ───── VLM 导航推理
  │
2025  StreamVLN (52引用) ──── 流式 SlowFast VLN
  │   MapNav (44引用) ─────── 语义地图记忆
  │   VLN-R1 (43引用) ─────── 强化微调
  │   JanusVLN (41引用) ───── 双隐式记忆
  │   NavDP (35引用) ──────── 扩散策略 Sim2Real
  │   DualVLN (10引用) ────── 双系统基础模型 ◄ 锚点论文
```

## 3. 六大技术流派对比

| 流派 | 代表作 | 引用总和 | 优势 | 局限 | 趋势 |
|------|--------|----------|------|------|------|
| **A. 拓扑图+Transformer** | DUET, ETPNav, GridMM, BEVBert | 652 | 显式空间推理，可解释 | 依赖准确建图 | 被视频流方法超越 |
| **B. 视频流 VLM** | NaVid, Uni-NaVid, StreamVLN | 343 | 极简输入，强泛化 | 长序列压力 | 主流方向，快速发展 |
| **C. LLM 推理驱动** | NavGPT, NavGPT-2, InstructNav | 539 | 可解释推理，零样本 | 推理延迟高 | 与 RL 结合 |
| **D. 导航基础模型** | GNM, ViNT, NoMaD, NaVILA | 924 | 跨机器人通用 | 需大量多机器人数据 | 引用最高 |
| **E. 双系统/层级式** | DualVLN, NavDP, Hi Robot | 192 | 解耦高低层，适合部署 | 较新，验证不足 | 最新前沿 |
| **F. 强化微调** | VLN-R1, EvolveNav | 58 | 后训练提升 | DeepSeek-R1 启发 | 2025 新兴 |

## 4. 核心团队图谱

### 上海 AI Lab（Jiangmiao Pang / Tai Wang / Meng Wei）
- **定位**: VLN 领域 2025 年最活跃的团队
- **核心输出**: StreamVLN → DualVLN → NavDP → LoGoPlanner
- **技术路线**: 流式处理 + 双系统 + 扩散策略
- **特点**: 从高层规划到低层执行的完整栈

### 北京大学（He Wang / Jiazhao Zhang）
- **定位**: 视频 VLM 导航的开创者
- **核心输出**: NaVid → Uni-NaVid → NaVid-4D → OctoNav
- **技术路线**: 视频理解驱动的端到端导航
- **特点**: 快速扩展到多任务和多模态

### UC Berkeley（Sergey Levine / Dhruv Shah）
- **定位**: 导航基础模型的定义者
- **核心输出**: GNM → ViNT → NoMaD（三部曲，总 781 引用）
- **技术路线**: 跨机器人预训练 + 扩散策略
- **特点**: 学术影响力最大

### 阿德莱德大学（Qi Wu / Yicong Hong / Gengze Zhou）
- **定位**: VLN 领域的老牌团队，R2R 合著者
- **核心输出**: R2R, NavGPT(328), NavGPT-2(88), ScaleVLN
- **技术路线**: LLM 推理 + 数据扩展
- **特点**: NavGPT 是 LLM-based VLN 最高引用工作

### CASIA/NLPR（Dongyan An / Yuankai Qi）
- **核心输出**: ETPNav(171), BEVBert(125)
- **技术路线**: 拓扑规划 + BEV 表征

### Hanqing Wang（多机构）
- **核心输出**: SSM(150), Dreamwalker(91), Active Perception(84)
- **技术路线**: 场景记忆 + 心理规划

### INRIA（Shizhe Chen / Cordelia Schmid / Ivan Laptev）
- **核心输出**: DUET(231)
- **技术路线**: 双尺度图 Transformer

### Meta AI / Georgia Tech（Dhruv Batra / Jacob Krantz）
- **核心输出**: VLN-CE(454), Habitat, Waypoint Models(143)
- **技术路线**: 连续环境基础设施 + 模拟器

## 5. 2026 最新动态（锚点论文被引分析）

DualVLN 已被 10 篇 2026 年论文引用，其中值得关注的：

| 论文 | 方向 | 亮点 |
|------|------|------|
| **AgentVLN** (2603.17670) | Agentic VLN | Agent 范式做 VLN |
| **DecoVLN** (2603.13133) | 解耦观察-推理-纠错 | 三阶段解耦 |
| **HaltNav** (2603.12696) | 反应式视觉停止 | 轻量拓扑先验 |
| **ABot-N0** (2602.11598) | VLA 导航基础模型 | 多功能导航 |
| **TIC-VLA** (2602.02459) | Think-in-Control | 动态环境 VLN |

## 6. 关键发现与洞察

### 趋势 1: 从离散到连续再到流式
R2R(离散) → VLN-CE(连续) → StreamVLN(流式) → DualVLN(双系统)。导航的动作空间和处理方式持续进化。

### 趋势 2: 从显式建图到隐式记忆
DUET/ETPNav(显式拓扑图) → NaVid(视频隐式记忆) → JanusVLN(隐式神经记忆)。趋势是减少手工设计的空间表征。

### 趋势 3: 双系统成为新范式
DualVLN 的 System 1 + System 2 设计与 Robotics 中的层级控制思想一致。预计 2026 年会有更多双系统 VLN 工作。

### 趋势 4: RL 后训练浪潮
VLN-R1 把 GRPO 引入 VLN，类似 DeepSeek-R1 的思路。强化微调可能成为 VLN 模型的标准后训练步骤。

### 趋势 5: 跨形态泛化
从轮式 (GNM/ViNT) → 四足 (NaVILA) → 人形 (Hi Robot)，导航基础模型向多机器人形态扩展。

## 7. 推荐阅读顺序

**入门**（理解任务定义）:
1. R2R (2018) → VLN-CE (2020)

**核心方法**（三条主线各读一篇）:
2. DUET (2022) — 图方法代表
3. NaVid (2024) — 视频流代表
4. NavGPT (2023) — LLM 推理代表

**导航基础模型**:
5. GNM (2022) → ViNT (2023) → NoMaD (2023)

**最新前沿**:
6. StreamVLN (2025) → DualVLN (2025) — 流式 + 双系统
7. VLN-R1 (2025) — RL 后训练

**深入阅读**:
8. ETPNav, BEVBert, Uni-NaVid, NaVILA, InstructNav
