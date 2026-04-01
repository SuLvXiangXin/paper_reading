# SaiVLA-0: Cerebrum–Pons–Cerebellum Tripartite Architecture for Compute-Aware VLA

| 字段 | 内容 |
|------|------|
| **标题** | SaiVLA-0: Cerebrum–Pons–Cerebellum Tripartite Architecture for Compute-Aware Vision-Language-Action |
| **作者** | Xiang Shi, Wenlong Huang, Menglin Zou, Xinhai Sun (Synthoid.ai) |
| **时间** | 2026年3月（arXiv: 2603.08124v1） |
| **方法线归属** | **冻结VLM + 分类式动作解码（Tripartite Architecture）** |
| **一句话总结** | 神经科学启发的三元架构：冻结大VLM（Cerebrum）低频提供多层语义先验，Pons Adapter编译为执行token，ParaCAT（Cerebellum）高频输出{-1,0,+1}三元分类动作，两阶段缓存训练+固定比率调度，LIBERO 99.0% |

## 核心问题
现有 VLA 将语义理解和高频控制耦合在单一系统中，导致：
1. 高延迟、不稳定（特别是小数据场景下端到端微调大 VLM 不现实）
2. 仅用最后一层表示难以同时捕捉全局语义和局部几何/接触细节
3. 不一致的 prompt/标定影响可复现性

## 方法

### 三元架构（Cerebrum–Pons–Cerebellum）
类比大脑皮层（高层认知）→ 脑桥（编译传递）→ 小脑（快速运动控制）：

**1. Cerebrum（冻结 VLM）**
- 冻结大 VLM（默认 Qwen-VL-8B，支持 4B/32B scaling）
- 低频运行（每 N=5 个 chunk 调用一次）
- 暴露 early/mid/late 多层隐藏状态 {H_B^(l)}
- 使用结构化 JSON prompt（goal/constraints/objects/failure_cases/environment，训练时 50% 随机 field 顺序）

**2. Pons Adapter（可训练桥接）**
- "语义→动力学编译器"：将多层 Cerebrum 输出投影、融合、池化为固定长度上下文 token C ∈ R^{Nc×d}
- 层间投影 → GLU + cross-layer attention → attention token pooling（可学习 query）
- 与 Cerebellum 联合训练（Stage B）

**3. Cerebellum / ParaCAT（高频执行）**
- **Parallel Categorical Action Transformer**：encoder-only Transformer
- 输入序列：[C; V(图像); W(文本); s(状态); {q_{k,j}}(动作 query)]
- K×D 个可学习动作 query → 并行 softmax 分类解码 → 每维 {-1, 0, +1} 三元 delta
- **稳定性控制**：hysteresis 阈值（θ↑/↓=0.2）+ EMA（α=0.8）+ temperature annealing（1.5→0.7）+ entropy cap（H_max=0.9）
- 固定步长 δ_p=5mm, δ_θ=1°
- D=16（双 7-DoF 臂 + 2 夹爪）

### 两阶段训练（Feature Caching）
- **Stage A**：离线运行冻结 Cerebrum，缓存多层隐藏状态（npz/mmap，带版本 hash/校验和）
- **Stage B**：在缓存特征 + 当前帧上联合训练 Pons Adapter + Cerebellum
- **Stage C（可选）**：轻微调整桥接层

### 双频调度（Fixed-Ratio Scheduling）
- Cerebrum 每 N=5 个 chunk 调用一次
- 每次 Cerebellum forward 产出 K=20 步动作
- 有效动作率 f_eff ≈ K × f_fwd

### 注视式 ROI（Foveated Vision）
- 通过标定投影将末端执行器投影到图像坐标 → 裁剪两个腕部 ROI（各 256²）
- **不是固定腕部相机**，而是几何绑定到工具坐标系 → 运动稳定、高分辨率、对精细姿态/接触变化敏感
- ROI 与主视图通过 cross-attention 融合
- 低置信度/遮挡时回退到主视图 + 保守解码策略

### 训练细节
- 损失函数：class-weighted CE + label smoothing + entropy 正则 + 时间平滑 KL
- 数据：LIBERO + 小规模真机桌面操作 + 可选仿真
- 训练预算：20k steps, batch 80 × 8 GPUs

