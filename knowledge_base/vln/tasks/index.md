# VLN 任务类型索引

## 核心任务

| 任务 | 描述 | 代表 Benchmark |
|------|------|---------------|
| **指令跟随导航 (Instruction Following)** | 根据详细指令逐步导航 | R2R, R2R-CE |
| **目标导向导航 (ObjectNav)** | 导航到指定类别的物体 | REVERIE, SOON |
| **视觉问答导航 (EQA)** | 导航到能回答问题的位置 | EQA |
| **人物跟踪导航 (People Tracking)** | 跟踪移动的人 | Uni-NaVid |
| **探索 (Exploration)** | 无特定目标的环境探索 | NoMaD |

## 按动作空间分类
- **离散导航图**: R2R, REVERIE — 在预定义节点间跳转
- **连续环境**: R2R-CE, RxR-CE — 低层连续动作（前进、转向）
- **连续 + 扩散策略**: DualVLN, NavDP — 扩散模型生成平滑轨迹
