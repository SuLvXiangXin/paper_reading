# Helix: A Vision-Language-Action Model for Generalist Humanoid Control (2025)

## 基本信息
- 作者: Figure AI 团队（官方页未列出个人作者）
- 机构: Figure AI
- arXiv: 不适用
- 来源类型: 官方技术页/非论文
- 发布日期: 2025-02-20
- 链接: https://www.figure.ai/news/helix

## 一句话总结
Helix 是 Figure 的闭源 humanoid VLA 技术发布：用 7B System 2 VLM 在低频产生语义 latent，再由 80M System 1 visuomotor transformer 在 200Hz 输出 35-DoF 上半身连续控制，在约 500 小时遥操作数据上端到端训练，展示单一权重完成多种家用物体操作和双机器人协作，但证据主要是官方视频与内部 claim，没有公开标准 benchmark。

## 问题
传统 VLM 具备语义泛化但推理太慢，传统 visuomotor policy 控制快但泛化窄；类人机器人的上半身控制又包含头、躯干、双臂、手腕与手指，动作维度和控制频率都高于常见夹爪平台。Helix 要解决的是：如何把互联网 VLM 的常识和语言理解转成高频、连续、全上半身的 humanoid 控制，同时避免每个任务单独写程序或单独微调。

## 方法
- 方法线归属: VLM + 连续 visuomotor policy / 分层 VLA；不是公开论文中的 diffusion/flow head，而是 Figure 的 System 1 / System 2 闭源连续动作变体。
- 核心 idea: 将慢速语义理解和快速闭环控制拆成两个可异步运行的神经模块，并通过一个连续 latent 向量连接；S2 负责理解场景和语言，S1 负责把 latent 条件化为高频动作。
- 关键技术点:
  - System 2: 7B open-weight VLM，使用单目机器人图像、腕部位姿和手指状态，结合自然语言命令输出单个连续语义 latent。
  - System 1: 80M cross-attention encoder-decoder transformer，带全卷积多尺度视觉 backbone，从 S2 latent、图像和本体状态生成低层动作。
  - 动作表示: 直接连续回归，不走离散 action token；输出 35-DoF 上半身控制，包括腕部目标、手指屈伸/外展、头部与躯干方向，并加入合成的任务完成百分比动作作为终止信号。
  - 训练数据: 官方称约 500 小时多机器人、多操作员遥操作数据；用自动标注 VLM 对片段生成 hindsight instruction，并排除训练中出现过的物体用于评测。
  - 训练方式: raw pixels + text 到连续动作端到端训练，标准 regression loss，梯度通过 S1 到 S2 的 latent 通道回传；单阶段、单权重、无任务专用 action head。
  - 部署方式: S2 以约 7-9Hz 异步更新共享 latent，S1 维持 200Hz 控制环；训练时加入 S1/S2 输入时间偏移以匹配部署延迟。

## 实验
- Benchmark: 无公开标准 benchmark；没有 LIBERO、RoboCasa、真实家庭标准套件等可复现评测。
- 公开视频/内部 claim:
  - 官方视频展示双机器人协作整理杂货、抽屉/冰箱操作、不同物体 pick-and-place 和跨机器人 handover。
  - 官方称单一权重可操作数千个未见家庭物体，并可在 onboard embedded low-power GPUs 上运行。
  - 官方称约 500 小时数据即可覆盖多任务上半身控制，数据规模小于此前大规模 VLA 数据集的 5%。
- 公开 benchmark:
  - 未提供公开数据、模型、评测协议或统计显著性结果。
- 对比基线:
  - 主要是与 prior VLA/BC 方法的定性比较，如动作 token 难以扩展到高维 humanoid 控制、专用 BC 泛化差；没有可复现数值对比。

## 评价
- 优势: Helix 把 humanoid 上半身 35-DoF、200Hz 连续控制放进 VLA 讨论，提出了清晰的慢语义 S2 + 快控制 S1 异步部署范式；对高频 humanoid 控制，比自回归 action token 更符合控制频率和动作维度需求。
- 局限: 闭源、非论文、无公开 benchmark；数千未见物体泛化、商业可部署等表述来自官方 claim，不能等同于经过外部验证的学术结果；训练数据、失败率、episode 数和评测分布都不完整。
- 对 VLA 领域的贡献: 可作为 Figure humanoid VLA 路线的起点，位置类似闭源工业 release card：它强调连续动作、高频控制、单一权重与异步分层部署，和 π0/π0.5 的 VLM+continuous-action 方向相邻，但不是 diffusion/flow matching 论文线。
