# Paper Reader — 论文速读工具

## 项目概述
基于 Claude API + Tool Use 的论文速读 Agent，自动分析论文、构建领域知识库、同步到飞书。
支持多领域分区管理，每个领域独立维护知识体系和调研报告。

## 目录结构
```
paper_reader/
├── paper_reader.py          # 核心 Agent（PDF提取 + Claude API Tool Use 循环）
├── feishu_sync.py           # 飞书知识库同步（Markdown → 飞书文档 blocks）
├── .feishu_sync_state.json  # 飞书同步状态（节点 token 映射，勿手动修改）
├── pdf_cache/               # 下载的 PDF 缓存
├── README.md                # 整体规划文档
└── knowledge_base/          # 本地知识库（核心数据）
    ├── index.md             # 跨领域总览 Dashboard
    └── vla/                 # VLA 领域（第一个领域）
        ├── index.md         # L0: VLA 领域总览
        ├── reports/         # 调研报告（交叉分析）
        │   └── index.md    # 报告清单
        ├── methods/         # 方法分类
        │   ├── index.md
        │   ├── diffusion_policy.md
        │   ├── vlm_action_token.md
        │   ├── vlm_diffusion_head.md
        │   ├── transformer_diffusion_head.md
        │   └── hierarchical_vla.md
        ├── papers/          # 论文卡片
        │   ├── index.md
        │   ├── pi05_2025.md
        │   ├── pi0_2024.md
        │   ├── openvla_2024.md
        │   ├── octo_2024.md
        │   ├── diffusion_policy_2023.md
        │   └── rt2_2023.md
        ├── components/      # 技术组件
        │   ├── index.md
        │   └── data_strategy.md
        ├── tasks/           # 任务类型
        │   └── index.md
        └── benchmarks/      # 评测体系
            └── index.md
```

新增领域时，在 `knowledge_base/` 下创建同结构的子目录即可（如 `world_models/`）。

## 使用方式

```bash
# 分析一篇论文（支持 arXiv ID、URL、本地 PDF）
python paper_reader.py read 2504.16054
python paper_reader.py read https://arxiv.org/abs/2504.16054
python paper_reader.py read /path/to/paper.pdf

# 指定领域（默认 vla）
python paper_reader.py read 2504.16054 --domain vla

# 批量分析
python paper_reader.py batch /path/to/pdfs/

# 基于知识库问答
python paper_reader.py ask "action chunking 和 diffusion policy 的区别"

# 调研相关论文（收集引用关系）
python paper_reader.py survey 2504.16054 2410.24164 --name vla_survey

# 生成调研报告（基于知识库的交叉分析）
python paper_reader.py report "VLA方法路线对比"
python paper_reader.py report "开源VLA现状" --papers pi0_2024 openvla_2024 octo_2024

# 同步到飞书
python feishu_sync.py                # 同步所有领域
python feishu_sync.py --domain vla   # 只同步指定领域
python feishu_sync.py --rebuild      # 重建飞书结构
```

## 技术细节

### Agent 架构
- 模型: `claude-opus-4-6`（当前 API key 仅支持此模型）
- 环境变量 `PAPER_READER_MODEL` 可覆盖模型选择
- 最大 tool use 轮数: 15
- API key 和 base URL 从环境变量读取（ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL）

### Agent 工具
1. `read_knowledge` — 读取知识库文件（渐进式加载，基于当前领域目录）
2. `update_knowledge` — 写入/更新知识库文件
3. `search_papers` — 搜索已有论文卡片
4. `list_knowledge` — 列出知识库目录结构

### 多领域架构
- 所有命令支持 `--domain` 参数，默认 `vla`
- 工具操作的路径相对于领域目录（如 `papers/xxx.md` 实际对应 `knowledge_base/vla/papers/xxx.md`）
- 新增领域只需创建 `knowledge_base/<domain>/index.md`，飞书同步会自动发现

### 调研报告
- `report` 命令使用专门的 `REPORT_SYSTEM_PROMPT`，指导 Agent 做交叉分析
- 报告保存在 `<domain>/reports/` 目录
- 可指定 `--papers` 缩小分析范围，否则 Agent 自动选择相关论文

### 知识库层级原则
| 层级 | 内容 | 加载时机 |
|------|------|----------|
| L0 index.md | 领域全貌 | 每次都加载 |
| L1 子目录 index.md | 方向脉络 | Agent 判断相关时 |
| L2 具体文件 | 技术细节 | 需要深入对比时 |
| 论文卡片 | 单篇结构化信息 | 需要引用时 |
| 调研报告 | 多论文交叉分析 | 按需查阅 |

