# SMASH: Mastering Scalable Whole-Body Skills for Humanoid Ping-Pong with Egocentric Vision (2026)

## 基本信息
- 作者: Junli Ren*, Yinghui Li*, Kai Zhang*, Penglin Fu*, Haoran Jiang, Yixuan Pan, Guangjun Zeng, Tao Huang, Weizhong Guo, Peng Lu, Tianyu Li, Jingbo Wang, Li Chen, Hongyang Li, Ping Luo
- 机构: The University of Hong Kong, Kinetix AI
- arXiv: 2604.01158
- 链接: https://arxiv.org/abs/2604.01158, https://mmlab.hk/Smash/

## 一句话总结
SMASH 把 humanoid 乒乓球从外部感知/上肢击球推进到 onboard egocentric perception + whole-body strike matching，在 Unitree G1 上实现连续击球、低身救球和全身 smash。

## 问题
乒乓球要求小球高速感知、短时预测、移动到合适击球位并协调全身完成击球。既有 humanoid 乒乓系统多依赖外部相机或 motion capture，控制上也常把上肢击球和下肢移动解耦，导致反应空间、动作自然性和部署自主性受限。

## 方法
- 方法线归属: Agile / Athletic WBC；Humanoid-object interaction；motion prior + task RL
- 核心 idea: 用生成式 strike motion library 覆盖可达击球空间，再按目标击球点/速度做 task-conditioned motion matching，让 RL policy 同时追踪全身参考和优化击球任务；部署时用 onboard 双相机完成球状态、机器人位姿和击球目标估计
- 关键技术点:
  - Egocentric perception: onboard 相机估计球状态和机器人 pose，感知/控制链路约 50-120Hz，不依赖部署期外部摄像头
  - Motion-VAE: 从少量 MoCap 击球 clip 生成更多 strike motion，经 tracker/filter 保留机器人可跟踪的全身动作
  - Motion matching: 用相对击球位置、目标速度和 time-to-strike 检索全身参考动作，而不是只模仿固定 forehand/backhand
  - Task RL: 结合击球成功、球拍位置/速度/朝向误差、全身 tracking、平滑和力矩正则
  - Adaptive training: workspace region adaptive sampling 和 adaptive tracking sigma 处理稀有高球区域与早期 reward 稀疏

## 实验
- Benchmark: 仿真 policy evaluation；Unitree G1 真实乒乓击球；mocap 感知与 onboard egocentric 感知设置
- 主要结果:
  - 仿真中 SMASH strike success 86.38%，接近 HITTER 86.63%，但 MPJPE 75.01 明显优于 HITTER 100.05，力矩也更低
  - 仅用 PPO task reward 成功率 75.28%，说明 motion prior 对学习效率和动作质量关键
  - Motion-VAE 数据扩展把 400 MoCap clips 提升到 400-5k-gen 后，成功率从 76.55% 提升到 86.38%；去掉 tracker filter 后 MPJPE 恶化到 91.02
  - 真实机器人展示 smash、低身救球、大范围横移和 onboard 连续击球
- 对比基线: PPO task-only、Mimic/BeyondMimic-style pure motion imitation、HITTER-style upper-body-focused humanoid table tennis

## 评价
- 优势: 将高动态体育任务和 onboard egocentric perception 结合，是 WBC 从“可跟踪动作”走向“实时交互任务”的重要例子；motion generation + matching 比固定动作库更能覆盖击球空间；相较 HITTER 更强调全身协调和动作自然性
- 局限: smash 仍需专门策略/数据，说明多风格统一还有距离；乒乓感知链路复杂且任务专用；核心结果集中在单一体育任务，对通用 loco-manipulation 的迁移还需要验证
- 对 Whole-Body Control 的贡献: SMASH 可归入 Agile / Athletic WBC，与 BeyondMimic 的高动态运动不同，它强调“外界高速物体交互 + onboard perception + task-conditioned whole-body matching”，补足了动态物体交互任务线
