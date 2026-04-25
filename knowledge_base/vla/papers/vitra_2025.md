# VITRA: Scalable Vision-Language-Action Model Pretraining for Robotic Manipulation with Real-Life Human Activity Videos (2025)

## 基本信息
- 作者: Qixiu Li*, Yu Deng*, Yaobo Liang*, Lin Luo*, Lei Zhou, Chengtang Yao, Lingqi Zeng, Zhiyuan Feng, Huizhi Liang, Sicheng Xu, Yizhong Zhang, Xi Chen, Hao Chen, Lily Sun, Dong Chen, Jiaolong Yang, Baining Guo
- 机构: Tsinghua University, Microsoft Research Asia
- arXiv: 2510.21571
- 项目: https://microsoft.github.io/VITRA/

## 一句话总结
VITRA 将无标注、无脚本的真实人类第一视角活动视频自动转成与机器人示范同格式的 V-L-A episode，用 1M atomic hand-action episodes 预训练 PaliGemma-2 + diffusion action expert，在少量真实灵巧手机器人数据微调后显著提升 seen/unseen 物体和背景泛化。

## 问题
机器人 VLA 预训练受限于遥操作数据成本，尤其是多指灵巧手数据几乎没有可规模化语料。人类日常活动视频虽然量大、多样，但原始视频存在三类不对齐：
- 时间粒度不对齐：长视频未切成机器人数据常用的短时 atomic manipulation episode
- 标签不对齐：缺少语言指令、3D hand motion、camera motion 和帧级动作标签
- 采集条件不对齐：来自单目、未标定、移动相机，且活动无脚本、环境噪声大

核心问题是：能否把无标注 real-life human activity videos 自动转成与机器人 V-L-A 数据等价的预训练数据，而不是只把人类视频用于表征、affordance 或 latent action proxy？

## 方法
- 方法线归属: Human Data Pretraining for VLA / VLM + Diffusion Head / 野外无标注 egocentric 视频自动 V-L-A 化
- 核心 idea: 把人手当作灵巧机器人末端执行器，用 3D 重建 + 速度极小值切分 + 轨迹可视化 captioning，把原始人类视频转成 "language instruction + observation frames + camera-frame 3D hand action chunk" 数据，再用显式 3D 动作监督预训练灵巧手 VLA。
- 关键技术点:
  - **全自动 human activity analysis pipeline**:
    - 相机/手部 3D 运动标注：DroidCalib/MoGe-2/DeepCalib 估计相机参数，HaWoR 重建 camera-space MANO hand，MegaSAM + MoGe-2 追踪 metric-scale camera pose，再合成 world-space hand motion
    - atomic action segmentation：用 world-space wrist speed minima 作为切点，左右手独立切分，避免 fixed-interval clip 把多个动作混在一起
    - instruction labeling：每段采样 8 帧，叠加从当前帧到 clip 末尾的 3D palm trajectory，交给 GPT-4.1 输出 imperative action description 或 N/A
  - **Hand V-L-A Dataset**:
    - 来源: Ego4D、EPIC-KITCHENS、EgoExo4D、Something-Something-V2 原始视频
    - 规模: 约 1M episodes / 26M frames，其中 Ego4D 77%、EPIC-KITCHENS 12%、EgoExo4D 6%、SSV2 5%
    - 不使用原数据集人工动作标注；论文显示原标注的时间边界/粒度不适合 VLA 预训练
  - **模型架构**:
    - VLM: PaliGemma-2 3B，SigLIP vision encoder 冻结，加入 camera FoV token 和 learnable cognition token
    - Action expert: DiT-Base diffusion head，用 cognition feature、当前 hand/robot state、noisy action chunk 和 action mask 做迭代去噪
    - action space: 双手 102D，包含左右手 wrist relative translation/rotation + 15 个 MANO joints 的 Euler angles
  - **统一单双手动作预测**: 指令固定为 `Left hand: ... Right hand: ...`，对缺失手的动作维度用 action mask 排除 loss
  - **Causal action denoising**: action token 只 attend 到前序动作，避免短 atomic clip 末尾 zero padding 污染前面动作预测
  - **Trajectory-aware augmentation**: 对图像做 crop/perspective warp/FoV 变化，并同步变换 3D action，保证投影手部轨迹仍在裁剪画面内
  - **机器人微调对齐**: 将 Realman + XHand 的 EEF 6D pose 和 12-DoF hand joints 映射到人手 102D superset action space，未映射维度用 mask；手关节监督使用未来执行命令而不是由机器人状态差分得到的标签

## 实验

