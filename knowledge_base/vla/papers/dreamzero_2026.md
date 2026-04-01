# DreamZero: World Action Models are Zero-shot Policies (2026)

## 基本信息
- 作者: Seonghyeon Ye†, Yunhao Ge*, Kaiyuan Zheng*, Shenyuan Gao*, Sihyun Yu* 等（NVIDIA, †Project Leads, *Core Contributors）
- 机构: NVIDIA
- arXiv: 2602.15922
- 日期: 2026-02-17
- 开源: 模型权重（含 DROID checkpoint）、推理代码、RoboArena/PolaRiS/Genie Sim 3.0 评测代码
- 项目主页: https://dreamzero0.github.io
- GitHub: https://github.com/dreamzero0/dreamzero

## 一句话总结
基于 Wan2.1-I2V-14B 视频扩散骨干，构建 14B World Action Model（WAM），通过自回归 chunk-wise 联合视频+动作 flow matching 去噪，在仅 500 小时**多样非重复**遥操作数据上实现零样本任务/环境泛化（比 SOTA VLA 提升 2x+），并通过 38x 推理加速实现 7Hz 实时闭环控制，以及 30 分钟 play data 的少样本跨具身迁移。

## 问题
1. **VLA 的物理泛化瓶颈**：现有 VLAs（π₀.5, GR00T N1.6）继承 VLM 的语义先验擅长 object/semantic generalization，但缺乏时空动力学先验，无法泛化到未见过的物理动作/运动技能（如"解鞋带"、"用画笔画画"）
2. **VLA 依赖重复性示教数据**：传统 VLA 需要每个任务大量重复示教，难以从多样异构数据中有效学习
3. **视频扩散模型的实时性挑战**：14B 参数的视频 diffusion model 原始推理 ~5.7 秒/chunk，无法闭环控制
4. **跨具身迁移效率低**：现有 VLA 跨具身迁移需要大量带动作标注的数据

## 方法
- **方法线归属**: World Model + VLA → **流派B: 视频+动作联合去噪**（同一 diffusion 框架内联合去噪视频帧和动作序列）
- **核心 idea**: 将预训练视频扩散模型的时空动力学先验直接用于机器人策略学习——联合预测视频和动作本质上是 **自回归视频预测 + 隐式逆动力学模型（IDM）** 的统一，使动作学习从"dense state-action imitation"转变为"inverse dynamics aligned with visual futures"
- **与 Cosmos Policy 的关键区别**: DreamZero 采用**自回归架构**（vs Cosmos Policy 的双向/并行），14B 参数规模（vs 2B），强调从多样非重复数据的零样本泛化（vs 任务特定微调+规划），并实现跨具身迁移

### 关键技术点

#### 1. 模型架构：自回归 chunk-wise DiT
- **骨干**: Wan2.1-I2V-14B-480P（14B image-to-video diffusion transformer）
- **最小架构修改**: 仅新增 state encoder, action encoder, action decoder；多视角图像拼接为单帧
- **Chunk-wise 自回归**: 每 chunk = K=2 latent frames，对应 H=48 action steps（1.6s/chunk）；M=4 chunks 最大上下文 6.6s
- **Teacher forcing**: 当前 chunk 去噪时条件于前序 clean chunks
- **闭环 KV Cache 替换**: 推理时执行 action 后用真实观测替换 KV cache 中的预测帧→**消除自回归视频生成的累积误差**（WAM 独有优势）
- **冻结组件**: Text encoder, image encoder, VAE 保持冻结；更新所有 DiT blocks + state/action encoder/decoder
- **LoRA 验证**: 实验尝试 LoRA 但效果不佳，采用全参数更新

#### 2. 训练目标：联合 flow matching
- 视频和动作共享 denoising timestep：$t_k \sim \mathcal{U}(0,1)$（加速收敛，不同于 UWM 的解耦 timestep）
- Flow matching velocity prediction：$\mathcal{L}(\theta) = \mathbb{E}\left[\frac{1}{K}\sum_{k=1}^{K} w(t_k) \|u_\theta([z^k_{t_k}, a^k_{t_k}]; \mathcal{C}_k, c, q_k, t_k) - v_k\|^2\right]$
- 端到端单模型训练（vs Seer/UniPi 的两阶段 pipeline）
- 默认动作表示：relative joint positions，过滤 idle actions

