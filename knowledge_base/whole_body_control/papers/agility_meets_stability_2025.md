# Agility Meets Stability: Versatile Humanoid Control with Heterogeneous Data (2025)

## 基本信息
- 作者: Yixuan Pan*, Ruoyi Qiao*, Li Chen, Kashyap Chitta, Liang Pan, Haoguang Mai, Qingwen Bu, Hao Zhao, Cunyuan Zheng, Ping Luo, Hongyang Li
- 机构: The University of Hong Kong, NVIDIA, Tsinghua University, Individual Contributor
- arXiv: 2511.17373
- 链接: https://arxiv.org/abs/2511.17373, https://opendrivelab.com/AMS/

## 一句话总结
AMS 用 MoCap 动态动作 + 合成极端平衡动作训练单一 WBC policy，同时覆盖跑步/舞蹈等敏捷动作和单腿深蹲等稳定性动作。

## 问题
现有 humanoid whole-body tracking 往往专注敏捷动态动作或极端平衡动作之一。MoCap 数据富含舞蹈、跑步等动态行为，但平衡姿态长尾稀缺且受人类能力限制；稳定性 reward 又可能抑制动态动作需要的自然动量转移，导致统一策略难以兼顾 agility 和 stability。

## 方法
- 方法线归属: Motion Imitation / Agile WBC + Balance Control
- 核心 idea: 用异构数据补齐分布缺口：AMASS/LAFAN1 提供人类动态动作，直接在 humanoid motion space 中生成 synthetic balance motions；训练时只对合成平衡数据注入 balance-specific priors，避免干扰动态动作
- 关键技术点:
  - Synthetic balance data: 生成满足单脚支撑、接触和 CoM 约束的合成平衡轨迹，补充人类 MoCap 不足
  - Hybrid rewards: 所有数据使用 general tracking reward；只对 synthetic balance data 使用 CoM alignment、接触稳定等 balance prior
  - Adaptive sampling: 按 motion performance 动态采样困难动作，处理长尾和平衡难例
  - Adaptive reward shaping: 为不同 motion 维护独立 tracking tolerance，避免统一 reward 尺度压制某类动作
  - 部署: teacher-student 式全身跟踪策略迁移到 Unitree G1

## 实验
- Benchmark: IsaacGym 仿真；Unitree G1 真实机器人；训练数据约 8,000 AMASS/LAFAN1 sequences + 10,000 synthetic balance sequences
- 主要结果:
  - All dataset 上 AMS: Eg-mpjpe 54.06、Empjpe 29.02、Success 99.78%，优于 OmniH2O 69.84/44.18/98.93% 和 HuB 151.26/98.42/77.23%
  - 在 MoCap dynamic data 上 AMS 保持 99.69% success，同时 synthetic balance data 上 99.95% success，说明未以牺牲动态性能换平衡
  - 去掉 synthetic balance data 后，synthetic balance success 降到 94.54%，Eg-mpjpe 恶化到 112.20
  - OOD 测试中 AMS success 99.7%，优于 w/o synthetic balance 96.0% 和 OmniH2O w/ all data 99.1%，且 tracking error 更低
  - 真实 G1 展示未见过的 Ip Man's Squat、单腿平衡、跑步、舞蹈和 RGB pose teleoperation
- 对比基线: OmniH2O-style WBT、HuB-style balance reward、无 synthetic balance data、general-only reward、all-rewards-for-all-data、无 adaptive learning

## 评价
- 优势: 明确指出“敏捷 vs 平衡”的数据分布与 reward 冲突，并用异构数据+条件化 reward 解决；相比单纯扩大 MoCap，合成平衡数据直接覆盖 robot-specific balance space；对 HOVER/OmniH2O 式 WBT 是重要补充
- 局限: 主要是 reference motion tracking，不提供精确末端操作控制；RGB pose teleoperation 噪声较大，不适合高动态远程操作；合成平衡生成和 reward 仍依赖任务先验
- 对 Whole-Body Control 的贡献: AMS 可视为 WBC 中“运动模仿 scaling”之外的稳定性补齐路线，强调异构数据和 reward gating 对统一全身控制的价值
