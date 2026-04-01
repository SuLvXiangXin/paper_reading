# Xiaomi-Robotics-0: An Open-Sourced Vision-Language-Action Model with Real-Time Execution (2026)

## 基本信息
- 作者: Xiaomi Robotics 团队 (Rui Cai, Jun Guo, Xinze He 等)
- 机构: Xiaomi (小米)
- arXiv: 2602.12684
- 日期: 2026.02.13
- 开源: 预训练/后训练检查点 + 推理代码 (https://xiaomi-robotics-0.github.io)

## 一句话总结
基于 Qwen3-VL-4B + DiT 的 4.7B VLA 模型，通过两阶段预训练（VLM action capability + 冻结VLM训DiT）+ 异步执行后训练（Λ-shape attention mask 解决 action prefix shortcut 问题），在消费级 GPU（RTX 4090, 80ms 延迟）上实现流畅实时双臂操作，LIBERO 98.7%、CALVIN 4.80/4.75 均达 SOTA。

## 问题
VLA 模型因参数量大（数十亿级），推理延迟不可忽视，导致真机部署时面临两难：
1. **同步执行**：机器人在等待推理时停滞，动作不连续，降低吞吐量
2. **异步执行（Training RTC）**：虽然用 action prefix conditioning 保证连续性，但引入 **shortcut 问题**——后续时间步的动作预测会"复制"前缀动作而非关注视觉/语言输入，导致策略反应性下降、陷入重复循环

**核心问题**：如何在保持异步执行连续性的同时，避免 action prefix 带来的策略退化？

## 方法
- **方法线归属**: VLM + Diffusion/Flow Head（继承 π₀ 系列，属于 MoT + DiT + Flow Matching 架构）
- **核心 idea**: 在 DiT 中使用 **Λ-shape attention mask** 替代 causal attention，使紧邻前缀的动作 token 可以看到前缀（保证平滑过渡），而后续时间步的动作 token 看不到前缀（强制关注视觉/语言信号），从而在异步执行中兼顾连续性与反应性。

### 关键技术点:

#### 1. 两阶段预训练（Pre-training）
**第一阶段：赋予 VLM 动作生成能力**
- 在 Qwen3-VL-4B-Instruct 上同时训练动作预测和视觉语言任务
- **动作预测**：采用 **Choice Policies** [Qi et al. 2025] 处理轨迹多模态性——同时预测 N 个动作 chunk 候选 + 对应 scores，winner-takes-all 训练（仅 L1 距离最小的候选被更新）
- **VL 数据 co-training**：VL:Robot = 1:6，80M+ VL 样本（grounding/VQA/captioning/embodied reasoning），避免灾难性遗忘
- 架构：在 token 序列末尾追加 T 个可学习 action token [A_i] 和 1 个 score token [S]

**第二阶段：冻结 VLM，训练 DiT**
- 冻结 VLM 作为多模态 conditioner（KV cache），从头训练 16 层 DiT
- Flow matching loss：线性插值噪声路径，Beta 分布采样时间步（偏向高噪声）
- DiT 条件注入：adaLN（flow-matching timestep）+ VLM 最后 16 层 KV cache
- **Attention sink token**：在 DiT 输入前加 learnable sink token 稳定注意力分布
- DiT 内部使用 causal attention 建模时间关系

#### 2. 异步执行后训练（Post-training）— 核心贡献
- **Action prefix conditioning**（继承 Training RTC [Black et al. 2025]）：将前一次推理的 ∆tc 步已提交动作作为 clean prefix 拼接在 noisy action 前
- **Λ-shape attention mask**（本文提出）：
  - 紧邻前缀的 noisy action token 可以 attend to 前缀 → 保证平滑过渡
  - 后续 noisy action token **不能** attend to 前缀 → 强制关注视觉/语言信号，防止 shortcut
  - 每个 noisy action token 还可 attend to VLM KV cache（视觉/语言）、sink token、state token、以及前 w 步 action token
- **RoPE 位置偏移**：给 noisy action token 的位置索引加偏移量（+10），使模型区分 clean prefix 与 noisy action
- **动态 loss 重加权**：当 ∆tc > 0 时，基于在线预测与 GT 的 L1 误差重加权 flow-matching loss，优先纠正偏差大的样本
- 训练时 ∆tc 从 {0,1,...,6} 中随机采样

#### 3. 部署策略
- **同步执行**：执行 T_e 步后等待下一次推理
- **异步执行**：执行 T_e 步后触发推理，机器人继续执行当前 chunk 剩余动作；新 chunk 从第 ∆t_inf 步开始执行（∆tc ≥ ∆t_inf 保证推理期间始终有动作可执行）
- **推理**：5 步 flow-matching（Euler 积分 τ: 0→1），RTX 4090 上 80ms
- **传感器同步**：所有模态重采样到 30Hz 统一时间线

#### 4. 数据
- **机器人轨迹**：~200M 时间步，来源包括 DROID、MolmoAct 等开源数据 + 自采双臂数据（Lego Disassembly 338 小时 + Towel Folding 400 小时）
- **VL 数据**：80M+ 样本，4 类任务（grounding/VQA/captioning/embodied reasoning & planning），使用 Grounded SAM + Grounding DINO 1.5 + LLMDet 交叉验证做 grounding 标注

### 模型架构
- VLM backbone: Qwen3-VL-4B-Instruct
- DiT: 16 层 diffusion transformer
- 总参数: 4.7B
- 采用 Mixture-of-Transformers (MoT) 架构：VLM 和 DiT 以 KV cache 方式交互
- 动作 chunk 长度: T=30（真机，1 秒 @30Hz），T=10（LIBERO/CALVIN），T=4（SimplerEnv）

## 实验

### 仿真 Benchmark
| Benchmark | 指标 | Xiaomi-Robotics-0 | 对比最优 |
|-----------|------|-------------------|----------|
| LIBERO (avg) | 成功率 | **98.7%** | EO-1 98.2% |
| CALVIN ABCD→D | Avg Len | **4.80** | FLOWER 4.67 |
| CALVIN ABC→D | Avg Len | **4.75** | FLOWER 4.53 |
| SimplerEnv Google VM | 成功率 | **85.5%** | EO-1 76.5% |
| SimplerEnv Google VA | 成功率 | **74.7%** | EO-1 63.0% |
| SimplerEnv WidowX | 成功率 | **79.2%** | EO-1 72.7% |

- 在所有三个仿真 benchmark 的所有设置中均达到 SOTA
- SimplerEnv 特别亮眼：Visual Matching 85.5%、Visual Aggregation 74.7% 大幅超越 π₀ (71.4%/54.7%)

### 真机实验（双臂平台，3 摄像头）
**Lego Disassembly**：
- 成功率：同步方法（π₀.5, Sync）略高于异步方法（因异步反应性稍弱导致夹取张力问题）
- 吞吐量：Xiaomi-Robotics-0 (async) > Xiaomi-Robotics-0 (sync) > π₀.5
- **关键发现**：异步执行有效提升吞吐量，同时保持高成功率

**Towel Folding**：
- π₀.5 / Sync / Training RTC: ~1 pcs/min
- **Xiaomi-Robotics-0: 1.2 pcs/min**（最高吞吐）
- **关键发现**：Training RTC 变体会陷入"重复抖动"循环（反复执行展开动作），验证了 action prefix shortcut 问题；Λ-shape mask 有效避免此问题

### VL 能力保留
| 指标 | Xiaomi-Robotics-0 | Qwen3-VL-4B (Base VLM) | π₀.5 | MolmoAct |
|------|-------------------|------------------------|------|----------|
| ERQA | **40.8** | 40.0 | 0.0 | 33.5 |
| SEED | 78.6 | 78.8 | 21.5 | 72.7 |
| POPE | 88.5 | 89.7 | 0.0 | 86.6 |
| MMBench | 84.4 | 88.7 | 22.1 | 80.1 |

- 有效保留了 VLM 能力，在大多数 benchmark 上仅略低于原始 Qwen3-VL-4B
- 在 ERQA（embodied reasoning）上反超 Qwen3-VL-4B（40.8 vs 40.0），得益于 robot-centric VL 数据
- π₀ 和 π₀.5 在多数 VL benchmark 上几乎归零，验证了不含 VL co-training 会导致灾难性遗忘

### 对比基线
- LIBERO: OpenVLA, π₀, π₀-FAST, π₀.5, GR00T-N1, UniVLA, EO-1, FLOWER 等
- CALVIN: RoboFlamingo, GR-1, MoDE, UniVLA, FLOWER 等
- SimplerEnv: RT-1/1-X/2-X, Octo, OpenVLA, π₀, SpatialVLA, EO-1 等
- 真机: π₀.5, 自身同步变体, Training RTC 变体

## 评价

### 优势
1. **针对性解决实际部署痛点**：异步执行中 action prefix shortcut 是真实存在但此前未被充分解决的问题，Λ-shape attention mask 是简洁有效的方案
2. **全面的仿真 SOTA**：在三大主流 benchmark（LIBERO/CALVIN/SimplerEnv）上全部 SOTA，覆盖单步操作、长时序多任务、real-to-sim 迁移
3. **消费级 GPU 部署**：RTX 4090 上 80ms 推理延迟，5 步 flow-matching，可实际部署，降低硬件门槛
4. **VL 能力保留出色**：通过两阶段预训练（第一阶段 co-training + 第二阶段冻结 VLM）+ 大量 VL 数据有效避免灾难性遗忘，在 VL benchmark 上几乎匹配原始 VLM
5. **开源**：预训练/后训练检查点 + 推理代码开源，对社区有实际价值
6. **工程设计完善**：传感器 30Hz 同步、attention sink token、RoPE 偏移等细节设计务实

### 局限
1. **仅评测双臂固定平台**：未涉及移动操作、灵巧手、人形机器人等更广泛的具身形态，跨具身泛化能力未验证
2. **异步执行成功率略低于同步**：在需要极高精度的 Lego 任务中，异步方法的反应性仍不如同步方法
3. **缺乏层次化推理**：不支持高层子任务分解，限制了在 open-world 长时序任务上的能力（与 π₀.5 相比）
4. **预训练第一阶段的 Choice Policies 在最终架构中未被使用**：第一阶段用 Choice Policies 训 VLM，第二阶段冻结 VLM 训 DiT（flow matching），两阶段的关联逻辑可进一步阐明
5. **真机任务仅两个**：虽然 Lego Disassembly 和 Towel Folding 都有挑战性，但任务多样性有限
6. **自采数据量大**：Lego 338 小时 + Towel 400 小时，数据采集成本不低

### 对 VLA 领域的贡献
1. **提出 Λ-shape attention mask 解决异步执行中的 action prefix shortcut 问题**：这是一个简洁的结构性方案，可被其他 VLA 模型采用
2. **验证了"冻结 VLM + 训 DiT"的两阶段预训练可有效保留 VL 能力**：与 Knowledge Insulating VLA [Driess et al. 2025] 的思路一致，提供了独立验证
3. **系统性的仿真 benchmark SOTA**：在所有主流仿真 benchmark 上建立新基线，为后续工作提供参考
4. **消费级 GPU 部署的实践参考**：80ms/RTX 4090 的推理延迟为社区提供了实际部署的工程模板
5. **开源推动社区发展**：在 π₀/π₀.5 闭源的背景下提供可复现的强基线

### 与相关工作的关系
- **vs π₀**：继承 VLM + Flow Matching + Action Expert 的核心架构，但用 Qwen3-VL-4B（vs PaliGemma 3B）+ 独立 DiT（vs 共享 attention 的 action expert），更强调部署效率和异步执行
- **vs π₀.5**：在仿真 benchmark 上全面超越 π₀.5，但 π₀.5 的优势在于层次化推理和 open-world 家庭任务泛化（本文未涉及）；真机比较中吞吐量超越 π₀.5
- **vs Being-H0.5**：两者都用 MoT 架构 + flow matching + 开源策略，但 Being-H0.5 聚焦跨具身泛化（30 种具身 + 统一动作空间），本文聚焦实时部署效率；Being-H0.5 的 UAC 也解决异步分块问题，但方法不同（随机延迟采样 vs Λ-shape mask）
- **vs Training RTC [Black et al. 2025]**：直接对比基线，Λ-shape mask 解决了 Training RTC 的 shortcut 问题
- **vs Knowledge Insulating VLA [Driess et al. 2025]**：两者都通过"冻结 VLM + 训练 flow head"避免灾难性遗忘，思路一致