#### 3. 自回归 vs 双向架构选择
- **自回归优势**: (1) KV cache 加速推理 3-4x, (2) 保留原始 FPS 确保视频-动作对齐, (3) 任意长度上下文支持
- **双向问题**: 固定长度序列需视频下采样→distort native FPS→破坏视频-动作-语言三模态对齐；采样点在 mid-task 时，语言描述与生成内容不匹配
- **消融对比**: AR 和 BD 在 task progress 上接近（50% vs 50%），但 AR 方差更小（±6.3% vs ±14.4%），动作更平滑

#### 4. DreamZero-Flash：解耦噪声调度
- 核心洞察：少步推理时动作需完全去噪但视频仍有残留噪声→训练-推理 mismatch
- 解决：$t^{video}_k = 1 - \eta, \eta \sim \text{Beta}(7,1)$（视频偏向高噪声，E[t_video]=0.125），$t^{action}_k \sim \mathcal{U}(0,1)$（动作均匀）
- 训练时暴露模型于"从噪声视频预测干净动作"的配置，匹配少步推理条件
- 效果：4 步→1 步去噪，推理从 350ms→150ms，性能仅降 9%（83%→74% table bussing）
- **作为主训练后的最终阶段** (Flash training)
- **与 UWM 的区别**: UWM 解耦 timestep 用于灵活切换 policy/forward/inverse dynamics；DreamZero-Flash 解耦 timestep 专门用于推理加速

#### 5. 38x 推理加速系统
| 优化层级 | 技术 | 效果 |
|---------|------|------|
| 系统级 | CFG 双 GPU 并行 | 47% per-step 延迟降低 |
| 系统级 | DiT Caching（cosine similarity 阈值复用 velocity） | 有效步数 16→4 |
| 实现级 | torch.compile + CUDA Graphs（fullgraph=True, 静态 shape） | 消除 CPU 开销 |
| 实现级 | NVFP4 量化（Blackwell SM100，QKV/Softmax 保持 FP8，非线性 FP16） | 进一步加速 |
| 实现级 | cuDNN backend for attention + scheduler 迁移到 GPU | 消除 CPU-GPU 同步 |
| 模型级 | DreamZero-Flash | 去噪步数 4→1 |
| 执行级 | 异步闭环（推理与执行并行，目标延迟 <200ms） | 消除阻塞等待 |
| **总计** | H100: 9.6x, GB200: **38x** | 5.7s→150ms |

- Action chunk smoothing: 2x 上采样 → Savitzky-Golay filter (window=21, order=3) → 下采样

#### 6. 数据策略：多样性优先于重复性
- **500 小时** AgiBot G1 遥操作数据，22 个真实环境（家庭/餐厅/超市/咖啡厅/办公室）
- 每集 ~4.4 分钟，~42 个子任务——远长于典型操作数据集
- **任务淘汰机制**: 每任务收集 50 集后即 deprecated，迫使操作者持续提出新任务→长尾分布
- **每日工作流**: 操作者每集从任务表选 3 个粗粒度任务连续执行（如"整理物品"、"清扫垃圾"）
- 消融实验证实：500h 多样数据 >> 500h 重复数据（50% vs 33%）
- 也在 DROID（公开数据集）上验证有效性，DROID checkpoint 已开源
- 技能分布：包含 navigation、torso adjustment、各类 manipulation

#### 7. 训练配置
- AgiBot: 100K steps, batch size 128
- DROID: 100K steps, batch size 128
- Post-training: 50K steps per task
- 视频采样 5FPS，动作采样 30Hz (AgiBot) / 15Hz (DROID)

## 实验

