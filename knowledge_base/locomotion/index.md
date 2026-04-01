# Locomotion — 机器人运动控制

## 领域概述
基于深度强化学习的机器人运动控制（Locomotion），涵盖四足、双足/人形、轮腿混合等形态。核心研究方向包括 sim-to-real 迁移、地形自适应、敏捷运动（parkour）、全身控制等。

## 研究形态分类

### 四足机器人（Quadruped）
- **盲行（Proprioceptive）**: 纯本体感知，teacher-student 框架，ETH RSL 主导
- **感知行走（Perceptive）**: 融合视觉/深度/高度图，多模态融合
- **敏捷运动（Parkour/Agile）**: 跳跃、攀爬、翻越障碍
- **代表平台**: ANYmal (ETH), Unitree Go1/A1 (MIT/Berkeley), Mini Cheetah (MIT)

### 双足/人形（Bipedal/Humanoid）
- **行走与奔跑**: 速度跟踪、步态切换、抗干扰
- **敏捷运动**: 足球、跑酷、跳跃
- **代表平台**: Cassie (Oregon State/Berkeley), Digit (Agility), Atlas (BD), H1/G1 (Unitree)

### 轮腿混合（Wheeled-Legged）
- **混合运动**: 轮式巡航 + 腿式越障无缝切换
- **代表平台**: ANYmal-W (ETH), Ascento, Swiss-Mile

## 核心技术脉络

| 技术方向 | 代表工作 | 关键创新 |
|---------|---------|---------|
| Sim-to-Real 迁移 | Tan 2018, Hwangbo 2019 | Domain randomization, actuator network |
| 大规模并行训练 | Rudin 2021 (IsaacGym) | GPU 并行 → 分钟级训练 |
| Teacher-Student | Lee 2020 | 特权信息蒸馏到部署策略 |
| 快速在线适应 | RMA (Kumar 2021) | 适应模块在线推断环境参数 |
| 多模态感知 | Miki 2022 | 本体感知+外部感知注意力融合 |
| 运动模仿 | AMP (Peng 2021), DeepMimic 2018 | 对抗式模仿自然运动 |
| 敏捷跑酷 | Cheng 2023, Hoeller 2024 | 端到端视觉→动作跑酷 |
| 人形行走 | Radosavovic 2024, Li 2024 | Transformer + 因果推理 |

## 关键研究机构
- **ETH Zurich RSL** (Marco Hutter): 四足领域绝对霸主，ANYmal 系列
- **UC Berkeley** (Malik, Sreenath, Abbeel, Levine): 双足/人形领先
- **CMU** (Deepak Pathak): 敏捷运动/跑酷
- **MIT** (Pulkit Agrawal): 快速运动、行为多样性
- **Google DeepMind**: 双足足球、RL 算法创新
- **KAIST**: 可变形地形、四足鲁棒性

## 知识库结构
- `reports/` — 调研报告
- `papers/` — 论文卡片
- `methods/` — 方法分类
- `components/` — 技术组件（sim-to-real, reward design 等）
- `benchmarks/` — 评测体系
- `tasks/` — 任务类型
