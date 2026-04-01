# VLN Benchmarks 索引

| Benchmark | 环境 | 动作空间 | 年份 | 引用 | 特点 |
|-----------|------|---------|------|------|------|
| **R2R** | Matterport3D | 离散 | 2018 | 1653 | VLN 经典，21K 指令 |
| **R×R** | Matterport3D | 离散 | 2020 | 467 | 多语言 + 密集 grounding |
| **REVERIE** | Matterport3D | 离散 | 2020 | — | 目标物体定位 + 导航 |
| **SOON** | Matterport3D | 离散 | 2021 | — | 场景-目标导航 |
| **VLN-CE (R2R-CE)** | Habitat | 连续 | 2020 | 454 | 连续环境标准 |
| **RxR-CE** | Habitat | 连续 | 2022 | — | R×R 连续版 |
| **Habitat 3.0** | Habitat | 连续 | 2023 | 233 | 人-Avatar-机器人协作 |

## 评测指标
- **SR (Success Rate)**: 到达目标的比例
- **SPL (Success weighted by Path Length)**: 考虑路径效率的成功率
- **nDTW**: 归一化动态时间规整距离
- **SDTW**: 成功加权 DTW