### 评测设计亮点
- **默认设置是 OOD**: 预训练和评测在不同地理位置，所有评测天然测试环境泛化
- **任务粒度定义**: 运动类型 × 物体类型（折叠衬衫→看到的任务；折叠袜子→未见任务，因运动不同）
- **AgiBot**: 4台机器人，80 rollouts/checkpoint (seen + unseen)
- **DROID-Franka**: 40 tasks, 80 rollouts/checkpoint

### 主要结果

#### Pretraining（零样本评测，新环境+新物体）
| 设置 | DreamZero | 最佳 VLA 基线 | 提升 |
|------|-----------|-------------|------|
| AgiBot 见过任务（avg task progress） | 62.2% | 27.4% (π₀.5-pretrained) | **2.3x** |
| AgiBot 未见任务（avg task progress） | 39.5% | 16.3% (π₀.5-pretrained) | **2.4x** |
| DROID 见过任务（success rate） | 75% | 69% (GR00T N1.6-pretrained) | +6% |
| DROID 未见任务（success rate） | 22.5% | 12.5% (GR00T N1.6-pretrained) | **1.8x** |

- **关键发现**: From-scratch VLAs 在多样数据上几乎完全失败（0-2.1%），即使预训练 VLA 也仅部分成功
- **失败模式洞察**: "大多数 DreamZero 失败源于视频生成错误而非动作预测"——策略忠实执行视频预测的轨迹。VLA 则倾向于无论指令如何都尝试抓取（overfit 到 pick-and-place）

#### Post-training（任务特定微调后仍保持环境泛化）
| 任务 | DreamZero | 最佳 VLA 基线 | 备注 |
|------|-----------|-------------|------|
| 衬衫折叠 | 92.5% | 92.5% (π₀.5-pt) | 持平 |
| 水果装袋 | 96% | 71% (π₀.5-pt) | **+25%** |
| 收桌 | 83% | 76% (π₀.5-pt) | **+7%** |
| 平均 | **90.5%** | 79.8% | **+10.7%** |

- 关键：post-training 后环境泛化能力得以保持

#### 跨具身迁移
| 设置 | 未见任务 Task Progress |
|------|----------------------|
| DreamZero 基线 | 38.3% ± 7.6% |
| + Human2Robot Transfer（12min 人类视频） | **54.3% ± 10.4%** (+42% relative) |
| + Robot2Robot Transfer（20min YAM 视频） | **55.4% ± 9.5%** (+45% relative) |
| 少样本具身适配（30min YAM play data） | 保持零样本语言跟随泛化 |

- 跨具身数据仅用视频预测目标（无动作标注）
- 9 个未见任务，每任务 8 条 demo，co-train 10K steps（1:1 混合预训练数据）
- 少样本适配: 55 条轨迹，11 个任务，~30 min

#### DreamZero-Flash 评测
| Method | Denoising steps | Task Progress | Inference speed |
|--------|----------------|---------------|-----------------|
| DreamZero | 4 | 83% ± 6.1% | 350ms |
| DreamZero | 1 | 52% ± 10.2% | 150ms |
| DreamZero-Flash | 1 | 74% ± 10.1% | 150ms |

#### 消融实验（PnP Easy, 50K steps, batch 32）
| 消融 | Task Progress |
|------|---------------|
| 14B 多样数据 (AR) | **50% ± 6.3%** |
| 14B 重复数据 (AR) | 33% ± 4.2%（多样性重要） |
| 5B 多样数据 (AR) | 21% ± 4.2%（规模重要，scaling 明确） |
| 14B VLA 多样数据 (5B VLM base) | 0% ± 0.0%（VLA 无法从多样数据学习） |
| 14B VLA 多样数据 (14B VLM base, 截半+DiT action head) | 0% ± 0.0%（放大 VLA 也不行） |
| 14B 双向架构 (BD) | 50% ± 14.4%（均值同但方差大，且推理慢 3-4x） |

### 对比基线
- GR00T N1.6（from-scratch + from-pretrained）
- π₀.5（from-scratch + from-pretrained，后者含数千小时跨具身预训练）
- π₀.5-DROID, GR00T N1.6-DROID
- **公平对比**: 相同训练数据、相同 batch size 和 gradient steps

