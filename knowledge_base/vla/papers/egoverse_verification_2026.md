# EgoVerse: An Egocentric Human Dataset for Robot Learning from Around the World (2026)

## 基本信息
- 作者: Ryan Punamiya, Simar Kareer, Zeyi Liu, Josh Citron, Ri-Zhao Qiu, Xiongyi Cai, Alexey Gavryushin, Jiaqi Chen, Davide Liconti, Lawrence Y. Zhu, Patcharapong Aphiwetsa, Baoyu Li, Aniketh Cheluva, Pranav Kuppili, Yangcen Liu, Dhruv Patel, Aidan Gao, Hye-Young Chung, Ryan Co, Renee Zbizika, Jeff Liu, Xiaomeng Xu, Haoyu Xiong, Geng Chen, Sebastiano Oliani, Chenyu Yang, Xi Wang, James Fort, Richard Newcombe, Josh Gao, Jason Chong, Garrett Matsuda, Aseem Doriwala, Marc Pollefeys, Robert Katzschmann, Xiaolong Wang, Shuran Song, Judy Hoffman, Danfei Xu
- 机构: Georgia Institute of Technology, Stanford University, UC San Diego, ETH Zurich, MIT CSAIL, Meta Reality Labs Research, Mecka AI, Scale AI
- arXiv: 2604.07607
- 验证状态: 已验证为机器人学习相关 primary source；不是未解析占位条目

## 一句话总结
EgoVerse 是一个面向 robot learning 的协作式 ego 人类数据平台和数据集：当前 release 含 1,362 小时、80K episodes、1,965 tasks、240 scenes、2,087 demonstrators，并通过多实验室机器人 co-training study 证明 human ego data 可提升 robot policy，但有效 scaling 需要少量 domain-aligned human-robot anchor data。

## 问题
机器人数据昂贵且难以跨机构扩展，而已有 ego 人类数据集多为静态一次性 release，缺少统一格式、持续增长机制和下游 robot transfer 验证。核心问题不是再收一个视频数据集，而是建立可协作扩展、可复现实验的人类数据生态。

## 方法
- 方法线归属: Human Data Pretraining / Co-training 数据基础设施；不是 VLA 架构论文。
- 核心 idea: 用统一采集协议、EgoDB 数据管理系统和多机器人共享评测，把来自不同实验室/工业伙伴的 ego human demonstrations 变成可持续增长的 robot-learning-ready 数据集。
- 关键技术点:
  - EgoVerse-A: 学术伙伴使用 Project Aria glasses，围绕共享 flagship manipulation tasks 收集高一致性数据，用于可控 transfer study。
  - EgoVerse-I: 工业伙伴和社区硬件收集更开放的任务数据，覆盖更广场景与长尾任务。
  - 统一数据格式: egocentric video、3D hand poses、camera motion、task descriptions 和元数据 schema，支持按 task/scene/embodiment/source 过滤训练。
  - EgoDB: 云端聚合、处理和同步系统，将多源 human/robot data 转为训练就绪 PyTorch datasets。
  - Co-training policy: 使用人类和机器人样本联合训练，研究 aligned human data、diverse human data 和 robot demos 的比例关系。

## 实验
- Benchmark: 3 个机器人系统/多实验室复现实验，任务包括 object-in-container、cup-on-saucer、bag-grocery 等；另有 controlled diversity experiments 分析 demonstrator 和 scene scaling。
- 主要结果: 加入 EgoVerse-A human data 在多数机器人/任务的 ID 和 OOD 设置中提升性能，论文报告最高约 30% 相对提升；diverse EgoVerse-A data 或 in-domain aligned human data 单独使用都不足以稳定放大收益，少量 aligned data（例如 2h）作为 anchor 后，2h -> 8h diverse data scaling 才出现正向趋势；demonstrator diversity 和 scene diversity 都能提升泛化，scene diversity 在受限数据预算下尤其关键。
- 对比基线: robot-only / human-robot co-training variants；有无 EgoVerse-A diverse data、有无 in-domain aligned human data 的消融。

## 评价
- 优势: 相比 EgoDex/EgoMimic 的单团队数据集，EgoVerse 强调“living dataset + consortium-scale reproducibility”，并把 human data scaling 是否真正提升 robot policy 作为核心实验问题。
- 局限: 贡献主要是数据平台和实证研究，不提供新的 VLA 架构；有效迁移仍依赖 robot demos 和 aligned human data；论文观察到 Robot B 的 bag-grocery 负迁移，说明人类策略与机器人具身不匹配仍会伤害 co-training；更开放的 EgoVerse-I 如何直接用于 policy 仍是未来工作。
- 对 VLA 领域的贡献: 为 Human Data Pretraining 支线提供了“数据生态与 scaling 条件”的强证据：仅有大规模 diverse ego data 不够，必须有少量任务/场景语义对齐的 anchor 数据才能稳定转化为 robot policy 性能。
