# DexCap: Scalable and Portable Mocap Data Collection System for Dexterous Manipulation (2024)

## 基本信息
- 作者: Chen Wang, Haochen Shi, Weizhuo Wang, Ruohan Zhang, Li Fei-Fei, C. Karen Liu
- 机构: Stanford University
- arXiv: 2403.07788
- 发表: RSS 2024 (Robotics: Science and Systems)
- 项目页: https://dex-cap.github.io

## 一句话总结
提出便携式人手动捕系统 DexCap（EMF 手套 + SLAM 腕部追踪 + 胸部 RGB-D）和配套模仿学习算法 DexIL（fingertip IK retargeting + point cloud diffusion policy + human-in-the-loop correction），首次实现从野外人手动捕数据直接训练灵巧机器人策略，无需任何机器人遥操作数据。

## 问题
1. **数据采集瓶颈**：灵巧操作的遥操作数据采集昂贵（需要真实机器人且速度慢），而视觉手部追踪存在遮挡问题且缺乏精确 3D 信息
2. **便携性不足**：现有 mocap 系统多依赖标定好的第三视角相机，不便携；EMF 手套可追踪手指但缺乏 6-DoF 腕部位姿；IMU 容易漂移
3. **具身差异（Embodiment Gap）**：人手与机器人手在尺寸、比例、运动学结构上存在显著差异，如何将人手动捕数据转化为有效的机器人策略是核心算法挑战
4. **野外数据利用**：如何利用在实验室外采集的、相机随人体运动的数据训练鲁棒的机器人策略

## 方法

### 方法线归属
- **数据采集系统**: 属于"流派 B: 手部动作重定向（Retargeting）→ 机器人控制"（参考知识库 human_hand_data_robot_policy_survey）
- **学习算法**: 基于 Diffusion Policy（参考知识库 methods/diffusion_policy.md），扩展为 point cloud 输入 + Perceiver 编码器

### 核心 idea
设计一套完全便携、抗遮挡的人手动捕硬件（DexCap），配合 fingertip IK retargeting + point cloud diffusion policy 的算法（DexIL），使人类可以直接用手操作物体来采集数据，无需机器人硬件，数据经 retarget 后直接训练灵巧操作策略。

### 关键技术点

#### DexCap 硬件系统
- **手指追踪**: Rokoko EMF 动捕手套，磁传感器追踪指尖 3D 位置，抗视觉遮挡
- **腕部 6-DoF 追踪**: Intel RealSense T265 SLAM 相机安装在手套背面，结合鱼眼相机 + IMU 通过 SLAM 算法追踪腕部位姿，解决 IMU 漂移问题
- **3D 环境观测**: 胸部 Intel RealSense L515 RGB-D LiDAR 相机记录环境
- **快速标定**: 3D 打印相机架，T265 先在胸部架子上标定相对位姿，再移到手套上，标定仅需 ~10 秒
- **便携性**: Intel NUC 迷你 PC + 40000mAh 移动电源装在背包中（总重 3.96 磅），支持约 40 分钟连续采集
- **成本**: < $4,000 USD

#### DexIL 学习算法
1. **Action Retargeting**: 
   - 基于 fingertip position matching 的 IK（关键洞察：指尖是手与物体交互最频繁的区域）
   - 将人手 5 指映射到 LEAP Hand 4 指（舍弃小指）
   - 6-DoF 腕部位姿用于初始化 IK
   - 动作空间：双臂 7-DoF × 2 + 灵巧手 16-DoF × 2 = 46 维

2. **Observation Post-processing**:
   - RGB-D → point cloud，转换到统一世界坐标系（消除人体运动导致的相机晃动）
   - 过滤无关点（如桌面），将点云对齐到机器人操作空间
   - 通过 forward kinematics 将机器人手模型点云合并到观测中（弥补人手-机器人手外观差异）

3. **Point Cloud-based Diffusion Policy**:
   - 编码器: Perceiver（优于 PointNet，尤其在双手多物体任务上 +20%）
   - 解码器: Diffusion Policy（DDPM），输出 d 步动作轨迹
   - 输入: K 个下采样点 × 6（xyz + rgb）
   - 数据增强: 随机 2D 平移

4. **Human-in-the-loop Correction（可选）**:
   - 两种模式：残差校正（delta 叠加到策略动作上）和遥操作（直接控制）
   - 脚踏板切换模式
   - 校正数据与原始数据等概率采样进行策略微调（类似 IWR）
   - 通常只需少量校正（30 次）即可显著提升性能

## 实验
- **Hardware**: 双 Franka Emika 机械臂 + 双 LEAP Hand（4 指 16 关节）
- **Tasks（6个）**: 
  - 简单: Sponge picking, Ball collecting（单手抓取）
  - 中等: Plate wiping（双手协调）
  - 复杂: Packaging（双手 + 泛化到新物体）
  - 极难: Scissor cutting（工具使用）, Tea preparing（长时序多步）