### 评测平台
- AgiBot G1 双臂移动操作（4台机器人，80 rollouts/checkpoint）
- DROID-Franka 单臂操作（40 tasks, 80 rollouts/checkpoint）
- 100+ free-form 额外任务展示
- Genie Sim 3.0（100 仿真任务，未用仿真训练数据，展示非平凡 sim 性能）

### 额外评测
- **RoboArena 真机评测** 和 **PolaRiS 仿真评测** 代码已开源
- **Genie Sim 3.0**: 尽管仅训练于 ~500h 真机数据，在 100 个仿真任务上展示非平凡性能（未使用 10k 小时仿真数据）

## 评价

### 优势
1. **零样本物理泛化的突破**：首次系统性证明 WAM 在未见任务/环境上 2x+ 优于 SOTA VLAs，包括"解鞋带"、"熨衣服"、"画画"等需要全新物理运动的任务——这是 VLAs 语义先验无法覆盖的能力边界
2. **颠覆数据收集范式**：证明多样非重复数据 > 重复任务特定数据（对 WAM），使数据收集从实验室重复示教转向真实世界多样行为记录——显著降低数据成本
3. **清晰的 scaling 行为**：14B >> 5B（50% vs 21%），且 VLA 同样规模仍 0%——说明 WAM 的 scaling 行为与 VLA 本质不同（视频预测质量直接决定策略质量）
4. **跨具身迁移效率极高**：仅 video-only 数据（无动作标注）即可实现 42%+ 相对提升；30min play data 适配全新机器人——这是"学习 IDM"比"学习直接策略"更 sample-efficient 的有力证据
5. **工程完整度高**：38x 推理加速从论文概念到 7Hz 实时部署，包含系统/实现/模型三层优化的完整方案
6. **故障模式的深刻洞察**："大多数失败源于视频生成错误而非动作预测"——意味着改进视频骨干直接提升策略性能，提供了清晰的改进方向
7. **开源承诺完整**：模型权重、推理代码、多个评测基准代码均开源

### 局限
1. **计算成本高**：14B 模型需 2x GB200 才能 7Hz，远不如 VLA 的消费级 GPU 部署（如 Xiaomi-Robotics-0 RTX 4090 80ms）
2. **短时视觉记忆**：最大上下文 6.6 秒，不支持需要长期记忆的任务（论文承认为 System 1 模型）
3. **未测试高精度任务**：论文承认继承了 behavior cloning 对亚厘米精度任务的局限（但引用 Cosmos Policy 指出 WAM 在毫米级精度上可能有优势）
4. **未做多具身联合预训练**：AgiBot 和 DROID 分别预训练，未探索统一预训练（vs Being-H0.5 的 30 种具身联合训练）
5. **推理仍依赖视频生成**：即使 Flash 模式也需生成视频 latent，推理下限受限于视频 diffusion 的本质开销
6. **仿真基准缺失**：未在 LIBERO、CALVIN 等标准仿真基准上报告，难以与 Cosmos Policy（98.5% LIBERO）、Being-H0.5（98.9%）直接对比
7. **跨具身实验规模有限**：仅 AgiBot G1 ↔ YAM（都是双臂平行夹爪），未验证更大形态差异的迁移

### 论文提出的未来方向
1. **WAM Scaling Laws**：类似 LLM 的 scaling law，探索 WAM 在模型/数据/计算三维度的最优配比
2. **大规模人类视频学习**：利用 Ego4D 等互联网级人类视频增强 WAM
3. **更快推理**：如果小视频骨干也有强泛化，可部署到边缘设备
4. **长时序推理**：双系统架构（System 1 WAM + System 2 规划器）或扩展上下文窗口
5. **高精度任务**：探索 WAM 在亚厘米精度操作中的潜力
6. **具身设计**：人形机器人可能因形态接近人类而更高效利用视频预训练——尽管 DOF 更高，人类视频的规模可能弥补 IDM 学习成本

### 对 VLA 领域的贡献

