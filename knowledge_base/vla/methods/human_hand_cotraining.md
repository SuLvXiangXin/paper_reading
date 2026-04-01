# 人手数据 Co-training (Human Hand Data Co-training)

## 定义
将第一人称（egocentric）人类视频 + 3D 手部追踪数据作为与机器人遥操作数据等价的具身数据源，通过全栈对齐技术实现统一策略的跨具身 co-training。

## 核心思想
- **人手数据 = 另一种具身数据**：不把人类视频当辅助信息（提取高层意图），而是直接作为动作监督
- **全栈对齐**：硬件层面（共用传感器）、数据层面（坐标系/分布/外观对齐）、架构层面（共享编码器+域特定头）缺一不可
- **被动可扩展性**：利用消费级可穿戴设备（AR 眼镜、VR 头显）被动采集数据，无需机器人硬件

## 代表工作
- **EgoMimic** (Kareer et al. 2024, Georgia Tech) — 奠基工作
  - Project Aria 眼镜采集 ego RGB + SLAM + 3D 手部追踪
  - 基于 ACT 的统一架构，共享编码器 + Pose/Joint 双头输出
  - 三步数据对齐：坐标系统一 → 分布归一化 → 视觉遮罩
- **EgoBridge** (2025, Georgia Tech) — Domain adaptation 视角解决 ego human→robot gap
- **EgoVLA** (2025, NVIDIA) — 人手运动预训练 VLA → IK+retargeting 迁移
- **EgoZero** (2025, UC Berkeley) — Smart Glasses ego 数据 → 机器人学习
- **EMMA** (2025, Stanford) — Ego 人类数据 → 移动操作 scaling
- **Being-H0/H0.5** (2025-2026, BeingBeyond) — 35K+ 小时 UniHand 数据，大规模 VLA 预训练
- **EgoScale** (2026, NVIDIA) — 20K 小时 ego 视频，验证 scaling phenomenon

## 关键技术组件

### 数据采集硬件
| 设备 | 代表工作 | 信息 | 可穿戴性 |
|------|----------|------|----------|
| Project Aria 眼镜 | EgoMimic, EgoZero | ego RGB + SLAM + hand tracking (75g) | ★★★★★ |
| Apple Vision Pro | EgoDex | ego RGB + precise hand tracking | ★★★ |
| Meta Quest | 多项工作 | ego RGB + hand tracking | ★★★ |
| 便携 mocap (DexCap) | DexCap | 手指级精度 | ★★ |

### 跨域对齐技术
1. **坐标系统一**: 人类 ego 视频中相机不断移动 → 用 SLAM 将手部轨迹变换到当前相机帧
2. **动作分布对齐**: 人手和机器人的运动范围/速度/精度不同 → Gaussian Z-score 归一化
3. **视觉外观对齐**: 人手 vs 机器人臂外观差异大 → SAM 遮罩 + 结构化线条覆盖
4. **时间对齐**: 人类操作速度约为机器人 4 倍 → 调整 action horizon 或降采样

### 架构设计
- **共享编码器 + 域特定头**: 强制两个域学习共享表征
- **Pose 空间桥接**: 人手和机器人 EEF 都有 SE(3) 表示，用 pose 预测作为共享监督
- **Joint 空间控制**: 实际机器人用 joint-space action 控制（处理运动学冗余不足问题）

## 优势
- **数据采集效率极高**: 人手数据 10-23x 快于遥操作
- **无需机器人硬件**: 任何人戴上眼镜即可贡献数据
- **统一架构 > 层次化**: EgoMimic 实证显示统一 co-training 远优于 MimicPlay 的层次化方案（新场景泛化 63 vs 4 pts）
- **有利的 scaling 趋势**: 增加 1h 人手数据 >> 1h 机器人数据

## 局限
- **Gripper 信息缺失**: 可穿戴设备只追踪手部位姿，缺乏抓取动作信息
- **对齐工程量大**: 坐标系、分布、外观、时间等多重对齐需要逐一解决
- **需少量机器人数据**: 当前方案仍依赖机器人 demo 提供 joint-space 监督
- **尚未验证超大规模**: 最大规模验证为万小时级（EgoScale），距离互联网规模仍有差距

## 与其他方法线的关系
- **vs 层次化利用人类视频（MimicPlay 路线）**: 统一 co-training vs 高层 planner + 低层 policy，前者实证更优
- **vs 视觉表征预训练（R3M 路线）**: R3M 只学视觉特征，此路线直接学动作
- **vs 跨具身预训练（Octo/π₀ 路线）**: 互补——跨具身用不同机器人数据，此路线用人手数据；Physical Intelligence 的 "Emergence of H2R" 表明两者可以统一
- **vs Retargeting 路线（DexUMI）**: Retargeting 需显式运动学映射，co-training 让模型隐式学习映射

## 演进脉络
```
R3M (2022): 人类视频 → 视觉表征（不学动作）
  ↓
MimicPlay (2023): 人类视频 → 高层 planner → 引导低层策略（层次化）
  ↓
EgoMimic (2024): 人手数据 = 一等公民，统一 co-training（奠基）
  ↓
EgoBridge/EgoVLA/EgoZero (2025): 扩展到 domain adaptation / VLA 预训练 / smart glasses
  ↓
Being-H0.5 / EgoScale (2026): 万小时级 scaling，验证 transfer 是 scaling phenomenon
```
