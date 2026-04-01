# VLM-as-Controller 系统框架（Agentic Robotics Framework）

## 核心思想
使用现成的VLM/LLM作为高层元控制器，调度低层VLA策略执行具体操作。与"层次化VLA"（π₀.5, Hi Robot等模型内统一高低层）不同，这是一种**分离式外部编排**方案：高层推理由通用VLM负责，低层控制由独立的VLA策略负责。

## 与层次化VLA的对比
| 维度 | 模型内层次化 (π₀.5, Hi Robot) | 系统级层次化 / VLM-as-Controller (SayCan, RoboClaw) |
|------|-------------------------------|------------------------------------------------------|
| 模型 | 同一模型做高层+低层 | VLM做高层 + 独立VLA做低层 |
| 知识共享 | 通过共享权重实现 | 通过上下文（prompt/memory）传递 |
| 训练 | 联合训练 | 分别训练 |
| 部署 | 单一模型 | 需要维护VLM + 多个VLA策略 |
| 灵活性 | 架构固定 | 可自由替换VLM/VLA组件，策略库可扩展 |
| 延迟 | 单次推理 | VLM推理+VLA推理两次 |
| 运行时适应 | 受限于训练分布 | 可通过VLM推理动态适应新情况 |

## 发展脉络
```
LLM/VLM 用于机器人规划（早期）:
Language Models as Zero-Shot Planners (2022) — LLM分解高层计划
Code as Policies (2022) — LLM生成控制代码
SayCan (2022) — LLM规划 + affordance grounding + 低层策略
VoxPoser (2023) — LLM生成3D value maps

运行时监督演进:
Inner Monologue (2022) — +环境反馈+重规划循环
LITEN (2025) — +推理时affordance学习
HAMSTER (2025) — 层次化子任务抽象+plan-verify
Agentic Robot (2025) — brain-inspired VLA框架

系统级全生命周期:
RoboClaw (2026) — VLM元控制器统一数据收集+策略学习+执行
  - 新增：EAP自重置数据收集
  - 新增：MCP工具接口标准化
  - 新增：结构化记忆（角色/任务/工作记忆）
  - 新增：收集-部署共享同一决策循环
```

## 代表工作

### SayCan (2022, Google)
- LLM提供语义规划 + affordance function过滤不可行动作
- 低层策略独立训练
- 无运行时监督，开环执行

### Inner Monologue (2022, Google)
- LLM规划 + 环境反馈（成功检测、场景描述、人类反馈）
- 通过反馈触发重规划
- 首次引入执行时的闭环反馈

### RoboClaw (2026, AgiBot/NUS/SJTU)
- **VLM元控制器** + π₀.5低层VLA
- **全生命周期统一**：同一VLM决策循环同时用于数据收集和任务执行
- **Entangled Action Pairs (EAP)**：正-逆动作配对实现自重置数据收集
- **结构化记忆**：角色身份 + 任务级记忆 + 工作记忆
- **MCP工具接口**：Start/Terminate/Switch Policy, Env Summary, Call Human
- **过程监督**：运行时持续监控 + 失败分类（退化/非退化）+ 恢复策略调度
- **闭环学习**：部署轨迹回流训练，失败经验转化为恢复策略
→ 详见 [papers/roboclaw_2026.md](../papers/roboclaw_2026.md)

## 关键设计要素
1. **高层推理机制**：ICL/CoT/规划/代码生成
2. **低层策略接口**：MCP工具调用 / API / 技能库
3. **记忆系统**：短期（当前上下文）+ 长期（任务进度/经验）
4. **运行时监督**：成功检测、失败分类、恢复决策
5. **人工升级机制**：自主失败恢复不行时请求人类介入
6. **数据闭环**：执行轨迹回流到训练管线

## 方法线总结
VLM-as-Controller 是一种实用的系统设计范式，适合以下场景：
- 需要灵活组合多种已有策略
- 需要运行时监督和恢复的长时序任务
- 团队不具备训练端到端层次化VLA的能力
- 需要统一数据收集和部署的工作流

**局限**：VLM推理延迟、高层/低层知识不共享、系统复杂度高
**趋势**：随着VLM能力提升，这类系统框架可能与模型内层次化VLA融合（如π₀.5已在模型内实现部分功能）