### PDF 处理
- 使用 PyMuPDF (fitz) 提取文本
- 最多提取 30 页，文本截断 80K 字符
- arXiv PDF 自动下载并缓存到 pdf_cache/

### 飞书同步
- 飞书 App: cli_a927261c6b78dcee
- 知识库「科研」space_id: 7615497891934751969
- 同步结构: Paper Reading → 总览 Dashboard + 各领域子树
- 飞书树结构:
  ```
  Paper Reading/
  ├── 总览 Dashboard
  └── VLA（视觉-语言-动作模型）/
      ├── 领域总览
      ├── 调研报告/
      ├── 论文卡片/
      ├── 方法分类/
      ├── 技术组件/
      ├── 评测体系/
      └── 任务类型/
  ```
- 自动发现领域目录，按领域独立同步
- 支持 `--rebuild` 重建（清空状态，不删旧节点）
- 同步状态持久化在 .feishu_sync_state.json
- Markdown → 飞书 blocks 转换支持: 标题、段落、列表、代码块、引用、加粗、行内代码
- 表格自动转为飞书原生表格（block_type 31），失败时回退代码块
- 支持增量同步：通过 MD5 hash 对比，只同步变更的文件
- 支持 `--force` 强制全量同步
- 支持 `pull` 反向同步：从飞书下载到本地，带冲突检测
- 每次 batch 最多 40 个 blocks，避免 API 限速

### 已知问题
- 反向同步的表格转换为 `[表格 — 需手动检查]` 占位符
- 论文文本超长时（>80K 字符）会截断，可能丢失附录信息
- 旧版飞书节点（扁平结构）需要手动清理，rebuild 后会在新 VLA 节点下重建

## 网络与代理

### 直连可用（无需代理）
| 服务 | 地址 | 用途 |
|------|------|------|
| Claude API | `apicz.boyuerichdata.com` | Agent 核心 |
| 飞书 API | `open.feishu.cn` | 知识库同步 |
| arXiv | `arxiv.org` | PDF 下载 |
| Semantic Scholar | `api.semanticscholar.org` | 引用/参考文献 |

### 需要代理
| 服务 | 地址 | 用途 |
|------|------|------|
| Brave Search | `api.search.brave.com` | 论文搜索（MCP 工具） |

### 代理配置
- Clash 代理：`bash /inspire/hdd/global_user/guchun-240107140023/modules/clash-for-linux/run.sh`（别名 `clash_on`）
- 代理端口：`127.0.0.1:7890`（HTTP/SOCKS5）
- **不要设全局 `https_proxy`**，会干扰飞书和 Claude API 等国内服务
- 仅在 `.mcp.json` 中为 Brave Search MCP 单独配置代理
- Brave Search API Key 存放于 `/root/.openclaw/openclaw.json` 的 `tools.web.search.apiKey`

### Brave Search MCP 代理修复
Node.js 22 的原生 `fetch()`（基于 undici）**不会**自动读取 `http_proxy`/`https_proxy` 环境变量。
修复方式：在 `/usr/local/bin/mcp-server-brave-search` 入口文件 shebang 后注入：
```js
import { setGlobalDispatcher, ProxyAgent } from 'undici';
const _proxy = process.env.https_proxy || process.env.http_proxy;
if (_proxy) { try { setGlobalDispatcher(new ProxyAgent(_proxy)); } catch(e) {} }
```
- 全局安装了 `undici` 包（`npm install -g undici`）
- `.mcp.json` 中同时配置了 `NODE_OPTIONS: "--import /usr/local/lib/proxy-preload.mjs"` 作为备选方案
- ⚠️ 如果 `npm update -g @modelcontextprotocol/server-brave-search`，入口文件会被覆盖，需重新注入

## 运行环境
- **Conda 环境**: `paper_reader`（Python 3.10）
- 激活: `conda activate paper_reader`
- 运行: `conda run -n paper_reader python paper_reader.py ...`
- 飞书同步: `conda run -n paper_reader python feishu_sync.py ...`

### 依赖
```
anthropic    # Claude API
pymupdf      # PDF 文本提取（import fitz）
requests     # HTTP 请求（飞书 API、arXiv 下载）
```

## 已实现功能
- [x] paper_reader.py 分析完自动触发飞书同步（`--no-sync` 可跳过）
- [x] 增量同步（MD5 hash 对比，`--force` 可强制全量）
- [x] 飞书表格支持（block_type 31 原生表格，失败回退代码块）
- [x] 论文引用图谱自动生成（`python paper_reader.py graph`，Mermaid 格式）
- [x] 飞书反向同步（`python feishu_sync.py pull`，带冲突检测）
