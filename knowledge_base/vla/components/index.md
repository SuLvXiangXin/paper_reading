# 技术组件概览

## 动作表示
- **离散 token**: 将连续动作 bin 到固定数量的离散值（RT-2/OpenVLA 用 256 bins）
  - OpenVLA 改进: 用百分位数替代 min-max 划分 bin 边界
- **连续向量**: 直接输出连续动作值
- **Action Chunking**: 一次预测多步动作（ACT 提出，减少累积误差）
- **FAST tokenizer**: 高效压缩动作chunk为离散token，训练效率远高于直接离散化（Pertsch et al. 2025）
- **混合离散+连续**: π₀.5 预训练用 FAST（高效）→ 后训练加 flow matching action expert（精确+快推理）
- **混合连续+离散运动表示**: Being-H0.5 在同一实例中同时监督连续 flow matching 和离散 masked token prediction，两通道共享上下文但互相不可见
→ 详见 [action_repr.md](action_repr.md)

## 动作空间设计
- **统一动作空间（Unified Action Space）**: Being-H0.5 首创——将人手 MANO 参数和 30 种异构机器人控制映射到固定长度高维向量，按物理语义分隔子空间（EEF 位姿、夹爪、手指关节、底座等），保留原始物理量级不做统计归一化
  - 与 π₀/π₀.5 的零填充方案不同：π₀.5 用独立 MLP 头适配不同具身，Being-H0.5 用语义对齐的共享槽位 + 稀疏激活
  - 优势：共享物理先验、支持人手→机器人知识迁移、避免独立头的参数碎片化
- **零填充对齐**: π₀/Octo 方案，低维机器人动作空间零填充到最大维度
- **Position control vs velocity control**: Diffusion Policy 首次证明 position control 更优

## 视觉编码器
- **SigLIP**: Google 的对比学习视觉编码器，VLA 中最常用（π₀, π₀.5, MEM 均使用 SigLIP 400M）
- **DINOv2**: Meta 的自监督 ViT，空间/几何特征更好
- **SigLIP + DINOv2 融合**: OpenVLA/Prismatic 的关键创新，通道维拼接两个编码器的特征
  - SigLIP 提供高层语义，DINOv2 提供空间细节
  - 实验验证比单编码器在语言 grounding 任务上高 10%+
  - 成为后续 VLA 研究中的常见选择
- **多视角**: 同时用多个摄像头输入（π₀.5 用4个摄像头：前/后/双腕）
- **视频编码器（Video Encoder）** 🆕: MEM 提出——将 ViT 扩展为视频编码器处理多帧输入
  - 空间-时间分离注意力：每 4 层交替双向空间注意力（帧内）+ 因果时间注意力（同 patch 跨帧）
  - 复杂度：O(Kn² + nK²)（vs naive O(n²K²)），K=帧数，n=patch数
  - Token 压缩：仅传当前帧 token 给 VLA backbone → 与单帧 VLA token 数一致
  - **不引入新参数**：仅修改注意力模式 + 固定正弦时间位置编码（t=0 时为 0，保证 K=1 时与原始 VLM 完全一致）
  - 16帧约 300ms（vs naive 约 4s），满足实时约束
  - 灵感来源：ViViT (Arnab et al. 2021), TimeSformer (Bertasius et al. 2021) 的空间-时间分离注意力
→ 详见 [vision_encoder.md](vision_encoder.md)

## 架构设计
- **Mixture-of-Transformers (MoT)**: 共享 attention + 独立 FFN 的双专家设计（理解+动作），π₀ 开创，Being-H0.5/BAGEL 继承
- **Mixture-of-Flow (MoF)**: Being-H0.5 首创——将 flow-based 动作专家分为共享基础层（通用运动原语）+ Top-K 路由的特化专家层（具身/任务特定），实现参数量与激活参数量解耦，支持边缘部署
- **流形保持门控 (MPG)**: Being-H0.5 首创——用 Sliced-Wasserstein Distance 衡量上下文特征可靠性，门控 feature residual + 无门控先验偏置，解决分布偏移下 flow matching 的动作抖动问题
- **通用异步分块 (UAC)**: Being-H0.5 首创——训练时随机采样延迟偏移，推理时双线程异步执行，使单一检查点适配不同控制频率/延迟的机器人

