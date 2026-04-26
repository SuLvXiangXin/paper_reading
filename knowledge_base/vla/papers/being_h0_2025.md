# Being-H0: Vision-Language-Action Pretraining from Large-Scale Human Videos (2025)

## 基本信息
- 作者: Hao Luo, Yicheng Feng, Wanpeng Zhang, Sipeng Zheng, Ye Wang, Haoqi Yuan, Jiazheng Liu, Chaoyi Xu, Qin Jin, Zongqing Lu
- 机构: Peking University, Renmin University of China, BeingBeyond
- arXiv: 2507.15597
- 项目: https://research.beingbeyond.com/being-h0
- 代码/模型: https://github.com/BeingBeyond/Being-H0, https://huggingface.co/BeingBeyond/Being-H0
- 日期: 2025.07.21

## 一句话总结
Being-H0 首次把大规模人类手部视频显式转成 VLA 预训练信号：用 UniHand 的 MANO 手部运动 token 做 physical instruction tuning，再通过少量机器人后训练迁移到 Franka+Inspire 灵巧手任务，证明"人手作为 foundation manipulator"可以为 VLA 提供可迁移的操作先验。

## 问题
灵巧操作 VLA 的主要瓶颈不是视觉语言能力，而是动作监督稀缺且形态不统一：机器人遥操作数据规模小，仿真存在 sim-to-real gap，Web/ego 人类视频虽然丰富但缺少可直接训练策略的动作标签。H0 要回答的问题是：能否像 visual instruction tuning 一样，将人手视频转成显式的 vision-language-motion 指令数据，让 VLA 先学会人类手部运动，再迁移到机器人控制？

## 方法
- 方法线归属: Human Data Pretraining for VLA；VLM + Action Token/MLP Action Head；Being-H 系列的人类中心预训练起点。
- 核心 idea: 将人手视为高自由度"通用操作器"，把 RGB/语言/手部 MANO 运动统一成自回归 token 序列；预训练阶段学习视觉-语言-运动对齐，后训练阶段用 learnable action queries + MLP 投影到机器人末端位姿和灵巧手关节。
- 关键技术点:
  - **Physical Instruction Tuning**: 包含人类视频 VLA 预训练、物理空间对齐、机器人后训练三步；用相同视觉/文本 backbone 贯穿 motion generation、motion translation 和 robot control。
  - **Part-Level Motion Tokenization**: 基于 GRQ-VAE，将手腕全局位姿和手指精细关节拆开量化；默认 MANO-D162，8 层 GRQ、wrist/finger 各 4096 codebook，每秒每只手 128 个 motion tokens。
  - **UniHand / UniHand-2.5M**: 聚合 11 个来源（motion capture、VR、pseudo annotation），总计 444.1K trajectories、130M frames、1155 小时、166.5M motion-instruction pairs；受算力限制从中均衡采样 2.5M 样本训练。
  - **动作表示**: 预训练动作是离散 MANO hand-motion tokens；机器人后训练动作是 action chunk，包含 Franka 末端位姿和 Inspire 6-DoF 手关节。
  - **数据标注**: 用 Gemini 生成 chunk 级/秒级层次化动作描述，构造 motion generation、motion translation、contextual motion prediction 三类指令任务，并做 view-invariant motion distribution balancing。

## 实验
- Benchmark: 手部运动生成/翻译、长时序手部运动生成、真实 Franka Research 3 + Inspire hand 灵巧操作。
- 主要结果:
  - 手部运动生成随模型规模提升：14B 在 visual-grounded generation 上 MPJPE 6.87/8.11 cm（head/tail），优于适配后的 GR00T N1.5 9.82/15.35 cm。
  - 运动 token 格式学习明显依赖规模：valid rate 从 1B 的 64.8% 提升到 8B 的 99.8%、14B 的 100.0%。
  - 真机每任务 20 次随机试验，Being-H0 在 Pick-Place-Toy seen/unseen/clutter、Close-Toolbox、Close-Lid、Pour-Cup、Unfold-Clothes 上分别为 75/65/60/85/60/100/75%，整体优于 InternVL3 和 GR00T N1.5；Pour-Cup 达 100%，Unfold-Clothes 达 75%。
- 对比基线: GR00T N1.5（同样含 ego/human 数据但偏隐式 latent action）、InternVL3（同架构规模但无 physical instruction tuning）。

## 评价
- 优势: 首次把人类手部视频显式转成 VLA 可训练的 motion-token 指令数据；part-level tokenizer 对精细手指和手腕轨迹区分清晰；真实灵巧手实验显示人手运动先验能改善未见物体、杂乱场景、倒液和布料展开等任务。
- 局限: H0 仍是单一机器人后训练验证，跨具身泛化尚未系统解决；预训练只用 2.5M 子集，远小于完整 UniHand；后训练控制头是简单 MLP/action-query 方案，不如后续 flow matching 稳定；Ego4D/EPIC-KITCHENS 等更大野外视频因手部遮挡/动态视角暂未充分使用。
- 对 VLA 领域的贡献: 建立 Being-H 系列的第一块基石：把"人手运动是机器人操作的物理母语"从口号变成可训练的 motion-token VLA recipe。

### 与 H0.5 / JALA / EgoScale 的关系
- **vs H0.5**: H0 证明人手 motion token 预训练有效；H0.5 将其扩展到 UniHand-2.0、统一动作空间、flow matching、MoT/MoF、30 种具身和跨具身部署。
- **vs JALA**: JALA 继承 H0 的 hand-motion tokenizer/InternVL3 框架，但用 predictive embedding 与 latent action joint alignment 支持无标注野外视频；H0 仍主要依赖显式 hand-motion 伪标签。
- **vs EgoScale**: 两者都主张 ego human video scaling；H0 的贡献是显式 motion-token 指令预训练和开源路线，EgoScale 更偏 flow policy + retargeted joint-space + Scale/Align/Post-train 三阶段，并给出 20K 小时 scaling law。
