# WBC 数据集与评测体系

## 主要数据集

| 数据集 | 年份 | 内容 | 规模 | 来源 |
|--------|------|------|------|------|
| AMASS | 2019 | 动作捕捉数据集合（CMU MoCap等合并） | 大规模 | 学术界 |
| SONIC 数据集 | 2025 | 高质量全身动捕数据 | 100M帧, 700小时 | NVIDIA |
| OmniH2O-6 | 2024 | 六种日常任务全身控制遥操作数据 | - | CMU/NVIDIA |
| HumanPlus 数据集 | 2024 | 遥操作全站任务数据 | - | Stanford |

## 常用仿真平台

| 平台 | 特点 | 常用论文 |
|------|------|---------|
| Isaac Gym / Isaac Lab | NVIDIA GPU加速并行RL训练 | HOVER, SONIC, BeyondMimic |
| MuJoCo | 精确物理，标准RL环境 | PHC, MaskedMimic |
| Genesis | 新兴高速仿真平台 | - |

## 常用机器人平台

| 机器人 | 制造商 | 常用论文 |
|--------|--------|---------|
| Unitree H1 / H1-2 / G1 | Unitree | HOVER, BeyondMimic, ASAP |
| Figure 01/02 | Figure AI | - |
| 1X NEO | 1X Technologies | - |
| Boston Dynamics Atlas | Boston Dynamics | - |

## 评测指标

- **运动跟踪精度**：关节角度误差、根节点位置误差（MPJPE, PA-MPJPE）
- **任务成功率**：遥操作任务、抓取任务的成功百分比
- **鲁棒性**：扰动下的恢复能力、零样本泛化
- **Sim-to-Real Gap**：仿真表现 vs 真实表现的差距
- **运动多样性**：能控制的不同运动技能数量
