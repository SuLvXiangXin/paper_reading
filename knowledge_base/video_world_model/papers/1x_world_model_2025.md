# 1X World Model (1XWM)

> **1X World Model: Evaluating Bits, not Atoms**
> 1X World Model Team (Daniel Ho, Jack Monas, Juntao Ren, Christina Yu)
> 技术报告, 2025 | [PDF](https://www.1x.tech/1x-world-model.pdf)

## 一句话总结
首个面向全身人形机器人的视频世界模型，通过预测未来视频+state value实现策略离线评估，与真机评测高度相关，可替代昂贵的真实世界评估完成checkpoint选择和架构对比。

## 方法线归属
**机器人策略评估型世界模型** — 不同于追求视频质量的生成模型，1XWM核心目标是准确预测动作后果+评估成功/失败，用于policy evaluation。

## 核心方法

### 架构
- **编码器**: 时序图像编码器（初始帧→latent）+ 动作编码器（低层动作序列→latent）
- **骨干**: 预测4秒clip的latent状态序列
- **解码器**: 视频解码器（未来帧重建）+ state-value解码器（成功/失败预测）
- **Latent Space操作**: 支持EVE和NEO两种具身的动作空间co-training
- **分辨率**: 256×256 和 512×512

### 训练策略
- **预训练**: Web-scale视频数据
- **后训练**: 1X机器人数据（遥操作 + 自主rollout），带二值成功标签
- **State Value标签**: 最终帧 +1(成功)/-1(失败)，temporal discounting回传到中间帧

### Action Controllability
- 同一初始帧 + 4组不同动作序列 → 4个完全不同的物理合理未来
- 支持接触丰富的全身操作（开门、抓取、擦桌、行走）
- 精确到帧级别的动作响应（颈部行走时的微妙晃动都能捕捉）

## 关键实验

### Scaling Results
| 任务 | 机器人 | 描述 |
|------|--------|------|
| Airfryer | NEO | 拉出空气炸锅托盘→抓物体→放入→推回 |
| Arcade | EVE | 抓取目标物体→投入投放站 |
| Shelf | EVE | 语言指令→跨象限拾取放置（含换手） |

- **数据量scaling**: 10%→100%数据，Airfryer和Arcade的alignment准确率均显著上升
- **跨任务迁移**: Shelf(216M token) + Arcade(1.46B token) → alignment 63.06% → 71.17%

### 数据源重要性
**自主rollout数据 >> 遥操作数据 >> 人类视频/play数据**
- 失败数据尤其关键（无失败→乐观偏差：物体自动重新定位、抓取半径高估）
- 刻意遥操作的失败有明显偏差，不如自主策略的真实失败分布

### Real-World Correlation（核心价值）
1. **Checkpoint Selection**: 真实成功率差距15%时，70%alignment的WM可以90%概率选对更好的checkpoint
2. **Architecture Selection**: ViT-B vs ViT-L对比，WM预测趋势与真机一致
3. **Sampling Strategy**: mu-only vs max-conf，多组实验WM均正确预测mu-only更优
4. **Dataset Curation**: 生产环境失败案例快照→反事实评估→策略部署信心

### 评估公式
Arcade任务: `score = (successes - 3×resets + 0.3×attempts) / attempts`
- 惩罚人工干预（resets），奖励更高尝试频率
- 双盲A/B测试，同一机器人同一环境

## 局限性
- **未见物体**: 对训练中未出现的物体交互建模不准确（如新品牌咖啡机）
- **位置累积误差**: 下半身位置预测误差逐步累积，限制长距离导航评估
- **任务特定**: 当前仍为task-specific评估，尚未达到production-level通用评估

## 与其他工作的关系
| 对比方向 | 1XWM | 其他 |
|----------|------|------|
| vs UWM/DreamZero | 评估导向（state value预测） | 策略训练导向（联合去噪生成动作） |
| vs COSMOS Policy | 全身人形（NEO/EVE） | 桌面机械臂 |
| vs 传统仿真器 | 数据驱动、无需资产建模 | 需要手工建模、sim-to-real gap |
| vs AUTOEVAL | 离线批量、无需真机 | 每天仅~850 episodes、需物理冷却 |
| vs Vista/GAIA-2 | 人形机器人操作 | 自动驾驶场景 |

## 启示
1. **World Model as Evaluator** 是被低估的应用方向 — 不需要生成完美视频，只需要state value预测准确
2. **On-policy failure data > Teleoperated failure data** — 数据分布比数据量更重要
3. **Cross-task transfer有效** — 共享的抓取运动学、碰撞先验可以跨任务迁移
4. **Scaling law存在** — 更多数据→更准确的评估，且效果可预测
