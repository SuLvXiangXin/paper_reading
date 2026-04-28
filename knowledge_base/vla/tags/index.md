# VLA Tag Taxonomy

This file defines preferred tag names for VLA paper cards. Use these names first when adding `## 标签` to new papers.

## method_tags
- VLM + Action Token: VLM/LLM directly emits discretized robot action tokens, e.g. RT-2 and OpenVLA.
- VLM + Diffusion/Flow Head: VLM features condition continuous action generation through diffusion or flow matching, e.g. pi0 and pi0.5.
- Transformer + Diffusion Head: Non-VLM or lightweight transformer policy with diffusion action head, e.g. Octo/RDT-style policies.
- Latent Action Pretraining: Learn latent action tokens from action-free video or weak action supervision.
- Human Data Pretraining: Use egocentric human video, hand motion, or human demonstrations to pretrain robot policies.
- Hierarchical VLA: Separate high-level planning/memory/subtask prediction from low-level action generation.
- World Model + VLA: Use video/world/action models for prediction, data generation, value estimation, or policy conditioning.
- VLA RL Post-training: Improve pretrained VLA policies with online RL, rejection sampling, advantage labels, or value guidance.
- Lightweight VLA: Reduce model size, inference cost, or deployment footprint while preserving VLA capability.
- VLA Reasoning: Explicitly improve affordance, spatial, geometric, or chain-of-thought reasoning for VLA.

## task_tags
- manipulation
- dexterous manipulation
- mobile manipulation
- bimanual manipulation
- long-horizon
- long-memory
- navigation
- cross-embodiment
- humanoid loco-manipulation
- partial observability

## component_tags
- action chunking
- action tokenization
- flow matching
- diffusion policy
- memory
- world-action model
- visual encoder
- spatial perception
- 3D geometry
- tactile sensing
- hierarchical planning
- value model
- reward model
- policy distillation

## benchmark_tags
- LIBERO
- ALOHA
- CALVIN
- RLBench
- RoboCasa
- SimplerEnv
- DROID
- BridgeData V2
- Open X-Embodiment
- real-robot

## data_tags
- robot demonstrations
- human video
- egocentric video
- teleoperation
- cross-embodiment data
- synthetic data
- world-model generated data
- tactile data
- internet data co-training

## robot_tags
- Franka
- ALOHA
- WidowX
- Google Robot
- UR5
- Unitree G1
- humanoid
- dexterous hand

## application_tags
- open-source
- real-robot
- simulation
- memory
- humanoid
- production deployment
- data collection
- post-training
- reasoning
- spatial grounding
