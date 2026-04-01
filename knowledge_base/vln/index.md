# VLN（Vision-Language Navigation）领域总览

## 领域定义
视觉-语言导航（VLN）：智能体根据自然语言指令，在视觉环境中自主导航到目标位置。核心挑战在于语言理解、视觉感知、空间推理和动作规划的统一。

## 发展脉络

### 第一阶段：离散导航图（2018-2021）
- **R2R**（Anderson et al., 2018）定义了 VLN 任务，在 Matterport3D 预定义导航图上移动
- 核心方法：Seq2Seq + Attention → Transformer → 拓扑图规划
- 代表工作：R2R, R×R, DUET, Structured Scene Memory

### 第二阶段：连续环境导航（2020-2023）
- **VLN-CE**（Krantz et al., 2020）将 VLN 推向连续动作空间
- 核心挑战：从离散跳转到连续运动控制，需要路径点预测和局部规划
- 代表工作：VLN-CE, Waypoint Models, LAW, ETPNav, GridMM, BEVBert

### 第三阶段：基础模型时代（2023-2025）
- 两条主线并行发展：
  - **导航基础模型**（GNM → ViNT → NoMaD）：跨机器人通用导航
  - **VLM/LLM 驱动 VLN**（NavGPT, NaVid, InstructNav）：利用大模型的语言理解和推理能力
- 代表工作：NaVid, Uni-NaVid, NavGPT, InstructNav, NaVILA

### 第四阶段：流式与双系统（2025-）
- **StreamVLN**：流式处理视觉输入，SlowFast 上下文建模，实时推理
- **DualVLN**：System 2（VLM 全局规划）+ System 1（DiT 局部执行），首个双系统 VLN 基础模型
- **VLN-R1**：强化微调（GRPO），DeepSeek-R1 思路引入 VLN
- 代表工作：StreamVLN, DualVLN, NavDP, VLN-R1, JanusVLN

## 方法流派

| 流派 | 核心思路 | 代表工作 | 引用数 |
|------|---------|---------|--------|
| **A. 拓扑图 + Transformer** | 构建拓扑图/地图表征，Transformer 做全局-局部推理 | DUET(231), ETPNav(171), GridMM(125), BEVBert(125) | 高 |
| **B. 视频流 VLM** | 将导航视为视频理解问题，VLM 直接从视频流推理下一步 | NaVid(198), Uni-NaVid(93), StreamVLN(52) | 中高 |
| **C. LLM 推理驱动** | 利用 LLM/VLM 的推理能力做显式规划 | NavGPT(328), NavGPT-2(88), InstructNav(123) | 高 |
| **D. 导航基础模型** | 跨机器人、跨场景的通用导航策略 | GNM(214), ViNT(277), NoMaD(290), NaVILA(143) | 高 |
| **E. 双系统/层级式** | 高层规划 + 低层执行的分离架构 | DualVLN(10), NavDP(35), Hi Robot(147) | 新兴 |
| **F. 强化微调** | RL/GRPO 后训练提升 VLN 性能 | VLN-R1(43), EvolveNav(15) | 新兴 |

## 关键作者与团队

| 团队 | 机构 | 代表工作 | 方向 |
|------|------|---------|------|
| **He Wang / Jiazhao Zhang** | 北京大学 | NaVid, Uni-NaVid, OctoNav, TrackVLA | 视频 VLM 导航 |
| **Jiangmiao Pang / Tai Wang** | 上海 AI Lab | DualVLN, StreamVLN, NavDP, LoGoPlanner | 双系统 + 流式 VLN |
| **Sergey Levine / Dhruv Shah** | UC Berkeley | GNM → ViNT → NoMaD | 导航基础模型三部曲 |
| **Qi Wu / Yicong Hong** | 阿德莱德大学 | R2R, NavGPT, NavGPT-2, ScaleVLN | LLM VLN + 数据扩展 |
| **Hanqing Wang** | 多单位 | SSM, Dreamwalker, Active Perception | 场景记忆 + 心理规划 |
| **Dongyan An / Yuankai Qi** | CASIA/NLPR | ETPNav, BEVBert | 拓扑规划 + BEV 表征 |
| **Shizhe Chen / C. Schmid** | INRIA | DUET | 双尺度图 Transformer |
| **Dhruv Batra / Jacob Krantz** | Meta / Georgia Tech | VLN-CE, Habitat, Waypoint Models | 连续环境基础设施 |

## 核心 Benchmark

| 数据集 | 环境 | 动作空间 | 特点 |
|--------|------|---------|------|
| **R2R** | Matterport3D | 离散（导航图） | VLN 经典 benchmark |
| **R×R** | Matterport3D | 离散 | 多语言 + 密集时空 grounding |
| **VLN-CE (R2R-CE)** | Habitat | 连续 | 连续环境 VLN 标准 |
| **RxR-CE** | Habitat | 连续 | R×R 的连续环境版本 |
| **REVERIE** | Matterport3D | 离散 | 目标物体定位 + 导航 |
| **SOON** | Matterport3D | 离散 | 场景-目标导航 |

## 论文索引
→ 详见 [papers/index.md](papers/index.md)

## 方法分类
→ 详见 [methods/index.md](methods/index.md)

## 调研报告
→ 详见 [reports/index.md](reports/index.md)
