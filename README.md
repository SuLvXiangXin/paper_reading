# Paper Reader — 论文速读工具规划

## 目标

用最少的时间抓住每篇论文的核心内容，构建可积累的领域知识库。

---

## 整体架构

```
PDF论文 → Agent 分析（渐进式加载知识库）→ 写入 Markdown → 同步到飞书 → 手机/电脑查看
```

---

## 一、知识库设计（本地 Markdown，层级结构）

```
knowledge_base/
├── index.md                    # L0: 领域总览（500字以内）
│
├── methods/                    # 方法分类
│   ├── index.md                # L1: 方法分类概览
│   ├── vlm_action_token.md     # L2: VLM 直接输出动作（RT-2, OpenVLA）
│   ├── vlm_diffusion_head.md   # L2: VLM + 扩散/flow head（π₀, RDT）
│   ├── reward_learning.md      # L2: 奖励学习路线
│   └── world_model.md          # L2: 世界模型路线
│
├── tasks/                      # 任务类型
│   ├── index.md                # L1: 任务类型概览
│   ├── manipulation.md         # L2: 抓取/操作
│   ├── navigation.md           # L2: 导航
│   └── dexterous.md            # L2: 灵巧手
│
├── components/                 # 通用技术组件
│   ├── index.md                # L1: 技术组件概览
│   ├── action_repr.md          # L2: 动作表示（chunk, discrete, continuous）
│   ├── vision_encoder.md       # L2: 视觉编码器
│   └── data_strategy.md        # L2: 数据策略（co-training, augmentation）
│
├── benchmarks/                 # 评测体系
│   ├── index.md                # L1: 评测概览
│   └── ...
│
└── papers/                     # 论文卡片
    ├── index.md                # 论文清单 + 一句话总结
    ├── pi0_2024.md
    ├── rt2_2023.md
    └── ...
```

### 层级原则

| 层级 | 内容 | 长度 | 加载时机 |
|------|------|------|----------|
| L0 `index.md` | 整个领域的地图 | ~500 字 | 每次都加载 |
| L1 子目录 `index.md` | 某方向的脉络和演进 | ~1000 字 | Agent 判断相关时加载 |
| L2 具体主题 | 技术细节、对比 | ~2000 字 | 需要深入分析时加载 |
| 论文卡片 | 单篇论文结构化信息 | ~300 字 | 需要对比时加载 |

### 渐进式加载逻辑

```
用户给一篇新论文
  → Agent 先读 L0 index.md（了解领域全貌）
  → 读论文 abstract，判断属于哪个方向
  → 加载对应的 L1 index
  → 需要细节对比时再加载 L2
  → 生成论文卡片 + 更新知识库
```

---

## 二、Agent 设计

### 技术方案：Claude API + Tool Use

Agent 拥有 3 个工具：

```python
tools = [
    {
        "name": "read_knowledge",
        "description": "读取知识库中的某个文件",
        "input_schema": {
            "properties": {
                "path": {"type": "string", "description": "知识库内的相对路径，如 methods/vlm_diffusion_head.md"}
            }
        }
    },
    {
        "name": "update_knowledge",
        "description": "更新或创建知识库文件",
        "input_schema": {
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            }
        }
    },
    {
        "name": "search_papers",
        "description": "在已有论文卡片中搜索关键词",
        "input_schema": {
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
]
```

### 调用流程

```python
# 核心循环
while True:
    response = client.messages.create(
        model="claude-sonnet-4-6",    # 日常用 Sonnet（便宜快）
        system=SYSTEM_PROMPT,          # 包含角色定义和知识库使用规则
        messages=messages,
        tools=tools
    )

    if response.stop_reason == "tool_use":
        tool_result = execute_tool(response)
        messages.append(tool_result)
    else:
        break  # Agent 完成，输出最终结果
```

### 模型选择策略

| 场景 | 模型 | 理由 |
|------|------|------|
| 日常论文速读 | Sonnet | 便宜快，够用 |
| 深度分析/对比 | Opus | 推理能力强 |
| 批量处理摘要 | Haiku | 最便宜，适合简单提取 |

---

## 三、论文卡片模板

每篇论文生成一个结构化卡片：

```markdown
# 论文名 (年份)

## 基本信息
- 作者：xxx
- 机构：xxx
- 链接：arXiv:xxxx.xxxxx

## 一句话总结
xxx

## 问题
解决什么问题？

## 方法
- 方法线归属：VLM + Diffusion Head / VLM Action Token / ...
- 核心 idea：1-2 句话
- 关键技术点：

## 实验
- Benchmark：xxx
- 主要结果：xxx
- 对比基线：xxx

## 评价
- 优势：
- 局限：
- 对我们的启发：
```

---

## 四、展示层：飞书同步

### 同步方式

Agent 每分析完一篇论文 → 调用飞书 API → 自动创建/更新文档

### 飞书文档结构（与知识库目录对应）

```
飞书知识库/
├── VLA 领域总览
├── 方法分类/
│   ├── VLM 直接输出动作
│   ├── VLM + 扩散头
│   └── ...
├── 论文卡片/
│   ├── π₀ (2024)
│   ├── RT-2 (2023)
│   └── ...
└── 阅读清单
```

### 需要实现的飞书 API 调用

1. 创建文档：`POST /open-apis/docx/v1/documents`
2. 更新内容：`PATCH /open-apis/docx/v1/documents/:document_id/blocks`
3. Markdown → 飞书 Block 格式转换

### 飞书 API 准备工作

- [ ] 创建飞书应用（开发者后台）
- [ ] 获取 App ID 和 App Secret
- [ ] 开通文档权限（docx:document:write）
- [ ] 创建目标知识库空间

---

## 五、使用流程

### 单篇论文速读

```bash
python paper_reader.py read paper.pdf
# 或
python paper_reader.py read https://arxiv.org/abs/xxxx.xxxxx
```

输出：论文卡片（终端显示 + 写入知识库 + 同步飞书）

### 批量处理

```bash
python paper_reader.py batch papers/  # 处理整个文件夹的 PDF
```

### 知识库查询

```bash
python paper_reader.py ask "action chunking 和 diffusion policy 的区别"
```

---

## 六、实现优先级

| 阶段 | 内容 | 预计工作量 |
|------|------|-----------|
| **P0** | 知识库目录结构 + 手动填充几篇核心论文 | 先用 Claude Code 手动跑 |
| **P1** | Agent 核心脚本（PDF 读取 + Tool Use 循环） | ~200 行 Python |
| **P2** | 飞书同步模块 | ~100 行 Python |
| **P3** | 批量处理 + CLI 界面 | ~100 行 Python |
| **P4** | 知识库自动聚类和演进分析 | 进阶功能 |

### 建议执行顺序

1. 先用 Claude Code 手动分析 5-10 篇核心论文，验证知识库结构
2. 结构稳定后写 P1 Agent 脚本
3. 加上飞书同步
4. 最后做批量和 CLI

---

## 七、目录结构（本仓库）

```
paper_reader/
├── README.md              # 本文件：整体规划
├── paper_reader.py        # 主脚本（待实现）
├── feishu_sync.py         # 飞书同步模块（待实现）
├── config.yaml            # 配置（API key、飞书凭证、知识库路径等）
└── knowledge_base/        # 知识库（核心数据）
    ├── index.md
    ├── methods/
    ├── tasks/
    ├── components/
    ├── benchmarks/
    └── papers/
```
