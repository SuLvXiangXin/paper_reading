# 任务类型概览

## 桌面操作 (Manipulation)
最常见的评测场景，包括抓取、放置、推移、叠放等。
- 主要 benchmark: LIBERO, RLBench, Language Table
→ 详见 [manipulation.md](manipulation.md)

## 灵巧手 (Dexterous)
多指机械手的精细操作，难度远高于平行夹爪。
- 代表工作：π₀ 的灵巧手实验, DexCap, VITRA, EgoScale, UniDex, MM-Hand
- 新趋势：egocentric human hand data 正在从表征/retargeting 转向直接预训练灵巧手 VLA；VITRA 证明无标注真实人类活动视频可自动转成显式 3D hand-action V-L-A 预训练数据，UniDex 的 FAAS 和 Being-H0.5 的统一动作空间则是两条动作空间对齐路线；MM-Hand/TAMEn/FreeTacMan 则把触觉和可复制硬件纳入数据闭环
→ 详见 [dexterous.md](dexterous.md)

## 接触丰富操作 (Contact-Rich Manipulation) 🆕
需要稳定接触、滑移感知、插入/对齐或柔性物体交互的任务。
- 代表工作：FreeTacMan（robot-free 视觉触觉数据）、TAMEn（触觉感知闭环数据采集）、χ0/kai0（长时序衣物操作可靠性）
- 挑战：纯视觉难以判断接触状态；失败往往来自微小偏差累积；需要触觉、恢复数据和 train-deploy alignment

## 导航 (Navigation)
移动机器人到目标位置，通常结合视觉和语言指令。
→ 详见 [navigation.md](navigation.md)

## 移动操作 (Mobile Manipulation)
移动底盘 + 机械臂协同完成任务，是最接近真实家庭应用的场景。
- 典型任务：清洁厨房/卧室、收拾桌面、整理衣物、铺床
- 挑战：长时序（10-15分钟）、需要导航+操作协同、open-world环境多样性
- 代表工作：π₀.5（首次在全新家庭中端到端完成长时序操作）
- 新代表：EMMA 用 egocentric human data co-training 替代 mobile teleoperation 数据；DreamZero/GigaWorld 系列则用 world model 或 data engine 扩展移动双臂任务覆盖
- 典型平台：双臂移动操作平台（全向底盘 + 双6DoF臂 + 平行夹爪）
- 评测方式：在训练未见的mock homes和real homes中评估任务完成进度

## 人形机器人 Loco-Manipulation 🆕
全身移动、双臂操作、躯干/腿部平衡和手部操作耦合的任务，是 VLA 与 whole-body control 的交叉方向。
- 代表工作：EgoHumanoid（Unitree G1）、Figure Helix 02（官方技术页）、Being-H0.5/H0.7（多具身/latent WAM）
- 典型任务：Pillow Placement、Trash Disposal、Toy Transfer、Cart Stowing、洗碗机整理、物流包裹处理
- 挑战：人类 ego 示范和机器人全身动作接口差异大，需要 view alignment、action alignment、底层 whole-body controller 或系统分层

## Egocentric Hand Motion / Perception 🆕
这类任务不是机器人策略评测本身，但为 human data pretraining 提供关键中间监督。
- 手部运动重建：HaWoR 从 ego video 恢复 world-space hand motion
- 手部运动预测：Uni-Hand 预测 wrist/finger/interaction state，并能转换为 ALOHA 轨迹
- 手-物运动生成：MEgoHand 生成 MANO hand-object interaction motion
- Ego 视频理解：OpenMMEgo 提供 egocentric LMM 数据、模型和 benchmark

## 长时序任务 (Long-Horizon)
需要多步规划和子任务分解的复杂任务。
- 与层次化VLA方法自然结合
- 评测指标通常为任务进度百分比而非binary success rate
- π₀.5展示了10-15分钟的端到端长时序操作（清洁整个房间）
