# Frontier VLA / Robot Foundation Model Paper List

> Created: 2026-04-25  
> Updated: 2026-04-25  
> Scope: company/team/person paper list only. No paper cards were created and no knowledge taxonomy was updated.  
> Grouping rule: grouped by company / team / person first; Ego / human-video related works are also collected in a separate cross-cutting section.

## Legend

- **To read**: candidate for later learning.
- **Existing card**: this repo already has a paper card; keep it in the list for completeness.
- **Tech page only**: company release / project page found, but no standalone paper found in this pass.
- **Needs verification**: name/entity appears ambiguous or needs another focused pass before learning.

## BeingBeyond / 智在无界

Source priority: [BeingBeyond GitHub org](https://github.com/BeingBeyond), [Being-H family repo](https://github.com/BeingBeyond/Being-H), official research pages.

### Being-H / VLA / WAM Core

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Being-H0: Vision-Language-Action Pretraining from Large-Scale Human Videos | 2025 | [arXiv:2507.15597](https://arxiv.org/abs/2507.15597), [project](https://beingbeyond.github.io/Being-H0), [repo](https://github.com/BeingBeyond/Being-H0) | To read | First Being-H release; human-video VLA pretraining. |
| Being-H0.5: Scaling Human-Centric Robot Learning for Cross-Embodiment Generalization | 2026 | [arXiv:2601.12993](https://arxiv.org/abs/2601.12993), [project](https://research.beingbeyond.com/being-h05), [repo](https://github.com/BeingBeyond/Being-H) | Existing card | Already in `papers/being_h05_2026.md`. |
| Being-H0.7: A Latent World-Action Model from Egocentric Videos | 2026 | [project](https://research.beingbeyond.com/being-h07), [PDF](https://research.beingbeyond.com/projects/being-h07/being-h07.pdf), [repo](https://github.com/BeingBeyond/Being-H) | To read | Latest Being-H WAM release; official page says 200K hours ego video + 15K hours robot demos. |
| JALA: Joint-Aligned Latent Action: Towards Scalable VLA Pretraining in the Wild | 2026 | [arXiv:2602.21736](https://arxiv.org/abs/2602.21736), [project](https://research.beingbeyond.com/jala), [repo](https://github.com/BeingBeyond/JALA) | Existing card | Already in `papers/jala_2026.md`. |
| Rethinking Visual-Language-Action Model Scaling: Alignment, Mixture, and Regularization | 2026 | [arXiv:2602.09722](https://arxiv.org/abs/2602.09722), [project](https://research.beingbeyond.com/rethink_vla), [repo](https://github.com/BeingBeyond/Rethink_VLA) | To read | Controlled VLA scaling study; appears in Being-H repo's "projects based on Being-H". |
| DiG-Flow: Discrepancy-Guided Flow Matching for Robust VLA Models | 2025 | [arXiv:2512.01715](https://arxiv.org/abs/2512.01715), [project](https://beingbeyond.github.io/DiG-Flow), [repo](https://github.com/BeingBeyond/DiG-Flow) | To read | Robust flow-matching VLA method. |
| VIPA-VLA: Spatial-Aware VLA Pretraining through Visual-Physical Alignment from Human Videos | 2025 | [arXiv:2512.13080](https://arxiv.org/abs/2512.13080), [project](https://beingbeyond.github.io/VIPA-VLA), [repo](https://github.com/BeingBeyond/VIPA-VLA) | To read | Human-video physical alignment for spatial-aware VLA pretraining. |
| BeTTER: Unmasking the Illusion of Embodied Reasoning in Vision-Language-Action Models | 2026 | [arXiv:2604.18000](https://arxiv.org/abs/2604.18000), [project](https://research.beingbeyond.com/better), [repo](https://github.com/BeingBeyond/BeTTER) | To read | Diagnostic benchmark for embodied reasoning failures in VLAs. |
| PTR: Conservative Offline Robot Policy Learning via Posterior-Transition Reweighting | 2026 | [arXiv:2603.16542](https://arxiv.org/abs/2603.16542), [project](https://research.beingbeyond.com/ptr), [repo](https://github.com/BeingBeyond/PTR) | To read | Offline robot policy learning; listed as Being-H-based project. |
| DexHiL: A Human-in-the-Loop Framework for VLA Model Post-Training in Dexterous Manipulation | 2026 | [arXiv:2603.09121](https://arxiv.org/abs/2603.09121), [project](https://chenzhongxi-sjtu.github.io/dexhil/) | To read | Not a BeingBeyond repo, but listed by Being-H repo as a project built on Being-H. |

### Humanoid / Whole-Body / Dexterous Control

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Being-0: A Humanoid Robotic Agent with Vision-Language Models and Modular Skills | 2025 | [arXiv:2503.12533](https://arxiv.org/abs/2503.12533), [project](https://beingbeyond.github.io/Being-0), [repo](https://github.com/BeingBeyond/Being-0) | To read | Humanoid agent with VLM + modular skills. |
| FAST: General Humanoid Whole-Body Control via Pretraining and Fast Adaptation | 2026 | [arXiv:2602.11929](https://arxiv.org/abs/2602.11929), [project](https://beingbeyond.github.io/FAST/), [repo](https://github.com/BeingBeyond/FAST) | To read | Not PI FAST; BeingBeyond whole-body controller. |
| Jaeger: Dual-Level Humanoid Whole-Body Controller | 2025 | [arXiv:2505.06584](https://arxiv.org/abs/2505.06584), [repo](https://github.com/BeingBeyond/Jaeger) | To read | Dual-level whole-body controller; missing in the earlier pass. |
| BumbleBee: From Experts to a Generalist: Toward General Whole-Body Control for Humanoid Robots | 2025 | [arXiv:2506.12779](https://arxiv.org/abs/2506.12779), [project](https://beingbeyond.github.io/BumbleBee/), [repo](https://github.com/BeingBeyond/BumbleBee) | To read | NeurIPS 2025 spotlight according to repo. |
| RLPF: RL from Physical Feedback: Aligning Large Motion Models with Humanoid Control | 2025 | [arXiv:2506.12769](https://arxiv.org/abs/2506.12769), [project](https://beingbeyond.github.io/RLPF), [repo](https://github.com/BeingBeyond/RLPF) | To read | Motion model alignment with physical feedback. |
| DemoGrasp: Universal Dexterous Grasping from a Single Demonstration | 2025 | [arXiv:2509.22149](https://arxiv.org/abs/2509.22149), [project](https://beingbeyond.github.io/DemoGrasp/), [repo](https://github.com/BeingBeyond/DemoGrasp) | To read | ICLR 2026 according to repo. |
| DemoHLM: From One Demonstration to Generalizable Humanoid Loco-Manipulation | 2025 | [arXiv:2510.11258](https://arxiv.org/abs/2510.11258), [project](https://beingbeyond.github.io/DemoHLM/), [repo](https://github.com/BeingBeyond/DemoHLM) | To read | One-demo humanoid loco-manipulation. |
| DemoFunGrasp: Universal Dexterous Functional Grasping via Demonstration-Editing Reinforcement Learning | 2025 | [arXiv:2512.13380](https://arxiv.org/abs/2512.13380), [project](https://beingbeyond.github.io/DemoFunGrasp/), [repo](https://github.com/BeingBeyond/DemoFunGrasp) | To read | CVPR 2026 according to repo. |
| UniTacHand: Unified Spatio-Tactile Representation for Human to Robotic Hand Skill Transfer | 2025 | [arXiv:2512.21233](https://arxiv.org/abs/2512.21233), [project](https://beingbeyond.github.io/UniTacHand/), [repo](https://github.com/BeingBeyond/UniTacHand) | To read | Human tactile glove to robotic hand transfer. |

### Motion / Vision-Language / Ego Understanding

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Being-M0: Scaling Motion Generation Models with Million-Level Human Motions | 2024 | [arXiv:2410.03311](https://arxiv.org/abs/2410.03311), [project](https://beingbeyond.github.io/Being-M0), [repo](https://github.com/BeingBeyond/Being-M0) | To read | Human motion foundation model. |
| Being-M0.5: A Real-Time Controllable Vision-Language-Motion Model | 2025 | [arXiv:2508.07863](https://arxiv.org/abs/2508.07863), [project](https://beingbeyond.github.io/Being-M0.5), [repo](https://github.com/BeingBeyond/Being-M0.5) | To read | Real-time controllable VL motion model. |
| Being-VL-0: From Pixels to Tokens: Byte-Pair Encoding on Quantized Visual Modalities | 2024 | [arXiv:2410.02155](https://arxiv.org/abs/2410.02155), [repo](https://github.com/BeingBeyond/Being-VL-0) | To read | ICLR 2025 according to repo. |
| Being-VL-0.5: Unified Multimodal Understanding via Byte-Pair Visual Encoding | 2025 | [arXiv:2506.23639](https://arxiv.org/abs/2506.23639), [project](https://beingbeyond.github.io/Being-VL-0.5), [repo](https://github.com/BeingBeyond/Being-VL-0.5) | To read | ICCV 2025 highlight according to repo. |
| MEgoHand: Multimodal Egocentric Hand-Object Interaction Motion Generation | 2025 | [arXiv:2505.16602](https://arxiv.org/abs/2505.16602), [project](https://beingbeyond.github.io/MEgoHand/), [repo](https://github.com/BeingBeyond/MEgoHand) | To read | Ego hand-object motion generation. |
| OpenMMEgo: Enhancing Egocentric Understanding for LMMs with Open Weights and Data | 2025 | [NeurIPS page](https://neurips.cc/virtual/2025/loc/san-diego/poster/119544), [repo](https://github.com/BeingBeyond/OpenMMEgo) | To read | NeurIPS 2025; ego-video LMM data/model/benchmark. |

### Open-Source / Platform

| Release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| BeingBeyond D1 SDK | 2026 | [repo](https://github.com/BeingBeyond/Beingbeyond_D1) | Tech page only | Official D1 SDK / platform repo; no standalone paper confirmed in this pass. |

## GigaAI / 极佳

Source priority: [GigaAI-research GitHub org](https://github.com/GigaAI-research), [open-gigaai GitHub org](https://github.com/open-gigaai), [GigaAI-Research Hugging Face papers](https://huggingface.co/GigaAI-Research/papers), project pages.

### Robotics / VLA / Embodied World-Action Models

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| VLA-R1: Enhancing Reasoning in Vision-Language-Action Models | 2025 | [arXiv:2510.01623](https://arxiv.org/abs/2510.01623), [project](https://gigaai-research.github.io/VLA-R1), [code](https://github.com/GigaAI-research/VLA-R1) | To read | Reasoning-enhanced VLA with RLVR/GRPO. |
| SwiftVLA: Unlocking Spatiotemporal Dynamics for Lightweight VLA Models at Minimal Overhead | 2025 | [arXiv:2512.00903](https://arxiv.org/abs/2512.00903), [project](https://swiftvla.github.io/), [code](https://github.com/GigaAI-research/SwiftVLA) | To read | Lightweight VLA with 4D spatiotemporal features. |
| GigaBrain-0: A World Model-Powered Vision-Language-Action Model | 2025 | [arXiv:2510.19430](https://arxiv.org/abs/2510.19430), [project](https://gigabrain0.github.io/), [repo](https://github.com/open-gigaai/giga-brain-0) | To read | Core GigaAI VLA model. |
| GigaBrain-0.5M*: a VLA That Learns From World Model-Based Reinforcement Learning | 2026 | [arXiv:2602.12099](https://arxiv.org/abs/2602.12099), [project](https://gigabrain05m.github.io/) | To read | RAMP / world-model-conditioned RL. |
| GigaWorld-0: World Models as Data Engine to Empower Embodied AI | 2025 | [arXiv:2511.19861](https://arxiv.org/abs/2511.19861), [project](https://giga-world-0.github.io/), [repo](https://github.com/open-gigaai/giga-world-0) | To read | World model used as embodied AI data engine. |
| GigaWorld-Policy: An Efficient Action-Centered World-Action Model | 2026 | [arXiv:2603.17240](https://arxiv.org/abs/2603.17240), [project](https://gigaai-research.github.io/GigaWorld-Policy/), [repo](https://github.com/open-gigaai/giga-world-policy) | To read | Action-centered WAM; 9x faster than WAM baseline per paper/project. |
| π-StepNFT: Wider Space Needs Finer Steps in Online RL for Flow-based VLAs | 2026 | [arXiv:2603.02083](https://arxiv.org/abs/2603.02083), [project](https://wangst0181.github.io/pi-StepNFT/) | To read | Critic-free, likelihood-free online RL for flow-based VLAs. |
| ViVa: A Video-Generative Value Model for Robot Reinforcement Learning | 2026 | [arXiv:2604.08168](https://arxiv.org/abs/2604.08168), [project](https://viva-value-model.github.io/) | To read | Video-generative value model for robot RL. |
| EmbodieDreamer: Advancing Real2Sim2Real Transfer for Policy Training via Embodied World Modeling | 2025 | [arXiv:2507.05198](https://arxiv.org/abs/2507.05198), [repo](https://github.com/GigaAI-research/EmbodieDreamer) | To read | Real2Sim2Real policy training with embodied world modeling. |
| MimicDreamer: Aligning Human and Robot Demonstrations for Scalable VLA Training | 2025 | [arXiv:2509.22199](https://arxiv.org/abs/2509.22199), [repo](https://github.com/GigaAI-research/MimicDreamer) | To read | Human-to-robot demo alignment for VLA training; also listed in Ego cluster. |
| EgoDemoGen: Novel Egocentric Demonstration Generation Enables Viewpoint-Robust Manipulation | 2025 | [arXiv:2509.22578](https://arxiv.org/abs/2509.22578), [project](https://egodemogen.github.io/), [repo](https://github.com/GigaAI-research/EgoDemoGen) | To read | Ego-view manipulation demo generation; also listed in Ego cluster. |

### Driving / Reconstruction / Physical World Models

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| DriveDreamer: Towards Real-world-driven World Models for Autonomous Driving | 2023 | [arXiv:2309.09777](https://arxiv.org/abs/2309.09777), [project](https://drivedreamer.github.io/), [repo](https://github.com/GigaAI-research/DriveDreamer) | To read | ECCV 2024; early GigaAI driving world-model line. |
| DriveDreamer-2: LLM-Enhanced World Models for Diverse Driving Video Generation | 2024 | [arXiv:2403.06845](https://arxiv.org/abs/2403.06845), [project](https://drivedreamer2.github.io/), [repo](https://github.com/GigaAI-research/DriveDreamer2) | To read | User-controllable multi-view driving video generation. |
| DriveDreamer4D: World Models Are Effective Data Machines for 4D Driving Scene Representation | 2024 | [arXiv:2410.13571](https://arxiv.org/abs/2410.13571), [project](https://drivedreamer4d.github.io/), [repo](https://github.com/GigaAI-research/DriveDreamer4D) | To read | CVPR 2025; world-model priors for 4D driving representation. |
| ReconDreamer: Crafting World Models for Driving Scene Reconstruction via Online Restoration | 2024 | [arXiv:2411.19548](https://arxiv.org/abs/2411.19548), [project](https://recondreamer.github.io/), [repo](https://github.com/GigaAI-research/ReconDreamer) | To read | CVPR 2025; driving scene reconstruction. |
| ReconDreamer++: Harmonizing Generative and Reconstructive Models for Driving Scene Representation | 2025 | [arXiv:2503.18438](https://arxiv.org/abs/2503.18438), [repo](https://github.com/GigaAI-research/ReconDreamer-Plus) | To read | Follow-up to ReconDreamer; improves novel-trajectory rendering. |
| ReconDreamer-RL: Enhancing Reinforcement Learning via Diffusion-based Scene Reconstruction | 2025 | [arXiv:2508.08170](https://arxiv.org/abs/2508.08170), [repo](https://github.com/GigaAI-research/ReconDreamer-RL) | To read | Driving RL with reconstruction + diffusion priors. |
| DriveGen3D: Boosting Feed-Forward Driving Scene Generation with Efficient Video Diffusion | 2025 | [arXiv:2510.15264](https://arxiv.org/abs/2510.15264), [project](https://lhmd.top/drivegen3d) | To read | GigaAI-Research HF paper; driving scene generation. |
| DriveDreamer-Policy: A Geometry-Grounded World-Action Model for Unified Generation and Planning | 2026 | [arXiv:2604.01765](https://arxiv.org/abs/2604.01765) | To read | GigaAI-Research HF paper; autonomous-driving WAM. |
| ReconPhys: Reconstruct Appearance and Physical Attributes from Single Video | 2026 | [arXiv:2604.07882](https://arxiv.org/abs/2604.07882), [project](https://chuanshuogushi.github.io/ReconPhys/) | To read | GigaAI-Research HF paper; physical reconstruction from video. |
| GeoWorld: Geometric World Models | 2026 | [arXiv:2602.23058](https://arxiv.org/abs/2602.23058) | Needs verification | Appears on GigaAI-Research HF activity; affiliation/project ownership needs verification. |
| MWM: Mobile World Models for Action-Conditioned Consistent Prediction | 2026 | [arXiv:2603.07799](https://arxiv.org/abs/2603.07799), [project](https://aigeeksgroup.github.io/MWM) | Needs verification | Appears on GigaAI-Research HF activity, but project is AIGeeksGroup; keep separate until verified. |

### Video / Human / 3D Generation

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| HumanDreamer: Generating Controllable Human-Motion Videos via Decoupled Generation | 2025 | [arXiv:2503.24026](https://arxiv.org/abs/2503.24026), [repo](https://github.com/GigaAI-research/HumanDreamer) | To read | CVPR 2025; MotionVid / human-motion video generation. |
| HumanDreamer-X: Photorealistic Single-image Human Avatars Reconstruction via Gaussian Restoration | 2025 | [arXiv:2504.03536](https://arxiv.org/abs/2504.03536), [repo](https://github.com/GigaAI-research/HumanDreamer-X) | To read | Single-image human avatar reconstruction. |
| Motion-R1: Chain-of-Thought Reasoning and Reinforcement Learning for Human Motion Generation | 2025 | [arXiv:2506.10353](https://arxiv.org/abs/2506.10353), [project](https://motion-r1.github.io/), [repo](https://github.com/GigaAI-research/Motion-R1) | To read | Human motion generation with decomposed CoT + RL binding. |
| GigaVideo-1: Advancing Video Generation via Automatic Feedback with 4 GPU-Hours Fine-Tuning | 2025 | [arXiv:2506.10639](https://arxiv.org/abs/2506.10639), [repo](https://github.com/GigaAI-research/GigaVideo-1) | To read | Efficient video-generation fine-tuning. |
| WonderTurbo: Generating Interactive 3D World in 0.72 Seconds | 2025 | [arXiv:2504.02261](https://arxiv.org/abs/2504.02261), [project](https://wonderturbo.github.io/), [repo](https://github.com/GigaAI-research/WonderTurbo) | To read | ICCV 2025; interactive 3D world generation acceleration. |
| WonderFree: Enhancing Novel View Quality and Cross-View Consistency for 3D Scene Exploration | 2025 | [arXiv:2506.20590](https://arxiv.org/abs/2506.20590), [project](https://wonder-free.github.io/), [repo](https://github.com/GigaAI-research/WonderFree) | To read | Interactive 3D scene exploration. |

### Open-Source Infrastructure / Benchmarks

| Release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| GigaModels | 2025-2026 | [repo](https://github.com/open-gigaai/giga-models) | Tech page only | Includes refactored PI0/PI0.5 and Cosmos-Predict2.5/Cosmos-Transfer2.5 implementations. |
| GigaTrain | 2025-2026 | [repo](https://github.com/open-gigaai/giga-train) | Tech page only | Training framework. |
| GigaDatasets | 2025-2026 | [repo](https://github.com/open-gigaai/giga-datasets) | Tech page only | Data processing/curation/visualization framework. |
| GigaBrain Challenge 2026 | 2026 | [repo](https://github.com/GigaAI-research/GigaBrain-Challenge-2026) | Tech page only | CVPR 2026 workshop challenge; not a standalone paper in this pass. |
| PhysClaw*: Physical Continual Learning Agent Workflow | 2026 | [repo](https://github.com/GigaAI-research/PhysClaw) | Tech page only | Early development framework for distributed physical AI agents. |

## Physical Intelligence / π

Source: [Physical Intelligence research page](https://www.pi.website/research).

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| π0: A Vision-Language-Action Flow Model for General Robot Control | 2024 | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164), [blog](https://physicalintelligence.company/blog/pi0) | Existing card | Already in `papers/pi0_2024.md`. |
| π0.5: A Vision-Language-Action Model with Open-World Generalization | 2025 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054), [blog](https://pi.website/blog/pi05) | Existing card | Already in `papers/pi05_2025.md`. |
| FAST: Efficient Robot Action Tokenization | 2025 | [PI research](https://www.pi.website/research/fast) | To read | Official PI research list. |
| Teaching Robots to Listen and Think Harder | 2025 | [PI research](https://www.pi.website/research/hirobot) | To read | Official PI research list. |
| Emergence of Human to Robot Transfer in VLAs | 2025 | [PI research](https://www.pi.website/research/human_to_robot) | Existing card | Already in `papers/emergence_h2r_transfer_2025.md`. |
| VLAs that Train Fast, Run Fast, and Generalize Better | 2025 | [PI research](https://www.pi.website/research/knowledge_insulation) | To read | Official PI research list. |
| VLAs with Long and Short-Term Memory | 2025 | [PI research](https://www.pi.website/research/memory) | Existing card | Already in `papers/mem_2025.md`. |
| Real-Time Action Chunking with Large Models | 2025 | [PI research](https://www.pi.website/research/real_time_chunking) | To read | Official PI research list. |
| Precise Manipulation with Efficient Online RL | 2025 | [PI research](https://www.pi.website/research/rlt) | Existing card | Already in `papers/rlt_2025.md`. |

## NVIDIA / Stanford / Cosmos-DreamZero

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning | 2026 | [arXiv:2601.16163](https://arxiv.org/abs/2601.16163), [NVIDIA research](https://research.nvidia.com/labs/dir/cosmos-policy/) | Existing card | Already in `knowledge_base/vla/papers/cosmos_policy_2026.md`; explicit user target `cosmospolicy`. |
| DreamZero: World Action Models are Zero-shot Policies | 2026 | [arXiv:2602.15922](https://arxiv.org/abs/2602.15922), [project](https://dreamzero0.github.io/), [repo](https://github.com/dreamzero0/dreamzero) | Existing card | Already in `knowledge_base/vla/papers/dreamzero_2026.md`; explicit user target `dreamzero`. |

## Figure

Source: [Figure news page](https://www.figure.ai/news). These are technical/company releases; no standalone arXiv papers were confirmed in this pass.

| Release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Helix: A Vision-Language-Action Model for Generalist Humanoid Control | 2025 | [Figure news](https://www.figure.ai/news/helix) | Tech page only | Core Helix release. |
| Helix Accelerating Real-World Logistics | 2025 | [Figure news](https://www.figure.ai/news/helix-logistics) | Tech page only | Follow-up logistics deployment. |
| Scaling Helix: a New State of the Art in Humanoid Logistics | 2025 | [Figure news](https://www.figure.ai/news/scaling-helix-logistics) | Tech page only | Follow-up technical release. |
| Project Go-Big: Internet-Scale Humanoid Pretraining and Direct Human-to-Robot Transfer | 2025 | [Figure news](https://www.figure.ai/news/project-go-big) | Tech page only | Human-to-robot transfer at scale. |
| Introducing Helix 02: Full-Body Autonomy | 2026 | [Figure news](https://www.figure.ai/news/helix-02) | Tech page only | Follow-up system release. |

## AgiBot / 智元

Source: [AgiBot Research](https://agibot.com/research/).

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| AgiBot World & GO-1 | 2024 | [project](https://agibot-world.com), [AgiBot research](https://agibot.com/research/) | To read | Official AgiBot research page. |
| SOP: Scaling General-Purpose Robots in the Real World | 2025 | [AgiBot research](https://agibot.com/research/sop_en) | To read | Online updates of VLA models across fleets. |
| Genie Envisioner | 2024 | [AgiBot research](https://www.agibot.com/research/genie-envisioner) | To read | World foundation platform for manipulation. |
| Genie Centurion | 2025 | [arXiv:2505.18793](https://arxiv.org/abs/2505.18793) | Existing card | Already in `papers/genie_centurion_2025.md`. |

## Unitree / 宇树

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| UnifoLM-VLA-0 | 2026? | [GitHub search](https://github.com/search?q=UnifoLM-VLA-0&type=repositories) | Tech page only | No standalone paper confirmed in this pass. |
| UnifoLM-WMA-0 | 2026? | [GitHub search](https://github.com/search?q=UnifoLM-WMA-0&type=repositories) | Tech page only | No standalone paper confirmed in this pass. |
| UnifoLM-WBT-Dataset | 2026? | [GitHub search](https://github.com/search?q=UnifoLM-WBT-Dataset&type=repositories) | Tech page only | Dataset candidate; verify before learning. |

## Galaxea / 星海图

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Galaxea Open-World Dataset and G0 Dual-System VLA Model | 2025 | [arXiv:2509.00576](https://arxiv.org/abs/2509.00576) | To read | Explicit user target via 星海图. |
| Fast-WAM: Do World Action Models Need Test-time Future Imagination? | 2026 | [arXiv:2603.16666](https://arxiv.org/abs/2603.16666), [project](https://yuantianyuan01.github.io/FastWAM/) | To read | Explicit user target; authors overlap with Galaxea G0/Huazhe Xu/Hang Zhao ecosystem. |
| GR-RL: Going Dexterous and Precise for Long-Horizon Robotic Manipulation | 2025 | [arXiv:2512.01801](https://arxiv.org/abs/2512.01801) | To read | Explicit user target. |

## Galbot / 银河通用 / He Wang Ecosystem

Source: [He Wang publication page](https://hughw19.github.io/) and local VLN cards.

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| UrbanVLA: A Vision-Language-Action Model for Urban Micromobility | 2025 | [arXiv:2510.23576](https://arxiv.org/abs/2510.23576), [project](https://pku-epic.github.io/UrbanVLA-Web) | To read | Galbot / urban mobility VLA ecosystem. |
| TrackVLA: Embodied Visual Tracking in the Wild | 2025 | [arXiv:2505.23189](https://arxiv.org/abs/2505.23189), [project](https://pku-epic.github.io/TrackVLA-web/) | To read | Visual tracking VLA. |
| TrackVLA++: Unleashing Reasoning and Memory Capabilities in VLA Models for Embodied Visual Tracking | 2025 | [arXiv:2510.07134](https://arxiv.org/abs/2510.07134), [project](https://pku-epic.github.io/TrackVLA-plus-plus-Web) | To read | Follow-up to TrackVLA. |
| DexVLG: Dexterous Vision-Language-Grasp Model at Scale | 2025 | [arXiv:2507.02747](https://arxiv.org/abs/2507.02747) | To read | Dexterous grasp pose model. |
| SAGE: Bridging Semantic and Actionable Parts for Generalizable Manipulation of Articulated Objects | 2023 | [arXiv:2312.01307](https://arxiv.org/abs/2312.01307), [project](https://geometry.stanford.edu/projects/sage/) | To read | Earlier articulated-object manipulation line. |
| NaVid: Video-based VLM Plans the Next Step | 2024 | [arXiv:2402.15852](https://arxiv.org/abs/2402.15852), [project](https://pku-epic.github.io/NaVid/) | Existing VLN card | Already under `knowledge_base/vln/papers/navid_2024.md`. |
| Uni-NaVid | 2024 | [arXiv:2412.06224](https://arxiv.org/abs/2412.06224), [project](https://pku-epic.github.io/Uni-NaVid/) | Existing VLN card | Already under `knowledge_base/vln/papers/uni_navid_2024.md`. |
| NaVid-4D | 2025 | [project](https://lhrrhl0419.github.io/NaVid4D/) | To read | RGB-D egocentric navigation; exact arXiv link should be verified before learning. |

## Huazhe Xu / TEA Lab

Source: [Huazhe Xu publication page](https://hxu.rocks/publication.html). Filtered toward robotics, manipulation, VLA, tactile, and robot-learning work rather than every RL theory paper.

| Paper | Year | Link | Status | Notes |
|---|---:|---|---|---|
| UniDex: A Robot Foundation Suite for Universal Dexterous Hand Control from Egocentric Human Videos | 2026 | [arXiv:2603.22264](https://arxiv.org/abs/2603.22264) | To read | Explicit user target; Huazhe Xu is an author. |
| DemoSpeedup: Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration | 2025 | [arXiv:2506.05064](https://arxiv.org/abs/2506.05064), [project](https://demospeedup.github.io/) | To read | CoRL 2025 oral. |
| FACET: Force-Adaptive Control via Impedance Reference Tracking for Legged Robots | 2025 | [project](https://facet.pages.dev/) | To read | arXiv link on source page may need verification. |
| DemoGen: Synthetic Demonstration Generation for Data-Efficient Visuomotor Policy Learning | 2025 | [arXiv:2502.16932](https://arxiv.org/abs/2502.16932), [project](https://demo-generation.github.io/) | To read | RSS 2025. |
| DOGlove: Dexterous Manipulation with a Low-Cost Open-Source Haptic Force Feedback Glove | 2025 | [arXiv:2502.07730](https://arxiv.org/abs/2502.07730), [project](https://do-glove.github.io/) | To read | Dexterous teleoperation / haptics. |
| Reactive Diffusion Policy: Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation | 2025 | [arXiv:2503.02881](https://arxiv.org/abs/2503.02881), [project](https://reactive-diffusion-policy.github.io/) | To read | Contact-rich manipulation. |
| Two by Two: Learning Multi-task Pairwise Objects Assembly for Generalizable Robot Manipulation | 2025 | [arXiv:2504.06961](https://arxiv.org/abs/2504.06961), [project](https://tea-lab.github.io/TwoByTwo/) | To read | CVPR 2025. |
| RoboDuet: A Framework Affording Mobile-Manipulation and Cross-Embodiment | 2025 | [arXiv:2403.17367](https://arxiv.org/abs/2403.17367), [project](https://locomanip-duet.github.io/) | To read | Mobile manipulation / cross-embodiment. |
| Stem-OB: Generalizable Visual Imitation Learning with Stem-Like Convergent Observation through Diffusion Inversion | 2025 | [project](https://hukz18.github.io/Stem-Ob/) | To read | ICLR 2025 spotlight. |
| DenseMatcher: Learning 3D Semantic Correspondence for Category-Level Manipulation from a Single Demo | 2025 | [arXiv:2412.05268](https://arxiv.org/abs/2412.05268), [project](https://densematcher.github.io/) | To read | ICLR 2025 spotlight. |
| Robots Pre-Train Robots: Manipulation-Centric Robotic Representation from Large-Scale Robot Datasets | 2025 | [arXiv:2410.22325](https://arxiv.org/abs/2410.22325), [project](https://robots-pretrain-robots.github.io/) | To read | Robot representation pretraining. |
| Catch It! Learning to Catch in Flight with Mobile Dexterous Hands | 2025 | [arXiv:2409.10319](https://arxiv.org/abs/2409.10319), [project](https://mobile-dex-catch.github.io/) | To read | Mobile dexterous hands. |
| DTactive: A Vision-Based Tactile Sensor with Active Surface | 2024 | [arXiv:2410.08337](https://arxiv.org/abs/2410.08337), [project](https://ieqefcr.github.io/DTactive/) | To read | Tactile sensing. |
| Make-An-Agent: A Generalizable Policy Network Generator with Behavior-Prompted Diffusion | 2024 | [arXiv:2407.10973](https://arxiv.org/abs/2407.10973), [project](https://cheryyunl.github.io/make-an-agent/) | To read | Policy generation. |
| Learning to Manipulate Anywhere | 2024 | [arXiv:2407.15815](https://arxiv.org/abs/2407.15815), [project](https://gemcollector.github.io/maniwhere/) | To read | Visual generalizable RL. |
| RiEMann: Near Real-Time SE(3)-Equivariant Robot Manipulation without Point Cloud Segmentation | 2024 | [arXiv:2403.19460](https://arxiv.org/abs/2403.19460), [project](https://riemann-web.github.io/) | To read | 3D equivariant manipulation. |
| GenSim2: Scaling Robotic Data Generation with Multi-modal and Reasoning LLMs | 2024 | [arXiv:2410.03645](https://arxiv.org/abs/2410.03645), [project](https://gensim2.github.io/) | To read | Simulation/data generation. |
| Robo-ABC: Affordance Generalization Beyond Categories via Semantic Correspondence for Robot Manipulation | 2024 | [arXiv:2401.07487](https://arxiv.org/abs/2401.07487), [project](https://tea-lab.github.io/Robo-ABC/) | To read | Semantic correspondence. |
| Diffusion Reward: Learning Rewards via Conditional Video Diffusion | 2023 | [arXiv:2312.14134](https://arxiv.org/abs/2312.14134), [project](https://diffusion-reward.github.io/) | To read | Reward learning via video diffusion. |
| 3D Diffusion Policy | 2024 | [arXiv:2403.03954](https://arxiv.org/abs/2403.03954), [project](https://3d-diffusion-policy.github.io/) | To read | 3D policy baseline. |
| GenSim: Generating Robotic Simulation Tasks via Large Language Models | 2023 | [arXiv:2310.01361](https://arxiv.org/abs/2310.01361), [project](https://liruiw.github.io/gensim/) | To read | Predecessor to GenSim2. |

## Ego / Human-Video Related Works

This section is a cross-cutting reading cluster, intentionally separated from company grouping. Some entries also appear in company/team sections above.

| Paper / release | Organization / team | Year | Link | Status | Notes |
|---|---|---:|---|---|---|
| EgoMimic: Scaling Imitation Learning via Egocentric Video | Georgia Tech | 2024 | [arXiv:2410.24221](https://arxiv.org/abs/2410.24221) | Existing card | Foundation for ego-video co-training line. |
| EgoDex: Learning Dexterous Manipulation from Large-Scale Egocentric Video | Apple | 2025 | [arXiv:2505.11709](https://arxiv.org/abs/2505.11709), [code](https://github.com/apple/ml-egodex) | Existing card | Already in `papers/egodex_2025.md`. |
| EgoScale: Scaling Dexterous Manipulation with Diverse Egocentric Human Data | NVIDIA | 2026 | [arXiv:2602.16710](https://arxiv.org/abs/2602.16710), [project](https://research.nvidia.com/labs/gear/egoscale/) | Existing card | Already in `papers/egoscale_2026.md`. |
| EgoVLA: Learning VLA Models from Egocentric Human Videos | NVIDIA | 2025 | [arXiv:2507.12440](https://arxiv.org/abs/2507.12440) | To read | Directly related to EgoScale/EgoDex line. |
| EgoZero: Robot Learning from Smart Glasses | UC Berkeley | 2025 | [arXiv:2505.20290](https://arxiv.org/abs/2505.20290) | To read | Smart-glasses ego data line. |
| EMMA: Scaling Mobile Manipulation via Egocentric Human Data | Stanford | 2025 | [arXiv:2509.04443](https://arxiv.org/abs/2509.04443) | To read | Mobile manipulation + ego data. |
| MimicDreamer: Aligning Human and Robot Demonstrations for Scalable VLA Training | GigaAI | 2025 | [arXiv:2509.22199](https://arxiv.org/abs/2509.22199), [repo](https://github.com/GigaAI-research/MimicDreamer) | To read | Human manipulation videos + robot demos for scalable VLA training. |
| EgoDemoGen: Novel Egocentric Demonstration Generation Enables Viewpoint-Robust Manipulation | GigaAI / academic collaborators | 2025 | [arXiv:2509.22578](https://arxiv.org/abs/2509.22578), [project](https://egodemogen.github.io/) | To read | Ego-view demonstration generation for manipulation robustness. |
| EgoHumanoid: Unlocking In-the-Wild Loco-Manipulation with Robot-Free Egocentric Demonstrations | TBD | 2026 | [arXiv:2602.10106](https://arxiv.org/abs/2602.10106) | To read | Humanoid loco-manipulation from ego demos. |
| Uni-Hand: Universal Hand Motion Forecasting in Egocentric Views | TBD | 2025 | [arXiv:2511.12878](https://arxiv.org/abs/2511.12878) | To read | Hand-motion forecasting and policy transfer. |
| HaWoR: World-Space Hand Motion Reconstruction from Egocentric Videos | TBD | 2025 | [arXiv:2501.02973](https://arxiv.org/abs/2501.02973) | To read | Useful for hand-pose preprocessing. |
| MEgoHand: Multimodal Egocentric Hand-Object Interaction Motion Generation | BeingBeyond | 2025 | [arXiv:2505.16602](https://arxiv.org/abs/2505.16602), [project](https://beingbeyond.github.io/MEgoHand/) | To read | Also listed under BeingBeyond. |
| OpenMMEgo: Enhancing Egocentric Understanding for LMMs with Open Weights and Data | BeingBeyond | 2025 | [NeurIPS page](https://neurips.cc/virtual/2025/loc/san-diego/poster/119544), [repo](https://github.com/BeingBeyond/OpenMMEgo) | To read | Ego-video LMM understanding. |
| Being-H0 / H0.5 / H0.7 | BeingBeyond | 2025-2026 | [Being-H repo](https://github.com/BeingBeyond/Being-H) | To read / Existing card | Human-video pretraining family. |
| UniDex: A Robot Foundation Suite for Universal Dexterous Hand Control from Egocentric Human Videos | Huazhe Xu / TEA Lab | 2026 | [arXiv:2603.22264](https://arxiv.org/abs/2603.22264) | To read | Explicit user target; bridges ego video and dexterous hand control. |
| EgoVerse | TBD | TBD | [search](https://www.google.com/search?q=EgoVerse+robotics+arXiv) | Needs verification | Exact intended paper/entity still unclear. |

## UBTECH / 优必选

| Paper / release | Year | Link | Status | Notes |
|---|---:|---|---|---|
| Thinker / Thinker-VLA / Thinker-WM | 2025-2026 | [UBTECH annual report source](https://m.10jqka.com.cn/20260421/c668407427.shtml) | Tech page only | Search found company/model references, but no standalone ThinkerVLA paper was confirmed in this pass. |
| VLA-Thinker | 2026 | [arXiv:2603.14523](https://arxiv.org/abs/2603.14523) | Needs verification | Similar name to ThinkerVLA, but not confirmed as UBTECH. Track separately. |

## Unresolved / Follow-Up Search Items

| Query | Current finding | Next step |
|---|---|---|
| EgoVerse | Exact robotics paper/entity not resolved. | Ask user if they mean a specific EgoVerse project, or rerun focused search. |
| UBTECH ThinkerVLA | UBTECH Thinker/Thinker-WM appears in company materials; no standalone ThinkerVLA paper confirmed. | Check UBTECH official technical reports, GitHub, and Chinese media releases. |
| Unitree UnifoLM | Unitree UnifoLM names appear as release candidates; no standalone paper confirmed. | Verify official Unitree GitHub/project pages before learning. |
| GigaAI HF activity entries | `GeoWorld` and `MWM` appear in GigaAI-Research HF activity, but company affiliation/ownership is not clear from primary project pages. | Verify whether to treat them as GigaAI papers or adjacent world-model works. |
| GigaAI EMMA repo | A `GigaAI-research/EMMA` repo exists but was empty in this pass; the resolved EMMA paper in this list is Stanford's arXiv:2509.04443. | Recheck if GigaAI later publishes a distinct EMMA page/paper. |

## Source Pages Checked

- [BeingBeyond GitHub org](https://github.com/BeingBeyond)
- [Being-H family repo](https://github.com/BeingBeyond/Being-H)
- [Being-H0.7 official page](https://research.beingbeyond.com/being-h07)
- [GigaAI-research GitHub org](https://github.com/GigaAI-research)
- [open-gigaai GitHub org](https://github.com/open-gigaai)
- [GigaAI-Research Hugging Face papers](https://huggingface.co/GigaAI-Research/papers)
- [Cosmos Policy NVIDIA page](https://research.nvidia.com/labs/dir/cosmos-policy/)
- [DreamZero project page](https://dreamzero0.github.io/)
- [Physical Intelligence research page](https://www.pi.website/research)
- [Figure news page](https://www.figure.ai/news)
- [AgiBot Research page](https://agibot.com/research/)
- [Huazhe Xu publication page](https://hxu.rocks/publication.html)
- [He Wang / Galbot-related publication page](https://hughw19.github.io/)
- arXiv pages linked in the tables above.
