# Introducing Helix 02: Full-Body Autonomy (2026)

## 基本信息
- 作者: Figure AI 团队（官方页未列出个人作者）
- 机构: Figure AI
- arXiv: 不适用
- 来源类型: 官方技术页/非论文
- 发布日期: 2026-01-27
- 链接: https://www.figure.ai/news/helix-02

## 一句话总结
Helix 02 将 Figure 的 S1/S2 Helix 扩展到全身 loco-manipulation：新增 1kHz System 0 学习式全身控制器，S1 变为 all sensors in / all joints out 的 200Hz 全身 visuomotor policy，S2 继续提供语义 latent；官方展示 4 分钟、61 个动作的洗碗机任务和触觉/掌心相机驱动的精细操作，但仍是官方视频 release，没有公开 benchmark。

## 问题
Humanoid loco-manipulation 难以拆成独立的走路、稳定、抓取和搬运控制器：拿起物体会改变平衡，迈步会改变可达空间，手臂和腿持续互相约束。传统 state machine 拼接控制器在接触变化、物体移动和长时序任务中脆弱。Helix 02 要解决的是：如何让单一学习系统从像素、触觉和本体状态直接协调全身，连续完成行走、平衡和操作。

## 方法
- 方法线归属: 分层 VLA + 全身学习控制；在 VLA 知识库中属于 humanoid full-body extension，同时也应和 whole_body_control / locomotion 域交叉引用。
- 核心 idea: 在 Helix 的 S2 语义层和 S1 visuomotor 层之下加入 System 0 全身控制先验，让 S2 产生任务语义、S1 输出全身 joint targets、S0 以 kHz 频率处理平衡、接触和全身协调，形成 pixels-to-torque 的三层神经层级。
- 关键技术点:
  - System 0: 10M 参数 learned whole-body controller，用全身关节状态和 base motion 输入，输出 1kHz joint-level actuator commands。
  - S0 训练: 官方称使用超过 1,000 小时 joint-level retargeted human motion data，并在超过 200,000 个并行仿真环境中用 sim-to-real reinforcement learning 和 domain randomization 训练。
  - System 1: 从原 Helix 的上半身控制扩展为 all sensors in / all joints out；输入包括头部相机、掌心相机、指尖触觉和全身本体状态；输出腿、躯干、头、双臂、腕和手指的完整 joint-level targets。
  - System 2: 保持语义推理层，理解场景和语言并产生 latent goals；任务从“拿起番茄酱”扩展到“走到洗碗机并打开”“把碗拿到台面”等房间级语义指令。
  - 新硬件感知: Figure 03 的掌心相机提供 in-hand vision，指尖触觉可检测低至约 3g 的力，用于遮挡场景下的接触确认和力调节抓取。
  - 代码替换 claim: 官方称 S0 用单一神经先验替代 109,504 行手写 C++ 全身控制逻辑；这是官方工程口径，未给外部验证。

## 实验
- Benchmark: 无公开标准 benchmark；没有可复现的 humanoid loco-manipulation 任务套件或统计表。
- 公开视频/内部 claim:
  - 官方视频展示机器人连续 4 分钟完成洗碗机相关任务：走到洗碗机、卸载餐具、穿过房间、堆叠到柜子、装载并启动洗碗机；官方称无 reset、无人介入，全部 onboard sensors autonomous。
  - 官方称该任务包含 61 个 loco-manipulation actions，覆盖持物行走、双臂协调、用髋部关抽屉、用脚抬洗碗机门等全身动作。
  - 触觉和掌心相机精细操作视频包括拧瓶盖、从药盒取单个药片、注射器推出 5ml、从杂乱盒中取金属小件。
- 公开 benchmark:
  - 未公开模型、数据、episode 数、失败率、任务定义、对比方法或第三方复现。
- 对比基线:
  - 主要与前代 Helix 上半身控制和传统分离控制器做定性对比；没有数值基线。

## 评价
- 优势: Helix 02 把 VLA 的动作空间从上半身 manipulation 扩展到全身 loco-manipulation，并把 tactile + in-hand vision 纳入端到端 policy 输入，是 Figure 路线中从“手臂策略”走向“全身 autonomous humanoid”的关键节点。
- 局限: 证据仍是官方 demo 和 claim；4 分钟任务是否可重复、泛化到多少厨房/物体、失败恢复如何定义都不清楚；S0/S1/S2 的训练接口、loss、数据混合方式未披露。
- 对 VLA 领域的贡献: 这张卡应作为 VLA 与 whole-body control 的交叉 release：S2/S1/S0 三层时间尺度设计提供了 humanoid VLA 的工程范式，但其科学结论需要公开 benchmark 或论文验证后才能进入核心 taxonomy。
