# 论文清单

| 论文 | 年份 | 方法线 | 一句话总结 | 卡片 |
|------|------|--------|-----------|------|
| **RT-2** | **2023** | **VLM + Action Token** | **首次提出 VLA 概念，将机器人动作编码为文本 token 在预训练 VLM（PaLI-X/PaLM-E, 12B-55B）上 co-fine-tuning，6k 次真机评测证明互联网预训练知识可迁移到低层机器人控制，展示符号理解、多语言、常识推理等涌现能力** | **[rt2_2023.md](rt2_2023.md)** |
| Diffusion Policy | 2023 | Diffusion Policy (BC + Diffusion 奠基) | 首次将 DDPM 系统性引入机器人视觉运动策略，通过条件去噪扩散 + action sequence prediction + receding horizon control，在 15 个任务上平均提升 46.9%，奠定了扩散模型在机器人策略学习中的基础 | [diffusion_policy_2023.md](diffusion_policy_2023.md) |
| Octo | 2024 | Transformer + Diffusion Head (Cross-embodiment GRP) | 首个完全开源的跨具身通用机器人策略，基于 ViT + diffusion head 在 800k OXE 轨迹上预训练，通过模块化 token 化 + block-wise attention 支持灵活微调到新传感器/动作空间/机器人形态 | [octo_2024.md](octo_2024.md) |
| OpenVLA | 2024 | VLM + Action Token | 首个开源 7B 参数通用 VLA，基于 Prismatic VLM（SigLIP+DINOv2 + Llama 2 7B）在 970k OXE 轨迹上微调，以 7x 更少参数超越闭源 RT-2-X (55B) 16.5%，并首次系统探索 LoRA 微调和量化推理 | [openvla_2024.md](openvla_2024.md) |
| π0 | 2024 | VLM + Flow Head | 首个将 VLM（PaliGemma）与 flow matching action expert 结合的 VLA，通过 action chunking + flow matching 在 50Hz 下生成连续动作，10,000+ 小时跨具身预训练，首次展示端到端策略完成洗衣折叠、组装纸箱等高灵巧度长时序任务 | [pi0_2024.md](pi0_2024.md) |
| HG-DAgger | 2019 | Human-in-the-Loop 模仿学习 | 人类专家保持完整控制权（而非 DAgger 随机切换），解决 RC Sampling 的 actuator lag 和标签质量下降问题；集成神经网络 doubt 指标 + 数据驱动阈值学习安全边界；真实车辆自动驾驶任务零碰撞零出界 | [hgdagger_2019.md](hgdagger_2019.md) |
| **RoboCopilot** | **2024** | **交互式模仿学习 / 数据收集系统** | **顺应性双边遥操作系统实现无缝人机控制切换，将 HG-DAgger 落地于复杂双臂操作；交互数据（Batched DAgger）在移动搬运任务中以更少轨迹实现 91.7% vs 58.3% 的成功率，长时序任务首次实现完整流程通过** | **[robocopilot_2024.md](robocopilot_2024.md)** |
| **HACTS** | **2025** | **交互式数据收集 / 遥操作硬件系统** | **低成本（<$300）双边位置同步遥操作系统，通过 follower→leader 关节位置反向同步实现无缝人类介入，为 IL 提供 action-correction 数据、为 HITL RL 提供实时干预能力，首次在同一系统上展示对 IL+RL 双范式的支持** | **[hacts_2025.md](hacts_2025.md)** |
| π0.5 | 2025 | VLM + Flow Head + 层次化推理 | 通过异构数据co-training（跨机器人、高层语义、网络数据、口头指令）实现VLA在全新家庭的open-world长时序操作泛化 | [pi05_2025.md](pi05_2025.md) |
| **MEM** | **2025** | **VLM + Flow Head + 多尺度记忆** | **提出多尺度记忆系统，通过高效视频编码器实现短时视觉记忆 + 语言摘要机制实现长时语义记忆，使 VLA 能在保持实时推理下完成长达 15 分钟的复杂操作任务（厨房清洁、菜谱准备），同时解锁上下文适应能力** | **[mem_2025.md](mem_2025.md)** |
| **Genie Centurion (GCENT)** | **2025** | **交互式模仿学习 / DAgger-inspired 数据收集** | **"deploy-then-collect"范式：不完美策略部署→失败时倒带历史状态→人类精修；Task Sentinel 自动检测步骤完成使单人监督多机器人成立；同等数据下成功率提升 40%，达到同等性能仅需 44.5% 数据** | **[genie_centurion_2025.md](genie_centurion_2025.md)** |
| **Being-H0.5** | **2026** | **VLM + Flow Head + 人类中心学习 + 跨具身统一动作空间** | **以人手运动为"物理母语"，构建最大具身预训练语料 UniHand-2.0（35K 小时/30 种具身/120B token），通过统一动作空间 + Mixture-of-Flow + 流形保持门控实现单一检查点在 5 种异构平台的跨具身泛化，LIBERO 98.9%/RoboCasa 53.9% SOTA** | **[being_h05_2026.md](being_h05_2026.md)** |
| **RaC** | **2025** | **交互式数据收集 / Recovery+Correction 数据构成** | **在IL预训练后显式扩展"恢复+修正"行为：两条规则（恢复配对修正+介入后终止）使数据效率提升10x，5小时数据超越89小时SOTA（衬衫挂架78.3%），并首次证明机器人策略的o1-style测试时Scaling（恢复次数↑→成功率线性增加）** | **[rac_2025.md](rac_2025.md)** |
| **RoboClaw** | **2026** | **VLM-as-Controller 系统框架** | **VLM元控制器统一数据收集、策略学习和长时序任务执行，通过Entangled Action Pairs（正-逆动作对）实现自重置数据收集，运行时过程监督+技能编排使长时序任务成功率提升25%，人力减少53.7%** | **[roboclaw_2026.md](roboclaw_2026.md)** |
| **Xiaomi-Robotics-0** | **2026** | **VLM + Flow Head（实时部署优化）** | **基于 Qwen3-VL-4B + DiT 的 4.7B VLA，提出 Λ-shape attention mask 解决异步执行中 action prefix shortcut 问题，在消费级 GPU（RTX 4090, 80ms）上实现流畅实时双臂操作，LIBERO 98.7%/CALVIN 4.80/SimplerEnv 85.5% 全面 SOTA** | **[xiaomi_robotics_0_2026.md](xiaomi_robotics_0_2026.md)** |
| **DreamZero** | **2026** | **World Action Model（视频+动作联合去噪）** | **基于 Wan2.1-I2V-14B 视频扩散骨干的 14B WAM，自回归 chunk-wise 联合视频+动作 flow matching，仅 500h 多样非重复数据实现零样本任务/环境泛化（2x+ 优于 SOTA VLAs），38x 推理加速实现 7Hz 实时闭环，30min play data 少样本跨具身迁移** | **[dreamzero_2026.md](dreamzero_2026.md)** |
| **Hi-ORS** | **2025** | **VLA RL 后训练 / Rejection Sampling Post-training** | **用拒绝采样代替 Q 函数解决 RL VLA 后训练不稳定问题：outcome-based 过滤消除值估计误差（I1），reward-weighted flow matching 监督全部去噪步骤提供密集信号（I2）；人类干预提供 error-recovery 示教；3 个真机任务 1.5h 达 80% 成功率，+23.3% vs BC，展示 test-time scaling** | **[hi_ors_2025.md](hi_ors_2025.md)** |
| **Evo-0** | **2025** | **VLM + Flow Head + 隐式3D空间增强** | **将 VGGT（Visual Geometry Grounded Transformer）作为即插即用空间编码器注入 π₀：单层 Cross-Attention 融合 2D visual tokens + VGGT 3D tokens，无需深度传感器从 RGB 隐式获取几何先验；RLBench 5任务平均 56% vs π₀ 41%（+15pp），在精细定位/碰撞敏感任务增益最大** | **[evo0_2025.md](evo0_2025.md)** |
| **Evo-1** | **2025** | **轻量 VLA（InternVL3-1B + Cross-Modulated DiT，无机器人预训练）** | **0.77B 轻量 VLA：InternVL3-1B 原生多模态骨干（前14层）+ Cross-only DiT（仅 Cross-Attention，更紧凑）+ 两阶段语义保护训练（Stage1冻结VLM，Stage2解冻微调）；Meta-World 80.6% SOTA（+12.4pp vs SmolVLA），LIBERO 94.8%，RoboTwin 37.8% SOTA，真机 78%，无机器人数据预训练** | **[evo1_2025.md](evo1_2025.md)** |
| **Evo-RL** | **2026** | **VLA RL 后训练（离线 ACP，真机开源）** | **Advantage-Conditioned Policy（ACP）：训练价值函数→推断 n-step advantage→二值化为 indicator 标签注入 task text→条件化策略训练；完全离线 RL 循环，避免真机在线探索风险；基于 LeRobot 0.4.4，支持 SO101 和 AgileX PiPER/PiPER-X，论文待发布，代码完全开源** | **[evo_rl_2026.md](evo_rl_2026.md)** |
| **SaiVLA-0** | **2026** | **冻结VLM + 分类式动作解码（Tripartite Architecture）** | **神经科学启发三元架构：冻结大VLM（Cerebrum）低频提供多层语义先验，Pons Adapter编译为执行token，ParaCAT（Cerebellum）高频输出{-1,0,+1}三元分类动作并行K步解码，两阶段特征缓存训练（-40%时间），固定比率调度（N=5,K=20），注视式几何ROI，LIBERO 99.0% SOTA** | **[saivla0_2026.md](saivla0_2026.md)** |
| **RLT** | **2025** | **VLA RL 后训练（RL Token + 轻量 Actor-Critic）** | **冻结 VLA（π0.6）上训练 encoder-decoder transformer 暴露紧凑 "RL Token" 表征，作为轻量 actor-critic 的状态接口 + BC 正则化 + chunk-level RL，数小时真机在线 RL 即可提升关键阶段速度 3× 并超越人类遥操作速度，Ethernet 任务中位完成步数 66 vs 遥操作 146** | **[rlt_2025.md](rlt_2025.md)** |
| **RDT2** | **2025** | **VLM + Flow Head（跨具身泛化方向，UMI 数据 Scaling）** | **基于 Qwen2.5-VL-7B 的 7.4B 机器人基础模型，增强版 UMI 硬件采集 10,000+ 小时具身无关数据（100+场景/3000+物体），三阶段渐进训练（RVQ 离散化对齐语言-动作→Flow Matching 连续精度→单步蒸馏实时推理），首次实现"4U"零样本泛化（Unseen embodiment/scene/object/instruction），乒乓球/射箭等动态任务~100ms 反应** | **[rdt2_2025.md](rdt2_2025.md)** |
| **VITRA** | **2025** | **Human Data Pretraining + 野外视频 V-L-A 自动构造** | **将 Ego4D/EPIC/EgoExo4D/SSV2 的无标注真实人类活动视频自动转成 1M atomic hand-action V-L-A episodes（3D 手/相机运动 + 速度极小值切分 + trajectory-overlay GPT caption），预训练 PaliGemma-2 + diffusion action expert 后在 Realman+XHand 真机上达到 71.0% seen / 64.6% unseen 成功率，显著优于 π0 和 OXE pretrain** | **[vitra_2025.md](vitra_2025.md)** |
| RISE | 2026 | World Model RL / VLA Self-Improvement | 用 controllable dynamics model + progress value model 在 imagination rollout 中产生 advantage，对 π0.5 类策略做离线自提升；世界模型只用于训练，部署仍是普通 VLA | [rise_2026.md](rise_2026.md) |
| χ0 / kai0 | 2026 | VLA 部署分布对齐 / 长时序衣物操作 | 将长时序衣物操作失败归因到 demonstration、policy bias、deployment trajectory 分布不一致，用 model arithmetic、stage advantage 和 train-deploy alignment 在有限资源下提升 π0.5 可靠性 | [kai0_2026.md](kai0_2026.md) |
| MM-Hand | 2026 | 灵巧手硬件 / 多模态触觉平台 | 开源 21-DoF 模块化灵巧手，集成远程绳驱、in-palm stereo vision 和可拆卸触觉指尖，为人手数据到灵巧机器人策略提供可复制执行端 | [mm_hand_2026.md](mm_hand_2026.md) |
| TAMEn | 2026 | 触觉感知闭环数据收集 | 跨夹爪 wearable interface + mocap/VR 双模式采集 + feasibility checking + tactile recovery teleoperation，把接触丰富任务数据收集做成闭环数据飞轮 | [tamen_2026.md](tamen_2026.md) |
| GO-1-Pro | 2025 | 机器人数据多样性 Scaling | 系统拆解 task / embodiment / expert diversity 对大规模 manipulation 预训练的作用，指出 task diversity 最关键、expert diversity 可能造成 velocity ambiguity，并用 distribution debiasing 提升数据效率 | [go1_pro_2025.md](go1_pro_2025.md) |
| FreeTacMan | 2025 | Robot-free 视觉-触觉数据采集 | 用低成本手持夹爪和 GelSight 风格触觉传感器采集接触丰富任务数据，再训练视觉-触觉 diffusion policy 迁移到真实机器人 | [freetacman_2025.md](freetacman_2025.md) |
| UniVLA | 2025 | Task-centric Latent Action | 用无动作视频学习 task-centric latent action token，将 action-free video、跨具身机器人数据和导航数据统一到潜动作空间；下游只需轻量 action decoder 适配目标机器人 | [univla_2025.md](univla_2025.md) |
| AgiBot World Colosseo | 2025 | 大规模机器人数据与评测平台 | 真实机器人操作数据、统一 schema 和 Colosseo benchmark 组成平台化数据基础设施，推动 VLA 从单实验室 demo 走向持续数据运营 | [agibot_world_colosseo_2025.md](agibot_world_colosseo_2025.md) |
| Self-Directed Learning | 2025 | VLA 观点论文 / 自导学习 | 指出仅靠 BC/VLA scaling 会遇到平台期，提出 goal identification、skill acquisition、monitoring/evaluation 的 self-directed learning 研究议程 | [self_directed_learning_2025.md](self_directed_learning_2025.md) |
| EgoVLA | 2025 | Human Data Pretraining for VLA | 用带手腕/手姿态标注的 egocentric 人类视频预训练 VLM-action 模型，再用少量 humanoid robot demos 后训练，通过 MANO 统一动作空间、IK 和 retargeting 迁移到双臂灵巧手机器人；证明 human-video pretraining 能显著提升机器人后训练效果，但不是 robot-free zero-shot policy | [egovla_2025.md](egovla_2025.md) |
| EgoZero | 2025 | Robot-free egocentric imitation learning | 用 Project Aria smart glasses 采集 in-the-wild 人类示范，把视觉和手部动作压缩成 egocentric 3D point state-action，在 7 个 Franka 任务上用每任务约 20 分钟人类数据、无机器人训练数据达到约 70% zero-shot 成功率 | [egozero_2025.md](egozero_2025.md) |
| EMMA | 2025 | Human Data Pretraining + Mobile Manipulation | 将 egocentric human data 从桌面扩展到移动操作，通过 navigation retargeting、manipulation coordinate alignment 和 phase-aware control，与静态机器人操作数据 co-train，在无需 mobile teleoperation 数据下接近或超过 Mobile ALOHA 风格遥操作基线 | [emma_2025.md](emma_2025.md) |
| EgoHumanoid | 2026 | Human Data Pretraining + Humanoid Loco-Manipulation | 通过 view alignment 和 unified action alignment，把 in-the-wild 人类示范与少量 Unitree G1 robot teleop co-train 到 π0.5 policy，在未采集机器人数据的新场景中相对 robot-only 提升 51pp | [egohumanoid_2026.md](egohumanoid_2026.md) |
| Uni-Hand | 2025 | Egocentric Hand Motion Forecasting | 将 egocentric hand trajectory prediction 扩展到多模态输入、多维 2D/3D、多目标 wrist/finger joint 和 hand-object interaction state 预测，并首次用 ALOHA 真机验证 hand-motion forecasting 可转成机器人末端轨迹与抓取时序 | [uni_hand_2025.md](uni_hand_2025.md) |
| HaWoR | 2025 | World-space Hand Motion Reconstruction | 将 egocentric hand reconstruction 从相机坐标系提升到世界坐标系，结合 adaptive egocentric SLAM、metric scale alignment 和 motion infiller，为 ego human data 到 robot policy 提供手部轨迹标注基础设施 | [hawor_2025.md](hawor_2025.md) |
| MEgoHand | 2025 | Egocentric Hand-Object Motion Generation | 用 frozen VLM + monocular depth 形成高层语义条件，再用 DiT flow-matching motion decoder 生成 MANO hand-object interaction 轨迹，是 human hand data 路线的运动生成组件 | [megohand_2025.md](megohand_2025.md) |
| OpenMMEgo | 2025 | Egocentric LMM / Perception Component | 构建 OME10M 与 OMEBench，用 semantic-aware visual token compression 和 dual curriculum 提升第一人称视频理解，是 VLA 的 egocentric 感知语义组件而非动作策略 | [open_mm_ego_2025.md](open_mm_ego_2025.md) |
| Being-H Series | 2025-2026 | Human-centered VLA / Latent WAM | 从 H0 的人手视频 VLA 预训练，经 H0.5 的 35K+ 小时/30 具身/统一动作空间跨具身 VLA，到 H0.7 的 200K 小时 ego 视频 + 15K 小时机器人数据 latent world-action model | [being_h_series_2026.md](being_h_series_2026.md) |
| UniDex | 2026 | Human Data Pretraining + Dexterous Unified Action Space | 从 ego 人类视频 retarget 出 8 种灵巧手、50K+ 轨迹的 robot-centric 预训练数据，提出 82D Function-Actuator-Aligned Space 统一动作空间，并训练 3D flow VLA，在 5 个真实工具任务上达到 81% 平均 task progress | [unidex_2026.md](unidex_2026.md) |
| EgoVerse | 2026 | Ego Human Dataset / Co-training Infrastructure | 协作式 ego 人类数据平台，当前 release 含 1,362 小时、80K episodes、1,965 tasks、240 scenes、2,087 demonstrators；多实验室 co-training study 表明 human ego data 有效 scaling 需要少量 domain-aligned human-robot anchor data | [egoverse_verification_2026.md](egoverse_verification_2026.md) |
| EmbodieDreamer | 2025 | World Model as Data Engine / Real2Sim2Real | 用 PhysAligner 对齐仿真动力学、VisAligner 将低保真仿真渲染转为真实感视频，使 ACT/π0 可在生成的高保真仿真轨迹上做 RL/IL 增强，真机平均成功率较单纯真实数据微调提升约 29.17% | [embodiedreamer_2025.md](embodiedreamer_2025.md) |
| MimicDreamer | 2025 | Human Ego Demo → Robot VLA Supervision | 用 EgoStabilizer、IK 和 H2R Aligner 把低成本 egocentric 人类示范转成机器人视频与动作监督；20 条人类转机器人数据 + 20 条机器人数据使 π0 类策略平均成功率从 65.8% 提升到 85.0% | [mimicdreamer_2025.md](mimicdreamer_2025.md) |
| EgoDemoGen | 2025 | Egocentric Demonstration Generation | 同时迁移动作坐标系并生成新视角观测，通过 EgoTrajTransfer + EgoViewTransfer 生成配对 observation-action 数据，提高 novel-view manipulation 成功率 | [egodemogen_2025.md](egodemogen_2025.md) |
| GigaWorld-0 | 2025 | World Model as Data Engine | 将 world model 定位为 VLA 数据引擎：生成 appearance/view/mimic/action-semantics 可控视频，并通过 3D/IDM/planning 产出 paired video-action 数据，训练 GigaBrain-0 等 VLA 在无额外真实交互下提升泛化 | [gigaworld0_2025.md](gigaworld0_2025.md) |
| VLA-R1 | 2025 | VLA Reasoning / RLVR | 将 CoT 数据合成与 RLVR/GRPO 后训练引入 VLA，让模型先显式推理 affordance、几何关系和轨迹逻辑再输出动作，显著提升 affordance 和 trajectory 对齐 | [vla_r1_2025.md](vla_r1_2025.md) |
| SwiftVLA | 2025 | Lightweight VLA + 4D Geometry Distillation | 0.45B 轻量 VLA，通过冻结 4D visual geometry transformer + temporal cache、Fusion Tokens 和 mask-and-reconstruct，把 4D 时空几何蒸馏进小 VLM，推理时可移除 4D 分支，在 Jetson Orin 上保持低延迟 | [swiftvla_2025.md](swiftvla_2025.md) |
| GigaBrain-0 | 2025 | World Model-powered VLA / Embodied CoT | 用 GigaWorld 数据引擎通过 Real2Real、View Transfer、Sim2Real、人类视频转机器人、多视角视频生成和 IDM 合成数据扩展 VLA 训练；结合 RGB-D 输入和 Embodied CoT，在 G1/PiPER 真机任务上优于 π0 | [gigabrain0_2025.md](gigabrain0_2025.md) |
| GigaBrain-0.5M* | 2026 | VLA RL 后训练 / RAMP | 在 10K+ 小时预训练的 GigaBrain-0.5 上引入 RAMP，用世界模型预测未来状态和值作为策略条件，形成 HIL rollout → world model/policy 持续训练闭环，在 RoboChallenge 以 51.67% 平均 SR 排名第一 | [gigabrain05m_2026.md](gigabrain05m_2026.md) |
| GigaWorld-Policy | 2026 | Action-centered WAM | 训练时用未来视觉动态提供稠密监督，推理时关闭未来视频生成只解码动作；RoboTwin 2.0 达到 0.86 simulation SR、A100 延迟 360ms，真实 PiPER 4 任务平均 0.83 SR | [gigaworld_policy_2026.md](gigaworld_policy_2026.md) |
| π-StepNFT | 2026 | VLA RL 后训练 / Critic-free Flow RL | 面向 flow-based VLA 的 critic-free、likelihood-free 在线 RL，用 Flow-SDE 扩大探索空间，再用 step-wise contrastive ranking 对每个去噪小步做正/负分支排序，在 LIBERO few-shot 上大幅提升 π0/π0.5 | [pi_stepnft_2026.md](pi_stepnft_2026.md) |
| ViVa | 2026 | Video-generative Value Model / RL | 把预训练视频生成模型改造成价值函数，输入当前多视角图像和 proprioception，联合预测未来 proprioception 与当前 state value；接入 RECAP 后提升真机 Box Assembly 成功率和吞吐 | [viva_value_model_2026.md](viva_value_model_2026.md) |
| Figure Helix | 2025 | 官方技术页 / Humanoid VLA | Figure 闭源 humanoid VLA 技术发布：7B System 2 VLM 低频产生语义 latent，80M System 1 visuomotor transformer 200Hz 输出 35-DoF 上半身连续控制；证据主要是官方视频和内部 claim | [figure_helix_2025.md](figure_helix_2025.md) |
| Figure Helix Logistics | 2025 | 官方技术页 / Humanoid Logistics | 将 Helix 应用到物流包裹分拣/重定向，重点升级隐式 stereo、多尺度视觉、learned visual proprioception、自校准、数据筛选和 action chunk 重采样 Sport Mode | [figure_helix_logistics_2025.md](figure_helix_logistics_2025.md) |
| Figure Scaling Helix Logistics | 2025 | 官方技术页 / Data Scaling + Memory | Helix 物流路线 follow-up：示教数据从约 10 小时扩到 60 小时，并加入 vision memory、state history、force feedback 和更大 S1 decoder；仍属于内部物流评测而非公开 benchmark | [figure_scaling_helix_logistics_2025.md](figure_scaling_helix_logistics_2025.md) |
| Figure Project Go-Big | 2025 | 官方技术页 / Human Ego Pretraining | Figure 面向 humanoid 的人类 egocentric 视频预训练计划，报告 Helix 仅用人类第一视角视频训练即可 zero-shot 输出机器人 SE(2) 导航控制、执行 speech-to-nav，但缺少公开数据规模和 benchmark | [figure_project_go_big_2025.md](figure_project_go_big_2025.md) |
| Figure Helix 02 | 2026 | 官方技术页 / Full-body Humanoid VLA | 将 S1/S2 Helix 扩展到全身 loco-manipulation，新增 1kHz System 0 学习式全身控制器，S1 变为 all sensors in / all joints out 的 200Hz 全身 visuomotor policy；仍是官方视频 release | [figure_helix_02_2026.md](figure_helix_02_2026.md) |
| RoboDual | 2024 | 双系统 VLA / Generalist + Specialist | 用 OpenVLA 类慢速 generalist 提供语义和粗动作计划，小型 diffusion specialist 高频输出连续动作，改善泛化、精度和控制频率 | [robodual_2024.md](robodual_2024.md) |
| CLOVER | 2024 | 生成式视觉计划 + 闭环控制 | 视频 diffusion 生成 RGB-D 子目标，反馈策略用当前-目标 embedding error 做动作、子目标切换和 replanning，把 open-loop visual planning 改成闭环控制 | [clover_2024.md](clover_2024.md) |
| MPI | 2024 | 操作交互表征预训练 | 用 Ego4D hand-object interaction 学习预测交互过程帧和交互物体位置，获得更适合机器人 manipulation 的视觉表征 | [mpi_2024.md](mpi_2024.md) |

