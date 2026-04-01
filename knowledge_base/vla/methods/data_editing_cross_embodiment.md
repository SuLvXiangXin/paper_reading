# 跨具身 Data-Editing 方法

## 核心思想
通过**编辑观测图像**来消除不同具身形态（embodiment）之间的视觉外观差异，使 vision-based imitation learning policy 可以跨具身迁移，而无需修改策略网络架构。

这是一条**正交于策略网络架构**的方法线——它可以与 Diffusion Policy、ACT、或任意 VLA 模型组合使用。

## 问题定义
给定源具身形态（source embodiment）的演示数据，训练一个策略部署到目标具身形态（target embodiment）上。
- **Robot-to-Robot**: 在 Robot A 上收集数据 → 部署到 Robot B
- **Human-to-Robot**: 用人类手部演示 → 部署到机器人

核心挑战：不同具身形态在图像中的外观差异导致视觉策略的 distribution shift。

## 三类主要策略

### 1. Inpainting + Virtual Overlay（代表: RoviAug, Phantom）
- **训练时**: 分割并 inpaint 掉源具身形态 → 渲染目标具身形态虚拟模型叠加
- **测试时**: 在目标具身形态真实图像上叠加虚拟渲染（对齐训练分布）
- **效果**: 最佳（Phantom 实验验证 92% Pick&Place, 84% OOD sweep）
- **优点**: 生成最真实的图像，背景完整恢复
- **缺点**: 依赖高质量 inpainting 模型（但实验表明低质量 inpainting 也可接受）

### 2. Mask + Virtual Overlay（代表: Shadow）
- **训练时**: 黑色遮罩覆盖源具身形态 → 叠加目标具身形态渲染
- **测试时**: 叠加源具身形态的黑色遮罩 + 目标具身形态渲染
- **效果**: 与 Inpainting 方案接近，但推理慢 73%（需额外 diffusion model 生成 hand mask）
- **优点**: 无需 inpainting 模型
- **缺点**: 黑色遮罩残留在图像中，测试时需匹配源具身形态的遮罩

### 3. Abstract Representation Overlay（代表: EgoMimic 的 Red Line）
- **训练时**: 遮罩源具身形态 → 用抽象表征（红线）替代
- **测试时**: 遮罩目标具身形态 → 同样用红线替代
- **效果**: 在 human-to-robot 场景下完全失败（0% 成功率），可能因为抽象表征丢失了太多空间信息
- **注意**: EgoMimic 原始论文中 Red Line 配合 robot co-training 可以工作，但单独使用（无 robot data）则不行

## 关键实验发现（来自 Phantom, 2025）

### Data-editing 策略对比
| 策略 | Pick/Place | Stack Cups | Tie Rope | Rotate Box |
|------|:---:|:---:|:---:|:---:|
| Inpainting + Overlay | 0.92 | 0.72 | 0.64 | 0.72 |
| Mask + Overlay | 0.92 | 0.52 | 0.60 | 0.76 |
| Red Line | 0.0 | 0.0 | 0.0 | 0.0 |
| Vanilla (无编辑) | 0.0 | 0.0 | 0.0 | 0.0 |

### Inpainting 质量的影响
| 方法 | 成功率 |
|------|:---:|
| E2FGVI (高质量视频 inpainting) | 84% |
| OpenCV inpaint (低质量) | 76% |
| Mask only (无 inpainting) | 60% |

**关键洞察**: 虚拟机器人叠加（overlay）是必需的；inpainting 质量有帮助但非决定性因素。

## 代表工作

| 工作 | 年份 | 迁移方向 | 核心策略 | 需要 robot data? |
|------|------|----------|----------|:---:|
| **RoviAug** | 2024 | Robot → Robot | Inpainting + Virtual Overlay | ✗ |
| **Shadow** | 2024 | Robot → Robot | Mask + Virtual Overlay | ✗ |
| **AR2-D2** | 2023 | Human → Robot | Inpainting + Virtual Overlay | ✓ (co-training) |
| **EgoMimic** | 2024 | Human → Robot | Red Line + Ego 视角 | ✓ (co-training) |
| **Phantom** | 2025 | Human → Robot | Inpainting + Virtual Overlay | **✗ (零 robot data)** |

## Phantom 的独特定位
Phantom 是第一个证明 **Inpainting + Virtual Overlay data-editing 策略足以在无任何机器人数据的情况下实现 human-to-robot 闭环策略迁移** 的工作。之前的 human-to-robot 方法（AR2-D2, EgoMimic）都需要 robot data co-training 来弥合 embodiment gap。

## 与其他跨具身方法的关系
- **Co-training 路线**（EgoScale, Being-H0/H0.5, Emergence of H2R）: 通过大规模数据 + 架构设计实现跨具身迁移，需要 robot data
- **Retargeting 路线**（DexUMI, DexCap）: 通过运动学映射实现迁移，需要 embodiment-specific 映射
- **Data-editing 路线**: 通过编辑图像消除视觉差异，方法最简洁，Phantom 证明可完全不需要 robot data

## 技术依赖
- 手部姿态估计: HaMeR (Phantom)
- 分割: SAM2
- 视频 Inpainting: E2FGVI
- 虚拟渲染: MuJoCo
- 策略网络: 任意 IL 方法（Phantom 使用 Diffusion Policy）
