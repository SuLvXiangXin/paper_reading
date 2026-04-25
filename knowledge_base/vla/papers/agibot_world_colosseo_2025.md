# AgiBot World Colosseo: A Large-scale Manipulation Platform for Scalable and Intelligent Embodied Systems (2025)

## 基本信息
- 作者: The AgiBot World Team
- 机构: AgiBot / OpenDriveLab / 上海人工智能实验室等
- arXiv: 2503.06669
- 项目页: https://agibot-world.com/

## 一句话总结
提出 AgiBot World Colosseo，一个面向大规模机器人操作数据、模型训练和评测的平台，围绕百万级真实机器人轨迹、统一任务/场景/硬件接口和基准评测，推动具身智能从小规模 demo 走向数据平台化。

## 问题
VLA 和通用机器人策略的核心瓶颈是高质量真实机器人数据与标准评测不足：
1. 单实验室数据集规模小、硬件异构、任务定义不统一；
2. 现有 benchmark 往往偏仿真或少量桌面任务，难以评估真实长期泛化；
3. 数据、训练、评测割裂，难以形成可迭代的数据飞轮；
4. 缺少面向 humanoid/mobile manipulation 的大规模真实世界基础设施。

## 方法
- **方法线归属**: 大规模机器人数据平台 / embodied foundation model infrastructure；与 DROID、OXE 同属真实机器人数据基础设施，但更强调统一平台、评测和可扩展采集。
- **核心 idea**: 用平台化方式组织机器人、场景、任务、数据和评测，使真实机器人操作数据可以持续扩展并直接服务通用具身模型训练。
- **关键技术点**:
  - **Large-scale real robot data**：覆盖多场景、多任务、多物体的真实机器人轨迹，而非仅依赖仿真或互联网视频。
  - **Unified task and data schema**：统一语言指令、视觉观测、机器人状态、动作和元数据，便于训练 VLA。
  - **Colosseo benchmark/platform**：提供任务定义、评测协议和模型比较入口，支持持续迭代。
  - **Scalable data engine**：把采集、清洗、标注、训练和评测组织成闭环，为后续大模型训练提供数据基础。

## 实验
- **Benchmark**: AgiBot World / Colosseo manipulation benchmark
- **主要结果**:
  - 发布大规模真实机器人操作数据和评测平台；
  - 展示基于该数据训练的策略在多类操作任务上的能力；
  - 支持对不同模型、数据规模和任务设置进行统一比较。
- **对比基线**: DROID、Open X-Embodiment、BridgeData、RoboNet 等真实机器人数据集/平台，以及常规单任务 imitation learning 设置。

## 评价
- **优势**:
  1. 平台化程度高，关注数据、训练和评测闭环，而不仅是一次性数据集；
  2. 真实机器人数据对 VLA 的动作落地价值高于纯视频数据；
  3. 统一 schema 和 benchmark 有助于减少跨数据集整合成本；
  4. 与 OpenDriveLab 其他工作形成互补：Colosseo 提供大规模平台，FreeTacMan/MM-Hand/TAMEn 提供触觉和灵巧操作专项数据能力。
- **局限**:
  1. 平台数据质量、标注一致性和硬件覆盖范围决定其长期价值，需要持续维护；
  2. 大规模真实数据仍可能受少数机器人形态和场景分布限制；
  3. 若评测任务与训练数据重合度高，容易高估泛化；
  4. 数据访问、复现实验成本和硬件依赖可能高于开源视觉数据集。
- **对 VLA 领域的贡献**:
  AgiBot World Colosseo 是 VLA 数据基础设施路线的重要样本，代表从"收集若干机器人演示"转向"持续运营真实机器人数据与评测平台"。
