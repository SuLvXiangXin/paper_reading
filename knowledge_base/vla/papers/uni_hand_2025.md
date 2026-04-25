# Uni-Hand: Universal Hand Motion Forecasting in Egocentric Views (2025)

## 基本信息
- 作者: Junyi Ma, Wentao Bao, Jingyi Xu, Guanzhong Sun, Yu Zheng, Erhang Zhang, Xieyuanli Chen, Hesheng Wang
- 机构: Shanghai Jiao Tong University, Meta Reality Labs, China University of Mining and Technology, National University of Defense Technology
- arXiv: 2511.12878
- 项目: https://irmvlab.github.io/unihand.github.io

## 一句话总结
Uni-Hand 将 egocentric hand trajectory prediction 从“预测手中心点”扩展到多模态输入、多维 2D/3D、多目标 wrist/finger joint 和 hand-object interaction state 预测，并首次用 ALOHA 真机任务验证 hand-motion forecasting 可以直接转成机器人末端轨迹与抓取时序。

## 问题
现有 egocentric hand trajectory prediction 通常只预测 hand center，缺少手腕/手指级目标、语言任务条件和与机器人执行的闭环验证；同时 ego 视角中头部运动和手部运动耦合，导致仅从视觉历史预测未来手轨迹容易混入相机 egomotion。

## 方法
- 方法线归属: Human Data Pretraining for VLA 的前处理/接口层；更准确地说是 egocentric hand motion forecasting，而不是端到端 VLA policy。
- 核心 idea: 用统一的 hand-motion forecasting 模型预测机器人可用的未来手腕/手指 waypoint 和接触状态，把人类第一人称运动意图转成低层 policy 或轨迹规划的中间监督。
- 关键技术点:
  - 视觉-语言融合、全局上下文和 task-aware text embedding 注入，用语言指令区分同一场景下的不同操作目标。
  - dual-branch diffusion 同时建模 head/camera motion 和 hand motion，缓解手-头运动纠缠。
  - target indicator 支持在同一模型内预测 hand center、wrist、thumb/index/middle fingertip 等不同目标点。
  - 额外预测 contact/separation 状态，用于决定机器人 gripper 的开合时机。
  - Hand-ALOHA-Transfer benchmark 将预测的手部 waypoint 映射为 ALOHA 末端轨迹和抓取动作，验证下游可执行性。

## 实验
- Benchmark: EgoPAT3D-DT、H2O-PT、HOT3D-Clips、CABH/CABH-E；下游包含 Hand-ALOHA-Transfer、EPIC-KITCHENS action anticipation/recognition。
- 主要结果: 在 2D/3D hand center forecasting 和 multi-joint forecasting 上整体优于 CVH/OCT/USST/S-Mamba/Diff-IP/MADiff；HAT 真机 5 个任务中 Uni-Hand 成功率为 100%/90%/80%/80%/20%，S-Mamba 为 40%/20%/0%/0%/0%。
- 对比基线: CVH, OCT, USST, S-Mamba, Diff-IP2D/3D, MADiff/MADiff3D；机器人转移中主要对比 S-Mamba。

## 评价
- 优势: 把 hand trajectory prediction 明确推向“可服务机器人”的接口层，目标从中心点扩展到 wrist/finger/contact timing，比 EgoDex 的离线轨迹 benchmark 更接近下游控制。
- 局限: 不是端到端机器人 policy；机器人执行仍依赖手工设计的人手 waypoint 到 EEF/gripper 的映射；默认 contact 状态存在人工标注；长时序复杂 pick-and-place 任务仍只有 20% 成功率。
- 对 VLA 领域的贡献: 为 EgoScale/Being-H 系列这类大规模 ego 人手数据路线提供一个可插拔的 hand-motion target 设计参考，说明“预测哪些手部点”和“何时接触”比单纯预测 hand center 更适合作为 robot policy transfer 的中间监督。
