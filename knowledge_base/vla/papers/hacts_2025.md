# HACTS: a Human-As-Copilot Teleoperation System for Robot Learning (2025)

## 基本信息
- 作者: Zhiyuan Xu*, Yinuo Zhao*, Kun Wu*, Ning Liu, Junjie Ji, Zhengping Che, Chi Harold Liu, Jian Tang
- 机构: Beijing Innovation Center of Humanoid Robotics, Beijing Institute of Technology
- arXiv: 2503.24070

## 一句话总结
提出低成本（<$300）双边位置同步遥操作系统 HACTS，通过 follower-to-leader 关节位置反向同步实现无缝人类介入（copilot 模式），为模仿学习提供 action-correction 数据、为人在回路强化学习提供实时干预能力，在 UR5 平台上验证了 IL 和 RL 两种范式的性能提升。

## 问题
**现有遥操作系统缺乏双向同步，无法支持人类无缝介入**：
1. **单向控制限制**：VR、外骨骼、动捕等遥操作系统只支持 leader→follower 控制，当机器人自主执行策略时，遥操作硬件与机器人状态脱同步；
2. **介入不连续**：人类想接管自主运行中的机器人时，leader-follower 位姿存在偏差，产生突变和安全隐患（类比自动驾驶中方向盘不同步的接管问题）；
3. **现有双边系统门槛高**：力反馈/触觉双边系统（Bi-ACT、FACTR 等）需要昂贵的力传感硬件和复杂的控制算法，大多数机器人平台（如 UR5）不具备此能力；
4. **结果**：人在回路的 IL（action-correction 数据收集）和 RL（在线干预）无法高效进行。

## 方法
- **方法线归属**: 交互式数据收集（Interactive Data Collection）/ 遥操作硬件系统，与 RoboCopilot (2024) 同属"双边遥操作 + Human-in-the-loop"支线
- **核心 idea**: 不追求复杂的力反馈，仅通过**双边关节位置同步**（follower→leader 反向位置控制）就能实现人类无缝介入——这是几乎所有机器人平台都支持的最简接口。

### 关键技术点

#### 1. 双边位置同步（Bilateral Position Synchronization）
- **Leader→Follower**（传统模式）：与 ALOHA/GELLO 相同，用于离线数据采集
- **Follower→Leader**（核心创新）：策略自主执行时，机器人关节位置经反向偏移补偿后发送到 leader 端电机，使遥操作设备实时跟随机器人状态
- **切换机制**：脚踏板作为模式切换接口——踩下切换为人类控制（leader→follower），松开切回自主执行（follower→leader）
- **关键优势**：仅需位置信息同步（不需要力/触觉传感），适配几乎所有机器人平台

#### 2. 低成本运动学等价硬件
- 基于 UR5 的 DH 参数设计运动学等价的缩比模型
- 使用 DYNAMIXEL XL430（前 3 关节，高扭矩）+ XL330（后部关节+夹爪，轻量低成本）
- 3D 打印 PLA 结构件
- **总成本 < $300**（对比 RoboCopilot 的 QDD 关节 < $2000/臂）

#### 3. 软件架构
- DYNAMIXEL API 直接读写电机位置
- 初始偏移标定 → 正向/反向偏移补偿
- 10Hz 环境更新频率

### 应用于两种学习范式

#### A. 模仿学习（IL）
- 用 pre-trained 策略（ACT/DP）执行任务
- 策略失败时人类通过 HACTS 介入，收集 action-correction 轨迹
- 将 50 条 HACTS 修正轨迹 + 50 条原始专家轨迹混合训练

#### B. 强化学习（RL）
- RLPD-HACTS：结合 RLPD（off-policy RL）+ HACTS 人类干预
- 三阶段：(1) 训练 ResNet-10 reward classifier → (2) BC 预训练 actor → (3) RLPD 在线微调 + HACTS 人类修正
- 动作空间：末端执行器 6D 相对运动 + 夹爪状态

## 实验

### 硬件平台
- UR5 + Robotiq 2f-85 夹爪
- RTX 4090 工作站
- 336 腕部相机 + 336L 外部相机

### IL 实验（3 个任务 × 4 个设置）
**任务**：OpenBox（按开关开盒子）、SteamBun（夹包子放蒸屉）、UprightMug（翻杯放正）

**4 种设置**：
1. **EADC**（等量数据对比）：50 expert + 50 HACTS vs 100 expert
2. **FCID**（分布内失败修正）：针对 ID 失败收集修正数据
3. **ODSS**（OOD 静态泛化）：物体位置完全不同于训练集
4. **ODDS**（OOD 动态泛化）：执行过程中手动移动目标物体

**关键结果（ACT，Tab. II）**：