## 时间线
```
RT-2 (2023.07, VLM+Action Token, 首个VLA, 闭源)
  ↓
Diffusion Policy (2023, DDPM用于BC策略, 单任务奠基)
  → Octo (2024.01, 开源GRP, ViT+diffusion head)
    → OpenVLA (2024.06, 开源VLA, RT-2的开源替代, 7B超越55B)
      → RoboCopilot (2024.CoRL, 交互式模仿学习系统, HG-DAgger+双边遥操作)
      → π₀ (2024.10, VLM+Flow Head, 解决Action Token的精度/chunking局限)
        → π₀.5 (2025, 层次化+开放世界)
          → MEM (2025, +多尺度记忆, 视频编码器+语言记忆, 15分钟任务)
        → Being-H0.5 (2026, 人类中心+跨具身统一动作空间+30种具身, 开源)
        → Xiaomi-Robotics-0 (2026, 实时异步执行+Λ-shape mask, 消费级GPU部署, 开源)
        → RoboClaw (2026, 系统框架, VLM元控制器+EAP自重置+生命周期统一, 基于π₀.5)
        → Hi-ORS (2025.10, π₀ RL后训练, 拒绝采样替代Q函数, 1.5h真机)
        → Evo-0 (2025.07, π₀+VGGT空间增强, RLBench 56% vs 41%, 无深度传感器)
        → Evo-1 (2025.11, 0.77B轻量VLA, InternVL3-1B+Cross-only DiT, Meta-World 80.6% SOTA, 无预训练)
        → Evo-RL (2026.02, 离线ACP RL循环, 优势标签注入task text, 真机开源)

VLM + Flow Head + UMI数据Scaling:
RDT (2024, Transformer+Diffusion Head, 无VLM)
  → RDT2 (2025, +Qwen2.5-VL-7B, +10K小时UMI数据, +RVQ三阶段训练, "4U"零样本泛化)

冻结VLM + 分类动作解码 (Tripartite):
SaiVLA-0 (2026.03, 冻结VLM三元架构, Cerebrum+Pons+ParaCAT, {-1,0,+1}分类动作, LIBERO 99.0%)

数据收集/交互式学习方法线:
DAgger (2010, RC Sampling, 随机切换控制权)
  → HG-DAgger (2019.ICRA, 人类门控+doubt阈值学习, 解决actuator lag)
被动遥操作 (ALOHA/GELLO式, offline)
  → RoboCopilot (2024.CoRL, 力反馈双边遥操作+HG-DAgger, 无缝人机切换)
  → HACTS (2025, 位置同步双边遥操作, <$300, IL+RL双范式支持)
  → GCENT/Genie Centurion (2025, 倒带机制+Task Sentinel, 单人监控多机器人, AgiBot)
  → RaC (2025.09.CMU, 两条规则标准化recovery+correction配对, 10x数据效率, test-time scaling)
  → RoboClaw EAP (2026, 正-逆动作对自重置, 全生命周期统一)
  → Hi-ORS (2025, 人类干预 error recovery, rejection sampling 过滤, RL后训练)

VLA RL 后训练方法线:
SERL (2024, 无VLA, Q-function RL)
  → HIL-SERL (2024, +人类干预, Q-function+HITL, 高维action chunking不稳定)
  → Q-Chunking (2025, +distillation loss稳定RL, 主要仿真)
  → PA-RL (2024, +监督目标稳定在线训练, 仍需精确值估计)
  → Hi-ORS (2025, 拒绝采样完全value-free, +reward-weighted flow supervision, +HITL, 真机1.5h)
  → RLT (2025, PI, RL Token紧凑表征+冻结VLA+轻量actor-critic+chunk-level RL, 数小时真机, 超人类速度)

World Action Model (WAM) 方法线:
GR-1 (2024, 视频预训练→动作微调, 开创范式)
  → GR-2 (2024, 互联网规模视频预训练)
  → Cosmos Policy (2025, latent frame injection, 2B, 单平台微调+规划)
  → DreamZero (2026, 14B, 自回归chunk-wise, 零样本泛化, 跨具身迁移)
```