1. **确立 WAM 作为独立方法范式**：DreamZero 是首个系统性证明 WAM 全面优于 VLA 的工作，且优势不是渐进式的而是质变的（2x+）。"World Action Model" 术语的正式提出标志着该方向从概念验证走向方法范式
2. **揭示 VLA vs WAM 的本质差异**：
   - VLA 学"观测→动作"直接映射，需要密集重复数据覆盖
   - WAM 学"观测→视觉未来→动作"，利用视频预训练的物理先验降低动作学习难度
   - 这解释了为什么 VLA 从多样数据学习失败（0%）而 WAM 成功（50%）
3. **推动数据收集范式变革**：从"task-specific repetitive demos"到"diverse non-repetitive play data"，这可能是机器人数据 scaling 最重要的方向转变之一
4. **跨具身迁移的新范式**：仅用 video-only 数据（无动作标注）实现有效迁移——如果 scale 到互联网规模人类视频，WAM 可能获得远超 VLA 的技能多样性
5. **推理加速的工程范式**：DreamZero-Flash 的解耦噪声调度是通用技术，可应用于其他视频 diffusion 推理场景

## 与已有工作的关系

### vs π₀.5 / GR00T N1.6 (VLM + Flow/Diffusion Head VLAs)
- **核心区别**: VLA 预训练基座是 VLM（图文语义先验）；WAM 预训练基座是视频生成模型（时空动力学先验）
- **数据效率**: VLA 需要重复示教（π₀.5 数千小时）；WAM 从 500h 多样数据即可
- **泛化维度**: VLA 擅长语义泛化（识别新物体）；WAM 擅长物理泛化（执行新运动）
- **实验直接对比**: DreamZero 在相同数据上 2x+ 优于两者
- **VLA scaling 失败**: 即使将 VLA 放大到 14B（8B/32B VLM 截半 + DiT action head），多样数据上仍 0%

### vs Cosmos Policy (同为流派B 联合去噪)
- **规模**: DreamZero 14B vs Cosmos Policy 2B
- **架构**: 自回归 chunk-wise vs 双向并行
- **数据哲学**: 多样非重复 vs 任务特定微调
- **能力侧重**: 零样本泛化 vs 任务特定+规划（best-of-N）
- **跨具身**: DreamZero 展示跨具身迁移，Cosmos Policy 未验证
- **互补**: DreamZero 做零样本泛化，Cosmos Policy 做 best-of-N 规划；论文中 DreamZero 引用 Cosmos Policy 作为高精度任务有希望的信号

### vs UWM (解耦 timestep 联合去噪)
- UWM 的解耦 timestep 用于灵活切换 policy/forward/inverse dynamics
- DreamZero-Flash 的解耦 timestep 专注推理加速
- DreamZero 规模更大（14B vs UWM 小模型），验证了更强的零样本泛化
- DreamZero 共享 timestep 用于初始训练（加速收敛），Flash 解耦仅用于最终阶段

### vs GR-1/GR-2 (视频预训练→动作微调)
- GR-1/GR-2 先视频预训练再动作微调（两阶段或三阶段）
- DreamZero 端到端联合去噪视频+动作（单阶段）
- DreamZero 实现了闭环 KV cache 替换消除累积误差

### vs Being-H0.5 (跨具身 VLA)
- Being-H0.5 通过统一动作空间 + 人类手部数据实现 30 种具身联合训练
- DreamZero 通过 video-only 数据实现跨具身迁移（无需动作标注）
- 两者代表跨具身迁移的不同路径：统一表示空间 vs 视频作为跨具身桥梁

### vs Latent World Models (Dreamer, V-JEPA 2, PointWorld)
- Latent WMs 建模 p(s_{t+1}|s_t, a_t)→需要 goal-conditioned planning 或 search 出动作
- WAMs 建模 p(o_{t:t+H}, a_{t:t+H}|o_{0:t}, c)→直接产出动作轨迹，无需 test-time optimization
- WAM 可 7Hz 实时控制，搜索方法难以做到

## 关键引用数据
- 论文日期: 2026-02-17
- 知识库首次收录: 2026
- 知识库更新: 基于完整论文原文的详细更新
