# Being-M0: Scaling Motion Generation Models with Million-Level Human Motions (2024)

## 基本信息
- 作者: Ye Wang, Sipeng Zheng, Bin Cao, Qianshan Wei, Weishuai Zeng, Qin Jin, Zongqing Lu
- 机构: RUC / BAAI / PKU / BeingBeyond
- arXiv: 2410.03311
- 链接: https://research.beingbeyond.com/being-m0
- 日期: 2024.10.03
- 会议: ICML 2025
- 备注: 官方项目页使用 MotionLib / MotionBook 命名；arXiv 早期正文中对应称为 MotionBase / 2D lookup-free quantization。

## 一句话总结
Being-M0 是 BeingBeyond 的第一代 motion generation foundation model：用百万级 MotionLib 人体运动库和 MotionBook 运动 tokenization 训练 LLM 式自回归运动生成器，证明 human motion data/model scaling 能提升文本到运动和 OOD motion 泛化，但它仍是人类 SMPL 运动生成模型，不是闭环 robot policy。

## 问题
现有 text-to-motion / motion LLM 的主要瓶颈不是语言模型本身，而是运动数据和运动表示：
- 数据集过小，HumanML3D / Motion-X 难覆盖长尾人类动作，模型容易只在窄分布内有效。
- 常规 1D VQ 把每帧复杂运动特征压成单个 code，容易丢失关节、速度、接触等细节，也不利于部位级控制。
- 现有 FID / retrieval evaluator 多在小数据上训练，对大规模、OOD motion 的评价不稳定。

对 embodied/VLA 知识库的意义在于：机器人策略同样缺少大规模物理运动先验。Being-M0 不是直接控制机器人，但它把"语言 -> 人体运动 token"作为可规模化的基础模型问题提出，为 humanoid / whole-body policy 的高层 motion prior 提供了参考。

## 方法
- 方法线归属: Motion Generation Foundation Model / Motion Token LLM（VLA-adjacent，不是 VLA policy）
- 核心 idea: 构建百万级 MotionLib，并用 MotionBook 将连续人体运动压缩为更高容量的离散 token，再微调自回归 LLM 生成 motion token。
- 关键技术点:
  - **MotionLib**: 官方页称超过 1.2M motion sequences，包含层次化 body/part 文本描述；论文版 MotionBase 包含 42 个公开数据集和互联网视频，融合 RGB、depth、bbox、多人物、静态图像和合成数据。
  - **数据处理**: 从公开视频中过滤 human-centric 片段，做 2D/3D keypoint、SMPL-X 局部/全局姿态估计和全局运动优化；用 Gemini-1.5 Pro / GPT-4o-mini 生成 whole-body 与 part-level 伪标签。
  - **MotionBook / 2D-LFQ**: 将 motion clip 看作 `T x D x 1` 的单通道"图像"，按 root orientation、joint rotation、foot contact 等组件做 2D 编码；用 lookup-free quantization 扩展到 `2^16=16384` 级 codebook，缓解传统 VQ/RQ 的 codebook collapse。
  - **两阶段训练**: 先训练 motion tokenizer / decoder，再把 motion code 加入 LLM 词表，用 `<mot>` / `</mot>` 包裹 motion sequence，微调 GPT-2、LLaMA-2/3 等自回归模型生成 motion token。
  - **Scaling study**: 系统比较 0.02M、0.08M、0.5M、1M 数据规模和 GPT-2 / LLaMA-2-7B / LLaMA-2-13B / LLaMA-3-8B，验证数据和模型规模对 motion-text alignment 的增益。

## 实验
- Benchmark: HumanML3D、Motion-X、MotionLib/MotionBase、UNSEEN-90K OOD split、motion reconstruction。
- 主要结果:
  - HumanML3D 上 LLaMA-2-13B 版本达到 R@1 0.519、R@3 0.803、FID 0.166、MMDist 2.964，优于 MotionGPT、MotionLLM、AvatarGPT 等 LLM-based motion baseline。
  - MotionBase OOD split 中，MotionBase 训练模型在 R@1/R@3 上明显优于 HumanML3D 或 Motion-X 训练模型，说明大规模多源数据改善长尾动作泛化。
  - 2D-LFQ 在 Motion-X / MotionBase reconstruction 的 MPJPE 明显优于 VQ/RQ，且大 codebook 利用率更好；但 FID 可能反而异常，论文将其归因于 evaluator 泛化不足。
- 对比基线: MLD、MotionDiffuse、T2M-GPT、MotionGPT、MotionLLM、AvatarGPT、VQ-VAE、RQ-VAE。

## 评价
- 优势: 首次把 motion generation 明确推进到"数据和模型一起 scaling"的问题设定；MotionLib 的层次化 body/part 标签比传统单句 caption 更接近 embodied skill prior；MotionBook/2D-LFQ 解决了大 motion vocabulary 和 token 表达容量不足的问题；对自动指标失效的分析对后续大规模 motion/VLA 评测很有价值。
- 局限: 生成的是人体 kinematic motion，不输出机器人 action、proprioceptive feedback 或闭环控制；缺少接触力、物体交互、动力学稳定性和任务成功率评测；网页/伪标签数据会引入噪声；HumanML3D 等指标对大规模/OOD 场景不可靠；实时性和细粒度可控性还不是 M0 的重点。
- 对 VLA 领域的贡献: Being-M0 提供了一条和 robot VLA 互补的路线，即先学习大规模 human motion prior，再通过 retargeting、low-level controller 或 policy distillation 接入机器人。它更适合作为 humanoid / whole-body robot 的高层动作语言、行为先验、数据增强来源或 motion planner，而不是端到端 robot policy。
- 与 Being-M0.5 的关系: M0 证明 MotionLib + MotionBook 的 scaling 价值；M0.5 在此基础上转向实时、可控、视觉-语言-运动统一建模，并用 HuMo100M 和 PRQ 补齐随机指令、初始姿态、长时序、未见动作和部位控制能力。
