# Evo-RL: Open Real-World RL for VLA

## 基本信息
- **论文**: 暂无（Paper Coming Soon）
- **GitHub**: https://github.com/MINT-SJTU/Evo-RL
- **项目主页**: https://MINT-SJTU.github.io/Evo-RL/
- **机构**: SJTU MINT Lab + Evo-Tech（EvoMind）
- **发布时间**: 首次发布 2026.02.26（SO101），2026.03.07 增加 AgileX PiPER 支持
- **基础框架**: LeRobot 0.4.4
- **方法线归属**: **VLA RL 后训练（离线 RL + Advantage-Conditioned Policy，真机开源）**

## 核心问题
- 真机 RL（Real-World RL）缺乏可复现的开源实现
- 现有 VLA RL（HIL-SERL 等）代码未完全开放，硬件要求高
- 如何在消费级机器人平台（SO101, PiPER）上复现离线 RL 工作流

## 核心算法：Advantage-Conditioned Policy (ACP)

### 整体思路
不做 online RL（避免真机探索的安全风险），而是**离线 RL 循环**：
1. 收集带干预标注的轨迹数据
2. 训练价值函数评估轨迹质量
3. 推断每帧的 advantage（优势信号）
4. 将二值化优势标签注入 policy 的 **task text** 中进行条件化训练
5. 部署新策略，收集下一轮数据

### 关键设计
**ACP Indicator 注入 Task Text**：
- 用价值函数估计每帧 return-to-go（value）
- 计算 n-step advantage（相对于 baseline 的改进信号）
- 将 advantage 二值化为 indicator（top K% 为正例，如 top 30%）
- 训练时把 `acp_indicator` 拼接进任务文本（条件化）
- **Policy 必须支持 text/task input**，因为优势标签通过文本注入

**Indicator Dropout**：训练时以 30% 概率丢弃标签，让策略同时学习有/无标签两种条件

### Pipeline（7 步循环）
```
1. Data Collection (lerobot-human-inloop-record)
   └─ Human-in-the-loop 遥操作 + 干预（热键 i=接管, s=成功, f=失败）
   └─ 自动记录 rollout 数据

2. Value Function Training (lerobot-value-train)
   └─ 默认: Pi*0.6 价值函数 (--value.type=pistar06)
   └─ 可扩展：自定义 value model

3. Value Inference (lerobot-value-infer)
   └─ 输出: value, advantage, indicator 三列写回 dataset
   └─ 关键参数: --acp.n_step=50, --acp.positive_ratio=0.3

4. Policy Training (lerobot-train)
   └─ --acp.enable=true 启用 ACP
   └─ indicator 注入 task text

5. Closed-loop Rollout → 下一轮 Data Collection
```

### 硬件支持
| 平台 | 类型 | 接口 |
|------|------|------|
| SO100/SO101 | 低成本桌面臂 | Serial (by-id 稳定路径) |
| AgileX PiPER | 工业臂 | CAN interface |
| AgileX PiPER-X | 工业臂（升级版）| CAN interface |

支持单臂和双臂配置，相机支持 OpenCV + Intel RealSense。

### 人机协作数据收集（Human-in-the-Loop）
- `lerobot-human-inloop-record`：策略运行中人类实时接管
- 热键：`i`（接管/退出）、`s`（标成功）、`f`（标失败）
- 支持数据集质量报告：`lerobot-dataset-report`

## 与相关工作对比

| 方法 | RL 类型 | 价值估计 | VLA 集成 | 开源 |
|------|---------|---------|---------|------|
| HIL-SERL | Online RL | Q-function | 无（单独policy）| 部分 |
| Q-Chunking | Online RL | Q-function | 有（仿真为主）| 部分 |
| Hi-ORS | 拒绝采样（无Q） | Outcome-based | 有（π₀）| 无 |
| **Evo-RL** | **离线 RL (ACP)** | **Value+Advantage** | **有（LeRobot 兼容）** | **完全开源** |

**核心差异化**：
- Hi-ORS：用 outcome 直接过滤，无价值函数；Evo-RL：用价值函数估计 advantage，更精细的 per-step 优势信号
- HIL-SERL：online RL 需要实时 Q 更新；Evo-RL：离线训练，更安全，更易复现
- **最大价值：完全开源 + 可复现真机 RL pipeline**

## 方法创新点分析
1. **ACP 将 RL 信号转化为文本条件**：避免修改 policy 架构，任何支持文本输入的 VLA 均可接入
2. **离线 RL 循环**：每轮收集数据→训练价值函数→推断优势→条件化训练，无需危险的在线探索
3. **leRobot 生态整合**：复用 LeRobot 的数据收集/训练基础设施，降低工程门槛
4. **开放社区驱动**：持续发布数据/benchmark，鼓励社区贡献 RL 算法

## 局限性与当前状态
- 论文尚未发布（2026.03 时），缺乏系统性 benchmark 对比
- 当前默认价值函数为 Pi*0.6，自定义价值函数需要实现指定接口
- 仅在 SO101 和 AgileX PiPER 上验证，尚无跨平台泛化数据

## 与 Evo 系列关系
- **Evo-0**: VLA 空间感知增强（VGGT，架构创新）
- **Evo-1**: 轻量化 VLA（0.77B，语义保护训练）
- **Evo-RL**: 真机 RL 后训练框架（ACP，工程开放）
- 三者定位互补：Evo-0 提升空间推理，Evo-1 降低部署门槛，Evo-RL 实现真机持续改进
