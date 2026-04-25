# MM-Hand: A 21-DOF Multi-modal Modular Dexterous Robotic Hand with Remote Actuation (2026)

## 基本信息
- 作者: Yuting Chen, Huajie Fang, Ying Wang, Hanyi Chen, Shuo Yang, Peixuan Chen, Jianing Yang, Longting Pan, Xinyi Zhang, Jianlan Luo, Jianyu Chen, Li Chen, Hongyang Li
- 机构: Peking University, Shanghai AI Laboratory, The University of Hong Kong
- arXiv: 2604.17245
- 项目页: https://opendrivelab.com/MM-Hand

## 一句话总结
提出一款 21-DoF 模块化灵巧手 MM-Hand，将远程绳驱、3D 打印模块化结构、in-palm stereo vision 和可拆卸多模态触觉指尖集成到开源低成本平台中，指尖力可达 25N，用真实硬件能力补足 VLA/灵巧操作数据采集和部署的执行端短板。

## 问题
灵巧操作数据和策略越来越依赖人手轨迹、触觉和多指操作，但主流机器人手在成本、可维护性、触觉集成和力输出之间难以平衡：
1. 高端灵巧手昂贵且维护复杂，不利于大规模数据采集；
2. 低成本手常牺牲自由度、力输出或传感能力，难以覆盖人手级操作；
3. 触觉传感通常作为外接模块，和手指机械结构、标定流程割裂；
4. 缺少面向研究复现的完整硬件、标定、遥操作和 benchmark 套件。

## 方法
- **方法线归属**: VLA/灵巧操作硬件基础设施；与 DexCap、EgoDex 这类"人手数据"工作互补，MM-Hand 解决的是机器人执行端和触觉采集端。
- **核心 idea**: 通过模块化机械设计和多模态指尖，把灵巧手从昂贵封闭硬件变成可复制、可维护、可采触觉数据的开放平台。
- **关键技术点**:
  - **21-DoF 人手仿生结构**：5 指设计，覆盖屈伸、外展/内收和腕部/掌部协同所需自由度。
  - **远程绳驱 + 3D 打印模块化结构**：把电机远离手指末端，降低手部重量，同时提升可维护性和可复制性。
  - **多模态可拆卸指尖**：集成高分辨率 tactile sensing，支持按任务替换和维护。
  - **in-palm stereo vision**：掌内双目视觉补足外部/腕部视角在遮挡下的感知盲区。
  - **半自动化标定**：降低多关节、多传感器硬件的部署成本，使数据采集流程更稳定。
  - **配套遥操作和 benchmark**：面向抓取、旋拧、工具使用等多指操作验证硬件能力。

## 实验
- **Benchmark**: 论文自建 MM-Hand real-world manipulation benchmark
- **主要结果**:
  - 展示 21-DoF 灵巧手在抓取、旋转、精细接触和工具相关任务上的可操作性；
  - 指尖力可达约 25N，明显高于许多低成本灵巧手，更适合接触丰富任务；
  - 模块化指尖支持触觉/多模态数据采集，为后续 VLA 训练提供硬件入口。
- **对比基线**: 主要与 Shadow Hand、Allegro Hand、LEAP Hand、Inspire Hand 等灵巧手从自由度、成本、力输出、传感集成和可维护性维度对比。

## 评价
- **优势**:
  1. 硬件定位清晰：不是单纯追求低价，而是在 DoF、力输出、触觉、模块化之间做研究友好的折中；
  2. 对 VLA 数据闭环有直接意义：可同时作为执行器、触觉采集器和遥操作目标；
  3. 模块化指尖降低了触觉传感损坏后的维护成本；
  4. 与 EgoDex/DexCap 等人手数据路线互补，可承接人手轨迹重定向后的真实机器人部署。
- **局限**:
  1. 论文重点是硬件系统，策略学习和跨任务泛化验证有限；
  2. 多模态触觉数据能否显著提升大规模 VLA 仍需后续模型论文验证；
  3. 绳驱结构长期稳定性、回差和维护频率需要更长周期实测；
  4. benchmark 更偏硬件能力展示，尚未形成社区标准评测。
- **对 VLA 领域的贡献**:
  MM-Hand 为"人手数据 -> 灵巧机器人策略"路线提供了更可复制的执行端硬件，使触觉、多指高自由度和真实接触数据更容易进入 VLA 数据循环。
