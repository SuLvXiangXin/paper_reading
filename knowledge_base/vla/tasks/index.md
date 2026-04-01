# 任务类型概览

## 桌面操作 (Manipulation)
最常见的评测场景，包括抓取、放置、推移、叠放等。
- 主要 benchmark: LIBERO, RLBench, Language Table
→ 详见 [manipulation.md](manipulation.md)

## 灵巧手 (Dexterous)
多指机械手的精细操作，难度远高于平行夹爪。
- 代表工作：π₀ 的灵巧手实验, DexCap
→ 详见 [dexterous.md](dexterous.md)

## 导航 (Navigation)
移动机器人到目标位置，通常结合视觉和语言指令。
→ 详见 [navigation.md](navigation.md)

## 移动操作 (Mobile Manipulation)
移动底盘 + 机械臂协同完成任务，是最接近真实家庭应用的场景。
- 典型任务：清洁厨房/卧室、收拾桌面、整理衣物、铺床
- 挑战：长时序（10-15分钟）、需要导航+操作协同、open-world环境多样性
- 代表工作：π₀.5（首次在全新家庭中端到端完成长时序操作）
- 典型平台：双臂移动操作平台（全向底盘 + 双6DoF臂 + 平行夹爪）
- 评测方式：在训练未见的mock homes和real homes中评估任务完成进度

## 长时序任务 (Long-Horizon)
需要多步规划和子任务分解的复杂任务。
- 与层次化VLA方法自然结合
- 评测指标通常为任务进度百分比而非binary success rate
- π₀.5展示了10-15分钟的端到端长时序操作（清洁整个房间）
