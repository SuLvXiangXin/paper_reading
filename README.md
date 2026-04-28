# Paper Reader

本仓库现在是一个以 `knowledge_base/` 为核心的数据仓库，外加两套使用入口：

- `paper_reader.py`：命令行论文处理与知识库问答
- `paper_reader_web/` + `start_web.sh`：本地 Web 阅读与侧边栏 Codex 问答

## 当前功能

- 读取 arXiv ID、arXiv URL 或本地 PDF
- 基于现有领域知识库生成/更新论文卡片
- 按领域做问答、survey、report、graph
- 在本地 Web 中浏览知识库并对单页发起 Codex 问答

## 目录

```text
paper_reader/
├── paper_reader.py
├── codex_runner.py
├── paper_reader_web/
├── start_web.sh
├── knowledge_base/
├── pdf_cache/
└── web/
```

## 环境

推荐使用 `paper_reader` conda 环境：

```bash
conda run -n paper_reader python paper_reader.py --help
```

运行依赖：

- 本地 `codex` CLI
- `pymupdf`
- `requests`

常用环境变量：

- `PAPER_READER_CODEX_MODEL`
- `PAPER_READER_CODEX_TIMEOUT_SECONDS`
- `PAPER_READER_WEB_CODEX_MODEL`
- `PAPER_READER_WEB_CODEX_REASONING_EFFORT`
- `PAPER_READER_WEB_CODEX_TIMEOUT_SECONDS`
- `PAPER_READER_WEB_PORT`

如果本机访问 Codex 或 Brave Search 依赖代理，先在启动 shell 中设置好 `http_proxy` / `https_proxy`，`start_web.sh` 会把它们传给 Web 服务。

## CLI 用法

分析单篇论文：

```bash
conda run -n paper_reader python paper_reader.py read 2504.16054 --domain vla
conda run -n paper_reader python paper_reader.py read https://arxiv.org/abs/2504.16054 --domain vla
conda run -n paper_reader python paper_reader.py read /path/to/paper.pdf --domain vla
```

跳过自动 `git push`：

```bash
conda run -n paper_reader python paper_reader.py read 2504.16054 --domain vla --no-sync
```

知识库问答：

```bash
conda run -n paper_reader python paper_reader.py ask "action chunking 和 diffusion policy 的区别" --domain vla
```

交叉调研：

```bash
conda run -n paper_reader python paper_reader.py survey 2504.16054 2410.24164 --name vla_survey --domain vla
conda run -n paper_reader python paper_reader.py report "VLA RL 后训练路线对比" --domain vla
conda run -n paper_reader python paper_reader.py graph --domain vla
```

## Web 用法

启动服务：

```bash
./start_web.sh
```

启动后会打印本地地址和 notebook 代理地址。Web 端支持：

- 左侧知识库树浏览
- 主页搜索与论文筛选
- 文档页 Markdown 阅读
- 右侧 Codex 侧边栏问答

## 知识库约定

`knowledge_base/<domain>/` 下通常包含：

- `index.md`
- `papers/`
- `methods/`
- `components/`
- `tasks/`
- `benchmarks/`
- `reports/`

新增论文时，优先更新：

1. `papers/<paper>.md`
2. `papers/index.md`
3. 必要时更新对应方法线 / 组件 / benchmark / report

## 验证

代码检查：

```bash
python -m py_compile paper_reader.py codex_runner.py paper_reader_web/*.py
```

快速查看仓库状态：

```bash
git status --short
```