## 实验结果

### LIBERO（主要验证）
| 方法 | Spatial | Object | Goal | Long | Mean |
|------|---------|--------|------|------|------|
| **SaiVLA-0** | **99.8** | **100.0** | **98.2** | **97.8** | **99.0** |
| π₀ | 96.8 | 98.8 | 95.8 | 85.2 | 94.2 |
| OpenVLA-OFT | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 |
| GR00T-N1.6 | 97.7 | 98.5 | 97.5 | 94.4 | 97.0 |
| π₀.5 | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| GR00T-N1.5 (official) | 92.0 | 92.0 | 86.0 | 76.0 | 86.5 |

### Split Feature Caching 效果
| 方法 | Spatial | Object | Goal | Long | Mean | Train (h) |
|------|---------|--------|------|------|------|-----------|
| GR00T-N1.5 (official) | 92.0 | 92.0 | 86.0 | 76.0 | 86.5 | 7.5 |
| GR00T-N1.5 (split) | 97.8 | 99.6 | 79.6 | 92.8 | 92.5 | 4.5 |

→ 训练时间 7.5h → 4.5h（-40%），平均成功率 86.5% → 92.5%（+6pp），但 Goal 子集有所下降

### Backbone 对比
- Eagle2.5VLM (layer 12): 92.5% mean
- Qwen3VL-2B (layer 14): 90.1% mean

## 设计假设（可测试预测）
- H1: 三元分离在小数据场景下降低 jitter 和延迟
- H2: early/mid/late 多层 context 优于仅 last-layer
- H3: {-1,0,+1} 分类 + hysteresis/EMA 优于连续头
- H4: 两阶段缓存减少 wall-clock 和 seed variance
- H5: 固定 Cerebrum cadence 在相同预算下保持成功率
- H6: 几何绑定 ROI 改善接触敏感行为
- H7: 计算归一化指标 SRcn 提供更公平对比

## 核心创新
1. **三元架构分离**：明确区分语义（Cerebrum）、编译（Pons）、执行（Cerebellum），各自独立升级
2. **ParaCAT 分类动作头**：极简 {-1,0,+1} 三元 delta + 并行多步解码，单次 forward 输出 K 步
3. **两阶段特征缓存**：冻结 Cerebrum 离线缓存 → 下游轻量训练，快速迭代 + 可复现
4. **注视式几何 ROI**：非固定腕部相机，而是标定投影绑定末端执行器，运动稳定 + 高分辨率

## 局限性
1. **概念验证论文**：主要是设计理念 + 初步证据，不声称结论性优越
2. **分类精度天花板**：{-1,0,+1} 在亚毫米级精度任务可能不够（未来考虑混合头）
3. **无自适应调度**：固定 N=5 无法根据不确定性重新规划
4. **ROI 依赖标定**：需要精确内外参 + 时间同步，drift 会退化
5. **缓存一致性风险**：改变 tokenizer/prompt/标定会使缓存失效
6. **0-class 不平衡**：三元分类中"不动"类别主导，需仔细校准

## 与现有方法的关系
- **vs π₀/Being-H0.5（VLM+Flow Head）**：SaiVLA-0 用冻结 VLM + 分类动作（非 flow matching），更低延迟但精度有上限
- **vs GR00T-N1.5**：直接基于 N1.5 backbone 做 split training 验证，证明冻结+缓存策略有效
- **vs OpenVLA-OFT**：同为"冻结 backbone + 轻量头"思路，但 OFT 仍用连续回归；SaiVLA-0 用分类解码
- **vs Figure Helix**：类似的双系统思想（皮层规划 + 小脑执行），SaiVLA-0 形式化为三元架构
- **独特之处**：唯一将"冻结 VLM 多层缓存 + 可学习 Pons 编译器 + 分类式并行动作解码"三者统一的架构

## 关键指标
- **LIBERO Mean**: 99.0%（SOTA）
- **训练加速**: 40%（feature caching）
- **动作空间**: {-1, 0, +1}^D, δ_p=5mm, δ_θ=1°
- **硬件**: 双 7-DoF 臂 + 2 夹爪（D=16）
- **调度**: Cerebrum N=5, Cerebellum K=20