### Human Hand Action Prediction
- Benchmark:
  - Grasping: 47 个未见环境、396 个对象，Azure Kinect RGB-D 图像 + synthetic hands，指标为 predicted finger trajectory 到目标 object point cloud 的最小距离
  - General Action: 117 个手机拍摄未见真实环境，23 名用户对 rendered hand actions 做 top-3 ranking，得到 user score
- 主要结果:
  - Grasp median distance: Ours 6.2 cm，优于 bidirectional attention 7.2、no augmentation 10.7、human annotation 14.1、EgoDex lab data 18.3、Being-H0 18.4
  - General action user score: Ours 1.91，优于 bidirectional attention 1.69、no augmentation 1.43、human annotation 0.96、Being-H0 0.15
  - episode construction 消融: wrist-speed segmentation + trajectory overlay 优于 fixed interval segmentation 和 no trajectory overlay
  - 数据 scaling: 1%/10%/20%/50%/100% 子集上 grasp performance 随数据规模近似 log-linear 改善；EgoDex episode/frame 数更多但 diversity 低，泛化不如 VITRA 子集

### Real-World Robot Dexterous Manipulation
- 平台: Realman 机械臂 + 12-DoF XHand 灵巧手 + RealSense head camera
- 数据: 4 类任务共 1.2K teleoperated trajectories
- 任务:
  - General pick & place: 物体放入盒子，带随机 distractors
  - Functional grasping: 在功能部位抓取，例如手柄
  - Pouring: 拿瓶、倾倒、放回
  - Sweeping: 拿扫帚、扫垃圾进簸箕、放回
- 主要结果:
  - Seen objects/background average success: Ours 71.0%，高于 π0 46.9%、latent action pretrain 46.0%、OXE pretrain 41.3%、no VLA pretrain 32.1%、VPP 24.8%
  - Unseen objects/categories/background average success: Ours 64.6%，高于 π0 16.1%、no VLA pretrain 10.9%、OXE pretrain 7.8%、VPP 5.2%、latent action pretrain 0.0%
  - unseen category pick-place: Ours 70.8%，π0 33.3%，OXE/no pretrain 12.5%
  - pretraining hand-action prediction accuracy 与 robot pick-place success 明显正相关，说明 human-hand prediction benchmark 可作为下游机器人性能 proxy

### 对比基线
- VPP: diffusion video generation pretraining for dexterous manipulation
- π0: 大规模机器人数据预训练 VLA
- No VLA pretrain: PaliGemma-2 + 随机 action expert 直接微调
- OXE pretrain: 用 Open X-Embodiment 替代 human VLA data
- EgoDex / Lab data: 实验室人手数据
- Latent action pretrain: 同 episode/instruction，但用 LAPA latent action 替代显式 3D action labels

## 评价
- 优势:
  - 数据构造范式清晰：首次系统展示无脚本、无标注、单目真实人类活动视频可以自动转成机器人 VLA 同构数据
  - 显式 3D action supervision 比 latent action 更适合跨场景迁移；latent action 在 unseen robot setting 中直接 0%
  - 数据 diversity 贡献明确：与 EgoDex 相比，VITRA 不是靠更精密采集，而是靠开放环境/对象/动作覆盖提升泛化
  - 工程成本相对低：预训练 80K steps 约 2 天、8 H100，低于 EgoScale 256 GB200 的工业级规模
  - 给出了可用的 proxy benchmark：human-hand action prediction 与 robot success 的相关性便于快速筛选预训练配方
- 局限:
  - 自动标注仍受 3D reconstruction、SLAM、hand reconstruction 和 GPT caption 误差影响，论文未完全量化噪声传播
  - 主要聚焦短时 atomic manipulation，长时任务结构、规划和跨 clip temporal consistency 仍是 future work
  - 真实机器人实验以单手桌面灵巧操作为主，双手协同只做了简单 hand-over 展示
  - 机器人微调仍需要 1.2K teleop trajectories，不能直接 robot-free zero-shot 部署
  - action-space mapping 采用拓扑最近关节映射，简单有效但不如 FAAS/统一物理语义空间那样系统
- 对 VLA 领域的贡献:
  - 把 Human Data Pretraining 的数据源从有脚本/有设备追踪的 ego/lab captures 推向无脚本 real-life videos，补上了 "互联网式人类视频如何变成 VLA 数据" 这一环
  - 与 EgoScale 互补：VITRA 强调自动数据构造和无标注野外视频可用性，EgoScale 强调 20K 小时 scaling law 与对齐 mid-training
  - 与 JALA 互补：VITRA 选择显式 3D hand action labels，JALA 选择 predictive embedding/latent action alignment；VITRA 的 unseen robot 结果对 latent action 的背景纠缠风险给出强证据
  - 与 π0/OXE 路线对比表明，面向灵巧手的 human-hand data 比以 gripper 为主的机器人数据更能提供有效 motor prior