## 方法线演进
```
VLM + Flow Head 方法线:
π₀ (2024, 奠基: VLM + flow matching action expert)
├── π₀.5 (2025, +层次化推理, +异构co-training, +开放世界)
│   ├── MEM/π₀.6-MEM (2025, +多尺度记忆: 视频编码器短时+语言摘要长时, 15分钟任务)
│   └── RoboClaw (2026, 系统框架, 用π₀.5作底层VLA, +VLM元控制器+EAP+过程监督)
├── Being-H0 (2025, +人手运动tokenizer, +UniHand-1.0)
│   └── Being-H0.5 (2026, +UniHand-2.0 35K小时, +统一动作空间, +MoF, +MPG/UAC, +30种具身)
├── Xiaomi-Robotics-0 (2026, +Λ-shape mask异步执行, +VL co-training保留VLM能力, +消费级GPU部署)
└── GR00T-N1 (NVIDIA, +world model)

VLA 记忆方法线:
密集帧历史 (Octo, BET, 数秒)
  → 压缩记忆: Pool Memory (ContextVLA), Proprio Memory (TA-VLA), Keyframe (BPP, MeMeR), Point Tracks (TraceVLA)
  → 潜在记忆: Sam2Act, MemoryVLA
  → 语言记忆: OneTwoVLA
  → 多尺度混合模态记忆: MEM (2025, 视频+语言, 15分钟, 上下文适应)

World Action Model (WAM) 方法线:
视频预训练→动作微调:
  GR-1 (2024, 开创者) → GR-2 (2024, 互联网规模)
联合去噪范式:
  UWM (2025, 解耦timestep, 灵活推理) 
  → Cosmos Policy (2025, latent frame injection, 2B, 单平台微调+规划)
  → DreamZero (2026, 14B, 自回归chunk-wise, 零样本泛化2x+, 跨具身, 7Hz实时)

异步执行技术演进:
RTC (Black et al. 2025, 推理时inpainting, training-free)
  → Training RTC (Black et al. 2025, 训练时action prefix conditioning)
    → Xiaomi-Robotics-0 (2026, +Λ-shape attention mask解决shortcut)
  → Being-H0.5 UAC (2026, 随机延迟采样+双线程异步)
  → DreamZero (2026, 异步执行+KV cache替换消除累积误差)

系统框架支线（VLM-as-Controller + VLA-as-Executor）:
SayCan (2022, LLM规划+affordance grounding)
  → Inner Monologue (2022, +运行时反馈+重规划)
    → RoboClaw (2026, +全生命周期统一+EAP自重置+MCP工具接口+运行时过程监督)

交互式数据收集支线:
被动BC (ALOHA/GELLO式遥操作, offline data collection)
  → RoboCopilot (2024, CoRL, 力反馈双边遥操作+HG-DAgger, 人在回路修正数据)
  → HACTS (2025, 位置同步双边遥操作, <$300, IL+RL双范式, concurrent with RoboCopilot)
  → GCENT/Genie Centurion (2025, 倒带机制+Task Sentinel自动监控, 1:N多机器人, AgiBot)
  → RaC (2025.09.CMU, 两条规则recovery+correction显式配对, 10x数据效率, test-time scaling, VG-gap理论)
  → RoboClaw EAP (2026, 正-逆动作对自重置, 减少人力介入)
  → MEM 上下文适应 (2025, 策略从失败→修正数据中在线学习)
```