| 任务 | 设置 | pre-ACT | full-ACT (100exp) | HACTS-ACT (50exp+50hacts) |
|------|------|---------|-------------------|---------------------------|
| UprightMug | EADC | 40% | 60% | **70%** |
| UprightMug | FCID | 10% | 40% | **70%** |
| UprightMug | ODSS | 0% | 0% | **40%** |
| SteamBun | FCID | 20% | 60% | **80%** |
| OpenBox | ODDS(DP) | 0% | 0% | **40%** |

- **EADC**：同等数据量下 HACTS-ACT 全面超越 full-ACT
- **FCID**：修正数据显著修复失败案例（UprightMug: 10%→70%）
- **ODSS/ODDS**：原始策略和 full 策略均 0%，加入 HACTS 数据后开始 handle OOD 情况

### RL 实验（CloseBin 任务）
- **任务**：关闭随机放置/朝向的垃圾桶盖
- **RLPD-HACTS**：10 分钟 BC 预训练 + 45 分钟在线 RLPD → 80% 成功率
- 人类干预长度随训练下降：从 ~14 步降到 <6 步

### 对比基线
- IL：pre-ACT/DP（50 expert）、full-ACT/DP（100 expert）
- RL：BC-only baseline

## 评价

### 优势
1. **极低成本+高可复现性**：$247 总成本，3D 打印+现成电机，远低于 RoboCopilot ($2000+/臂) 和力反馈方案
2. **最简接口的实用性验证**：证明仅靠"位置同步"（不需要力/触觉反馈）就足以支持有效的人在回路交互，大幅降低了双边遥操作的技术门槛
3. **覆盖 IL+RL 两种范式**：论文同时展示了对 IL（action-correction 数据）和 RL（HITL online learning）的支持，比 RoboCopilot（仅 IL）更全面
4. **类比清晰**：自动驾驶方向盘同步类比直观表达了 follower→leader 同步的价值
5. **实验设置丰富**：EADC/FCID/ODSS/ODDS 四种设置系统回答了 action-correction 数据在不同场景下的价值

### 局限
1. **实验规模较小**：每项仅 10 次评估 rollout，统计显著性有限；所有任务均为 UR5 桌面操作，未在双臂/移动操作等更复杂场景验证
2. **缺乏与同类工作的直接对比**：未与 RoboCopilot（力反馈双边遥操作）、GCENT（倒带+Task Sentinel）等方法做定量对比
3. **RL 实验相对初步**：仅 CloseBin 单任务，成功率 80%（非 SOTA 级别），未对比 HIL-SERL 等成熟 HITL RL 方法
4. **无力反馈**：纯位置同步在接触丰富任务（如精密装配）中可能不足——RoboCopilot 的力反馈在此类任务中展示了更好的数据质量
5. **单机器人，无扩展性讨论**：未探索 1:N 多机器人监督，这一点 GCENT 的 Task Sentinel 方案远更成熟
6. **低扭矩电机限制**：XL430/XL330 的扭矩限制了可驱动的 leader 臂尺寸，扩展到更大机器人需要更高功率电机

### 与相关工作的定位对比

| 工作 | 双边同步方式 | 成本 | 支持 RL | 扩展性 | 真机平台 |
|------|------------|------|---------|--------|---------|
| **ALOHA/GELLO** | 无（单向） | ~$200-300 | ❌ | N/A | 多种 |
| **RoboCopilot** (2024) | 力反馈双边控制 | ~$2000+/臂 | ❌ | 单机 | 20-DoF 双臂 |
| **GCENT** (2025) | VR 遥操作+倒带 | 中等 | ❌ | **1:N** | AgiBot G01 |
| **HACTS（本文）** | **位置同步** | **<$300** | **✅** | 单机 | UR5 |

**核心定位**：HACTS 选择了最简的双边同步方案（位置同步），以最低成本实现了 copilot 功能，并首次将此类系统应用于 HITL RL。在成本-功能权衡上，HACTS 站在"最低门槛"端——牺牲力反馈和扩展性，换取极低成本和极高可复现性。

### 对 VLA 领域的贡献
1. **降低了人在回路交互数据收集的硬件门槛**：证明 $300 以内就能建立有效的双边遥操作系统，使更多实验室能采用 deploy-then-collect 范式
2. **IL+RL 双范式支持**：首次在同一硬件系统上展示 action-correction 数据对 IL 和 HITL RL 的价值，对 VLA 训练数据策略有参考意义
3. **action-correction 数据的系统验证**：四种实验设置（EADC/FCID/ODSS/ODDS）系统证明了修正数据在等量替代、失败修复、OOD 泛化等场景下的全面优势
4. **与 RoboCopilot 并发且互补**：RoboCopilot 解决力反馈和双臂操作，HACTS 解决最低成本和 RL 支持——两者共同推进了交互式数据收集硬件生态
