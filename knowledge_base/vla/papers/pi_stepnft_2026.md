# π-StepNFT: Wider Space Needs Finer Steps in Online RL for Flow-based VLAs (2026)

## 基本信息
- 作者: Siting Wang, Xiaofeng Wang, Zheng Zhu, Minnan Pei, Xinyu Cui, Cheng Deng, Jian Zhao, Guan Huang, Haifeng Zhang, Jun Wang
- 机构: GigaAI, CASIA, UCAS, Tsinghua University, Zhongguancun Academy, University of Edinburgh, UCL
- arXiv: 2603.02083
- 项目/代码: https://wangst0181.github.io/pi-StepNFT/

## 一句话总结
π-StepNFT 是面向 flow-based VLA 的 critic-free、likelihood-free 在线 RL：用 Flow-SDE 扩大探索空间，再用 step-wise contrastive ranking 对每个去噪小步做正/负分支排序；在 LIBERO few-shot 上让 π0 从 57.6% 提到 90.5%，π0.5 从 77.1% 提到 94.0%，并在 ManiSkill OOD 上比 PPO 高 10pp+。

## 问题
flow/ODE VLA 的动作 likelihood 难以计算，直接做 PPO/GRPO 需要近似或额外 critic；确定性 ODE 采样探索空间窄，SDE 虽能扩展探索但终点监督过粗，容易在多步去噪和顺序控制中累积误差。

## 方法
- 方法线归属: VLA RL 后训练 / critic-free online RL / flow-based policy optimization
- 核心 idea: "wider space needs finer steps"：用 SDE 噪声扩展专家轨迹附近的探索流形，再把监督目标从终点 x0 改成即时下一步 xt-，用成功/失败标签做局部正负分支排序。
- 关键技术点:
  - Flow-SDE rollout 记录每个环境步中的去噪链，随机抽一个 solver transition `(xt, xt-)` 做训练样本。
  - 在旧策略速度场两侧构造 mirror velocities `v+` / `v-`，共享协方差下计算 step error `E+` / `E-`。
  - logistic contrastive ranking: 成功轨迹要求 `E+ < E-`，失败轨迹反向，形成 push-pull 动态。
  - 不训练 value/critic，不反传 ODE solver；每个优化步只需一次 forward，降低 RL 计算和过拟合风险。

## 实验
- Benchmark: LIBERO 4 suites few-shot、ManiSkill PutOnPlateInScene IND/OOD。
- 主要结果: LIBERO few-shot π0 平均 57.6% → 90.5%（+32.9），π0.5 平均 77.1% → 94.0%（+16.9）；ManiSkill π0 OOD 平均 50.4%，高于 PPO 39.3%；π0.5 OOD 平均 59.5%，高于 PPO 49.3%。
- 对比基线: full SFT Octo/OpenVLA/πfast/OpenVLA-OFT/π0/π0.5，πRL Flow-SDE + PPO，πRL Flow-SDE + GRPO，weighted-MSE / positive-only / negative-only 消融。

## 评价
- 优势: 与 Hi-ORS 一样避免不稳定 Q 函数，但更深入 flow 去噪过程，在 step-level 提供细粒度偏好信号；相比 PPO，OOD 上不依赖视觉语言 critic，较少过拟合背景/提示词。
- 局限: 主要是仿真 benchmark，尚未展示真机在线 RL；长时序信用分配上 PPO 仍有优势，说明二值 episode label 对复杂长期任务可能不够密。
- 对 VLA 领域的贡献: 为 flow-based VLA 提供了无需 likelihood/critic 的在线 RL 公式化路径，可与 Hi-ORS、RLT、Evo-RL/RAMP 一起纳入 VLA RL 后训练方法线。
