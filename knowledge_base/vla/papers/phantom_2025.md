# Phantom: Training Robots Without Robots Using Only Human Videos (2025)

## 基本信息
- 作者: Marion Lepert, Jiaying Fang, Jeannette Bohg
- 机构: Stanford University
- arXiv: 2503.00779
- 时间: 2025.03

## 一句话总结
通过将 robot-to-robot 的 data-editing 技术（inpainting + 虚拟机器人叠加）适配到 human-to-robot 场景，结合手部姿态估计提取动作标签，首次实现仅用人类视频（无需任何机器人数据）训练闭环模仿学习策略并 zero-shot 部署到真实机器人。

## 问题
解决什么问题：
- 机器人数据收集昂贵、慢、场景多样性不足
- 现有利用人类视频的方法仍依赖 robot data co-training 或 RL 来弥合 embodiment gap
- 如何仅用人类视频（完全不需要机器人数据和硬件）训练可直接部署的闭环机器人策略？

## 方法
- **方法线归属**: 人手数据 → 机器人 Policy（流派C：人类视频预训练/表征学习→迁移到机器人），但更准确地说是一种**跨具身 data-editing 方法**，从 RoviAug/Shadow 的 robot-to-robot 设定拓展到 human-to-robot 设定
- **核心 idea**: 用 data-editing（inpainting 去除人手 + 渲染虚拟机器人叠加）消除人与机器人的视觉外观差异，用手部姿态估计器从 RGBD 视频中提取动作标签，将人类视频转化为"机器人"演示数据，直接训练 Diffusion Policy 并 zero-shot 部署
- **关键技术点**:
  - **动作提取**: HaMeR 手部姿态估计 → SAM2 手部分割 → 深度数据 ICP 对齐修正绝对3D位姿 → 从拇指/食指关键点推导末端执行器位姿(位置、朝向、夹爪开合)
  - **训练时 data-editing**: SAM2 分割人手 → E2FGVI 视频 inpainting 去除人手 → MuJoCo 渲染虚拟机器人叠加到对应位姿 → 利用深度信息处理遮挡
  - **推理时 data-editing**: 在真实机器人图像上叠加虚拟机器人渲染，确保训练/测试图像分布一致
  - **Hand joint 约束**: 限制拇指和食指末两个关节为单自由度，解决 HaMeR 在遮挡下的不合理预测
  - **相机外参增强**: 训练时随机扰动虚拟机器人基座位置，消除对部署相机外参先验知识的依赖
- **策略网络**: Diffusion Policy (DDIM, 100 train steps, 10 inference steps)
- **数据收集**: 人类用拇指-食指 pinch grasp 在 RGBD 相机前演示，250-950 demos/任务

## 实验
- **Benchmark**: 真机评测，6 个任务（Pick&Place Book, Stack Cups, Sweep Trash, Tie Rope, Rotate Box, Kinova Sweep），在 Franka 和 Kinova 两种机器人上
- **主要结果**:
  - **In-distribution**: Hand Inpaint 在4个任务上成功率 64%-92%（Pick/Place Book 92%, Stack Cups 72%, Tie Rope 64%, Rotate Box 72%）
  - **OOD 场景泛化**: 950 demos 训练后在3个未见场景成功率 64%-84%（Indoor Lounge 84%, Outdoor Lawn 72%, OOD Surface 64%）
  - **与遥操作对比**: 50 human demos (44%) vs 50 teleop demos (52%)，300 human demos (84%) ≈ 100 teleop demos (88%)
  - **Co-training 增益**: 100 teleop demos in-distribution 88% 但 OOD 0% → + 950 human demos → OOD 80%
- **对比基线（data-editing 策略）**:
  - **Hand Inpaint** (adapted from RoviAug): ✅ 最佳表现
  - **Hand Mask** (adapted from Shadow): 接近 Hand Inpaint 但推理慢 73%
  - **Red Line** (adapted from EgoMimic): 所有任务 0% 成功率
  - **Vanilla** (无编辑): 所有任务 0% 成功率
- **Inpainting 质量消融**: E2FGVI (84%) > OpenCV inpaint (76%) > Mask only (60%) > Red Line (0%)
- **相机外参增强**: 未知外参 (96%) ≈ 已知外参 (92%)

## 评价
### 优势
- **完全消除机器人硬件依赖**: 任何人只需一个 RGBD 相机即可收集数据，极大降低数据收集门槛
- **机器人无关**: 同一份人类数据可渲染任意目标机器人，适配多种平台
- **闭环 + 不依赖物体检测**: 相比 ORION、Im2Flow2Act 等方法更通用，适用于刚性/柔性/多物体
- **方法简洁有效**: 将已验证的 robot-to-robot data-editing 技术自然拓展到 human-to-robot，无需复杂的中间表征或强化学习
- **OOD 泛化**: 在未见场景（包括户外动态背景）中展示了可用的零样本迁移

### 局限
- **精度低于遥操作**: 手部姿态估计引入噪声，单条 demo 信息量不如遥操作数据，需要更多 demos 补偿
- **仅限 pinch grasp**: 受平行夹爪限制，无法展示更丰富的抓取策略
- **仅准静态任务**: 未解决人类演示与机器人执行之间的延迟/速度不匹配问题
- **相机约束**: 训练和部署时相机的高度和角度需大致一致
- **依赖手部姿态估计器质量**: 遮挡下性能受限，但会随 SOTA 手部估计器进步而改善

### 对 VLA 领域的贡献
- **定位**: 这是一篇"数据收集方法"论文，而非"模型架构"论文。核心贡献在于证明了一条极低成本的数据收集路径：**仅用人类视频 + 简单 data-editing 就能训练可部署的机器人策略**
- **与调研报告中的流派关系**: 属于流派C（人类视频→机器人Policy迁移），但独特之处在于完全不需要机器人数据，是该方向少有的"zero robot data"工作
- **与 EgoMimic 的区别**: EgoMimic 使用 ego 视角 + Red Line data-editing + 需要 robot co-training；Phantom 使用第三人称视角 + Inpainting data-editing + 完全不需要 robot data。实验证明 Red Line 策略在 human-to-robot 场景下完全失败
- **与 RoviAug/Shadow 的关系**: 直接将这两个 robot-to-robot data-editing 方法拓展到更难的 human-to-robot 场景，证明了 inpainting+overlay 策略在跨具身差距更大时仍然有效
- **与 UMI/DOBB-E 的区别**: UMI/DOBB-E 需要携带专用夹爪硬件采集数据；Phantom 只需 RGBD 相机和自己的手
- **规模化价值**: 生成的 observation-action 对可直接集成到 OXE 等大规模数据集中训练 generalist policy（如 π₀），这是比 flow-based 或 object-centric 方法更大的潜在优势
- **精度-规模 tradeoff**: 明确揭示了"用数量弥补精度"的可行性——300 human demos ≈ 100 teleop demos

## 关键方法对比表（论文 Table I）

| 方法 | 无需机器人数据 | 柔性物体 | 闭环 |
|------|:---:|:---:|:---:|
| WHIRL | ✗ | ✓ | ✓ |
| MimicPlay | ✗ | ✓ | ✓ |
| ORION | ✓ | ✗ | ✓ |
| Im2Flow2Act | ✗* | ✓ | ✓ |
| R+x | ✓ | ✓ | ✗ |
| **Phantom (Ours)** | **✓** | **✓** | **✓** |

*Phantom 是唯一同时满足三个条件的方法*
