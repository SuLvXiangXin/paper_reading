# 论文引用图谱

```mermaid
graph TD

    diffusion_policy_2023["Diffusion Policy: Visuomotor Pol...<br/>2023"]
    octo_2024["Octo: An Open-Source Generalist ...<br/>2024"]
    openvla_2024["OpenVLA: An Open-Source Vision-L...<br/>2024"]
    pi05_2025["π0.5: a Vision-Language-Action M...<br/>2025"]
    pi0_2024["π0: A Vision-Language-Action Flo...<br/>2024"]
    rt2_2023["RT-2: Vision-Language-Action Mod...<br/>2023"]

    rt2_2023 --> pi0_2024
    pi0_2024 --> pi05_2025
    diffusion_policy_2023 --> octo_2024
    pi0_2024 --> openvla_2024
    openvla_2024 --> pi0_2024
    octo_2024 --> pi0_2024
    rt2_2023 --> octo_2024
    openvla_2024 --> octo_2024
    pi0_2024 --> octo_2024
    rt2_2023 --> openvla_2024
    diffusion_policy_2023 --> pi0_2024
    octo_2024 --> openvla_2024
    diffusion_policy_2023 --> openvla_2024

    classDef method0 fill:#4CAF50,color:#fff,stroke:#333
    class diffusion_policy_2023 method0
    classDef method1 fill:#2196F3,color:#fff,stroke:#333
    class octo_2024 method1
    classDef method2 fill:#FF9800,color:#fff,stroke:#333
    class openvla_2024,rt2_2023 method2
    classDef method3 fill:#9C27B0,color:#fff,stroke:#333
    class pi05_2025,pi0_2024 method3
```

## 方法线分类

| 论文 | 年份 | 方法线 |
|------|------|--------|
| Diffusion Policy: Visuomotor Policy Learning via A | 2023 | Diffusion Policy |
| RT-2: Vision-Language-Action Models Transfer Web K | 2023 | VLM + Action Token |
| Octo: An Open-Source Generalist Robot Policy (2024 | 2024 | Transformer + Diffusion Head |
| OpenVLA: An Open-Source Vision-Language-Action Mod | 2024 | VLM + Action Token |
| π0: A Vision-Language-Action Flow Model for Genera | 2024 | VLM + Diffusion/Flow Head |
| π0.5: a Vision-Language-Action Model with Open-Wor | 2025 | VLM + Diffusion/Flow Head |

## 时间线

- **2023** Diffusion Policy: Visuomotor Policy Learning via Action Diff
- **2023** RT-2: Vision-Language-Action Models Transfer Web Knowledge t
- **2024** Octo: An Open-Source Generalist Robot Policy (2024) ← 基于 diffusion_policy_2023, rt2_2023, openvla_2024, pi0_2024
- **2024** OpenVLA: An Open-Source Vision-Language-Action Model (2024) ← 基于 pi0_2024, rt2_2023, octo_2024, diffusion_policy_2023
- **2024** π0: A Vision-Language-Action Flow Model for General Robot Co ← 基于 rt2_2023, openvla_2024, octo_2024, diffusion_policy_2023
- **2025** π0.5: a Vision-Language-Action Model with Open-World General ← 基于 pi0_2024