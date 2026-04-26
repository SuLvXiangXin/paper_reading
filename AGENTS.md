# Repository Instructions

## Purpose

This repository is a paper-reading knowledge base and automation tool. The core workflow is:

```text
PDF/arXiv paper -> extract text -> agent reads domain knowledge progressively -> update Markdown knowledge base -> git push -> GitHub Pages deploy
```

The goal is not to produce isolated summaries. Each new paper should be positioned inside the existing domain map: method line, task type, technical components, benchmarks, related papers, and research trend.

## Important Files

- `paper_reader.py`: main CLI and local Codex CLI agent.
- `feishu_sync.py`: local Markdown <-> Feishu wiki sync.
- `README.md`: planning document and high-level design.
- `mkdocs.yml`: MkDocs Material configuration. `knowledge_base/` is the docs root.
- `.github/workflows/deploy.yml`: deploys MkDocs to GitHub Pages on pushes to `master`.
- `knowledge_base/`: source of truth for all domain knowledge.
- `pdf_cache/`: cached downloaded arXiv PDFs.

## Knowledge Base Structure

`knowledge_base/` contains multiple domains:

- `vla`
- `video_world_model`
- `vln`
- `whole_body_control`
- `locomotion`
- `image_generation`

Each mature domain usually has:

- `index.md`: domain overview and method/task/component map.
- `papers/`: individual paper cards and `papers/index.md`.
- `methods/`: method taxonomy and detailed method-line notes.
- `components/`: reusable technical components.
- `tasks/`: task categories.
- `benchmarks/`: evaluation suites.
- `reports/`: cross-paper survey reports.

When adding a new domain, create `knowledge_base/<domain>/index.md` and follow the same subdirectory conventions.

## Environment

Use the `paper_reader` conda environment:

```bash
conda run -n paper_reader python paper_reader.py --help
```

Runtime dependencies include:

- local `codex` CLI on `PATH`
- `pymupdf` / `fitz`
- `requests`

The agent reads these environment variables:

- `PAPER_READER_CODEX_MODEL` optional; if unset, the local Codex CLI default model/profile is used.
- `PAPER_READER_CODEX_TIMEOUT_SECONDS` optional timeout for Codex CLI calls.
- `FEISHU_APP_SECRET` for Feishu sync.

## Common Commands

Analyze one paper:

```bash
conda run -n paper_reader python paper_reader.py read 2504.16054 --domain vla
conda run -n paper_reader python paper_reader.py read https://arxiv.org/abs/2504.16054 --domain vla
conda run -n paper_reader python paper_reader.py read /path/to/paper.pdf --domain vla
```

Skip the automatic git commit/push:

```bash
conda run -n paper_reader python paper_reader.py read 2504.16054 --domain vla --no-sync
```

Ask against the knowledge base:

```bash
conda run -n paper_reader python paper_reader.py ask "action chunking 和 diffusion policy 的区别" --domain vla
```

Generate a cross-paper report:

```bash
conda run -n paper_reader python paper_reader.py report "VLA RL 后训练路线对比" --domain vla
```

Collect related papers from citations/references:

```bash
conda run -n paper_reader python paper_reader.py survey 2504.16054 2410.24164 --name vla_survey --domain vla
```

Generate a Mermaid paper graph:

```bash
conda run -n paper_reader python paper_reader.py graph --domain vla
```

Sync Markdown to Feishu:

```bash
conda run -n paper_reader python feishu_sync.py --domain vla
```

Pull from Feishu with conflict checks:

```bash
conda run -n paper_reader python feishu_sync.py pull --domain vla
```

## Paper Learning Workflow

When given a paper:

1. Identify the correct domain. Default is `vla`, but choose another domain if the paper is clearly about VLN, video world models, locomotion, whole-body control, or image generation.
2. Read the domain overview first: `knowledge_base/<domain>/index.md`.
3. Read relevant `methods/index.md`, `components/index.md`, `tasks/index.md`, `benchmarks/index.md`, and existing related paper cards only as needed.
4. Extract the paper's core contribution, not every detail.
5. Classify the paper into an existing method line when possible.
6. Create or update a paper card under `knowledge_base/<domain>/papers/`.
7. Update `papers/index.md` with a concise one-line summary.
8. Update method/component/task/benchmark files if the paper adds a new concept, changes an existing taxonomy, or provides an important new result.
9. For broad comparisons, create or update a report under `reports/`.

Use the paper card format expected by `paper_reader.py`:

```markdown
# Paper Name (Year)

## 基本信息
- 作者: xxx
- 机构: xxx
- arXiv: xxxx.xxxxx

## 一句话总结
xxx

## 问题
解决什么问题?

## 方法
- 方法线归属: xxx
- 核心 idea: xxx
- 关键技术点:
  - xxx

## 实验
- Benchmark: xxx
- 主要结果: xxx
- 对比基线: xxx

## 评价
- 优势: xxx
- 局限: xxx
- 对 VLA 领域的贡献: xxx
```

## Implementation Notes

- `paper_reader.py read` supports arXiv IDs, arXiv URLs, and local PDFs.
- arXiv PDFs are downloaded to `pdf_cache/`.
- PDF extraction uses PyMuPDF, up to 30 pages and about 80K characters.
- Tool paths inside the agent are relative to the active domain directory, for example `papers/pi0_2024.md` maps to `knowledge_base/vla/papers/pi0_2024.md`.
- The agent runs through local `codex exec`; repository reads/searches/writes are done by the Codex CLI in the selected sandbox.
- `read` currently calls `_git_push()` after analysis unless `--no-sync` is used. It does not directly call `feishu_sync.py`.
- GitHub Pages deployment is triggered by pushing changes to `knowledge_base/**`, `mkdocs.yml`, or the deploy workflow on branch `master`.
- Feishu sync is incremental via MD5 hashes stored in `.feishu_sync_state.json`.
- Do not manually edit `.feishu_sync_state.json` unless explicitly repairing sync state.

## Editing Guidelines

- Treat `knowledge_base/` Markdown as the primary data.
- Keep paper summaries concise and comparative. Avoid generic abstract paraphrases.
- Preserve existing taxonomy wording unless there is a clear reason to revise it.
- When updating index tables, keep links relative and consistent with nearby rows.
- If adding a new method line, update both the relevant `methods/*.md` file and the domain `index.md`.
- If a paper is not enough to justify changing global taxonomy, only add the paper card and `papers/index.md` entry.
- Avoid unrelated formatting churn in large Markdown tables.

## Network Notes

- Direct access is expected for the local Codex CLI backend, Feishu API, arXiv, and Semantic Scholar.
- Brave Search MCP may require the configured Clash proxy.
- Current proxy endpoint is `127.0.0.1:16068` for HTTP/SOCKS5.
- Do not set a global `https_proxy` by default because it may break domestic services used by this repo.

## Verification

For code changes:

```bash
python -m py_compile paper_reader.py feishu_sync.py
```

For docs/site changes:

```bash
mkdocs build
```

For a quick repository check:

```bash
git status --short
```