- **数据量**: 30 分钟 DexCap 数据（简单任务），1 小时（复杂任务）

### 主要结果
| 设置 | 成功率 |
|------|--------|
| DexCap 数据直接训练（3 个简单任务） | **72%** 平均 |
| In-the-wild 数据训练 Packaging | **47%** 全任务, **40%** 未见物体 |
| + 30 次 human correction → Packaging | **57%** 全任务 |
| Scissor cutting（+ correction） | **20%** 全任务 |
| Tea preparing（+ correction） | **25%** 全任务 |

### 关键消融发现
- **Image vs Point Cloud**: 图像输入因人手-机器人外观差异完全失败（0%）；加遮罩后可用但丢失细节；point cloud 最佳
- **Diffusion Policy vs BC-RNN**: DP 比 BC-RNN 高 25%+，验证生成式策略对高维灵巧动作的优势
- **Perceiver vs PointNet**: Perceiver 在双手多物体任务上优 20%
- **Wild 数据 + Image**: 因相机移动，image-based 方法接近 0%；point cloud 转世界坐标系后稳定工作
- **数据采集速度**: DexCap 采集速度是遥操作的 3 倍，接近自然人手操作速度

### 对比基线
BC-RNN, BC-RNN-img-mask, BC-RNN-point, DP-img, DP-img-mask, DP-point-raw, DP-point, DP-perc（各种 encoder/input 组合）

## 评价

### 优势
1. **开创性的端到端方案**: 首次提出从便携式人手动捕数据到灵巧机器人策略的完整 pipeline，无需机器人遥操作数据
2. **工程完成度高**: 硬件设计模块化、低成本（<$4K）、便携（<4 磅）、快速标定（<10s），具有很好的可复制性
3. **Point cloud 的关键洞察**: 将 RGB-D 转为世界坐标系点云，同时解决了移动相机和人-机外观差异两个问题
4. **Human-in-the-loop correction 实用**: 仅 30 次校正就能显著提升复杂任务性能，减少了完全重新采集的成本
5. **任务难度高**: 展示了剪纸、泡茶等极具挑战的双手灵巧操作任务

### 局限
1. **电池续航仅 40 分钟**: 限制了大规模数据采集
2. **Fingertip IK retargeting 有限**: 只匹配指尖位置，忽略了手指力量/接触面积等差异（如握剪刀时手指需深入手柄）
3. **缺乏力感知**: 纯运动学数据，无触觉/力信息，导致某些需要力控制的任务（如按住盒子）表现不佳
4. **绝对成功率仍有提升空间**: 最复杂任务只有 20-25% 成功率
5. **依赖已停产硬件**: Intel RealSense T265 已停产，需要替代方案
6. **Retargeting 的泛化性**: Fingertip IK 对手指粗细差异大的机器人手（如弹钢琴场景）适用性有限

### 对 VLA 领域的贡献
- **数据采集范式**: 与 UMI（平行夹爪的便携采集）互补，DexCap 专注于灵巧手的便携数据采集，共同开创了"无机器人数据采集"的新方向
- **Point cloud policy 的早期验证**: 证明 point cloud 输入 + diffusion policy 是灵巧操作学习的有效方案，为后续 DexPoint、DexWild 等工作奠定基础
- **被广泛引用**: 226 citations（截至调研时），被 EgoScale、DexUMI、ManipTrans 等后续重要工作引用
- **启发后续发展**: DexWild（2025）、DexUMI（2025）等可视为 DexCap 思路的演进版本，用更轻量化的硬件或更好的 retargeting 方法

## 与知识库中其他论文的关系

### 与 Diffusion Policy (2023) 的关系
- **继承**: 使用 Diffusion Policy 作为 action decoder，继承了条件去噪 + action chunking 的核心设计
- **扩展**: 将输入从 image 扩展到 point cloud，将 action space 从简单夹爪扩展到 46 维灵巧手
- **验证**: 进一步验证了 diffusion policy 在高维动作空间（46-dim bimanual dexterous）的优势

### 与 UMI (Chi et al. 2024) 的关系
- **互补**: UMI 面向平行夹爪的便携数据采集，DexCap 面向灵巧手
- **共同贡献**: 同时期共同推动了"无机器人便携数据采集"的范式
- **技术差异**: UMI 用手持夹爪工具 + SLAM；DexCap 用 EMF 手套 + SLAM

### 在人手数据 → 机器人策略领域的定位
- 属于"流派 B: Retargeting"的代表工作
- 与后续的 EgoScale（流派 A，scaling ego 视频）和 Emergence of H2R（流派 C，co-training 涌现）形成技术路线对比
- DexCap 提供精确但规模有限的 mocap 数据，后续趋势转向更大规模但精度可能较低的 ego 视频数据