## 记忆机制 🆕
VLA 的记忆机制决定了策略能访问多长时间跨度的历史信息。不同方法在信息保真度和计算效率之间做取舍：
| 方法 | 类型 | 时间跨度 | 信息保真度 | 计算成本 | 代表工作 |
|------|------|---------|-----------|---------|---------|
| 密集帧历史 | 图像序列 | ~数秒 | 高 | 极高 | Octo, BET |
| 池化记忆 | 压缩图像 | ~十几秒 | 中 | 低 | ContextVLA |
| 本体感知记忆 | 关节状态 | ~分钟 | 低（仅自身） | 极低 | TA-VLA |
| 关键帧记忆 | 稀疏图像 | ~分钟 | 中 | 中 | BPP, MeMeR |
| 点轨迹记忆 | 2D轨迹 | ~十几秒 | 中 | 低 | TraceVLA |
| 潜在记忆 | 隐状态 | ~十几秒 | 未充分验证 | 低 | Sam2Act, MemoryVLA |
| 语言记忆 | 自然语言 | ~分钟 | 高（语义）/低（空间） | 低 | OneTwoVLA |
| **多尺度混合模态记忆** | **视频+语言** | **~15分钟** | **高（两尺度互补）** | **中** | **MEM (2025)** 🆕 |

**MEM 的核心洞察**：没有单一模态能同时满足短时精细记忆（解决遮挡、调整抓取）和长时语义记忆（追踪任务进度），因此用视频编码器处理短时（~54s），用语言摘要处理长时（~15min），两者互补。

## 高效微调与部署
- **LoRA 微调**: OpenVLA 首次系统验证 LoRA 对 VLA 的有效性
  - rank=32, 应用于所有线性层, 仅训练 1.4% 参数
  - 匹配全量微调性能，VRAM 从 163GB 降至 60GB
  - 单卡 A100, 10-15 小时
- **量化推理**: OpenVLA 验证 4-bit 量化无损（VRAM 7GB），8-bit 因速度慢反而降低性能
- **视觉编码器微调**: VLA 训练中视觉编码器必须微调（与 VLM 训练的最佳实践相反）
- **多 epoch 训练**: VLA 需要 27+ epochs（VLM 通常 1-2 epochs），action token accuracy 需达 >95%
- **具身特定适配 (ESA)**: Being-H0.5 的 slot-wise adapter bank，在统一动作空间中每种具身只更新其激活槽位的 adapter，共享硬件组件共享适配参数子集

## 数据策略
- **Cross-embodiment**: 混合不同机器人的数据训练
- **Co-training**: 机器人数据 + 互联网视觉语言数据 + 高层语义数据混合训练
  - RT-2/RT-2-X 采用 co-training 保留 VLM 预训练知识
  - OpenVLA 未采用 co-training，导致语义泛化弱于 RT-2-X
- **人类中心学习（Human-Centric Learning）**: 将人手运动视为"物理母语"，大规模 egocentric 人类视频提取手部运动作为行为先验
  - Being-H0 首创，Being-H0.5 扩展到 16K 小时
  - EgoScale 类似思路，20K 小时 ego 视频
  - 核心假设：不同机器人遵循共享物理法则，人手运动提供因果交互逻辑和接触物理的不变先验
- **Verbal Instruction**: 人类用语言实时指导机器人，收集高层决策示范（π₀.5新引入）
- **人类干预/修正数据** 🆕: MEM 用于训练上下文适应——收集策略失败后的人类修正示范，将失败尝试保留在短时记忆中训练，使策略学会从失败中调整策略
- **数据增强**: 图像变换、轨迹扰动等
- **数据筛选/加权**: Octo 和 OpenVLA 均对 OXE 数据集进行仔细筛选和加权
→ 详见 [data_strategy.md](data_strategy.md)

## 语言编码器/LLM backbone
- **T5-base (111M)**: Octo 使用，冻结
- **Llama 2 (7B)**: OpenVLA 使用，微调
- **Gemma 2B**: π₀ 使用（通过 PaliGemma）
- **Gemma3 4B**: MEM/π₀.6-MEM 使用 🆕
- **InternVL-3.5**: Being-H0.5 使用（decoder-only）
- **关键差异**: 小规模冻结编码器（Octo）vs 大规模微调 LLM（OpenVLA/π₀），后者语言理解和 grounding 能力更强
