# ETPNav: Evolving Topological Planning for VLN-CE (2023)

## 基本信息
- **标题**: ETPNav: Evolving Topological Planning for Vision-Language Navigation in Continuous Environments
- **作者**: Dongyan An, Hanqing Wang, Wenguan Wang, Zun Wang, Yan Huang, Keji He, Liang Wang
- **机构**: CASIA/NLPR
- **arXiv**: 2304.03047
- **年份**: 2023（CVPR 2022 RxR-Habitat Challenge 冠军）
- **引用数**: 171
- **方法线归属**: **拓扑图 + Transformer**

## 核心贡献
1. **将拓扑图方法从离散 VLN 扩展到连续环境 VLN-CE**
2. **在线自组织拓扑图**：不依赖预定义导航图，通过 waypoint 预测器动态构建
3. **三模块层次架构**：拓扑建图 → 跨模态规划 → 低层控制
4. **Tryout 避障机制**：处理 sliding-forbidden 场景中的死锁

## 方法架构

### 进化拓扑地图
- 图 G_t = ⟨N_t, E_t⟩，三类节点：已访问、当前、幽灵节点（已观测未探索）
- **Waypoint 预测器**（核心模块）：
  - 基于 Transformer，**仅用深度图**（RGB 对空间推理无用甚至有害）
  - 12 视角深度特征 + 朝向特征 → 2 层 Transformer → MLP → 空间概率热力图 → NMS 采样 K 个 waypoint
  - 在 MP3D 图数据集上预训练，**参数固定**

### 图更新规则（Waypoint Localization）
- 计算 waypoint 与图中所有节点的欧氏距离，阈值 γ=0.5m
  - Case 1：定位到已访问节点 → 添加边
  - Case 2：定位到幽灵节点 → 累积平均更新表征
  - Case 3：无匹配 → 创建新幽灵节点

### 跨模态规划器
- 文本编码器 9 层（R2R-CE 用 LXMERT 初始化，RxR-CE 用 RoBERTa）
- 跨模态图编码器 4 层（GASA + 双向交叉注意力）
- **仅从幽灵节点或 STOP 中选择目标**（mask 已访问/当前节点）
- Dijkstra 最短路径规划

### RF 控制器 + Tryout 避障
- Rotate-then-Forward：计算到子目标的 (Δθ, Δρ) → 量化为 ROTATE(15°) + FORWARD(25cm)
- **Tryout**：检测死锁（FORWARD 后位置不变）→ 7 方向尝试 → 脱困

## 与 DUET 的核心区别

| 维度 | DUET | ETPNav |
|------|------|--------|
| 拓扑地图 | 依赖预定义导航图 | 在线 waypoint 预测构建 |
| 环境 | 离散 VLN | 连续 VLN-CE |
| 图编码 | 双尺度（粗+细）| 单尺度 + GASA |
| 低层控制 | teleport（图上跳转）| RF 控制器 + Tryout |

公平对比：ETPNav 比 DUET 在 R2R-CE 上 **+3.5 SR, +2.72 SPL**

## 训练策略

### 预训练（~20h）
- R2R/RxR 离散路径 + 合成指令
- MLM + SAP，batch 64, lr 5e-5, 100K iter
- 用 Habitat 重建 RGB（消除与 MP3D 的域差距）

### 微调（~30h）
- Habitat 在线交互，student-forcing（scheduled sampling）
- 教师策略：R2R-CE 选最近目标幽灵节点，RxR-CE 路径保真策略
- batch 16, lr 1e-5, 15K iter, 2×RTX 3090

## 实验结果

### R2R-CE Val-Unseen / Test-Unseen
- SR **57 / 55**, SPL **49 / 48**
- 比 CWP-RecBERT: +13/+11 SR

### RxR-CE Val-Unseen / Test-Unseen
- SR **54.79 / 51.21**, SDTW **45.33 / 41.30**
- **CVPR 2022 RxR-Habitat Challenge 冠军**，SDTW 是第二名两倍

## 消融实验关键结论

| 消融 | SR 变化 | 结论 |
|------|---------|------|
| Depth-only vs RGBD waypoint | +0.77 | **RGB 对空间推理有害** |
| 幽灵节点删除（Del.）| +4.80 | 防反复选不可达目标 |
| 全局 vs 局部规划 | +3.29 | 全局规划优势明显 |
| GASA | +1.24 | 拓扑感知有效 |
| 预训练 MLM+SAP | +19.80 vs 从零 | 预训练至关重要 |
| RF+Tryout vs 无 Tryout | +26.69 SDTW | Tryout 对 sliding-forbidden 必不可少 |

## 局限性
1. **依赖 GT 位姿**：使用模拟器提供的精确位姿
2. **Waypoint 预测器固定**：无法适应分布外环境
3. **图节点随步数增长**：计算开销增加
4. **仅仿真验证**：未真实部署

## 关键技术细节
- 观测：全景 RGBD，12 视角（每 30°）
- 动作：FORWARD(0.25m), ROTATE(15°), STOP
- 最大步数：R2R-CE 15 步, RxR-CE 25 步
- 视觉编码器：CLIP ViT-B/32(RGB) + DD-PPO ResNet-50(Depth)，参数固定
- 定位阈值 γ=0.5m 最优（~24 节点/episode）
